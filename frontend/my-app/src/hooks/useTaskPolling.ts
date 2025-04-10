import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { TaskResponse } from '../types/api.types';
import { useEffect, useRef } from 'react';
// Moving this import into a conditional block to avoid circular dependency
// import { useTaskContext } from '../contexts/TaskContext';

const DEFAULT_POLLING_INTERVAL = 2000; // 2 seconds

interface UseTaskPollingOptions {
  /**
   * Polling interval in milliseconds
   * @default 2000
   */
  pollingInterval?: number;
  /**
   * Whether to enable polling
   * @default true
   */
  enabled?: boolean;
  /**
   * Callback when task completes successfully
   */
  onSuccess?: (taskResponse: TaskResponse) => void;
  /**
   * Callback when task fails
   */
  onError?: (error: Error, taskResponse: TaskResponse) => void;
  /**
   * Whether to use the global task context for the task ID
   * When true, it will use the activeTaskId from the global context if no taskId is provided
   * @default false
   */
  useGlobalTaskId?: boolean;
  /**
   * Optional task context data to use instead of the useTaskContext hook
   * This is used to avoid circular dependencies when the hook is used in the TaskProvider
   */
  taskContextData?: {
    activeTaskId: string | null;
    setActiveTask: (taskId: string | null) => void;
  };
}

/**
 * Hook for polling task status
 */
export function useTaskPolling(taskId: string | null, options: UseTaskPollingOptions = {}) {
  const queryClient = useQueryClient();
  
  // To break circular dependency when used in TaskProvider
  let globalTaskId = null;
  let setActiveTask = (id: string | null) => {};
  
  // If taskContextData is provided, use it directly instead of calling useTaskContext
  if (options.taskContextData) {
    globalTaskId = options.taskContextData.activeTaskId;
    setActiveTask = options.taskContextData.setActiveTask;
  } else {
    // Only import and use the context if we're not using provided data
    // This prevents circular dependencies when used in the TaskProvider
    try {
      // Dynamic import to avoid circular dependency at module level
      const { useTaskContext } = require('../contexts/TaskContext');
      const taskContext = useTaskContext();
      globalTaskId = taskContext.activeTaskId;
      setActiveTask = taskContext.setActiveTask;
    } catch (error) {
      console.warn('useTaskContext not available, using fallback empty values');
      // Keep the default empty values when context is not available
    }
  }
  
  const {
    pollingInterval = DEFAULT_POLLING_INTERVAL,
    enabled = true,
    onSuccess,
    onError,
    useGlobalTaskId = false
  } = options;

  // Use global task ID if requested and no specific task ID provided
  const effectiveTaskId = (useGlobalTaskId && !taskId) ? globalTaskId : taskId;

  // Keep track of the last status to detect changes
  const lastStatusRef = useRef<string | null>(null);
  // Keep track of polling rounds for debugging
  const pollCountRef = useRef(0);

  const query = useQuery<TaskResponse>({
    queryKey: ['tasks', effectiveTaskId],
    queryFn: async () => {
      if (!effectiveTaskId) throw new Error('No task ID provided');
      
      try {
        pollCountRef.current += 1;
        console.log(`[useTaskPolling] Polling task ${effectiveTaskId} (round ${pollCountRef.current})`);
        
        const response = await apiClient.get<TaskResponse>(`/tasks/${effectiveTaskId}`);
        console.log(`[useTaskPolling] Received response for task ${effectiveTaskId}:`, response.data);
        
        // Normalize the response by ensuring the id field is set properly
        if (response.data.task_id && !response.data.id) {
          response.data.id = response.data.task_id;
        }
        
        return response.data;
      } catch (error) {
        console.error(`[useTaskPolling] Error polling task ${effectiveTaskId}:`, error);
        throw error;
      }
    },
    enabled: !!effectiveTaskId && enabled,
    refetchInterval: (data) => {
      // Log the current status
      console.log(`[useTaskPolling] Current status for task ${effectiveTaskId}:`, data?.status);
      
      // Stop polling if task reaches a terminal state
      if (data?.status === 'completed' || data?.status === 'failed') {
        console.log(`[useTaskPolling] Task ${effectiveTaskId} reached terminal state (${data.status}), stopping poll`);
        return false;
      }
      
      console.log(`[useTaskPolling] Continuing to poll task ${effectiveTaskId} every ${pollingInterval}ms`);
      return pollingInterval;
    },
    // Decrease stale time to ensure we're getting fresh data
    staleTime: 0,
    // Force refetch on window focus to catch updates
    refetchOnWindowFocus: true,
    // Retry a few times on error
    retry: 3,
    retryDelay: 1000,
  });

  // Handle status changes
  useEffect(() => {
    const currentStatus = query.data?.status;
    console.log(`[useTaskPolling] Status check: last=${lastStatusRef.current}, current=${currentStatus}`);
    
    if (currentStatus && currentStatus !== lastStatusRef.current) {
      console.log(`[useTaskPolling] Status changed from ${lastStatusRef.current} to ${currentStatus} for task ${effectiveTaskId}`);
      lastStatusRef.current = currentStatus;

      if (currentStatus === 'completed' && onSuccess && query.data) {
        console.log(`[useTaskPolling] Calling onSuccess for completed task ${effectiveTaskId}`);
        onSuccess(query.data);
      } else if (currentStatus === 'failed' && onError && query.data) {
        console.log(`[useTaskPolling] Calling onError for failed task ${effectiveTaskId}`);
        onError(new Error(query.data.error_message || 'Task failed'), query.data);
      }
    }
  }, [query.data?.status, onSuccess, onError, effectiveTaskId, query.data]);

  // Force manual refetch when needed
  useEffect(() => {
    if (effectiveTaskId && enabled) {
      const interval = setInterval(() => {
        // Force a refetch every so often in case the refetchInterval approach isn't working
        queryClient.invalidateQueries({ queryKey: ['tasks', effectiveTaskId] });
        console.log(`[useTaskPolling] Forced refetch for task ${effectiveTaskId}`);
      }, pollingInterval * 2.5);  // Use longer interval for forced refetch
      
      return () => clearInterval(interval);
    }
  }, [effectiveTaskId, enabled, pollingInterval, queryClient]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (effectiveTaskId) {
        console.log(`[useTaskPolling] Cleaning up task polling for ${effectiveTaskId}`);
        queryClient.removeQueries({ queryKey: ['tasks', effectiveTaskId] });
        
        // Optionally, clear the global task state if it matches our task ID
        if (useGlobalTaskId && globalTaskId === effectiveTaskId) {
          console.log(`[useTaskPolling] Clearing global task state for ${effectiveTaskId}`);
          setActiveTask(null);
        }
      }
    };
  }, [effectiveTaskId, queryClient, useGlobalTaskId, globalTaskId, setActiveTask]);

  return {
    ...query,
    // Helper getters
    isPending: query.data?.status === 'pending',
    isProcessing: query.data?.status === 'processing',
    isCompleted: query.data?.status === 'completed',
    isFailed: query.data?.status === 'failed',
    // Provide method to force refresh
    forceRefresh: () => {
      console.log(`[useTaskPolling] Manually forcing refresh for task ${effectiveTaskId}`);
      return queryClient.invalidateQueries({ queryKey: ['tasks', effectiveTaskId] });
    }
  };
} 