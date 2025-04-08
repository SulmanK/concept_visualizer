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
    onError = () => {}
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
      console.error(`Error in ${operationName || 'async operation'}:`, error);
      
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
  } = {}
) => {
  const { handleError, showErrorToast } = errorHandler;
  const { showToast = true } = options;
  
  return {
    /**
     * onError handler for React Query hooks
     */
    onQueryError: (error: unknown) => {
      handleError(error);
      if (showToast) {
        showErrorToast();
      }
    },
    
    /**
     * onError handler for React Query mutations
     */
    onMutationError: (error: unknown) => {
      handleError(error);
      if (showToast) {
        showErrorToast();
      }
    }
  };
}; 