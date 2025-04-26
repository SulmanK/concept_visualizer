import React, { ReactNode, useMemo, useCallback } from "react";
import { createContext } from "use-context-selector";
import {
  useRateLimitsQuery,
  useOptimisticRateLimitUpdate,
} from "../hooks/useRateLimitsQuery";
import {
  RateLimitsResponse,
  RateLimitCategory,
} from "../services/rateLimitService";
import { useQueryClient } from "@tanstack/react-query";

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

// Create and export the context so it can be imported by hooks
export const RateLimitContext = createContext<RateLimitContextType>({
  rateLimits: null,
  isLoading: false,
  error: null,
  refetch: async () => {},
  decrementLimit: () => {},
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
export const RateLimitProvider: React.FC<RateLimitProviderProps> = ({
  children,
}) => {
  const queryClient = useQueryClient();

  // Use React Query for data fetching
  const {
    data,
    isLoading,
    error,
    refetch: queryRefetch,
  } = useRateLimitsQuery();

  // Get the optimistic update function
  const { decrementLimit } = useOptimisticRateLimitUpdate();

  // Custom refetch function that forces a refresh - wrapped in useCallback to prevent unnecessary re-renders
  const refetch = useCallback(
    async (forceRefresh: boolean = false) => {
      if (forceRefresh) {
        // Clear the cache first to ensure fresh data
        queryClient.removeQueries({ queryKey: ["rateLimits"] });
      }
      await queryRefetch();
    },
    [queryClient, queryRefetch],
  );

  // Memoize the context value to prevent unnecessary re-renders
  const contextValue = useMemo(
    (): RateLimitContextType => ({
      rateLimits: data as RateLimitsResponse | null,
      isLoading,
      error: error ? error.message : null,
      refetch,
      decrementLimit,
    }),
    [data, isLoading, error, refetch, decrementLimit],
  );

  return (
    <RateLimitContext.Provider value={contextValue}>
      {children}
    </RateLimitContext.Provider>
  );
};

// Hooks are now exported from src/hooks/useRateLimits.ts
