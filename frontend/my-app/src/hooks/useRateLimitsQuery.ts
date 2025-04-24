import { useQuery, useQueryClient } from "@tanstack/react-query";
import {
  fetchRateLimits,
  RateLimitsResponse,
  RateLimitCategory,
} from "../services/rateLimitService";
import { useErrorHandling } from "./useErrorHandling";
import { createQueryErrorHandler } from "../utils/errorUtils";

/**
 * Hook that provides rate limit information using React Query
 * @returns Query result with rate limits data and utility functions
 */
export function useRateLimitsQuery() {
  const errorHandler = useErrorHandling();
  const queryClient = useQueryClient();
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    showToast: false, // Don't show toast for background refresh errors
  });

  const query = useQuery({
    queryKey: ["rateLimits"],
    queryFn: () => fetchRateLimits(false),
    staleTime: 1000 * 30,
    refetchInterval: 1000 * 60,
    refetchOnWindowFocus: true,
    refetchIntervalInBackground: true,
    onError: onQueryError,
  });

  /**
   * Optimistically decrement a rate limit
   * @param category Rate limit category to decrement
   * @param amount Amount to decrement (default: 1)
   */
  const decrementLimit = (category: RateLimitCategory, amount = 1) => {
    queryClient.setQueryData<RateLimitsResponse>(["rateLimits"], (oldData) => {
      if (!oldData) return oldData;

      // Create a deep copy to avoid mutation
      const newData = JSON.parse(JSON.stringify(oldData)) as RateLimitsResponse;

      // Update the specific category if it exists
      if (newData.limits && newData.limits[category]) {
        newData.limits[category] = {
          ...newData.limits[category],
          remaining: Math.max(0, newData.limits[category].remaining - amount),
        };
      }

      return newData;
    });
  };

  /**
   * Enhanced refetch that ensures fresh data from the server
   * This overrides the standard refetch to force a true refresh
   */
  const enhancedRefetch = async () => {
    console.log("Performing enhanced rate limits refetch with force=true");

    try {
      // Force true refresh from server
      const freshData = await fetchRateLimits(true);

      // Update query cache with the fresh data
      queryClient.setQueryData(["rateLimits"], freshData);

      return {
        data: freshData,
        error: null,
        isSuccess: true,
        isError: false,
      };
    } catch (error) {
      console.error("Enhanced refetch failed:", error);
      return {
        data: query.data,
        error,
        isSuccess: false,
        isError: true,
      };
    }
  };

  // Return both the query result and the utility functions
  return {
    data: query.data as RateLimitsResponse | undefined,
    isLoading: query.isLoading,
    error: query.error,
    refetch: enhancedRefetch, // Use our enhanced refetch instead
    decrementLimit,
  };
}

/**
 * Hook that provides optimistic rate limit updates through React Query
 * @returns Functions to update rate limits optimistically
 */
export function useOptimisticRateLimitUpdate() {
  const queryClient = useQueryClient();

  /**
   * Optimistically decrement a rate limit
   * @param category Rate limit category to decrement
   * @param amount Amount to decrement (default: 1)
   */
  const decrementLimit = (category: RateLimitCategory, amount = 1) => {
    queryClient.setQueryData<RateLimitsResponse>(["rateLimits"], (oldData) => {
      if (!oldData) return oldData;

      // Create a deep copy to avoid mutation
      const newData = JSON.parse(JSON.stringify(oldData)) as RateLimitsResponse;

      // Update the specific category if it exists
      if (newData.limits && newData.limits[category]) {
        newData.limits[category] = {
          ...newData.limits[category],
          remaining: Math.max(0, newData.limits[category].remaining - amount),
        };
      }

      return newData;
    });
  };

  return { decrementLimit };
}
