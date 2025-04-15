import React, { ReactNode, useMemo, useEffect } from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { useRateLimitsQuery, useOptimisticRateLimitUpdate } from '../hooks/useRateLimitsQuery';
import { RateLimitsResponse, RateLimitCategory, fetchRateLimits } from '../services/rateLimitService';
import { useQueryClient } from '@tanstack/react-query';

// Define the shape of the context data
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
 * Fetches and manages rate limit data using React Query.
 * Includes functions for optimistic updates.
 */
export const RateLimitProvider: React.FC<RateLimitProviderProps> = ({ children }) => {
  const queryClient = useQueryClient();
  
  // Use React Query for data fetching
  const { 
    data, 
    isLoading, 
    error,
    refetch: queryRefetch 
  } = useRateLimitsQuery();
  
  // Get the optimistic update function
  const { decrementLimit } = useOptimisticRateLimitUpdate();
  
  // Custom refetch function that forces a refresh
  const refetch = async (forceRefresh: boolean = false) => {
    if (forceRefresh) {
      // Clear the cache first to ensure fresh data
      queryClient.removeQueries({ queryKey: ['rateLimits'] });
    }
    await queryRefetch();
  };

  // Add visibility change handler to refresh rate limits when tab becomes visible
  useEffect(() => {
    // Track when tab was last hidden
    let tabInactiveStartTime = 0;
    
    const handleVisibilityChange = async () => {
      if (document.visibilityState === 'visible') {
        const inactiveTimeMs = tabInactiveStartTime > 0 ? Date.now() - tabInactiveStartTime : 0;
        
        console.log(`[RateLimit] Tab became visible after ${Math.round(inactiveTimeMs/1000)}s, checking rate limits`);
        
        // Only force refresh if tab was inactive for more than 10 seconds
        // This prevents unnecessary refreshes for quick tab switches
        if (inactiveTimeMs > 10000) {
          console.log('[RateLimit] Long inactivity detected, forcing rate limits refresh');
          
          try {
            // Small delay to avoid multiple simultaneous requests on tab focus
            await new Promise(resolve => setTimeout(resolve, 300));
            
            // Fetch fresh data directly
            const freshData = await fetchRateLimits(true);
            
            // Update query cache with the fresh data
            queryClient.setQueryData(['rateLimits'], freshData);
            
            console.log('[RateLimit] Successfully refreshed rate limits after tab focus');
          } catch (err) {
            console.error('[RateLimit] Failed to refresh rate limits after tab focus:', err);
          }
        } else {
          // Just perform a normal refetch for short inactivity periods
          refetch(false).catch(err => 
            console.error('[RateLimit] Error in normal refetch after tab focus:', err)
          );
        }
        
        // Reset inactive timer
        tabInactiveStartTime = 0;
      } else if (document.visibilityState === 'hidden') {
        // Record when the tab was hidden
        tabInactiveStartTime = Date.now();
        console.log('[RateLimit] Tab hidden, tracking inactivity time');
      }
    };
    
    // Add event listener for visibility changes
    document.addEventListener('visibilitychange', handleVisibilityChange);
    
    // Clean up the event listener on unmount
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [queryClient]);

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo((): RateLimitContextType => ({
    rateLimits: data as RateLimitsResponse | null,
    isLoading,
    error: error ? error.message : null,
    refetch,
    decrementLimit
  }), [data, isLoading, error, refetch, decrementLimit]);

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