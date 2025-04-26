/**
 * Utilities for standardized error handling across the application
 */

import { UseErrorHandlingResult } from "../hooks/useErrorHandling";
import { RateLimitError } from "../services/apiClient";
import { useErrorHandling } from "../hooks/useErrorHandling";

/**
 * Creates a standardized error handler function for async operations
 *
 * @param errorHandler - The error handling hook result
 * @param options - Additional options for the error handler
 * @returns A function to wrap async operations with error handling
 */
export const createAsyncErrorHandler = (
  errorHandler: UseErrorHandlingResult,
  options: {
    showToast?: boolean;
    defaultErrorMessage?: string;
    onError?: (error: unknown) => void;
    context?: string;
  } = {},
) => {
  const { handleError, showErrorToast } = errorHandler;

  const {
    showToast = false,
    onError = () => {},
    context = "unknown",
  } = options;

  /**
   * Wraps an async operation with standardized error handling
   *
   * @param asyncOperation - The async operation to wrap
   * @param operationName - Optional name for logging purposes
   * @returns The result of the async operation or undefined if an error occurs
   */
  return async <R>(
    asyncOperation: () => Promise<R>,
    operationName?: string,
  ): Promise<R | undefined> => {
    try {
      return await asyncOperation();
    } catch (error) {
      const errorLocation = `${context}:${operationName || "async operation"}`;
      console.error(`[ERROR:${errorLocation}]`, error);

      if (error instanceof Error) {
        console.error(`[ERROR:${errorLocation}] Stack trace:`, error.stack);
      }

      // Log navigation-related errors more prominently
      if (
        errorLocation.includes("navigation") ||
        errorLocation.includes("route") ||
        (error instanceof Error &&
          (error.message.includes("navigation") ||
            error.message.includes("route") ||
            error.message.includes("page")))
      ) {
        console.warn(
          "[NAVIGATION_ERROR] This error may affect state synchronization across pages:",
          error,
        );
      }

      // Use the centralized error handling
      handleError(error);

      // Show toast if requested
      if (showToast) {
        showErrorToast();
      }

      // Execute custom error handler if provided
      onError(error);

      return undefined;
    }
  };
};

/**
 * Creates a function to handle errors in React Query mutations.
 * This is separated from useErrorHandling to prevent circular dependencies.
 *
 * @param errorHandler The error handler instance from useErrorHandling
 * @param options Configuration options
 * @returns Functions for error handling
 */
export const createQueryErrorHandler = (
  errorHandler: ReturnType<typeof useErrorHandling>,
  options: {
    defaultErrorMessage?: string;
    showToast?: boolean;
  } = {},
) => {
  const {
    defaultErrorMessage = "An unexpected error occurred",
    showToast = false,
  } = options;

  /**
   * Handle query errors in a consistent way
   */
  const onQueryError = (error: unknown) => {
    console.error("Query error:", error);

    // Handle RateLimitError separately
    if (error instanceof RateLimitError) {
      errorHandler.setError(
        error.getUserFriendlyMessage(),
        "rateLimit",
        "Please try again next month when the usage limits reset.",
        error,
      );
      return;
    }

    // Extract a usable error message
    const errorMessage =
      typeof error === "string"
        ? error
        : error instanceof Error
        ? error.message
        : defaultErrorMessage;

    // Handle other errors
    errorHandler.handleError(error);

    // Show toast notification if enabled
    if (showToast) {
      document.dispatchEvent(
        new CustomEvent("show-api-toast", {
          detail: {
            type: "error",
            message: errorMessage,
          },
        }),
      );
    }
  };

  return {
    onQueryError,
  };
};

export default createQueryErrorHandler;
