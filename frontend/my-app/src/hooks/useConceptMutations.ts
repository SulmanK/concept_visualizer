import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { 
  GenerationResponse, 
  PromptRequest, 
  RefinementRequest 
} from '../types';
import { useAuth } from '../contexts/AuthContext';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';
import { useRateLimitsDecrement } from '../contexts/RateLimitContext';

/**
 * Hook for generating a new concept using React Query's mutation capabilities
 */
export function useGenerateConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const errorHandler = useErrorHandling();
  const decrementLimit = useRateLimitsDecrement();
  
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to generate concept',
    showToast: true
  });
  
  return useMutation<GenerationResponse, Error, PromptRequest>({
    mutationFn: async (data) => {
      // Apply optimistic update for rate limits
      decrementLimit('generate_concept');
      
      // Make the API request
      const response = await apiClient.post<GenerationResponse>(
        '/concepts/generate-with-palettes', 
        data
      );
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      if (!response.data) {
        throw new Error('No data returned from API');
      }
      
      // Make sure the variations array is included in the result
      return {
        ...response.data,
        variations: response.data.variations || []
      };
    },
    onSuccess: (data) => {
      // Invalidate recent concepts list on success
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent', user?.id] 
      });
      
      // Optionally pre-populate the detail view cache
      if (data?.id) {
        queryClient.setQueryData(['concepts', 'detail', data.id], data);
      }
      
      // Also invalidate rate limits to refresh them
      queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
    },
    onError: onQueryError
  });
}

/**
 * Hook for refining an existing concept using React Query's mutation capabilities
 */
export function useRefineConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const errorHandler = useErrorHandling();
  const decrementLimit = useRateLimitsDecrement();
  
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to refine concept',
    showToast: true
  });
  
  return useMutation<GenerationResponse, Error, RefinementRequest>({
    mutationFn: async (data) => {
      // Apply optimistic update for rate limits
      decrementLimit('refine_concept');
      
      // Make the API request
      const response = await apiClient.post<GenerationResponse>('/concepts/refine', data);
      
      if (response.error) {
        throw new Error(response.error.message);
      }
      
      if (!response.data) {
        throw new Error('No data returned from API');
      }
      
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Extract concept ID from the original image URL if possible
      // This assumes the URL contains the concept ID in a predictable format
      const originalUrl = variables.original_image_url;
      const conceptIdMatch = originalUrl.match(/\/concepts\/([^\/]+)/);
      const originalConceptId = conceptIdMatch ? conceptIdMatch[1] : null;
      
      // Invalidate specific concept detail if we could extract an ID
      if (originalConceptId) {
        queryClient.invalidateQueries({ 
          queryKey: ['concepts', 'detail', originalConceptId] 
        });
      }
      
      // Invalidate recent concepts list
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent', user?.id] 
      });
      
      // Optionally pre-populate the detail view cache for the new concept
      if (data?.id) {
        queryClient.setQueryData(['concepts', 'detail', data.id], data);
      }
      
      // Also invalidate rate limits to refresh them
      queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
    },
    onError: onQueryError
  });
} 