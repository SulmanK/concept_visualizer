import { useEffect, useMemo, useState } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { TaskResponse } from '../types/api.types';
import { useNetworkStatus } from './useNetworkStatus';
import { queryKeys } from '../config/queryKeys';
import { DEFAULT_POLLING_INTERVAL, TASK_STATUS } from '../config/apiEndpoints';
import { useTaskStatusQuery } from './useTaskQueries';

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
  
  // Track document visibility for debugging
  const [isDocumentVisible, setIsDocumentVisible] = useState(() => 
    typeof document !== 'undefined' ? document.visibilityState === 'visible' : true
  );
  
  // Monitor visibility state changes
  useEffect(() => {
    if (typeof document === 'undefined') return;
    
    const handleVisibilityChange = () => {
      const isVisible = document.visibilityState === 'visible';
      setIsDocumentVisible(isVisible);
      
      console.log(`[TaskPolling] Document visibility changed to ${isVisible ? 'visible' : 'hidden'}`);
      
      // Force refetch when document becomes visible again
      if (isVisible && taskId && !isTaskCompleted && enabled) {
        console.log(`[TaskPolling] Document visible, forcing task status refetch for ${taskId}`);
        queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(taskId) });
      }
    };
    
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange);
    };
  }, [taskId, isTaskCompleted, enabled, queryClient]);
  
  // Check if the task is already in the completed tasks cache
  const cachedTask = useMemo(() => {
    if (!taskId) return null;
    return completedTasksCache.get(taskId) || null;
  }, [taskId]);
  
  // Log state for debugging
  useEffect(() => {
    if (taskId) {
      console.log(`[TaskPolling] Poll state for task ${taskId}:`, {
        enabled,
        isTaskCompleted,
        hasCachedTask: !!cachedTask,
        isOnline: networkStatus.isOnline,
        isDocumentVisible,
        timestamp: new Date().toISOString()
      });
    }
  }, [taskId, enabled, isTaskCompleted, cachedTask, networkStatus.isOnline, isDocumentVisible]);
  
  // If we have a cached completed task, use it instead of polling
  // Also check network status - don't poll when offline
  const shouldPoll = Boolean(
    enabled && 
    taskId && 
    !cachedTask && 
    !isTaskCompleted && 
    networkStatus.isOnline && 
    isDocumentVisible
  );
  
  // Use our standardized query hook instead of direct implementation
  const query = useTaskStatusQuery(taskId, {
    enabled: shouldPoll,
    refetchInterval: shouldPoll ? pollingInterval : false,
    refetchIntervalInBackground: false, // Disable background polling to avoid browser throttling
    refetchOnWindowFocus: true, // Ensure we refetch when window gets focus
    onSuccess: (data) => {
      console.log(`[TaskPolling] Successfully fetched status for task ${taskId}: ${data.status}`);
    }
  });
  
  // Set up polling with setInterval - we can keep this for additional control
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    
    if (shouldPoll) {
      console.log(`[TaskPolling] Starting polling for task ${taskId} with interval ${pollingInterval}ms`);
      
      // Initial fetch
      queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(taskId) });
      
      // Set up polling interval for additional invalidation control
      intervalId = setInterval(() => {
        if (!isTaskCompleted && document.visibilityState === 'visible') {
          console.log(`[TaskPolling] Interval triggered for task ${taskId}`);
          queryClient.invalidateQueries({ queryKey: queryKeys.tasks.detail(taskId) });
        } else if (isTaskCompleted && intervalId) {
          console.log(`[TaskPolling] Task completed, clearing interval for ${taskId}`);
          clearInterval(intervalId);
        } else if (document.visibilityState !== 'visible') {
          console.log(`[TaskPolling] Document not visible, skipping interval for ${taskId}`);
        }
      }, pollingInterval);
    }
    
    return () => {
      if (intervalId) {
        console.log(`[TaskPolling] Cleaning up interval for task ${taskId}`);
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
        console.log(`[TaskPolling] Manual refresh triggered for task ${taskId}`);
        return queryClient.refetchQueries({ queryKey: queryKeys.tasks.detail(taskId) });
      }
    }
  };
}