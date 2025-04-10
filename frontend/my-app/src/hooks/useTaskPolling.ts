import { useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { TaskResponse } from '../types/api.types';
import { useEffect, useRef } from 'react';

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
}

/**
 * Hook for polling task status
 */
export function useTaskPolling(taskId: string | null, options: UseTaskPollingOptions = {}) {
  const queryClient = useQueryClient();
  const {
    pollingInterval = DEFAULT_POLLING_INTERVAL,
    enabled = true,
    onSuccess,
    onError,
  } = options;

  // Keep track of the last status to detect changes
  const lastStatusRef = useRef<string | null>(null);

  const query = useQuery<TaskResponse>({
    queryKey: ['tasks', taskId],
    queryFn: async () => {
      if (!taskId) throw new Error('No task ID provided');
      const response = await apiClient.get<TaskResponse>(`/tasks/${taskId}`);
      return response.data;
    },
    enabled: !!taskId && enabled,
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
      if (taskId) {
        queryClient.removeQueries({ queryKey: ['tasks', taskId] });
      }
    };
  }, [taskId, queryClient]);

  return {
    ...query,
    // Helper getters
    isPending: query.data?.status === 'pending',
    isProcessing: query.data?.status === 'processing',
    isCompleted: query.data?.status === 'completed',
    isFailed: query.data?.status === 'failed',
  };
} 