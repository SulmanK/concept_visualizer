import {
  useQuery,
  UseQueryResult,
  UseQueryOptions,
} from "@tanstack/react-query";
import { ConceptData } from "../services/supabaseClient";
import { useErrorHandling } from "./useErrorHandling";
import { createQueryErrorHandler } from "../utils/errorUtils";
import {
  fetchRecentConceptsFromApi,
  fetchConceptDetailFromApi,
} from "../services/conceptService";
import { NotFoundError } from "../services/apiClient";

/**
 * Custom hook to fetch and cache recent concepts with standardized error handling
 * @returns Query result with array of concept data
 */
export function useRecentConcepts(
  userId: string | undefined,
  limit: number = 10,
): UseQueryResult<ConceptData[], Error> {
  // Set up error handling
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: "Failed to load recent concepts",
    showToast: false,
  });

  const queryKey = ["concepts", "recent", userId, limit];

  return useQuery<ConceptData[], Error>({
    queryKey,
    queryFn: async () => {
      if (!userId) {
        // Return empty array silently without logging
        return [];
      }

      const fetchStartTime = new Date().toISOString();
      console.log(
        `[useRecentConcepts] Fetching concepts for user: ${userId.substring(
          0,
          6,
        )}...`,
        {
          timestamp: fetchStartTime,
          queryKey: JSON.stringify(queryKey),
        },
      );

      try {
        // Use the new API service
        const concepts = await fetchRecentConceptsFromApi(userId, limit);

        const fetchEndTime = new Date().toISOString();
        console.log(`[useRecentConcepts] Fetched ${concepts.length} concepts`, {
          timestamp: fetchEndTime,
          conceptIds: concepts.map((c) => c.id).join(", "),
          fetchTime:
            new Date(fetchEndTime).getTime() -
            new Date(fetchStartTime).getTime() +
            "ms",
        });

        return concepts;
      } catch (error) {
        // Special handling for different error types
        console.error(
          "[useRecentConcepts] Error fetching recent concepts:",
          error,
        );

        // Let the error handler handle the error centrally
        onQueryError(error);

        // Re-throw to let React Query handle the error state
        throw error;
      }
    },
    enabled: !!userId, // Only run the query if we have a userId
    staleTime: 60 * 1000, // 1 minute
    // Use the meta approach instead of direct onError to avoid type issues
    meta: {
      onError: (error: Error) => {
        console.error("[useRecentConcepts] Query error:", error);
        onQueryError(error);
      },
    },
  } as UseQueryOptions<ConceptData[], Error>);
}

/**
 * Custom hook to fetch and cache a specific concept with standardized error handling
 */
export function useConceptDetail(
  conceptId: string | undefined,
  userId: string | undefined,
): UseQueryResult<ConceptData | null, Error> {
  // Set up error handling
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: "Failed to load concept details",
    showToast: false,
  });

  const queryKey = ["concepts", "detail", conceptId, userId];

  return useQuery<ConceptData | null, Error>({
    queryKey,
    queryFn: async () => {
      if (!conceptId || !userId) {
        return null;
      }

      const fetchStartTime = new Date().toISOString();
      console.log(`[useConceptDetail] Fetching concept: ${conceptId}`, {
        timestamp: fetchStartTime,
        queryKey: JSON.stringify(queryKey),
      });

      try {
        // Use the new API service
        const concept = await fetchConceptDetailFromApi(conceptId);

        const fetchEndTime = new Date().toISOString();
        if (!concept) {
          console.log(`[useConceptDetail] Concept not found: ${conceptId}`, {
            timestamp: fetchEndTime,
          });

          // Throw a not found error
          throw new NotFoundError(
            `Concept with ID ${conceptId} was not found`,
            `/concepts/${conceptId}`,
          );
        }

        console.log(`[useConceptDetail] Fetched concept:`, {
          timestamp: fetchEndTime,
          conceptId: concept.id,
          variationsCount: concept.color_variations?.length || 0,
          fetchTime:
            new Date(fetchEndTime).getTime() -
            new Date(fetchStartTime).getTime() +
            "ms",
        });

        return concept;
      } catch (error) {
        // Special handling for different error types
        console.error(
          "[useConceptDetail] Error fetching concept details:",
          error,
        );

        // Let the error handler handle the error
        onQueryError(error);

        // Re-throw to let React Query handle the error state
        throw error;
      }
    },
    enabled: !!conceptId && !!userId, // Only run if we have both IDs
    refetchOnMount: "always", // Always refetch on mount for this critical data
    refetchOnWindowFocus: true, // Always refetch on window focus
    // Use the meta approach instead of direct onError to avoid type issues
    meta: {
      onError: (error: Error) => {
        console.error("[useConceptDetail] Query error:", error);
        onQueryError(error);
      },
    },
  } as UseQueryOptions<ConceptData | null, Error>);
}
