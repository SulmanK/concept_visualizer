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
    mutationKey: ['conceptGeneration'],
    mutationFn: async (data) => {
      // Log the start of generation with timestamp
      console.log('[useGenerateConceptMutation] Starting generation', {
        timestamp: new Date().toISOString(),
        logoDescription: data.logo_description.substring(0, 20) + '...',
        themeDescription: data.theme_description.substring(0, 20) + '...'
      });
      
      try {
        // Apply optimistic update for rate limits
        decrementLimit('generate_concept');
        
        // Get API base URL
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
        const url = `${API_BASE_URL}/concepts/generate-with-palettes`;
        
        console.log('[useGenerateConceptMutation] Making direct fetch to:', url);
        
        // Get auth headers from Supabase
        const authHeaders = {};
        try {
          const { supabase } = await import('../services/supabaseClient');
          const { data: { session } } = await supabase.auth.getSession();
          if (session?.access_token) {
            authHeaders['Authorization'] = `Bearer ${session.access_token}`;
          }
        } catch (authErr) {
          console.error('[useGenerateConceptMutation] Auth error:', authErr);
        }
        
        // Make the request directly with fetch for debugging
        const response = await fetch(url, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...authHeaders
          },
          body: JSON.stringify(data),
          credentials: 'include'
        });
        
        // Log response status for debugging
        console.log('[useGenerateConceptMutation] Response status:', response.status);
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error(`[useGenerateConceptMutation] API error (${response.status}):`, errorText);
          throw new Error(`API error: ${response.status} - ${errorText}`);
        }
        
        const responseData = await response.json();
        
        console.log('[useGenerateConceptMutation] Successfully received API response', {
          timestamp: new Date().toISOString(),
          conceptId: responseData.id,
          hasVariations: (responseData.variations?.length || 0) > 0
        });
        
        // Make sure the variations array is included in the result
        return {
          ...responseData,
          variations: responseData.variations || []
        };
      } catch (error) {
        console.error('[useGenerateConceptMutation] Error during fetch:', error);
        throw error;
      }
    },
    onSuccess: (data) => {
      console.log('[Mutation] Generation successful, invalidating queries', {
        newConceptId: data?.id,
        userId: user?.id,
        timestamp: new Date().toISOString()
      });
      
      // Invalidate recent concepts list on success
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent', user?.id] 
      });
      
      // Optionally pre-populate the detail view cache
      if (data?.id) {
        console.log('[Mutation] Pre-populating detail cache for new concept', data.id);
        queryClient.setQueryData(['concepts', 'detail', data.id, user?.id], data);
      }
      
      // Also invalidate rate limits to refresh them
      queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
      
      console.log('[Mutation] Query invalidation complete for generation');
    },
    onError: (error) => {
      console.error('[useGenerateConceptMutation] Error during generation:', error);
      onQueryError(error);
    },
    // Add an onSettled handler to ensure cleanup
    onSettled: (data, error) => {
      console.log('[useGenerateConceptMutation] Generation settled', {
        timestamp: new Date().toISOString(),
        success: !!data,
        error: !!error
      });
      
      // Clean up the mutation cache to ensure fresh state for next generation
      setTimeout(() => {
        queryClient.removeQueries({ queryKey: ['conceptGeneration'] });
      }, 300);
    }
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
    mutationKey: ['conceptRefinement'],
    mutationFn: async (data) => {
      // Log the start of refinement
      console.log('[useRefineConceptMutation] Starting refinement', {
        timestamp: new Date().toISOString()
      });
      
      // Apply optimistic update for rate limits
      decrementLimit('refine_concept');
      
      // Make the API request
      const response = await apiClient.post<GenerationResponse>('/concepts/refine', data);
      
      if (response.error) {
        console.error('[useRefineConceptMutation] API returned an error:', response.error);
        throw new Error(response.error.message);
      }
      
      if (!response.data) {
        console.error('[useRefineConceptMutation] API returned no data');
        throw new Error('No data returned from API');
      }
      
      console.log('[useRefineConceptMutation] Successfully received API response', {
        timestamp: new Date().toISOString(),
        conceptId: response.data.id
      });
      
      return response.data;
    },
    onSuccess: (data, variables) => {
      // Extract concept ID from the original image URL if possible
      // This assumes the URL contains the concept ID in a predictable format
      const originalUrl = variables.original_image_url;
      const conceptIdMatch = originalUrl.match(/\/concepts\/([^\/]+)/);
      const originalConceptId = conceptIdMatch ? conceptIdMatch[1] : null;
      
      console.log('[Mutation] Refinement successful, invalidating queries', {
        originalConceptId,
        newConceptId: data?.id,
        userId: user?.id,
        timestamp: new Date().toISOString()
      });
      
      // Invalidate specific concept detail if we could extract an ID
      if (originalConceptId) {
        console.log('[Mutation] Invalidating original concept detail', originalConceptId);
        queryClient.invalidateQueries({ 
          queryKey: ['concepts', 'detail', originalConceptId, user?.id] 
        });
      }
      
      // Invalidate recent concepts list
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent', user?.id] 
      });
      
      // Optionally pre-populate the detail view cache for the new concept
      if (data?.id) {
        console.log('[Mutation] Pre-populating detail cache for new refined concept', data.id);
        queryClient.setQueryData(['concepts', 'detail', data.id, user?.id], data);
      }
      
      // Also invalidate rate limits to refresh them
      queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
      
      console.log('[Mutation] Query invalidation complete for refinement');
    },
    onError: (error) => {
      console.error('[useRefineConceptMutation] Error during refinement:', error);
      onQueryError(error);
    },
    // Add an onSettled handler to ensure cleanup
    onSettled: (data, error) => {
      console.log('[useRefineConceptMutation] Refinement settled', {
        timestamp: new Date().toISOString(),
        success: !!data,
        error: !!error
      });
      
      // Clean up the mutation cache to ensure fresh state for next refinement
      setTimeout(() => {
        queryClient.removeQueries({ queryKey: ['conceptRefinement'] });
      }, 300);
    }
  });
} 