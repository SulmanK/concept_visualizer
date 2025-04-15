import { useQuery, useMutation, UseMutationResult, UseQueryResult } from '@tanstack/react-query';
import { TaskResponse } from '../types/api.types';
import { apiClient } from '../services/apiClient';
import { API_ENDPOINTS } from '../config/apiEndpoints';
import { queryKeys } from '../config/queryKeys';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';
import { useState, useEffect } from 'react';

/**
 * Fetches the status of a task from the API
 * @param taskId The ID of the task to fetch
 * @returns The task response object
 */
async function fetchTaskStatus(taskId: string): Promise<TaskResponse> {
  if (!taskId) {
    throw new Error('No task ID provided for status check');
  }
  
  const startTime = Date.now();
  console.log(`[API] Fetching status for task ${taskId} at ${new Date().toISOString()}`);
  
  try {
    const response = await apiClient.get<TaskResponse>(API_ENDPOINTS.TASK_STATUS_BY_ID(taskId));
    
    // Normalize the response by ensuring the id field is set properly
    if (response.data.task_id && !response.data.id) {
      response.data.id = response.data.task_id;
    }
    
    const duration = Date.now() - startTime;
    console.log(`[API] Received status for task ${taskId}: ${response.data.status} (took ${duration}ms)`);
    return response.data;
  } catch (error) {
    const duration = Date.now() - startTime;
    console.error(`[API] Error fetching status for task ${taskId} (took ${duration}ms):`, error);
    throw error;
  }
}

/**
 * Hook to fetch a task status
 * 
 * @param taskId - ID of the task to fetch
 * @param options - Query options
 * @returns Query result for task status
 */
export function useTaskStatusQuery(
  taskId: string | null | undefined,
  options: { 
    enabled?: boolean,
    refetchInterval?: number | false,
    refetchIntervalInBackground?: boolean,
    refetchOnWindowFocus?: boolean,
    onSuccess?: (data: TaskResponse) => void
  } = {}
): UseQueryResult<TaskResponse, Error> {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);
  
  // Track document visibility state
  const [isDocumentVisible, setIsDocumentVisible] = useState(() => 
    typeof document !== 'undefined' ? document.visibilityState === 'visible' : true
  );
  
  // Update visibility state
  useEffect(() => {
    const handleVisibilityChange = () => {
      const isVisible = document.visibilityState === 'visible';
      setIsDocumentVisible(isVisible);
      console.log(`[TaskQuery] Document visibility changed to ${isVisible ? 'visible' : 'hidden'} for task ${taskId}`);
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [taskId]);
  
  // Log when the hook is used and when options change
  useEffect(() => {
    if (taskId) {
      console.log(`[TaskQuery] useTaskStatusQuery for task ${taskId} with options:`, {
        enabled: options.enabled !== false,
        refetchInterval: options.refetchInterval,
        refetchIntervalInBackground: options.refetchIntervalInBackground,
        refetchOnWindowFocus: options.refetchOnWindowFocus,
        hasSuccessCallback: !!options.onSuccess,
        isDocumentVisible
      });
    }
  }, [
    taskId, 
    options.enabled, 
    options.refetchInterval, 
    options.refetchIntervalInBackground, 
    options.refetchOnWindowFocus, 
    options.onSuccess,
    isDocumentVisible
  ]);
  
  return useQuery<TaskResponse, Error>({
    queryKey: queryKeys.tasks.detail(taskId),
    queryFn: () => {
      if (!taskId) {
        throw new Error('No task ID provided');
      }
      return fetchTaskStatus(taskId);
    },
    enabled: !!taskId && (options.enabled !== false) && isDocumentVisible,
    refetchInterval: 
      !!taskId && 
      (options.enabled !== false) && 
      isDocumentVisible && 
      options.refetchInterval ? 
      options.refetchInterval : false,
    refetchIntervalInBackground: options.refetchIntervalInBackground,
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? true, // Default to true
    onSuccess: (data) => {
      console.log(`[TaskQuery] Success fetching task ${taskId} status: ${data.status}`);
      if (options.onSuccess) {
        options.onSuccess(data);
      }
    },
    onError: (error) => {
      console.error(`[TaskQuery] Error fetching task ${taskId} status:`, error);
      onQueryError(error);
    },
    // Force data refresh after tab becomes active again
    refetchOnReconnect: true,
    // Use optimistic stale time that ensures data is always fetched
    staleTime: 0,
  });
}

/**
 * Hook to cancel a task
 * 
 * @returns Mutation result for task cancellation
 */
export function useTaskCancelMutation(): UseMutationResult<
  TaskResponse, 
  Error,
  string,
  unknown
> {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);
  
  return useMutation<TaskResponse, Error, string>({
    mutationFn: async (taskId: string) => {
      if (!taskId) {
        throw new Error('No task ID provided for cancellation');
      }
      
      console.log(`[API] Cancelling task ${taskId}`);
      const response = await apiClient.post<TaskResponse>(API_ENDPOINTS.TASK_CANCEL(taskId));
      return response.data;
    },
    onError: onQueryError,
  });
} 