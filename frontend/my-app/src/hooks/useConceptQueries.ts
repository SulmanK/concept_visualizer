import { useQuery, UseQueryResult, UseQueryOptions } from '@tanstack/react-query';
import { 
  ConceptData
} from '../services/supabaseClient';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';
import { fetchRecentConceptsFromApi, fetchConceptDetailFromApi } from '../services/conceptService';

/**
 * Custom hook to fetch and cache recent concepts with standardized error handling
 * @returns Query result with array of concept data
 */
export function useRecentConcepts(
  userId: string | undefined, 
  limit: number = 10
): UseQueryResult<ConceptData[], Error> {
  // Set up error handling
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);
  
  const queryKey = ['concepts', 'recent', userId, limit];
  
  return useQuery<ConceptData[], Error>({
    queryKey,
    queryFn: async () => {
      if (!userId) return [];
      
      const fetchStartTime = new Date().toISOString();
      console.log(`[useRecentConcepts] Fetching concepts for user: ${userId.substring(0, 6)}...`, {
        timestamp: fetchStartTime,
        queryKey: JSON.stringify(queryKey)
      });
      
      // Use the new API service instead of direct Supabase calls
      const concepts = await fetchRecentConceptsFromApi(userId, limit);
      
      const fetchEndTime = new Date().toISOString();
      console.log(`[useRecentConcepts] Fetched ${concepts.length} concepts`, {
        timestamp: fetchEndTime,
        conceptIds: concepts.map(c => c.id).join(', '),
        fetchTime: new Date(fetchEndTime).getTime() - new Date(fetchStartTime).getTime() + 'ms'
      });
      
      return concepts;
    },
    enabled: !!userId, // Only run the query if we have a userId
    // Use onError in a type-safe way
    ...onQueryError ? { 
      meta: {
        onError: onQueryError
      }
    } : {}
  } as UseQueryOptions<ConceptData[], Error>);
}

/**
 * Custom hook to fetch and cache a specific concept with standardized error handling
 */
export function useConceptDetail(
  conceptId: string | undefined, 
  userId: string | undefined
): UseQueryResult<ConceptData | null, Error> {
  // Set up error handling
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);
  
  const queryKey = ['concepts', 'detail', conceptId, userId];
  
  return useQuery<ConceptData | null, Error>({
    queryKey,
    queryFn: async () => {
      if (!conceptId || !userId) return null;
      
      const fetchStartTime = new Date().toISOString();
      console.log(`[useConceptDetail] Fetching concept: ${conceptId}`, {
        timestamp: fetchStartTime,
        queryKey: JSON.stringify(queryKey)
      });
      
      // Use the new API service instead of direct Supabase calls
      const concept = await fetchConceptDetailFromApi(conceptId);
      
      const fetchEndTime = new Date().toISOString();
      if (!concept) {
        console.log(`[useConceptDetail] Concept not found: ${conceptId}`, {
          timestamp: fetchEndTime
        });
        return null;
      }
      
      console.log(`[useConceptDetail] Fetched concept:`, {
        timestamp: fetchEndTime,
        conceptId: concept.id,
        variationsCount: concept.color_variations?.length || 0,
        fetchTime: new Date(fetchEndTime).getTime() - new Date(fetchStartTime).getTime() + 'ms'
      });
      
      return concept;
    },
    enabled: !!conceptId && !!userId, // Only run if we have both IDs
    refetchOnMount: 'always', // Always refetch on mount for this critical data
    refetchOnWindowFocus: true, // Always refetch on window focus
    // Use onError in a type-safe way
    ...onQueryError ? { 
      meta: {
        onError: onQueryError
      }
    } : {}
  } as UseQueryOptions<ConceptData | null, Error>);
} 