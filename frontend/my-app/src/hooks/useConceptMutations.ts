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
import { useTaskContext } from '../contexts/TaskContext';

/**
 * Hook for generating a new concept using React Query's mutation capabilities
 */
export function useGenerateConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const errorHandler = useErrorHandling();
  const decrementLimit = useRateLimitsDecrement();
  const { setActiveTask, clearActiveTask } = useTaskContext();
  
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to generate concept',
    showToast: true
  });

  return useMutation<TaskResponse, Error, PromptRequest>({
    mutationKey: ['conceptGeneration'],
    mutationFn: async (data) => {
      console.log('[useGenerateConceptMutation] Starting generation', {
        timestamp: new Date().toISOString()
      });
      
      try {
        // Apply optimistic update for rate limits
        decrementLimit('generate_concept');
        
        // Make the API request
        const response = await apiClient.post<TaskResponse>('/concepts/generate-with-palettes', data);
        
        if (!response.data) {
          throw new Error('No task data returned from API');
        }
        
        // Set the task ID in the global context
        setActiveTask(response.data.id);
        
        return response.data;
      } catch (error) {
        console.error('[useGenerateConceptMutation] Error during fetch:', error);
        throw error;
      }
    },
    onError: (error) => {
      console.error('[useGenerateConceptMutation] Error during generation:', error);
      onQueryError(error);
      
      // Clear the active task on error
      clearActiveTask();
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
 * Hook for refining a concept using React Query's mutation capabilities
 */
export function useRefineConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const errorHandler = useErrorHandling();
  const decrementLimit = useRateLimitsDecrement();
  const { setActiveTask, clearActiveTask } = useTaskContext();
  
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to refine concept',
    showToast: true
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
        
        // Set the task ID in the global context
        setActiveTask(response.data.id);
        
        return response.data;
      } catch (error) {
        console.error('[useRefineConceptMutation] Error during fetch:', error);
        throw error;
      }
    },
    onError: (error) => {
      console.error('[useRefineConceptMutation] Error during refinement:', error);
      onQueryError(error);
      
      // Clear the active task on error
      clearActiveTask();
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