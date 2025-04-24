# TaskContext

The `TaskContext` provides global state management for background processing tasks in the application. It enables tracking, monitoring, and responding to long-running operations across all components.

## Overview

Many operations in this application (like concept generation or image processing) run as background tasks on the server. The TaskContext:

- Tracks the currently active task
- Provides real-time status updates using WebSockets
- Exposes task state (pending, processing, completed, failed)
- Manages result IDs from completed tasks
- Provides a task event system for cross-component communication

## Context Interface

The context exposes the following properties and methods:

```typescript
interface TaskContextType {
  // Current active task ID being tracked
  activeTaskId: string | null;

  // Latest task data from the server
  activeTaskData: TaskResponse | null;

  // Set a new task to track
  setActiveTask: (taskId: string | null) => void;

  // Clear the current task
  clearActiveTask: () => void;

  // Whether there is an active task in progress
  hasActiveTask: boolean;

  // Whether the task is in pending state
  isTaskPending: boolean;

  // Whether the task is in processing state
  isTaskProcessing: boolean;

  // Whether the task has completed
  isTaskCompleted: boolean;

  // Whether the task has failed
  isTaskFailed: boolean;

  // Whether a task is being initiated (before task ID arrives)
  isTaskInitiating: boolean;

  // Set the initiating state
  setIsTaskInitiating: (isInitiating: boolean) => void;

  // Force a refresh of the task status
  refreshTaskStatus: () => void;

  // The result ID from the most recently completed task
  latestResultId: string | null;

  // Set the result ID manually
  setLatestResultId: (resultId: string | null) => void;

  // Subscribe to task cleared events
  onTaskCleared: (listener: () => void) => () => void;
}
```

## Usage

The context provides specialized selector hooks for optimal performance:

```tsx
import {
  useTaskContext,
  useHasActiveTask,
  useIsTaskProcessing,
  useIsTaskPending,
  useIsTaskCompleted,
  useIsTaskFailed,
  useLatestResultId,
  useTaskInitiating,
  useActiveTaskId,
  useOnTaskCleared,
} from "../contexts/TaskContext";

// Component that starts a task
function ConceptGenerator() {
  const setActiveTask = useContextSelector(
    TaskContext,
    (state) => state?.setActiveTask,
  );
  const setIsTaskInitiating = useContextSelector(
    TaskContext,
    (state) => state?.setIsTaskInitiating,
  );

  const handleGenerate = async () => {
    // Mark that we're initiating a task before we have the ID
    setIsTaskInitiating(true);

    try {
      // Make API call to start a task
      const response = await apiClient.post("/concepts/generate", formData);

      // Once task is created, track it
      setActiveTask(response.data.task_id);
    } catch (error) {
      // If task creation fails, reset initiating state
      setIsTaskInitiating(false);
      console.error("Failed to start task", error);
    }
  };

  return <button onClick={handleGenerate}>Generate Concept</button>;
}

// Status indicator that shows task progress
function TaskStatusIndicator() {
  // Selectively subscribe to just the task states we need
  const isProcessing = useIsTaskProcessing();
  const isPending = useIsTaskPending();
  const isCompleted = useIsTaskCompleted();
  const isFailed = useIsTaskFailed();
  const taskId = useActiveTaskId();

  if (!taskId) return null;

  if (isPending) return <span>Task queued...</span>;
  if (isProcessing) return <ProgressBar />;
  if (isCompleted) return <span>Task completed!</span>;
  if (isFailed) return <span>Task failed</span>;

  return null;
}

// Component that uses task results
function ResultDisplay() {
  const resultId = useLatestResultId();
  const onTaskCleared = useOnTaskCleared();

  // Subscribe to task cleared events
  useEffect(() => {
    // Return cleanup function from event subscription
    return onTaskCleared(() => {
      console.log("Task was cleared, time to update UI");
    });
  }, [onTaskCleared]);

  if (!resultId) return <p>No results yet</p>;

  return <ConceptDisplayCard conceptId={resultId} />;
}
```

## Implementation Details

### Real-time Updates

The `TaskContext` uses Supabase Realtime for WebSocket-based task updates:

- Establishes a subscription to the task when a task ID is set
- Listens for PostgreSQL changes to the task record
- Updates the local state and React Query cache when changes occur
- Manages cleanup of subscriptions when tasks change

### Task Lifecycle Management

Tasks go through several states, which the context tracks:

1. **Initiating** (`isTaskInitiating`): When a task is being created but we don't have a task ID yet
2. **Pending** (`isTaskPending`): When a task is waiting to be processed
3. **Processing** (`isTaskProcessing`): When a task is actively running
4. **Completed** (`isTaskCompleted`): When a task has successfully finished
5. **Failed** (`isTaskFailed`): When a task has encountered an error

### Auto-reset Protection

To prevent interface lockups, the context includes auto-reset logic:

- Automatically resets the initiating state if it's been active too long (7 seconds)
- Ensures clean state transitions between tasks

### Event System

The context includes a basic event system for task-related events:

```typescript
// Subscribe to task cleared events
const unsubscribe = onTaskCleared(() => {
  // Handle task cleared event
});

// Later, clean up the subscription
unsubscribe();
```

## Exposed Hooks

| Hook                    | Returns                                | Description                     |
| ----------------------- | -------------------------------------- | ------------------------------- |
| `useTaskContext()`      | `TaskContextType`                      | Complete task context           |
| `useHasActiveTask()`    | `boolean`                              | Whether there's an active task  |
| `useIsTaskProcessing()` | `boolean`                              | Whether a task is processing    |
| `useIsTaskPending()`    | `boolean`                              | Whether a task is pending       |
| `useIsTaskCompleted()`  | `boolean`                              | Whether a task has completed    |
| `useIsTaskFailed()`     | `boolean`                              | Whether a task has failed       |
| `useLatestResultId()`   | `string \| null`                       | Latest result ID                |
| `useTaskInitiating()`   | `boolean`                              | Whether a task is initiating    |
| `useActiveTaskId()`     | `string \| null`                       | Current active task ID          |
| `useOnTaskCleared()`    | `(listener: () => void) => () => void` | Task cleared event subscription |

## Task Response Structure

The `TaskResponse` object contains:

```typescript
interface TaskResponse {
  id: string; // Task ID
  status: string; // Task status (pending, processing, completed, failed)
  progress?: number; // Optional progress percentage (0-100)
  message?: string; // Optional status message
  result_id?: string; // Optional result ID for completed tasks
  result?: any; // Optional result data
  error?: string; // Optional error message
  created_at: string; // Creation timestamp
  updated_at: string; // Last update timestamp
}
```

## Related

- [useTaskSubscription](../hooks/useTaskSubscription.md) - Hook used for real-time task updates
- [useTaskQueries](../hooks/useTaskQueries.md) - Hooks for task API interactions
- [TaskStatusBar](../components/TaskStatusBar.md) - UI component for displaying task status
