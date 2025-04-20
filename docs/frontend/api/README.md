# API

This directory contains modules that handle direct communication with the backend API endpoints. These modules provide a clean interface for components and hooks to interact with the backend services.

## Purpose

The API modules abstract away the details of HTTP communication, allowing components and hooks to focus on business logic and UI rendering rather than network communication details. This separation of concerns makes the codebase more maintainable and testable.

## Structure

Each API module typically corresponds to a specific backend service or resource:

- `task.ts`: Handles communication with task-related endpoints
- Additional API modules for other backend resources (concepts, users, etc.)

## Implementation Pattern

API modules typically follow this pattern:

1. Import the base API client from services
2. Define TypeScript interfaces for request and response types
3. Implement functions for each API endpoint
4. Handle errors in a consistent manner

Example:

```tsx
import { apiClient } from 'services/apiClient';
import type { Task, TaskStatus } from 'types';

// Get a specific task by ID
export const getTask = async (taskId: string): Promise<Task> => {
  return apiClient.get<Task>(`/api/tasks/${taskId}`);
};

// Get all tasks for current user
export const getTasks = async (): Promise<Task[]> => {
  return apiClient.get<Task[]>('/api/tasks');
};

// Create a new task
export const createTask = async (task: Omit<Task, 'id'>): Promise<Task> => {
  return apiClient.post<Task>('/api/tasks', task);
};

// Update a task's status
export const updateTaskStatus = async (taskId: string, status: TaskStatus): Promise<Task> => {
  return apiClient.patch<Task>(`/api/tasks/${taskId}/status`, { status });
};

// Delete a task
export const deleteTask = async (taskId: string): Promise<void> => {
  return apiClient.delete(`/api/tasks/${taskId}`);
};
```

## Usage

API modules are typically used by hooks that handle data fetching and mutations:

```tsx
// Example usage in a hook
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getTasks, createTask, updateTaskStatus, deleteTask } from 'api/task';

export const useTasksQuery = () => {
  return useQuery(['tasks'], getTasks);
};

export const useTaskMutations = () => {
  const queryClient = useQueryClient();
  
  const createMutation = useMutation(createTask, {
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks']);
    },
  });
  
  const updateStatusMutation = useMutation(
    ({ taskId, status }) => updateTaskStatus(taskId, status),
    {
      onSuccess: () => {
        queryClient.invalidateQueries(['tasks']);
      },
    }
  );
  
  const deleteMutation = useMutation(deleteTask, {
    onSuccess: () => {
      queryClient.invalidateQueries(['tasks']);
    },
  });
  
  return {
    createTask: createMutation.mutate,
    updateTaskStatus: updateStatusMutation.mutate,
    deleteTask: deleteMutation.mutate,
  };
};
```

## Key Considerations

- API modules should handle errors consistently
- Request and response types should be clearly defined
- API modules should not contain business logic
- Authentication and authorization should be handled at the API client level
- Rate limiting concerns should be handled at the API client level 