import { useState, useCallback } from 'react';
import { useToast } from './useToast';
import { RateLimitError } from '../services/apiClient';
import { formatTimeRemaining } from '../services/rateLimitService';

export type ErrorCategory = 
  | 'validation'   // Form validation errors
  | 'network'      // Network/API request errors
  | 'permission'   // Permission/authorization errors
  | 'notFound'     // Resource not found errors
  | 'server'       // Server-side errors
  | 'client'       // Client-side errors
  | 'rateLimit'    // Rate limit errors
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
 * Custom hook for centralized error handling with categorization
 */
export const useErrorHandling = (options?: {
  /** Show toast on error automatically */
  showToastOnError?: boolean;
  
  /** Default error message when unable to parse error */
  defaultErrorMessage?: string;
}): UseErrorHandlingResult => {
  const {
    showToastOnError = false,
    defaultErrorMessage = 'An unexpected error occurred',
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
      
      if (showToastOnError) {
        // Map error category to toast type
        const toastType = 
          category === 'server' || category === 'client' ? 'error' :
          category === 'validation' ? 'warning' :
          category === 'network' ? 'info' :
          'error';
        
        toast.showToast(toastType, message);
      }
    },
    [showToastOnError, toast]
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
    // Handle our custom RateLimitError
    if (error instanceof RateLimitError) {
      return 'rateLimit';
    }
    
    // Handle axios or fetch errors
    if (typeof error === 'object' && error !== null) {
      const err = error as any;
      
      // Check for rate limit errors based on status code
      if (err.status === 429 || err.statusCode === 429) {
        return 'rateLimit';
      }
      
      // Network errors
      if (err.code === 'ECONNABORTED' || err.name === 'NetworkError' || err.message?.includes('Network Error')) {
        return 'network';
      }
      
      // Status code based categorization
      if (err.status === 401 || err.status === 403 || err.statusCode === 401 || err.statusCode === 403) {
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
      // Handle RateLimitError specifically
      if (error instanceof RateLimitError) {
        const formattedTime = formatTimeRemaining(error.resetAfterSeconds);
        return `Rate limit exceeded: ${error.current}/${error.limit} requests per ${error.period}. Try again in ${formattedTime}.`;
      }
      
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
          return defaultErrorMessage;
        }
      }
      
      return defaultErrorMessage;
    },
    [defaultErrorMessage]
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
      
      // Add rate limit specific properties if applicable
      if (category === 'rateLimit' && error instanceof RateLimitError) {
        setErrorState({
          message,
          details,
          category,
          originalError: error,
          limit: error.limit,
          current: error.current,
          period: error.period,
          resetAfterSeconds: error.resetAfterSeconds
        });
      } else {
        setError(message, category, details, error);
      }
    },
    [categorizeError, extractErrorMessage, extractErrorDetails, setError]
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