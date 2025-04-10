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

  const query = useQuery<TaskResponse>({
    queryKey: ['tasks', effectiveTaskId],
    queryFn: async () => {
      if (!effectiveTaskId) throw new Error('No task ID provided');
      const response = await apiClient.get<TaskResponse>(`/tasks/${effectiveTaskId}`);
      return response.data;
    },
    enabled: !!effectiveTaskId && enabled,
    refetchInterval: (data) => {
      // Stop polling if task reaches a terminal state
      if (data?.status === 'completed' || data?.status === 'failed') {
        return false;
      }
      return pollingInterval;
    },
    // Don't retry on error for task polling
    retry: false,
    // Keep data fresh
    staleTime: 0,
  });

  // Handle status changes
  useEffect(() => {
    const currentStatus = query.data?.status;
    if (currentStatus && currentStatus !== lastStatusRef.current) {
      lastStatusRef.current = currentStatus;

      if (currentStatus === 'completed' && onSuccess && query.data) {
        onSuccess(query.data);
      } else if (currentStatus === 'failed' && onError && query.data) {
        onError(new Error(query.data.error_message || 'Task failed'), query.data);
      }
    }
  }, [query.data?.status, onSuccess, onError]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (effectiveTaskId) {
        queryClient.removeQueries({ queryKey: ['tasks', effectiveTaskId] });
        
        // Optionally, clear the global task state if it matches our task ID
        if (useGlobalTaskId && globalTaskId === effectiveTaskId) {
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
  };
} 