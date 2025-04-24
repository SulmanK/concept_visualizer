/**
 * API client for the Concept Visualizer application.
 */

import { supabase, initializeAnonymousAuth } from "./supabaseClient";
import {
  extractRateLimitHeaders,
  formatTimeRemaining,
  mapEndpointToCategory,
  RateLimitCategory,
} from "./rateLimitService";
import axios, {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosResponse,
  AxiosError,
} from "axios";
import { queryClient } from "../main";

// Use the full backend URL instead of a relative path
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

// Create a toast function for use within this file (outside of React components)
const toast = (options: {
  title: string;
  message: string;
  type: string;
  duration?: number;
  action?: { label: string; onClick: () => void };
  isRateLimitError?: boolean;
  rateLimitResetTime?: number;
}) => {
  // We'll handle this through a custom event since we can't directly use hooks outside components
  document.dispatchEvent(
    new CustomEvent("show-api-toast", {
      detail: options,
    }),
  );
};

interface RequestOptions {
  headers?: Record<string, string>;
  body?: any;
  withCredentials?: boolean;
  retryAuth?: boolean; // Whether to retry with fresh auth token on 401
  /**
   * Whether to show a toast notification on rate limit errors
   * @default true
   */
  showToastOnRateLimit?: boolean;
  /**
   * A custom message to show in the toast notification for rate limit errors
   * If not provided, a default message will be generated
   */
  rateLimitToastMessage?: string;
  /**
   * Response type to expect from the request
   */
  responseType?: "json" | "blob" | "text";
  /**
   * Request signal for cancellation
   */
  signal?: AbortSignal;
}

// Rate limit error response interface
interface RateLimitErrorResponse {
  message?: string;
  reset_after_seconds?: number;
  limit?: number;
  current?: number;
  period?: string;
  [key: string]: any;
}

// Base custom error class
export class ApiError extends Error {
  status: number;
  url: string;

  constructor(message: string, status: number, url: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.url = url;
  }
}

// Authentication error class (401)
export class AuthError extends ApiError {
  constructor(message: string, url: string) {
    super(message, 401, url);
    this.name = "AuthError";
  }
}

// Permission error class (403)
export class PermissionError extends ApiError {
  constructor(message: string, url: string) {
    super(message, 403, url);
    this.name = "PermissionError";
  }
}

// Not found error class (404)
export class NotFoundError extends ApiError {
  constructor(message: string, url: string) {
    super(message, 404, url);
    this.name = "NotFoundError";
  }
}

// Server error class (5xx)
export class ServerError extends ApiError {
  constructor(message: string, status: number, url: string) {
    super(message, status, url);
    this.name = "ServerError";
  }
}

// Validation error class (422)
export class ValidationError extends ApiError {
  errors: Record<string, string[]>;

  constructor(
    message: string,
    url: string,
    errors: Record<string, string[]> = {},
  ) {
    super(message, 422, url);
    this.name = "ValidationError";
    this.errors = errors;
  }
}

// Network error class
export class NetworkError extends Error {
  isCORS?: boolean;
  possibleRateLimit?: boolean;

  constructor(message: string, isCORS?: boolean, possibleRateLimit?: boolean) {
    super(message || "Network connection error");
    this.name = "NetworkError";
    this.isCORS = isCORS;
    this.possibleRateLimit = possibleRateLimit;
  }
}

// Custom error class for rate limit errors
export class RateLimitError extends Error {
  status: number;
  limit: number;
  current: number;
  period: string;
  resetAfterSeconds: number;
  category?: RateLimitCategory; // Added category for context
  retryAfter?: Date; // Added specific retry time

  constructor(
    message: string,
    response: RateLimitErrorResponse,
    endpoint?: string,
  ) {
    super(message);
    this.name = "RateLimitError";
    this.status = 429;
    this.limit = response.limit || 0;
    this.current = response.current || 0;
    this.period = response.period || "unknown";
    this.resetAfterSeconds = response.reset_after_seconds || 0;

    // Try to determine the category from the endpoint
    if (endpoint) {
      const category = mapEndpointToCategory(endpoint);
      if (category !== null) {
        this.category = category;
      }
    }

    // Calculate the retry-after time if we have reset seconds
    if (this.resetAfterSeconds > 0) {
      this.retryAfter = new Date(Date.now() + this.resetAfterSeconds * 1000);
    }
  }

  /**
   * Get a user-friendly error message for display
   */
  getUserFriendlyMessage(): string {
    const categoryName = this.getCategoryDisplayName();
    const timeRemaining = formatTimeRemaining(this.resetAfterSeconds);

    return `${categoryName} limit reached (${this.current}/${this.limit}). Please try again in ${timeRemaining}.`;
  }

  /**
   * Get a display-friendly name for the rate limit category
   */
  getCategoryDisplayName(): string {
    if (this.category === "generate_concept") return "Concept generation";
    if (this.category === "refine_concept") return "Concept refinement";
    if (this.category === "store_concept") return "Concept storage";
    if (this.category === "get_concepts") return "Concept retrieval";
    if (this.category === "export_action") return "Image export";
    if (this.category === "sessions") return "Session";
    return "Usage";
  }
}

// Create an Axios instance with base configuration
const axiosInstance: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Add a request interceptor for authentication
axiosInstance.interceptors.request.use(
  async (config) => {
    try {
      // Fetch the current session
      const {
        data: { session },
      } = await supabase.auth.getSession();

      // If we have a valid token
      if (session?.access_token) {
        // Add the auth header
        config.headers = config.headers || {};
        config.headers.Authorization = `Bearer ${session.access_token}`;
      } else {
        // If no valid token, remove any existing auth header
        if (config.headers) {
          delete config.headers.Authorization;
        }
      }

      return config;
    } catch (error) {
      console.error("[AUTH INTERCEPTOR] Error in request interceptor:", error);
      return config; // Return the config even if there's an error to not block the request
    }
  },
  (error) => {
    console.error("[AUTH INTERCEPTOR] Request interceptor error:", error);
    return Promise.reject(error);
  },
);

// Add a response interceptor for error handling and token refresh
axiosInstance.interceptors.response.use(
  // Success handler - extract rate limit headers
  (response) => {
    // Skip rate limit header extraction for the rate-limits endpoints to avoid circular updates
    if (!response.config.url?.includes("/health/rate-limits")) {
      try {
        // Extract and process rate limit headers
        extractRateLimitHeaders(response, response.config.url);
      } catch (error) {
        // Ensure errors in header processing don't break the request flow
        console.error(
          "[RATE LIMIT INTERCEPTOR] Error extracting rate limit headers:",
          error,
        );
      }
    }

    return response;
  },

  // Error handler
  async (error) => {
    // Original request that caused the error
    const originalRequest = error.config;

    // Only process Axios errors
    if (!axios.isAxiosError(error)) {
      return Promise.reject(error);
    }

    const url = originalRequest?.url || "";

    // Handle network errors (no response)
    if (!error.response) {
      console.error("[API] Network error:", error);

      // Check if it's a timeout
      if (error.code === "ECONNABORTED") {
        const networkError = new NetworkError(
          "Request timeout. Please check your connection and try again.",
        );
        return Promise.reject(networkError);
      }

      // Check if it might be a CORS error by examining the message
      // Often CORS errors show up as network errors
      const isCORSError =
        error.message?.toLowerCase().includes("cors") ||
        error.message?.includes("Network Error") ||
        error.message?.includes("Cross-Origin");

      // Check if the URL suggests this might be a rate limit issue
      // For common rate-limited endpoints
      const isPossibleRateLimit =
        url.includes("/generate") ||
        url.includes("/refine") ||
        url.includes("/export") ||
        url.includes("/process");

      // Special handling for CORS errors that might be rate limits
      if (isCORSError && isPossibleRateLimit) {
        console.warn(
          "[API] CORS error on rate-limited endpoint detected:",
          error.message,
        );

        // Create a custom rate limit error with sensible defaults
        // Since we can't get the actual limits from the error response
        const rateLimitError = new RateLimitError(
          "Rate limit likely exceeded. Please try again later.",
          {
            message: "Rate limit exceeded",
            reset_after_seconds: 86400, // Default to 1 day
            limit: 10,
            current: 10,
            period: "month",
          },
          url,
        );

        // Show a toast about the possible rate limit
        toast({
          title: "Rate Limit Likely Reached",
          message:
            "You may have reached the monthly usage limit. Please try again later.",
          type: "warning",
          duration: 8000,
          isRateLimitError: true,
          rateLimitResetTime: 86400, // Default to 1 day
        });

        // Invalidate rate limits to force a refresh
        queryClient.invalidateQueries({ queryKey: ["rateLimits"] });

        return Promise.reject(rateLimitError);
      }

      // Generic network error
      const networkError = new NetworkError(
        "Network connection error. Please check your internet connection.",
        isCORSError,
        isPossibleRateLimit,
      );
      return Promise.reject(networkError);
    }

    // Get error response and status
    const response = error.response;
    const status = response.status;

    // Check if it's a 500 error that might actually be a rate limit
    if (status === 500) {
      // Check if there are indicators that this might be a rate limit issue
      const isPossibleRateLimit =
        url.includes("/generate") ||
        url.includes("/refine") ||
        url.includes("/export") ||
        url.includes("/process");

      if (isPossibleRateLimit) {
        console.warn(
          "[API] 500 error on rate-limited endpoint detected, might be a rate limit issue:",
          url,
        );

        // Create a custom rate limit error with sensible defaults
        const rateLimitError = new RateLimitError(
          "Rate limit likely exceeded. Please try again later.",
          {
            message: "Monthly usage limit reached",
            reset_after_seconds: 86400, // Default to 1 day - will update when we know the actual time until month end
            limit: 10,
            current: 10,
            period: "month",
          },
          url,
        );

        // Show a toast about the possible rate limit
        toast({
          title: "Monthly Usage Limit Reached",
          message:
            "You have reached your monthly usage limit. Please try again next month.",
          type: "warning",
          duration: 8000,
          isRateLimitError: true,
          rateLimitResetTime: 86400, // Default to 1 day
        });

        // Invalidate rate limits to force a refresh
        queryClient.invalidateQueries({ queryKey: ["rateLimits"] });

        return Promise.reject(rateLimitError);
      }
    }

    // Check if it's a 401 (Unauthorized) error and we haven't already tried to refresh
    if (
      status === 401 &&
      !originalRequest._retry &&
      originalRequest // Ensure we have a request to retry
    ) {
      console.log(
        "[AUTH INTERCEPTOR] 401 error detected, attempting to refresh token",
      );

      // Mark that we're retrying this request
      originalRequest._retry = true;

      try {
        // Attempt to refresh the session
        const { data, error: refreshError } =
          await supabase.auth.refreshSession();

        // If refresh was successful and we have a new token
        if (data.session?.access_token && !refreshError) {
          console.log(
            "[AUTH INTERCEPTOR] Token refresh successful, retrying request",
          );

          // Update the Authorization header with the new token
          originalRequest.headers.Authorization = `Bearer ${data.session.access_token}`;

          // Retry the original request with the new token
          return axiosInstance(originalRequest);
        } else {
          console.error(
            "[AUTH INTERCEPTOR] Token refresh failed:",
            refreshError,
          );

          // Dispatch an event to signal that we need to log out
          document.dispatchEvent(new CustomEvent("auth-error-needs-logout"));

          // If we reach this point, auth refresh failed
          const authError = new AuthError(
            "Your session has expired. Please sign in again.",
            url,
          );
          return Promise.reject(authError);
        }
      } catch (refreshError) {
        console.error(
          "[AUTH INTERCEPTOR] Error during token refresh:",
          refreshError,
        );

        // Dispatch an event to signal that we need to log out
        document.dispatchEvent(new CustomEvent("auth-error-needs-logout"));

        // If we reach this point, auth refresh failed
        const authError = new AuthError(
          "Your session has expired. Please sign in again.",
          url,
        );
        return Promise.reject(authError);
      }
    }

    // Handle rate limit errors (429)
    if (status === 429) {
      const response = error.response;

      // Create a more detailed error object for rate limit errors
      let rateLimitResponse: RateLimitErrorResponse = {
        message: response.data?.message || "Rate limit exceeded",
        reset_after_seconds: 0,
        limit: 0,
        current: 0,
        period: "unknown",
      };

      // Try to extract rate limit information from headers
      const limit = parseInt(
        (response.headers["x-ratelimit-limit"] as string) || "0",
        10,
      );
      const remaining = parseInt(
        (response.headers["x-ratelimit-remaining"] as string) || "0",
        10,
      );
      const current = limit - remaining;

      // Try to get reset time from headers
      const resetHeader = response.headers["x-ratelimit-reset"] as string;
      const retryAfter = response.headers["retry-after"] as string;
      let resetAfterSeconds = 0;

      // Parse X-RateLimit-Reset header if available
      if (resetHeader) {
        // If it's a timestamp
        if (!isNaN(Number(resetHeader))) {
          const resetTime = new Date(Number(resetHeader) * 1000);
          resetAfterSeconds = Math.max(
            0,
            Math.floor((resetTime.getTime() - Date.now()) / 1000),
          );
        } else {
          // Try as a relative time value in seconds
          resetAfterSeconds = parseInt(resetHeader, 10);
        }
      }
      // Fallback to Retry-After header
      else if (retryAfter) {
        resetAfterSeconds = parseInt(retryAfter, 10);
      }

      // Populate the response object with extracted data
      rateLimitResponse = {
        ...rateLimitResponse,
        limit,
        current,
        reset_after_seconds: resetAfterSeconds,
        period: "15min", // Default period if not specified
      };

      // Try to extract more details from response data if available
      if (response.data) {
        if (typeof response.data === "object") {
          // Override with any values from the response body
          rateLimitResponse = {
            ...rateLimitResponse,
            ...response.data,
            // Ensure we preserve our extracted headers if not in response
            limit: response.data.limit || rateLimitResponse.limit,
            current: response.data.current || rateLimitResponse.current,
            reset_after_seconds:
              response.data.reset_after_seconds ||
              rateLimitResponse.reset_after_seconds,
            period: response.data.period || rateLimitResponse.period,
          };
        }
      }

      // Create custom error with rate limit details
      const rateLimitError = new RateLimitError(
        rateLimitResponse.message || "Rate limit exceeded",
        rateLimitResponse,
        url,
      );

      console.warn("[RATE LIMIT]", rateLimitError);

      // Dispatch event or show toast notification if enabled in request options
      if (originalRequest && originalRequest.showToastOnRateLimit !== false) {
        const message =
          originalRequest.rateLimitToastMessage ||
          rateLimitError.getUserFriendlyMessage();

        toast({
          title: "Rate Limit Exceeded",
          message,
          type: "warning",
          duration: 8000,
          isRateLimitError: true,
          rateLimitResetTime: rateLimitResponse.reset_after_seconds,
        });
      }

      // Invalidate rate limits to force a refresh
      queryClient.invalidateQueries({ queryKey: ["rateLimits"] });

      // Return a rejected promise with our enhanced error
      return Promise.reject(rateLimitError);
    }

    // Handle other error types
    let apiError: Error;
    const errorMessage =
      response.data?.message || response.data?.error || "An error occurred";

    switch (status) {
      case 400:
        apiError = new ApiError(errorMessage, status, url);
        break;

      case 401:
        apiError = new AuthError(errorMessage, url);
        break;

      case 403:
        apiError = new PermissionError(
          "You do not have permission to access this resource",
          url,
        );
        break;

      case 404:
        apiError = new NotFoundError(
          "The requested resource was not found",
          url,
        );
        break;

      case 422:
        // Handle validation errors
        const validationErrors =
          response.data?.errors || response.data?.detail || {};
        apiError = new ValidationError(errorMessage, url, validationErrors);
        break;

      default:
        // Server errors (5xx)
        if (status >= 500) {
          apiError = new ServerError(
            "A server error occurred. Our team has been notified.",
            status,
            url,
          );
        } else {
          apiError = new ApiError(errorMessage, status, url);
        }
    }

    console.error(`[API] Error ${status}:`, apiError);

    // Return the custom error
    return Promise.reject(apiError);
  },
);

/**
 * Make a GET request to the API
 * @param endpoint API endpoint path
 * @param options Request options
 * @returns Response with generic type
 */
async function get<T>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<{ data: T }> {
  return request<T>(endpoint, { method: "GET", ...options });
}

/**
 * Make a POST request to the API
 * @param endpoint API endpoint path
 * @param body Request body
 * @param options Request options
 * @returns Response with generic type
 */
async function post<T>(
  endpoint: string,
  body: any,
  options: RequestOptions = {},
): Promise<{ data: T }> {
  return request<T>(endpoint, { method: "POST", body, ...options });
}

/**
 * Get the current auth token from Supabase
 * @returns Authorization header or empty object if no session
 * @deprecated This function is deprecated and will be removed in a future release.
 * Authentication is now handled by the Axios request interceptor.
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    console.log("[AUTH] Getting auth headers for request");

    // First check for an existing session
    const {
      data: { session },
    } = await supabase.auth.getSession();

    // If we have a session with a valid token, use it
    if (session?.access_token) {
      const now = Math.floor(Date.now() / 1000);

      // If token expires in less than 5 minutes, refresh it
      if (session.expires_at && session.expires_at - now < 300) {
        console.log(
          "[AUTH] Token is about to expire in",
          session.expires_at - now,
          "seconds. Refreshing before request",
        );
        // Refresh the session
        const { data: refreshData } = await supabase.auth.refreshSession();
        if (refreshData.session?.access_token) {
          const newExpiresAt = refreshData.session.expires_at;
          const validFor = newExpiresAt ? newExpiresAt - now : "unknown";
          console.log(
            "[AUTH] Successfully refreshed token before request. Valid for",
            validFor,
            "seconds",
          );
          return {
            Authorization: `Bearer ${refreshData.session.access_token}`,
          };
        } else {
          console.error(
            "[AUTH] Failed to refresh token - no new token received",
          );
        }
      } else {
        const validFor = session.expires_at
          ? session.expires_at - now
          : "unknown";
        console.log(
          "[AUTH] Using existing token for request. Valid for",
          validFor,
          "seconds",
        );
        return {
          Authorization: `Bearer ${session.access_token}`,
        };
      }
    }

    console.log(
      "[AUTH] No valid session found, attempting to sign in anonymously",
    );
    // Try to get a new anonymous session
    const newSession = await initializeAnonymousAuth();
    if (newSession?.access_token) {
      const now = Math.floor(Date.now() / 1000);
      const validFor = newSession.expires_at
        ? newSession.expires_at - now
        : "unknown";
      console.log(
        "[AUTH] Generated new auth token from anonymous sign-in. Valid for",
        validFor,
        "seconds",
      );
      return {
        Authorization: `Bearer ${newSession.access_token}`,
      };
    }

    console.error("[AUTH] Failed to get authentication token");
    return {};
  } catch (error) {
    console.error("[AUTH] Error getting auth token:", error);
    return {};
  }
}

/**
 * Make a request to the API
 * @param endpoint API endpoint path
 * @param options Request options
 * @returns Response with generic type
 */
async function request<T>(
  endpoint: string,
  {
    method = "GET",
    headers = {},
    body,
    withCredentials = true,
    retryAuth = true,
    showToastOnRateLimit = true,
    rateLimitToastMessage,
    responseType,
    signal,
  }: RequestOptions & { method: string },
): Promise<{ data: T }> {
  try {
    // Ensure endpoint starts with forward slash if not already
    const sanitizedEndpoint = endpoint.startsWith("/")
      ? endpoint
      : `/${endpoint}`;

    // We don't need to manually get auth headers anymore, the interceptor will handle it

    const requestConfig: AxiosRequestConfig = {
      method,
      url: sanitizedEndpoint,
      headers,
      data: body,
      withCredentials,
      signal,
      responseType:
        responseType === "blob"
          ? "blob"
          : responseType === "text"
          ? "text"
          : "json",
    };

    console.log(
      `Making ${method} request to ${API_BASE_URL}${sanitizedEndpoint}`,
    );

    const response = await axiosInstance(requestConfig);

    return { data: response.data as T };
  } catch (err) {
    // RateLimitError will already be thrown by the interceptor
    if (err instanceof RateLimitError) {
      throw err;
    }

    console.error("API request failed:", err);
    throw err;
  }
}

// Export types for use in the export image function
export type ExportFormat = "png" | "jpg" | "svg";
export type ExportSize = "small" | "medium" | "large" | "original";

/**
 * Export an image with the specified format and size
 * @param imageIdentifier Storage path identifier for the image
 * @param format Target format (png, jpg, svg)
 * @param size Target size (small, medium, large, original)
 * @param svgParams Optional SVG conversion parameters (only used when format is 'svg')
 * @param bucket Optional storage bucket name ('concept-images' or 'palette-images')
 * @param _timestamp Optional timestamp for cache-busting (not used in the request)
 * @returns Blob containing the exported image data
 */
async function exportImage(
  imageIdentifier: string,
  format: ExportFormat,
  size: ExportSize,
  svgParams?: Record<string, any>,
  bucket?: string,
  _timestamp?: number, // Add timestamp parameter but don't use it in the request
): Promise<Blob> {
  // Create the request body (omitting the timestamp which is just for cache-busting)
  const body = {
    image_identifier: imageIdentifier,
    target_format: format,
    target_size: size,
    svg_params: svgParams,
    storage_bucket: bucket || "concept-images", // Default to concept-images if not specified
  };

  console.log(
    `Making export request for ${imageIdentifier} in format ${format} at ${
      _timestamp || Date.now()
    }`,
  );

  // Set up the AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30-second timeout

  try {
    // Make the API call with blob response type
    const response = await request<Blob>("export/process", {
      method: "POST",
      body,
      responseType: "blob",
      signal: controller.signal,
    });

    return response.data;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Export the API client interfaces
export const apiClient = {
  get,
  post,
  exportImage,
  request,
};
