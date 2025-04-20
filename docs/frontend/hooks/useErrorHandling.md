# useErrorHandling

The `useErrorHandling` hook provides a centralized system for managing, categorizing, and displaying errors throughout the application.

## Overview

This hook is a cornerstone of the application's error management strategy. It provides a standardized way to handle errors from different sources (API calls, validation, network issues, etc.), categorize them appropriately, and present them to users in a consistent manner.

## Usage

```tsx
import { useErrorHandling } from '../hooks/useErrorHandling';

function MyComponent() {
  const { 
    error, 
    hasError, 
    handleError, 
    setError, 
    clearError, 
    showErrorToast 
  } = useErrorHandling({
    showToasts: true
  });
  
  const handleSubmit = async (data) => {
    try {
      clearError(); // Clear any previous errors
      await submitData(data);
    } catch (err) {
      // Automatically categorize and handle the error
      handleError(err);
    }
  };
  
  const handleManualError = () => {
    // Manually set a specific error with category
    setError('Please fill out all required fields', 'validation');
  };
  
  return (
    <div>
      {hasError && (
        <div className="error-container">
          <h3>Error: {error.message}</h3>
          {error.details && <p>{error.details}</p>}
          {error.category === 'validation' && (
            <div className="validation-errors">
              {Object.entries(error.validationErrors || {}).map(([field, errors]) => (
                <p key={field}>
                  {field}: {errors.join(', ')}
                </p>
              ))}
            </div>
          )}
          <button onClick={clearError}>Dismiss</button>
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        {/* Form fields... */}
        <button type="submit">Submit</button>
      </form>
    </div>
  );
}
```

## Parameters

The hook accepts an optional configuration object:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `showToasts` | boolean | `false` | Whether to automatically show toast notifications for errors |

## Return Value

The hook returns an object with the following properties:

```typescript
interface UseErrorHandlingResult {
  // Current error state
  error: ErrorWithCategory | null;
  
  // Whether there is an active error
  hasError: boolean;
  
  // Set an error with a specific category
  setError: (message: string, category?: ErrorCategory, details?: string, originalError?: unknown) => void;
  
  // Clear the current error
  clearError: () => void;
  
  // Handle an error and categorize it automatically
  handleError: (error: unknown) => void;
  
  // Show the current error in a toast notification
  showErrorToast: () => void;
  
  // Show the current error in a toast and clear the error state
  showAndClearError: () => void;
}
```

## Error Categories

The hook categorizes errors into the following types:

| Category | Description | Toast Type |
|----------|-------------|------------|
| `'validation'` | Form validation errors | warning |
| `'network'` | Network/API request errors | info |
| `'permission'` | Permission/authorization errors | error |
| `'notFound'` | Resource not found errors | warning |
| `'server'` | Server-side errors | error |
| `'client'` | Client-side errors | error |
| `'rateLimit'` | Rate limit errors | warning |
| `'auth'` | Authentication errors | error |
| `'unknown'` | Uncategorized errors | error |

## Error Object Structure

The `error` state uses the `ErrorWithCategory` interface:

```typescript
interface ErrorWithCategory {
  message: string;               // Primary error message
  details?: string;              // Additional error details
  category: ErrorCategory;       // Error category
  originalError?: unknown;       // Original error object
  
  // Rate limit specific properties
  limit?: number;                // Maximum allowed requests
  current?: number;              // Current request count
  period?: string;               // Time period (e.g., "1m", "1h")
  resetAfterSeconds?: number;    // Seconds until reset
  
  // Validation specific properties
  validationErrors?: Record<string, string[]>; // Field-specific errors
  
  // API error specific properties
  status?: number;               // HTTP status code
  url?: string;                  // Request URL
}
```

## Key Features

### Automatic Error Categorization

The `handleError` method automatically detects the error type based on its properties:

- Detects custom error instances (AuthError, ValidationError, etc.)
- Examines HTTP status codes
- Analyzes error messages for specific patterns
- Extracts additional metadata like validation errors or rate limit info

### Toast Integration

When `showToasts` is enabled:
- Automatically displays toast notifications for errors
- Maps error categories to appropriate toast types (error, warning, info)
- For rate limit errors, shows time remaining until reset

### Rich Error Information

For specialized errors, the hook extracts and preserves additional context:

- **Validation Errors**: Field-specific validation messages
- **Rate Limit Errors**: Limit values and reset times
- **API Errors**: Status codes and request URLs

## Implementation Details

- Maintains error state with useState
- Integrates with the useToast hook for notifications
- Preserves the original error object for debugging
- Formats rate limit reset times into human-readable values
- Extracts validation errors from response bodies

## Related

- `useToast` - Used for showing error notifications
- `apiClient` - Source of API errors with standard error types
- `ErrorBoundary` - Component-level error handling
- `ErrorMessage` - Standardized error display component 