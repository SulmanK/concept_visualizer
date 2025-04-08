import React, { ReactNode, useMemo } from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { useRateLimits as useRateLimitsHook } from '../hooks/useRateLimits';
import { RateLimitsResponse, RateLimitCategory } from '../services/rateLimitService';

// Define the shape of the context data, matching the return type of useRateLimits
interface RateLimitContextType {
  // Rate limit data and loading state
  rateLimits: RateLimitsResponse | null;
  isLoading: boolean;
  error: string | null;
  
  // Functions to interact with rate limit data
  refetch: (forceRefresh?: boolean) => Promise<void>;
  
  /**
   * Optimistically decrements a rate limit category before the API call completes
   * @param category The rate limit category to decrement (e.g., 'generate_concept')
   * @param amount The amount to decrement by (default: 1)
   */
  decrementLimit: (category: RateLimitCategory, amount?: number) => void;
}

// Create the context with an initial undefined value
const RateLimitContext = createContext<RateLimitContextType>({
  rateLimits: null,
  isLoading: false,
  error: null,
  refetch: async () => {},
  decrementLimit: () => {}
});

// Define props for the provider component
interface RateLimitProviderProps {
  children: ReactNode;
}

/**
 * Provides rate limit state to its children components.
 * Fetches and manages rate limit data using the useRateLimits hook.
 * Includes functions for optimistic updates.
 */
export const RateLimitProvider: React.FC<RateLimitProviderProps> = ({ children }) => {
  // Use the enhanced hook with decrementLimit functionality
  const rateLimitState = useRateLimitsHook();

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    ...rateLimitState
  }), [rateLimitState]);

  return (
    <RateLimitContext.Provider value={contextValue}>
      {children}
    </RateLimitContext.Provider>
  );
};

/**
 * Custom hooks to selectively consume parts of the rate limit context.
 * These hooks ensure components only re-render when their specific dependencies change.
 */

/**
 * Hook to access the rate limits data
 */
export const useRateLimitsData = () => {
  return useContextSelector(RateLimitContext, state => state.rateLimits);
};

/**
 * Hook to access the loading state
 */
export const useRateLimitsLoading = () => {
  return useContextSelector(RateLimitContext, state => state.isLoading);
};

/**
 * Hook to access the error state
 */
export const useRateLimitsError = () => {
  return useContextSelector(RateLimitContext, state => state.error);
};

/**
 * Hook to access the refetch function
 */
export const useRateLimitsRefetch = () => {
  return useContextSelector(RateLimitContext, state => state.refetch);
};

/**
 * Hook to access the decrementLimit function
 */
export const useRateLimitsDecrement = () => {
  return useContextSelector(RateLimitContext, state => state.decrementLimit);
};

/**
 * Original hook to consume the entire rate limit context.
 * This is maintained for backward compatibility but components
 * should migrate to using the more specific selector hooks above.
 * 
 * @example
 * const { rateLimits, decrementLimit } = useRateLimitContext();
 * 
 * // When user initiates an action that will consume a rate limit:
 * const handleGenerateClick = () => {
 *   // Update UI immediately before API call
 *   decrementLimit('generate_concept');
 *   
 *   // Then make the actual API call
 *   apiClient.post('/concepts/generate', payload);
 * };
 */
export const useRateLimitContext = (): RateLimitContextType => {
  // These individual selectors prevent re-renders for the entire context
  const rateLimits = useRateLimitsData();
  const isLoading = useRateLimitsLoading();
  const error = useRateLimitsError();
  const refetch = useRateLimitsRefetch();
  const decrementLimit = useRateLimitsDecrement();
  
  // Memoize the result to prevent unnecessary re-renders
  return useMemo(() => ({
    rateLimits,
    isLoading,
    error,
    refetch,
    decrementLimit
  }), [rateLimits, isLoading, error, refetch, decrementLimit]);
}; 