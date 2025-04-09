/**
 * Utilities for standardized error handling across the application
 */

import { UseErrorHandlingResult } from '../hooks/useErrorHandling';

/**
 * Creates a standardized error handler function for async operations
 * 
 * @param errorHandler - The error handling hook result
 * @param options - Additional options for the error handler
 * @returns A function to wrap async operations with error handling
 */
export const createAsyncErrorHandler = <T>(
  errorHandler: UseErrorHandlingResult,
  options: {
    showToast?: boolean;
    defaultErrorMessage?: string;
    onError?: (error: unknown) => void;
    context?: string;
  } = {}
) => {
  const { 
    handleError, 
    showErrorToast, 
    showAndClearError
  } = errorHandler;
  
  const {
    showToast = false,
    defaultErrorMessage = 'An error occurred',
    onError = () => {},
    context = 'unknown'
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
    operationName?: string
  ): Promise<R | undefined> => {
    try {
      return await asyncOperation();
    } catch (error) {
      const errorLocation = `${context}:${operationName || 'async operation'}`;
      console.error(`[ERROR:${errorLocation}]`, error);
      
      if (error instanceof Error) {
        console.error(`[ERROR:${errorLocation}] Stack trace:`, error.stack);
      }
      
      // Log navigation-related errors more prominently
      if (
        errorLocation.includes('navigation') || 
        errorLocation.includes('route') ||
        (error instanceof Error && 
          (error.message.includes('navigation') || 
           error.message.includes('route') ||
           error.message.includes('page')))
      ) {
        console.warn('[NAVIGATION_ERROR] This error may affect state synchronization across pages:', error);
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
 * Helper to standardize React Query error handling
 * 
 * @param errorHandler - The error handling hook result
 * @param options - Additional options
 * @returns An object with onError functions for React Query
 */
export const createQueryErrorHandler = (
  errorHandler: UseErrorHandlingResult,
  options: {
    showToast?: boolean;
    defaultErrorMessage?: string;
    context?: string;
  } = {}
) => {
  const { handleError, showErrorToast } = errorHandler;
  const { 
    showToast = true,
    defaultErrorMessage = 'An error occurred during the operation',
    context = 'reactQuery'
  } = options;
  
  return {
    /**
     * onError handler for React Query hooks
     */
    onQueryError: (error: unknown) => {
      console.error(`[ERROR:${context}:query]`, error);
      
      if (error instanceof Error) {
        console.error(`[ERROR:${context}:query] Stack trace:`, error.stack);
        
        // Check if this might be an auth-related error
        if (
          error.message.includes('auth') || 
          error.message.includes('token') ||
          error.message.includes('permission') ||
          error.message.includes('unauthorized') ||
          error.message.includes('401')
        ) {
          console.warn('[AUTH_ERROR] This error may be related to authentication issues:', error.message);
        }
      }
      
      handleError(error);
      if (showToast) {
        showErrorToast();
      }
    },
    
    /**
     * onError handler for React Query mutations
     */
    onMutationError: (error: unknown) => {
      console.error(`[ERROR:${context}:mutation]`, error);
      
      if (error instanceof Error) {
        console.error(`[ERROR:${context}:mutation] Stack trace:`, error.stack);
      }
      
      handleError(error);
      if (showToast) {
        showErrorToast();
      }
    }
  };
}; 