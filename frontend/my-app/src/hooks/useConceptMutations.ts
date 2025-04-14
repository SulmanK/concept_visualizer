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
 * Extract a more user-friendly error message from API error responses
 */
const getErrorMessageFromResponse = (error: any): string => {
  // Default error message
  let message = 'An unexpected error occurred';

  try {
    // Check if it's an axios error with response data
    if (error.response) {
      // Handle 422 Unprocessable Entity errors
      if (error.response.status === 422) {
        const data = error.response.data;
        
        // Extract validation error details
        if (data.detail) {
          if (Array.isArray(data.detail)) {
            // Get the first validation error message
            const firstError = data.detail[0];
            if (firstError.msg) {
              return firstError.msg;
            } else if (firstError.message) {
              return firstError.message;
            }
          } else if (typeof data.detail === 'string') {
            return data.detail;
          } else if (data.detail.msg) {
            return data.detail.msg;
          }
        }
        
        // Fallback for 422 errors
        return 'Invalid input: Please check your descriptions (minimum 5 characters required)';
      }
      
      // Extract message from other error responses
      if (error.response.data) {
        if (error.response.data.message) {
          message = error.response.data.message;
        } else if (error.response.data.error) {
          message = error.response.data.error;
        } else if (typeof error.response.data === 'string') {
          message = error.response.data;
        }
      }
    } else if (error.message) {
      // Direct error message
      message = error.message;
    }
  } catch (e) {
    console.error('Error while parsing API error:', e);
  }
  
  return message;
};

/**
 * Hook for generating a new concept using React Query's mutation capabilities
 */
export function useGenerateConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();
  const errorHandler = useErrorHandling();
  const decrementLimit = useRateLimitsDecrement();
  const { setActiveTask, clearActiveTask, setIsTaskInitiating, setLatestResultId } = useTaskContext();
  
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
        // Set initiating state to provide immediate feedback
        setIsTaskInitiating(true);
        
        // Set a timeout to clear the initiating state if the API call takes too long
        // This will prevent the UI from getting stuck in "initiating" if something goes wrong
        const initiatingTimeout = setTimeout(() => {
          console.log('[useGenerateConceptMutation] API call timeout, clearing initiating state');
          setIsTaskInitiating(false);
        }, 10000); // 10 seconds should be more than enough for the API to respond
        
        // Apply optimistic update for rate limits
        decrementLimit('generate_concept');
        
        // Make the API request
        const response = await apiClient.post<TaskResponse>('/concepts/generate-with-palettes', data);
        
        // Clear the timeout since we got a response
        clearTimeout(initiatingTimeout);
        
        if (!response.data) {
          throw new Error('No task data returned from API');
        }
        
        // Get the task ID from either id or task_id field (backend returns task_id)
        const taskId = response.data.task_id || response.data.id;
        
        // Set the task ID in the global context
        console.log(`[useGenerateConceptMutation] Setting active task ID: ${taskId}`);
        setActiveTask(taskId);
        
        // If result_id is already available, store it in the global context
        if (response.data.result_id) {
          console.log(`[useGenerateConceptMutation] Initial response already has result_id: ${response.data.result_id}`);
          setLatestResultId(response.data.result_id);
        }
        
        return response.data;
      } catch (error) {
        console.error('[useGenerateConceptMutation] Error during fetch:', error);
        // Make sure we clear the initiating state
        setIsTaskInitiating(false);
        
        // Create a more user-friendly error message
        const errorMessage = getErrorMessageFromResponse(error);
        const enhancedError = new Error(errorMessage);
        throw enhancedError;
      }
    },
    onError: (error) => {
      console.error('[useGenerateConceptMutation] Error during generation:', error);
      onQueryError(error);
      
      // Clear the active task and initiating state on error
      clearActiveTask();
      setIsTaskInitiating(false);
    },
    onSuccess: (response) => {
      console.log('[useGenerateConceptMutation] Success response:', {
        taskId: response.id || response.task_id,
        resultId: response.result_id,
        timestamp: new Date().toISOString()
      });
      
      // If we have a result_id, invalidate the concept detail query
      // This ensures that when navigating to the concept detail page, 
      // the data will be properly refetched
      if (response.result_id) {
        queryClient.invalidateQueries({
          queryKey: ['concepts', 'detail', response.result_id],
          exact: false
        });
        
        // Also invalidate recent concepts to ensure the concept list is refreshed
        queryClient.invalidateQueries({
          queryKey: ['concepts', 'recent'],
          exact: false
        });
      }
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
  const { setActiveTask, clearActiveTask, setIsTaskInitiating, setLatestResultId } = useTaskContext();
  
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
        // Set initiating state to provide immediate feedback
        setIsTaskInitiating(true);
        
        // Set a timeout to clear the initiating state if the API call takes too long
        // This will prevent the UI from getting stuck in "initiating" if something goes wrong
        const initiatingTimeout = setTimeout(() => {
          console.log('[useRefineConceptMutation] API call timeout, clearing initiating state');
          setIsTaskInitiating(false);
        }, 10000); // 10 seconds should be more than enough for the API to respond
        
        // Apply optimistic update for rate limits
        decrementLimit('refine_concept');
        
        // Make the API request
        const response = await apiClient.post<TaskResponse>('/concepts/refine', data);
        
        // Clear the timeout since we got a response
        clearTimeout(initiatingTimeout);
        
        if (!response.data) {
          throw new Error('No task data returned from API');
        }
        
        // Get the task ID from either id or task_id field (backend returns task_id)
        const taskId = response.data.task_id || response.data.id;
        
        // Set the task ID in the global context
        console.log(`[useRefineConceptMutation] Setting active task ID: ${taskId}`);
        setActiveTask(taskId);
        
        // If result_id is already available, store it in the global context
        if (response.data.result_id) {
          console.log(`[useRefineConceptMutation] Initial response already has result_id: ${response.data.result_id}`);
          setLatestResultId(response.data.result_id);
        }
        
        return response.data;
      } catch (error) {
        console.error('[useRefineConceptMutation] Error during fetch:', error);
        // Make sure we clear the initiating state
        setIsTaskInitiating(false);
        
        // Create a more user-friendly error message
        const errorMessage = getErrorMessageFromResponse(error);
        const enhancedError = new Error(errorMessage);
        throw enhancedError;
      }
    },
    onError: (error) => {
      console.error('[useRefineConceptMutation] Error during refinement:', error);
      onQueryError(error);
      
      // Clear the active task and initiating state on error
      clearActiveTask();
      setIsTaskInitiating(false);
    },
    onSuccess: (response) => {
      console.log('[useRefineConceptMutation] Success response:', {
        taskId: response.id || response.task_id,
        resultId: response.result_id,
        timestamp: new Date().toISOString()
      });
      
      // If we have a result_id, invalidate the concept detail query
      // This ensures that when navigating to the concept detail page, 
      // the data will be properly refetched
      if (response.result_id) {
        queryClient.invalidateQueries({
          queryKey: ['concepts', 'detail', response.result_id],
          exact: false
        });
        
        // Also invalidate recent concepts to ensure the concept list is refreshed
        queryClient.invalidateQueries({
          queryKey: ['concepts', 'recent'],
          exact: false
        });
      }
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