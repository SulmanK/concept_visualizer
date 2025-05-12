# Task API

The Task API module provides functions for interacting with task-related endpoints in the backend. Tasks represent long-running operations like concept generation or refinement that are processed asynchronously by the backend.

## Overview

The Task API allows clients to:

- Retrieve task status
- Cancel ongoing tasks

> ⚠️ **Note**: The direct API functions in `api/task.ts` are now deprecated and new code should use the React Query hooks in `hooks/useTaskQueries.ts` instead.

## Types

```tsx
/**
 * Task status type
 */
export type TaskStatus = "pending" | "processing" | "completed" | "failed";

/**
 * Task response model
 */
export interface TaskResponse {
  id: string;
  task_id?: string;
  status: TaskStatus;
  type: "generate_concept" | "refine_concept";
  result_id?: string;
  error_message?: string;
  created_at: string;
  updated_at: string;
}
```

## API Functions

### Fetch Task Status

```tsx
/**
 * @deprecated Use useTaskStatusQuery from src/hooks/useTaskQueries.ts instead
 * Fetches the status of a task from the API
 * @param taskId The ID of the task to fetch
 * @returns The task response object
 */
export async function fetchTaskStatus(taskId: string): Promise<TaskResponse> {
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
```

### Cancel Task

```tsx
/**
 * @deprecated Use useTaskCancelMutation from src/hooks/useTaskQueries.ts instead
 * Cancels a running task
 * @param taskId The ID of the task to cancel
 * @returns The updated task response
 */
export async function cancelTask(taskId: string): Promise<TaskResponse> {
  if (!taskId) {
    throw new Error("No task ID provided for cancellation");
  }

  console.log(`[API] Cancelling task ${taskId}`);
  const response = await apiClient.post<TaskResponse>(
    API_ENDPOINTS.TASK_CANCEL(taskId),
    {},
  );
  return response.data;
}
```

## React Query Hooks

For new code, use the React Query hooks in `hooks/useTaskQueries.ts` instead of the direct API functions.

### useTaskStatusQuery

```tsx
/**
 * Hook to fetch and subscribe to task status updates
 *
 * @param taskId The ID of the task to fetch
 * @param options Additional React Query options
 * @returns Query result with task status data
 */
export function useTaskStatusQuery(
  taskId: string | undefined,
  options: UseTaskStatusOptions = {},
): UseQueryResult<TaskResponse, Error> {
  // Query implementation...
}
```

### useTaskCancelMutation

```tsx
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
  // Mutation implementation...
}
```

## Usage Examples

### Using Task Hooks with React Query

```tsx
import {
  useTaskStatusQuery,
  useTaskCancelMutation,
} from "hooks/useTaskQueries";

function TaskMonitor({ taskId }) {
  // Subscribe to task status updates
  const {
    data: task,
    isLoading,
    error,
  } = useTaskStatusQuery(taskId, {
    // Poll every 2 seconds while in pending or processing state
    refetchInterval: (data) =>
      data?.status === "pending" || data?.status === "processing"
        ? 2000
        : false,
  });

  // Set up cancellation mutation
  const { mutate: cancelTask, isPending: isCancelling } =
    useTaskCancelMutation();

  // Handle cancel click
  const handleCancel = () => {
    if (taskId) {
      cancelTask(taskId);
    }
  };

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;
  if (!task) return <div>No task found</div>;

  return (
    <div>
      <h2>Task Status: {task.status}</h2>
      <p>Type: {task.type}</p>
      <p>Created: {new Date(task.created_at).toLocaleString()}</p>
      {task.error_message && <p>Error: {task.error_message}</p>}

      {(task.status === "pending" || task.status === "processing") && (
        <button onClick={handleCancel} disabled={isCancelling}>
          {isCancelling ? "Cancelling..." : "Cancel Task"}
        </button>
      )}

      {task.status === "completed" && task.result_id && (
        <div>
          <p>Result ID: {task.result_id}</p>
          {/* Display completed task result */}
        </div>
      )}
    </div>
  );
}
```

## API Endpoints

Task-related API endpoints are defined in `config/apiEndpoints.ts`:

```tsx
export const API_ENDPOINTS = {
  // Task endpoints
  TASK_STATUS_BY_ID: (taskId: string) => `/tasks/${taskId}`,
  TASK_CANCEL: (taskId: string) => `/tasks/${taskId}/cancel`,
  // ... other endpoints
};
```

## Related

- [useTask](../hooks/useTask.md) - Task context and hooks
- [useTaskQueries](../hooks/useTaskQueries.md) - React Query hooks for tasks
- [useConceptMutations](../hooks/useConceptMutations.md) - Mutation hooks that initiate tasks
