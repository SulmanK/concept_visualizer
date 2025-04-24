# apiClient

The `apiClient` is the central service for making HTTP requests to the application's backend API. It provides a standardized interface for API communication with built-in error handling, authentication, and rate limit management.

## Overview

This service acts as the foundation for all API interactions in the application. It:

- Manages authentication tokens
- Handles common HTTP request patterns (GET, POST, etc.)
- Translates HTTP errors into application-specific error types
- Processes rate limit information
- Retries failed requests when appropriate
- Manages request cancellation

## Core API

### HTTP Methods

```typescript
// GET request
async function get<T>(
  endpoint: string,
  options?: RequestOptions,
): Promise<{ data: T }>;

// POST request
async function post<T>(
  endpoint: string,
  body: any,
  options?: RequestOptions,
): Promise<{ data: T }>;

// PUT request
async function put<T>(
  endpoint: string,
  body: any,
  options?: RequestOptions,
): Promise<{ data: T }>;

// DELETE request
async function del<T>(
  endpoint: string,
  options?: RequestOptions,
): Promise<{ data: T }>;

// Generic request (used internally by other methods)
async function request<T>(
  endpoint: string,
  options: RequestOptions & { method: string },
): Promise<{ data: T }>;
```

### Special-Purpose Methods

```typescript
// Export image as a blob
async function exportImage(
  imageIdentifier: string,
  format: ExportFormat,
  size: ExportSize,
  svgParams?: Record<string, any>,
  bucket?: string,
): Promise<Blob>;

// Get authentication headers (used internally)
async function getAuthHeaders(): Promise<Record<string, string>>;
```

## Usage

```typescript
import { apiClient } from "../services/apiClient";

// Basic GET request
async function fetchConcepts() {
  try {
    const { data } = await apiClient.get("/concepts/recent");
    return data;
  } catch (error) {
    // Handle error
    console.error("Failed to fetch concepts:", error);
    throw error;
  }
}

// POST request with body
async function createConcept(conceptData) {
  try {
    const { data } = await apiClient.post("/concepts", conceptData);
    return data;
  } catch (error) {
    // Handle error
    console.error("Failed to create concept:", error);
    throw error;
  }
}

// Using request options
async function fetchConceptWithOptions(id) {
  try {
    const { data } = await apiClient.get(`/concepts/${id}`, {
      responseType: "json",
      showToastOnRateLimit: false,
      signal: abortController.signal,
    });
    return data;
  } catch (error) {
    // Handle error
    console.error("Failed to fetch concept:", error);
    throw error;
  }
}

// Export an image
async function downloadImage(imageId) {
  try {
    const blob = await apiClient.exportImage(imageId, "png", "large");
    const url = URL.createObjectURL(blob);
    // Create download link
    const a = document.createElement("a");
    a.href = url;
    a.download = `concept-${imageId}.png`;
    a.click();
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Failed to export image:", error);
    throw error;
  }
}
```

## Request Options

The `RequestOptions` interface allows customizing requests:

```typescript
interface RequestOptions {
  // Custom headers to include in the request
  headers?: Record<string, string>;

  // Request body (for POST/PUT)
  body?: any;

  // Whether to include credentials
  withCredentials?: boolean;

  // Whether to retry with fresh auth token on 401
  retryAuth?: boolean;

  // Whether to show a toast on rate limit errors
  showToastOnRateLimit?: boolean;

  // Custom message for rate limit toasts
  rateLimitToastMessage?: string;

  // Response type to expect
  responseType?: "json" | "blob" | "text";

  // AbortSignal for cancellation
  signal?: AbortSignal;
}
```

## Error Handling

The apiClient defines a hierarchy of error types for different error scenarios:

```typescript
// Base API error
class ApiError extends Error {
  status: number;
  url: string;
}

// Authentication errors (401)
class AuthError extends ApiError {}

// Permission errors (403)
class PermissionError extends ApiError {}

// Not found errors (404)
class NotFoundError extends ApiError {}

// Server errors (5xx)
class ServerError extends ApiError {}

// Validation errors (422)
class ValidationError extends ApiError {
  errors: Record<string, string[]>;
}

// Network errors
class NetworkError extends Error {
  isCORS?: boolean;
  possibleRateLimit?: boolean;
}

// Rate limit errors (429)
class RateLimitError extends Error {
  status: number;
  limit: number;
  current: number;
  period: string;
  resetAfterSeconds: number;
  category?: RateLimitCategory;
  retryAfter?: Date;

  getUserFriendlyMessage(): string;
  getCategoryDisplayName(): string;
}
```

When using the apiClient, catch errors and check their type:

```typescript
try {
  const { data } = await apiClient.get("/concepts/recent");
  return data;
} catch (error) {
  if (error instanceof RateLimitError) {
    // Handle rate limit specifically
    console.log(
      `Rate limit reached. Try again in ${error.resetAfterSeconds} seconds`,
    );
  } else if (error instanceof AuthError) {
    // Handle authentication error
    console.log("Authentication error, please log in again");
  } else if (error instanceof ValidationError) {
    // Handle validation errors
    console.log("Validation errors:", error.errors);
  } else {
    // Handle other errors
    console.error("An error occurred:", error.message);
  }
  throw error;
}
```

## Authentication

The apiClient automatically:

1. Retrieves the current auth token from Supabase
2. Adds it to request headers
3. Refreshes tokens when they expire
4. Retries requests with fresh tokens when authentication fails

## Rate Limiting

The apiClient handles rate limits by:

1. Extracting rate limit headers from responses
2. Converting rate limit errors into `RateLimitError` instances
3. Providing user-friendly messages via `getUserFriendlyMessage()`
4. Showing toast notifications for rate limit errors (unless disabled)

## Toast Notifications

The apiClient can show toast notifications for certain errors:

```typescript
// Custom toast function using custom events
const toast = (options: {
  title: string;
  message: string;
  type: string;
  duration?: number;
  action?: { label: string; onClick: () => void };
  isRateLimitError?: boolean;
  rateLimitResetTime?: number;
}) => {
  document.dispatchEvent(
    new CustomEvent("show-api-toast", { detail: options }),
  );
};
```

These toast events are captured by the `ApiToastListener` component.

## Related

- [rateLimitService](./rateLimitService.md) - Service for handling rate limits
- [supabaseClient](./supabaseClient.md) - Client for authentication tokens
- [useErrorHandling](../hooks/useErrorHandling.md) - Hook for processing API errors
