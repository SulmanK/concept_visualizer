# Task API

The Task API module provides functions for interacting with task-related endpoints in the backend. Tasks represent long-running operations like concept generation or refinement that are processed asynchronously by the backend.

## Overview

The Task API allows clients to:

- Retrieve task information
- Subscribe to task updates
- Check task status
- Cancel ongoing tasks

## Types

```tsx
// Task status enumeration
export enum TaskStatus {
  PENDING = "pending",
  PROCESSING = "processing",
  COMPLETED = "completed",
  FAILED = "failed",
  CANCELLED = "cancelled",
}

// Task object interface
export interface Task {
  id: string;
  status: TaskStatus;
  type: string;
  progress: number;
  result?: Record<string, any>;
  error?: string;
  createdAt: string;
  updatedAt: string;
  estimatedCompletionTime?: string;
}

// Error response
export interface ErrorResponse {
  message: string;
  code: string;
}
```

## API Functions

### Get Task

```tsx
/**
 * Retrieves a task by its ID
 * @param taskId - The unique identifier of the task
 * @returns The task object
 * @throws ApiError if the request fails
 */
export const getTask = async (taskId: string): Promise<Task> => {
  try {
    return await apiClient.get<Task>(`/api/tasks/${taskId}`);
  } catch (error) {
    throw handleApiError(error, "Failed to retrieve task");
  }
};
```

### Get Task Status

```tsx
/**
 * Retrieves the current status of a task
 * @param taskId - The unique identifier of the task
 * @returns The task status
 * @throws ApiError if the request fails
 */
export const getTaskStatus = async (taskId: string): Promise<TaskStatus> => {
  try {
    const task = await apiClient.get<Task>(`/api/tasks/${taskId}/status`);
    return task.status;
  } catch (error) {
    throw handleApiError(error, "Failed to retrieve task status");
  }
};
```

### Cancel Task

```tsx
/**
 * Cancels an ongoing task
 * @param taskId - The unique identifier of the task to cancel
 * @returns The updated task with cancelled status
 * @throws ApiError if the request fails
 */
export const cancelTask = async (taskId: string): Promise<Task> => {
  try {
    return await apiClient.post<Task>(`/api/tasks/${taskId}/cancel`);
  } catch (error) {
    throw handleApiError(error, "Failed to cancel task");
  }
};
```

### Get Task Result

```tsx
/**
 * Retrieves the result of a completed task
 * @param taskId - The unique identifier of the task
 * @returns The task result data
 * @throws ApiError if the task is not completed or the request fails
 */
export const getTaskResult = async (
  taskId: string,
): Promise<Record<string, any>> => {
  try {
    const task = await apiClient.get<Task>(`/api/tasks/${taskId}/result`);
    if (task.status !== TaskStatus.COMPLETED) {
      throw new Error("Task is not completed");
    }
    return task.result || {};
  } catch (error) {
    throw handleApiError(error, "Failed to retrieve task result");
  }
};
```

## Usage Examples

### Retrieving and Monitoring a Task

```tsx
import { getTask, getTaskStatus, TaskStatus } from "api/task";

// Fetch a task
const fetchAndMonitorTask = async (taskId: string) => {
  try {
    // Get initial task data
    const task = await getTask(taskId);
    console.log("Task retrieved:", task);

    // Set up polling if task is not complete
    if (
      task.status === TaskStatus.PENDING ||
      task.status === TaskStatus.PROCESSING
    ) {
      const interval = setInterval(async () => {
        const status = await getTaskStatus(taskId);
        console.log("Task status:", status);

        if (
          status === TaskStatus.COMPLETED ||
          status === TaskStatus.FAILED ||
          status === TaskStatus.CANCELLED
        ) {
          clearInterval(interval);

          // Get final task data if completed
          if (status === TaskStatus.COMPLETED) {
            const updatedTask = await getTask(taskId);
            console.log("Completed task:", updatedTask);
          }
        }
      }, 2000); // Poll every 2 seconds
    }
  } catch (error) {
    console.error("Error monitoring task:", error);
  }
};
```

### Cancelling a Task

```tsx
import { cancelTask } from "api/task";

const handleCancelTask = async (taskId: string) => {
  try {
    const cancelledTask = await cancelTask(taskId);
    console.log("Task cancelled:", cancelledTask);
    return cancelledTask;
  } catch (error) {
    console.error("Failed to cancel task:", error);
    throw error;
  }
};
```

## Error Handling

The Task API handles errors consistently by:

1. Catching any errors from the API client
2. Transforming them into standardized ApiError objects with meaningful messages
3. Preserving the original error information where possible

```tsx
const handleApiError = (error: any, defaultMessage: string): never => {
  if (error instanceof ApiError) {
    throw error;
  }

  if (error.response) {
    const errorData = error.response.data as ErrorResponse;
    throw new ApiError(
      errorData.message || defaultMessage,
      error.response.status,
      errorData.code,
    );
  }

  throw new ApiError(defaultMessage, 500);
};
```
