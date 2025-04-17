import { useState, useCallback } from 'react';
import useToast from './useToast';
import { formatTimeRemaining } from '../services/rateLimitService';
import { 
  RateLimitError, 
  AuthError, 
  PermissionError, 
  NotFoundError, 
  ServerError, 
  ValidationError, 
  NetworkError,
  ApiError 
} from '../services/apiClient';

export type ErrorCategory = 
  | 'validation'   // Form validation errors
  | 'network'      // Network/API request errors
  | 'permission'   // Permission/authorization errors
  | 'notFound'     // Resource not found errors
  | 'server'       // Server-side errors
  | 'client'       // Client-side errors
  | 'rateLimit'    // Rate limit errors
  | 'auth'         // Authentication errors (401)
  | 'validation'   // Validation errors (422)
  | 'unknown';     // Uncategorized errors

export interface ErrorWithCategory {
  message: string;
  details?: string;
  category: ErrorCategory;
  originalError?: unknown;
  // Rate limit specific properties
  limit?: number;
  current?: number;
  period?: string;
  resetAfterSeconds?: number;
  // Validation specific properties
  validationErrors?: Record<string, string[]>;
  // API error specific properties
  status?: number;
  url?: string;
}

export interface UseErrorHandlingResult {
  /**
   * Current error state
   */
  error: ErrorWithCategory | null;
  
  /**
   * Whether there is an active error
   */
  hasError: boolean;
  
  /**
   * Set an error with a specific category
   */
  setError: (message: string, category?: ErrorCategory, details?: string, originalError?: unknown) => void;
  
  /**
   * Clear the current error
   */
  clearError: () => void;
  
  /**
   * Handle an error and categorize it automatically
   */
  handleError: (error: unknown) => void;
  
  /**
   * Show the current error in a toast notification
   */
  showErrorToast: () => void;
  
  /**
   * Show the current error in a toast and clear the error state
   */
  showAndClearError: () => void;
}

/**
 * Hook for centralizing error handling in the application
 */
export const useErrorHandling = (options: {
  showToasts?: boolean;
} = {}): UseErrorHandlingResult => {
  const {
    showToasts = false,
  } = options || {};
  
  const [error, setErrorState] = useState<ErrorWithCategory | null>(null);
  const toast = useToast();
  
  const hasError = error !== null;
  
  /**
   * Set an error with a specific category
   */
  const setError = useCallback(
    (message: string, category: ErrorCategory = 'unknown', details?: string, originalError?: unknown) => {
      const newError = {
        message,
        details,
        category,
        originalError,
      };
      
      setErrorState(newError);
      
      if (showToasts) {
        // Map error category to toast type
        const toastType = 
          category === 'server' || category === 'client' ? 'error' :
          category === 'validation' ? 'warning' :
          category === 'network' ? 'info' :
          'error';
        
        toast.showToast(toastType, message);
      }
    },
    [showToasts, toast]
  );
  
  /**
   * Clear the current error
   */
  const clearError = useCallback(() => {
    setErrorState(null);
  }, []);
  
  /**
   * Categorize an error based on its properties or message
   */
  const categorizeError = useCallback((error: unknown): ErrorCategory => {
    // Check for our custom API error types
    if (error instanceof AuthError) {
      return 'auth';
    }
    
    if (error instanceof PermissionError) {
      return 'permission';
    }
    
    if (error instanceof NotFoundError) {
      return 'notFound';
    }
    
    if (error instanceof ServerError) {
      return 'server';
    }
    
    if (error instanceof ValidationError) {
      return 'validation';
    }
    
    if (error instanceof NetworkError) {
      // Check if this network error is a CORS error that might be a rate limit
      if (error.possibleRateLimit) {
        console.log('[useErrorHandling] Detected NetworkError that might be a rate limit issue');
        return 'rateLimit';
      }
      return 'network';
    }
    
    if (error instanceof RateLimitError) {
      return 'rateLimit';
    }
    
    if (error instanceof ApiError) {
      // Generic API error - categorize based on status code
      if (error.status >= 500) {
        return 'server';
      } else if (error.status >= 400) {
        return 'client';
      }
    }
    
    // Handle axios or fetch errors
    if (typeof error === 'object' && error !== null) {
      const err = error as any;
      
      // Check for rate limit errors based on status code or message
      if (err.status === 429 || err.statusCode === 429 || 
          (err.message && 
           (err.message.toLowerCase().includes('rate limit') ||
            err.message.toLowerCase().includes('too many requests')))) {
        return 'rateLimit';
      }
      
      // Network errors
      if (err.code === 'ECONNABORTED' || err.name === 'NetworkError' || err.message?.includes('Network Error')) {
        return 'network';
      }
      
      // Status code based categorization
      if (err.status === 401 || err.statusCode === 401) {
        return 'auth';
      }
      
      if (err.status === 403 || err.statusCode === 403) {
        return 'permission';
      }
      
      if (err.status === 404 || err.statusCode === 404) {
        return 'notFound';
      }
      
      if (err.status >= 500 || err.statusCode >= 500) {
        return 'server';
      }
      
      if (err.status >= 400 || err.statusCode >= 400) {
        return 'client';
      }
      
      // Validation errors
      if (err.name === 'ValidationError' || err.validationErrors || err.message?.includes('validation')) {
        return 'validation';
      }
    }
    
    return 'unknown';
  }, []);
  
  /**
   * Extract a human-readable message from an error object
   */
  const extractErrorMessage = useCallback(
    (error: unknown): string => {
      if (typeof error === 'string') {
        return error;
      }
      
      if (error instanceof Error) {
        return error.message;
      }
      
      if (typeof error === 'object' && error !== null) {
        const err = error as any;
        
        // Handle common error object patterns
        if (err.message) {
          return err.message;
        }
        
        if (err.error?.message) {
          return err.error.message;
        }
        
        if (err.data?.message) {
          return err.data.message;
        }
        
        if (err.response?.data?.message) {
          return err.response.data.message;
        }
        
        if (err.response?.data?.error) {
          return err.response.data.error;
        }
        
        // Try JSON serialization for debugging
        try {
          return `Error: ${JSON.stringify(error)}`;
        } catch (e) {
          // Fallback if JSON serialization fails
          return 'An unexpected error occurred';
        }
      }
      
      return 'An unexpected error occurred';
    },
    []
  );
  
  /**
   * Extract more detailed error information if available
   */
  const extractErrorDetails = useCallback((error: unknown): string | undefined => {
    if (typeof error === 'object' && error !== null) {
      const err = error as any;
      
      // Try to extract detailed error information
      if (err.response?.data?.details) {
        return err.response.data.details;
      }
      
      if (err.response?.data?.errors) {
        try {
          return JSON.stringify(err.response.data.errors);
        } catch (e) {
          return undefined;
        }
      }
      
      if (err.stack) {
        return err.stack;
      }
    }
    
    return undefined;
  }, []);
  
  /**
   * Handle an error and categorize it automatically
   */
  const handleError = useCallback(
    (error: unknown) => {
      const category = categorizeError(error);
      const message = extractErrorMessage(error);
      const details = extractErrorDetails(error);
      
      // Create the base error object
      const errorWithCategory: ErrorWithCategory = {
        message,
        details,
        category,
        originalError: error
      };
      
      // Add specific properties based on error type
      if (error instanceof ApiError) {
        errorWithCategory.status = error.status;
        errorWithCategory.url = error.url;
      }
      
      // Handle rate limit errors specifically to extract more data
      if (category === 'rateLimit') {
        if (error instanceof RateLimitError) {
          // Extract rate limit specific data
          errorWithCategory.limit = error.limit;
          errorWithCategory.current = error.current;
          errorWithCategory.period = error.period;
          errorWithCategory.resetAfterSeconds = error.resetAfterSeconds;
        } else if (error instanceof NetworkError && error.possibleRateLimit) {
          // For network errors that might be rate limits, set default values
          errorWithCategory.limit = 10;
          errorWithCategory.current = 10;
          errorWithCategory.period = '15min';
          errorWithCategory.resetAfterSeconds = 60; // Default 1 minute
          errorWithCategory.details = 'This might be due to hitting a rate limit or the server being temporarily unavailable. Please try again later.';
        } else if (typeof error === 'object' && error !== null) {
          // Try to extract rate limit data from generic error objects
          const err = error as any;
          errorWithCategory.limit = err.limit || err.response?.data?.limit;
          errorWithCategory.current = err.current || err.response?.data?.current;
          errorWithCategory.period = err.period || err.response?.data?.period;
          errorWithCategory.resetAfterSeconds = err.resetAfterSeconds || 
                                              err.response?.data?.reset_after_seconds ||
                                              err.response?.headers?.['retry-after'];
        }
      }
      
      // Handle validation errors
      if (category === 'validation' && error instanceof ValidationError) {
        errorWithCategory.validationErrors = error.errors;
      }
      
      setErrorState(errorWithCategory);
      
      if (showToasts) {
        // Map error category to toast type
        const toastType = 
          category === 'server' || category === 'client' ? 'error' :
          category === 'validation' ? 'warning' :
          category === 'network' ? 'info' :
          category === 'rateLimit' ? 'warning' :
          category === 'auth' ? 'error' :
          'error';
        
        toast.showToast(toastType, message);
      }
    },
    [categorizeError, extractErrorMessage, extractErrorDetails, setErrorState, showToasts, toast]
  );
  
  /**
   * Show the current error in a toast notification
   */
  const showErrorToast = useCallback(() => {
    if (error) {
      // Map error category to toast type
      const toastType = 
        error.category === 'server' || error.category === 'client' ? 'error' :
        error.category === 'validation' ? 'warning' :
        error.category === 'network' ? 'info' :
        'error';
      
      toast.showToast(toastType, error.message);
    }
  }, [error, toast]);
  
  /**
   * Show the current error in a toast and clear the error state
   */
  const showAndClearError = useCallback(() => {
    showErrorToast();
    clearError();
  }, [showErrorToast, clearError]);
  
  return {
    error,
    hasError,
    setError,
    clearError,
    handleError,
    showErrorToast,
    showAndClearError,
  };
};

export default useErrorHandling; 