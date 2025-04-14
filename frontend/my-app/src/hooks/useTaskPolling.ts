import { useEffect, useMemo, useState } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { TaskResponse } from '../types/api.types';
import { fetchTaskStatus } from '../api/task';
import { useNetworkStatus } from './useNetworkStatus';
import { queryKeys } from '../config/queryKeys';
import { DEFAULT_POLLING_INTERVAL, TASK_STATUS } from '../config/apiEndpoints';

// In-memory cache to store task results and prevent polling completed tasks
const completedTasksCache = new Map<string, TaskResponse>();

interface UseTaskPollingOptions {
  /**
   * ID of the task to poll for status
   */
  taskId: string | null;
  
  /**
   * Whether to enable polling
   * @default true
   */
  enabled?: boolean;
  
  /**
   * Interval in milliseconds for polling
   * @default 2000
   */
  pollingInterval?: number;
  
  /**
   * Callback function when task completes successfully
   */
  onSuccess?: (data: TaskResponse) => void;
  
  /**
   * Callback function when task fails
   */
  onError?: (error: Error) => void;
  
  /**
   * Callback function when task is complete (successfully or with error)
   */
  onComplete?: (data: TaskResponse) => void;
}

/**
 * Hook to poll for task status until task completes or fails
 */
export function useTaskPolling({
  taskId,
  enabled = true,
  pollingInterval = DEFAULT_POLLING_INTERVAL,
  onSuccess,
  onError,
  onComplete
}: UseTaskPollingOptions) {
  const queryClient = useQueryClient();
  const [isTaskCompleted, setIsTaskCompleted] = useState(false);
  const networkStatus = useNetworkStatus({ notifyOnStatusChange: false });
  
  // Check if the task is already in the completed tasks cache
  const cachedTask = useMemo(() => {
    if (!taskId) return null;
    return completedTasksCache.get(taskId) || null;
  }, [taskId]);
  
  // If we have a cached completed task, use it instead of polling
  // Also check network status - don't poll when offline
  const shouldPoll = Boolean(enabled && taskId && !cachedTask && !isTaskCompleted && networkStatus.isOnline);
  
  // Query for the task status
  const query = useQuery<TaskResponse, Error>({
    queryKey: queryKeys.tasks.detail(taskId),
    queryFn: () => {
      if (!taskId) {
        return Promise.reject(new Error('No task ID provided'));
      }
      return fetchTaskStatus(taskId);
    },
    enabled: shouldPoll,
    staleTime: 0,
    retry: 3,
    refetchOnReconnect: true, // Refetch when the connection is restored
  });
  
  // Set up polling with setInterval
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    
    if (shouldPoll) {
      // Initial fetch
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(taskId) });
      
      // Set up polling interval
      intervalId = setInterval(() => {
        if (!isTaskCompleted) {
          queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(taskId) });
        } else if (intervalId) {
          clearInterval(intervalId);
        }
      }, pollingInterval);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [taskId, shouldPoll, pollingInterval, queryClient, isTaskCompleted]);
  
  // Use the cached data if available
  const data = cachedTask || query.data;
  const isPending = !cachedTask && query.isPending;
  const error = query.error;
  
  // Handle task completion
  useEffect(() => {
    if (!taskId || !data) return;
    
    const isComplete = [
      TASK_STATUS.COMPLETED,
      TASK_STATUS.FAILED,
      TASK_STATUS.CANCELED
    ].includes(data.status);
    
    if (isComplete && !isTaskCompleted) {
      console.log(`[TaskPolling] Task ${taskId} completed with status: ${data.status}`);
      setIsTaskCompleted(true);
      
      // Cache the completed task
      if (!completedTasksCache.has(taskId)) {
        completedTasksCache.set(taskId, data);
      }
      
      // Call the appropriate callbacks
      if (data.status === TASK_STATUS.COMPLETED && onSuccess) {
        onSuccess(data);
      }
      
      if (data.status === TASK_STATUS.FAILED && onError) {
        onError(new Error(data.error_message || 'Task failed'));
      }
      
      if (onComplete) {
        onComplete(data);
      }
    }
  }, [taskId, data, isTaskCompleted, onSuccess, onError, onComplete]);
  
  // Clean up the query when the component unmounts
  useEffect(() => {
    return () => {
      if (taskId) {
        queryClient.cancelQueries({ queryKey: queryKeys.tasks.detail(taskId) });
      }
    };
  }, [taskId, queryClient]);
  
  // Return the current state of the task
  return {
    isLoading: isPending,
    error,
    data,
    // Adapter properties for TaskContext
    isPending: data?.status === TASK_STATUS.PENDING,
    isProcessing: data?.status === TASK_STATUS.PROCESSING,
    isCompleted: data?.status === TASK_STATUS.COMPLETED,
    isFailed: data?.status === TASK_STATUS.FAILED,
    refresh: () => {
      if (taskId) {
        return queryClient.refetchQueries({ queryKey: queryKeys.tasks.detail(taskId) });
      }
    }
  };
}