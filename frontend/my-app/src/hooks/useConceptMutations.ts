import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { 
  GenerationResponse, 
  PromptRequest, 
  RefinementRequest,
  TaskResponse
} from '../types';
import { useAuth } from '../contexts/AuthContext';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';
import { useRateLimitsDecrement } from '../contexts/RateLimitContext';
import { useTaskPolling } from './useTaskPolling';
import { useState } from 'react';

/**
 * Hook for generating a new concept using React Query's mutation capabilities
 */
export function useGenerateConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const errorHandler = useErrorHandling();
  const decrementLimit = useRateLimitsDecrement();
  const [taskId, setTaskId] = useState<string | null>(null);
  
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to generate concept',
    showToast: true
  });

  // Set up task polling
  const { data: taskData } = useTaskPolling(taskId, {
    onSuccess: async (task) => {
      if (task.result_id) {
        // Fetch the completed concept
        try {
          const response = await apiClient.get<GenerationResponse>(`/concepts/${task.result_id}`);
          const data = response.data;

          // Update caches and invalidate queries
          if (data) {
            console.log('[Mutation] Generation task completed, invalidating queries', {
              newConceptId: data.id,
              userId: user?.id,
              timestamp: new Date().toISOString()
            });
            
            // Invalidate recent concepts list
            queryClient.invalidateQueries({ 
              queryKey: ['concepts', 'recent', user?.id] 
            });
            
            // Pre-populate the detail view cache
            queryClient.setQueryData(['concepts', 'detail', data.id, user?.id], data);
            
            // Invalidate rate limits
            queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
          }
        } catch (error) {
          console.error('[useGenerateConceptMutation] Error fetching completed concept:', error);
          onQueryError(error);
        }
      }
    },
    onError: (error) => {
      console.error('[useGenerateConceptMutation] Task failed:', error);
      onQueryError(error);
    }
  });
  
  return useMutation<TaskResponse, Error, PromptRequest>({
    mutationKey: ['conceptGeneration'],
    mutationFn: async (data) => {
      console.log('[useGenerateConceptMutation] Starting generation', {
        timestamp: new Date().toISOString(),
        logoDescription: data.logo_description.substring(0, 20) + '...',
        themeDescription: data.theme_description.substring(0, 20) + '...'
      });
      
      try {
        // Apply optimistic update for rate limits
        decrementLimit('generate_concept');
        
        // Make the API request
        const response = await apiClient.post<TaskResponse>('/concepts/generate-with-palettes', data);
        
        if (!response.data) {
          throw new Error('No task data returned from API');
        }
        
        // Store task ID for polling
        setTaskId(response.data.id);
        
        return response.data;
      } catch (error) {
        console.error('[useGenerateConceptMutation] Error during fetch:', error);
        throw error;
      }
    },
    onError: (error) => {
      console.error('[useGenerateConceptMutation] Error during generation:', error);
      onQueryError(error);
    },
    onSettled: () => {
      console.log('[useGenerateConceptMutation] Generation settled', {
        timestamp: new Date().toISOString()
      });
      
      // Clean up the mutation cache
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
  const [taskId, setTaskId] = useState<string | null>(null);
  
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to refine concept',
    showToast: true
  });

  // Set up task polling
  const { data: taskData } = useTaskPolling(taskId, {
    onSuccess: async (task) => {
      if (task.result_id) {
        // Fetch the completed concept
        try {
          const response = await apiClient.get<GenerationResponse>(`/concepts/${task.result_id}`);
          const data = response.data;

          if (data) {
            console.log('[Mutation] Refinement task completed, invalidating queries', {
              newConceptId: data.id,
              userId: user?.id,
              timestamp: new Date().toISOString()
            });
            
            // Invalidate recent concepts list
            queryClient.invalidateQueries({ 
              queryKey: ['concepts', 'recent', user?.id] 
            });
            
            // Pre-populate the detail view cache
            queryClient.setQueryData(['concepts', 'detail', data.id, user?.id], data);
            
            // Invalidate rate limits
            queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
          }
        } catch (error) {
          console.error('[useRefineConceptMutation] Error fetching completed concept:', error);
          onQueryError(error);
        }
      }
    },
    onError: (error) => {
      console.error('[useRefineConceptMutation] Task failed:', error);
      onQueryError(error);
    }
  });
  
  return useMutation<TaskResponse, Error, RefinementRequest>({
    mutationKey: ['conceptRefinement'],
    mutationFn: async (data) => {
      console.log('[useRefineConceptMutation] Starting refinement', {
        timestamp: new Date().toISOString()
      });
      
      try {
        // Apply optimistic update for rate limits
        decrementLimit('refine_concept');
        
        // Make the API request
        const response = await apiClient.post<TaskResponse>('/concepts/refine', data);
        
        if (!response.data) {
          throw new Error('No task data returned from API');
        }
        
        // Store task ID for polling
        setTaskId(response.data.id);
        
        return response.data;
      } catch (error) {
        console.error('[useRefineConceptMutation] Error during fetch:', error);
        throw error;
      }
    },
    onError: (error) => {
      console.error('[useRefineConceptMutation] Error during refinement:', error);
      onQueryError(error);
    },
    onSettled: () => {
      console.log('[useRefineConceptMutation] Refinement settled', {
        timestamp: new Date().toISOString()
      });
      
      // Clean up the mutation cache
      setTimeout(() => {
        queryClient.removeQueries({ queryKey: ['conceptRefinement'] });
      }, 300);
    }
  });
} 