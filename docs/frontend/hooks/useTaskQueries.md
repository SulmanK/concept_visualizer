# useTaskQueries

The `useTaskQueries` module provides hooks for interacting with background tasks in the application. These hooks allow components to fetch task statuses and cancel long-running tasks when needed.

## Overview

In this application, many operations (like concept generation or image processing) run as background tasks on the server. This module provides React Query hooks to track and manage those tasks throughout their lifecycle.

## Hooks

### useTaskStatusQuery

Fetches and tracks the status of a specific task. This hook is particularly useful for displaying progress indicators and handling the completion of background operations.

#### Usage

```tsx
import { useTaskStatusQuery } from "../hooks/useTaskQueries";

function TaskTracker({ taskId }) {
  const {
    data: task,
    isLoading,
    error,
  } = useTaskStatusQuery(taskId, {
    // Poll every second while task is running
    refetchInterval: (data) => {
      return data?.status === "completed" || data?.status === "failed"
        ? false
        : 1000;
    },
    onSuccess: (data) => {
      if (data.status === "completed") {
        // Handle task completion
        console.log("Task completed:", data.result);
      }
    },
  });

  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h3>Task: {task?.name}</h3>
      <p>Status: {task?.status}</p>
      {task?.progress && <ProgressBar value={task.progress} />}
      {task?.message && <p>{task.message}</p>}
    </div>
  );
}
```

#### Parameters

| Parameter                 | Type                                                           | Required | Description                      |
| ------------------------- | -------------------------------------------------------------- | -------- | -------------------------------- |
| `taskId`                  | `string \| null \| undefined`                                  | Yes      | The ID of the task to fetch      |
| `options`                 | Object                                                         | No       | Additional query options         |
| `options.enabled`         | `boolean`                                                      | No       | Whether the query should execute |
| `options.refetchInterval` | `number \| false \| ((data: TaskResponse) => number \| false)` | No       | How often to refetch (in ms)     |
| `options.onSuccess`       | `(data: TaskResponse) => void`                                 | No       | Callback when fetch succeeds     |

#### Return Value

Returns a React Query `UseQueryResult` with the task status data:

```typescript
{
  data: TaskResponse | undefined; // Task data if available
  isLoading: boolean; // True when the query is loading
  isError: boolean; // True if the query encountered an error
  error: Error | null; // Error object if query failed
  // Additional React Query properties
}
```

### useTaskCancelMutation

Provides a mutation for canceling a task that is in progress.

#### Usage

```tsx
import { useTaskCancelMutation } from "../hooks/useTaskQueries";

function TaskController({ taskId }) {
  const cancelTask = useTaskCancelMutation();

  const handleCancelClick = () => {
    cancelTask.mutate(taskId, {
      onSuccess: () => {
        console.log("Task was canceled successfully");
        // Update UI or notify user
      },
    });
  };

  return (
    <button onClick={handleCancelClick} disabled={cancelTask.isLoading}>
      {cancelTask.isLoading ? "Canceling..." : "Cancel Task"}
    </button>
  );
}
```

#### Return Value

Returns a React Query `UseMutationResult` with methods for canceling tasks:

```typescript
{
  mutate: (taskId: string) => void;
  mutateAsync: (taskId: string) => Promise<TaskResponse>;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isSuccess: boolean;
  // Additional React Query mutation properties
}
```

## Task Response Structure

The `TaskResponse` object returned by these hooks has the following structure:

```typescript
interface TaskResponse {
  id: string; // Task ID
  task_id?: string; // Alternative task ID field (normalized to 'id')
  status: "pending" | "running" | "completed" | "failed" | "cancelled";
  name?: string; // Human-readable task name
  progress?: number; // Progress percentage (0-100)
  message?: string; // Status message
  result?: any; // Task result data when completed
  error?: string; // Error message if failed
  created_at: string; // ISO timestamp of task creation
  updated_at: string; // ISO timestamp of last update
}
```

## Implementation Details

- Tasks are fetched from the `/tasks/{taskId}` endpoint
- Task cancellation uses the `/tasks/{taskId}/cancel` endpoint
- The module normalizes inconsistent API responses (e.g., unifying `task_id` and `id` fields)
- Comprehensive error handling is provided via the application's error handling system
- Logging is included for debugging task operations

## Related

- `TaskContext` - Provides application-wide task tracking
- `TaskStatusBar` - UI component that displays task status
- `useTaskSubscription` - Companion hook for real-time task updates via WebSockets
