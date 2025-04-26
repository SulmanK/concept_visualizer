import { useMemo } from "react";
import { useContextSelector } from "use-context-selector";
import { RateLimitContext } from "../contexts/RateLimitContext";
import { RateLimitCategory } from "../services/rateLimitService";

/**
 * Hook to access the rate limits data
 */
export const useRateLimitsData = () => {
  return useContextSelector(RateLimitContext, (state) => state.rateLimits);
};

/**
 * Hook to access the loading state
 */
export const useRateLimitsLoading = () => {
  return useContextSelector(RateLimitContext, (state) => state.isLoading);
};

/**
 * Hook to access the error state
 */
export const useRateLimitsError = () => {
  return useContextSelector(RateLimitContext, (state) => state.error);
};

/**
 * Hook to access the refetch function
 */
export const useRateLimitsRefetch = () => {
  return useContextSelector(RateLimitContext, (state) => state.refetch);
};

/**
 * Hook to access the decrementLimit function
 */
export const useRateLimitsDecrement = () => {
  return useContextSelector(RateLimitContext, (state) => state.decrementLimit);
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
export const useRateLimitContext = () => {
  // These individual selectors prevent re-renders for the entire context
  const rateLimits = useRateLimitsData();
  const isLoading = useRateLimitsLoading();
  const error = useRateLimitsError();
  const refetch = useRateLimitsRefetch();
  const decrementLimit = useRateLimitsDecrement();

  // Memoize the result to prevent unnecessary re-renders
  return useMemo(
    () => ({
      rateLimits,
      isLoading,
      error,
      refetch,
      decrementLimit,
    }),
    [rateLimits, isLoading, error, refetch, decrementLimit],
  );
};

/**
 * Convenience function to decrement a rate limit
 * @param category The category to decrement
 * @param amount Amount to decrement by (default: 1)
 */
export const useDecrementRateLimit = () => {
  const decrementLimit = useRateLimitsDecrement();

  return (category: RateLimitCategory, amount: number = 1) => {
    decrementLimit(category, amount);
  };
};
