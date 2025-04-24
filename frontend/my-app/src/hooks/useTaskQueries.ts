import {
  useQuery,
  useMutation,
  UseMutationResult,
  UseQueryResult,
} from "@tanstack/react-query";
import { TaskResponse } from "../types/api.types";
import { apiClient } from "../services/apiClient";
import { API_ENDPOINTS } from "../config/apiEndpoints";
import { queryKeys } from "../config/queryKeys";
import { useErrorHandling } from "./useErrorHandling";
import { createQueryErrorHandler } from "../utils/errorUtils";

/**
 * Fetches the status of a task from the API
 * @param taskId The ID of the task to fetch
 * @returns The task response object
 */
async function fetchTaskStatus(taskId: string): Promise<TaskResponse> {
  if (!taskId) {
    throw new Error("No task ID provided for status check");
  }

  console.log(`[API] Fetching status for task ${taskId}`);
  const response = await apiClient.get<TaskResponse>(
    API_ENDPOINTS.TASK_STATUS_BY_ID(taskId),
  );

  // Normalize the response by ensuring the id field is set properly
  if (response.data.task_id && !response.data.id) {
    response.data.id = response.data.task_id;
  }

  console.log(
    `[API] Received status for task ${taskId}: ${response.data.status}`,
  );
  return response.data;
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
    enabled?: boolean;
    refetchInterval?: number | false;
    onSuccess?: (data: TaskResponse) => void;
  } = {},
): UseQueryResult<TaskResponse, Error> {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler);

  return useQuery<TaskResponse, Error>({
    queryKey: queryKeys.tasks.detail(taskId),
    queryFn: () => {
      if (!taskId) {
        throw new Error("No task ID provided");
      }
      return fetchTaskStatus(taskId);
    },
    enabled: !!taskId && options.enabled !== false,
    refetchInterval: options.refetchInterval,
    onSuccess: options.onSuccess,
    onError: onQueryError,
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
        throw new Error("No task ID provided for cancellation");
      }

      console.log(`[API] Cancelling task ${taskId}`);
      const response = await apiClient.post<TaskResponse>(
        API_ENDPOINTS.TASK_CANCEL(taskId),
      );
      return response.data;
    },
    onError: onQueryError,
  });
}
