import React, { useEffect } from 'react';
import { render, screen, waitFor, act, renderHook } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { TASK_STATUS } from '../../config/apiEndpoints';

// Sample task responses for tests
const mockPendingTask = {
  id: 'task-123',
  task_id: 'task-123',
  status: TASK_STATUS.PENDING,
  created_at: new Date().toISOString(),
  updated_at: new Date().toISOString(),
  result_id: null,
  type: 'generate_concept',
  is_cancelled: false,
};

const mockProcessingTask = {
  ...mockPendingTask,
  status: TASK_STATUS.PROCESSING,
};

const mockCompletedTask = {
  ...mockPendingTask,
  status: TASK_STATUS.COMPLETED,
  result_id: 'result-456',
};

const mockFailedTask = {
  ...mockPendingTask,
  status: TASK_STATUS.FAILED,
  error_message: 'Something went wrong',
};

// Mock variables to control the test behavior
let mockTaskData = null;
let mockSubscriptionError = null;
let mockSubscriptionStatus = null;

// Mock useTaskSubscription
vi.mock('../../hooks/useTaskSubscription', () => ({
  useTaskSubscription: (taskId) => ({
    taskData: taskId ? mockTaskData : null,
    error: mockSubscriptionError,
    status: mockSubscriptionStatus
  })
}));

// Mock useTaskQueries hook to avoid making actual API calls
vi.mock('../../hooks/useTaskQueries', () => ({
  useTaskStatusQuery: vi.fn().mockReturnValue({
    data: null,
    isLoading: false,
    isError: false,
    error: null,
    refetch: vi.fn()
  }),
  useTaskCancelMutation: vi.fn().mockReturnValue({
    mutate: vi.fn(),
    isLoading: false,
    isError: false,
    error: null
  })
}));

// Import after mocks are set up
import { 
  TaskProvider,
  useTaskContext,
  useActiveTaskId,
  useTaskInitiating,
  useOnTaskCleared
} from '../TaskContext';

// Component that consumes the context for testing
const TestTaskConsumer = () => {
  const { 
    activeTaskId,
    activeTaskData,
    setActiveTask,
    clearActiveTask,
    hasActiveTask,
    isTaskPending,
    isTaskProcessing,
    isTaskCompleted,
    isTaskFailed,
    isTaskInitiating,
    setIsTaskInitiating,
    latestResultId,
    refreshTaskStatus
  } = useTaskContext();
  
  return (
    <div>
      <div data-testid="active-task-id">{activeTaskId || 'none'}</div>
      <div data-testid="task-status">{activeTaskData?.status || 'no-status'}</div>
      <div data-testid="has-active-task">{String(hasActiveTask)}</div>
      <div data-testid="is-pending">{String(isTaskPending)}</div>
      <div data-testid="is-processing">{String(isTaskProcessing)}</div>
      <div data-testid="is-completed">{String(isTaskCompleted)}</div>
      <div data-testid="is-failed">{String(isTaskFailed)}</div>
      <div data-testid="is-initiating">{String(isTaskInitiating)}</div>
      <div data-testid="latest-result-id">{latestResultId || 'none'}</div>
      
      <button 
        data-testid="set-task"
        onClick={() => setActiveTask('task-123')}
      >
        Set Task
      </button>
      <button 
        data-testid="clear-task"
        onClick={() => clearActiveTask()}
      >
        Clear Task
      </button>
      <button 
        data-testid="set-initiating"
        onClick={() => setIsTaskInitiating(true)}
      >
        Set Initiating
      </button>
      <button 
        data-testid="refresh-task"
        onClick={() => refreshTaskStatus()}
      >
        Refresh Task
      </button>
    </div>
  );
};

// Component that tests the task cleared event
const TestTaskClearedListener = ({ onClearedCallback }) => {
  const { onTaskCleared } = useTaskContext();
  
  useEffect(() => {
    const unsubscribe = onTaskCleared(() => {
      onClearedCallback();
    });
    
    return unsubscribe;
  }, [onTaskCleared, onClearedCallback]);
  
  return null;
};

// Create wrapper function for the tests
const createWrapper = (queryClient: QueryClient) => {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <TaskProvider>
          {children}
        </TaskProvider>
      </QueryClientProvider>
    );
  };
};

describe('TaskContext', () => {
  let queryClient: QueryClient;
  
  beforeEach(() => {
    // Reset mock variables
    mockTaskData = null;
    mockSubscriptionError = null;
    mockSubscriptionStatus = null;
    
    // Reset all mocks
    vi.clearAllMocks();
    
    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    });
  });
  
  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });
  
  describe('TaskProvider initial state', () => {
    it('should initialize with empty state', () => {
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Check initial state
      expect(screen.getByTestId('active-task-id').textContent).toBe('none');
      expect(screen.getByTestId('task-status').textContent).toBe('no-status');
      expect(screen.getByTestId('has-active-task').textContent).toBe('false');
      expect(screen.getByTestId('is-pending').textContent).toBe('false');
      expect(screen.getByTestId('is-processing').textContent).toBe('false');
      expect(screen.getByTestId('is-completed').textContent).toBe('false');
      expect(screen.getByTestId('is-failed').textContent).toBe('false');
      expect(screen.getByTestId('is-initiating').textContent).toBe('false');
      expect(screen.getByTestId('latest-result-id').textContent).toBe('none');
    });
  });
  
  describe('TaskProvider actions', () => {
    it('should update activeTaskId when setActiveTask is called', async () => {
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Initial state check
      expect(screen.getByTestId('active-task-id').textContent).toBe('none');
      
      // Click set task button
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Wait for state update
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('task-123');
      });
    });
    
    it('should clear activeTaskId when clearActiveTask is called', async () => {
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // First set a task
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Wait for state update
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('task-123');
      });
      
      // Then clear it
      act(() => {
        screen.getByTestId('clear-task').click();
      });
      
      // Wait for state to be cleared
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('none');
      });
    });
    
    it('should update isTaskInitiating when setIsTaskInitiating is called', async () => {
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Initial state check
      expect(screen.getByTestId('is-initiating').textContent).toBe('false');
      
      // Click set initiating button
      act(() => {
        screen.getByTestId('set-initiating').click();
      });
      
      // Wait for state update
      await waitFor(() => {
        expect(screen.getByTestId('is-initiating').textContent).toBe('true');
      });
    });
    
    it('should invalidate queries when refreshTaskStatus is called', async () => {
      // Set up a spy on queryClient.invalidateQueries
      const invalidateQueriesSpy = vi.spyOn(queryClient, 'invalidateQueries');
      
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // First set a task
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Wait for state update
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('task-123');
      });
      
      // Then refresh it
      act(() => {
        screen.getByTestId('refresh-task').click();
      });
      
      // Wait for the invalidateQueries to be called
      await waitFor(() => {
        expect(invalidateQueriesSpy).toHaveBeenCalledWith({ 
          queryKey: ['tasks', 'detail', 'task-123'] 
        });
      });
    });
  });
  
  describe('Task subscription updates', () => {
    it('should update state when subscription data changes', async () => {
      // Set up initial pending task
      mockTaskData = mockPendingTask;
      
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Set a task to trigger subscription
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Wait for pending state
      await waitFor(() => {
        expect(screen.getByTestId('task-status').textContent).toBe(TASK_STATUS.PENDING);
      });
      
      expect(screen.getByTestId('is-pending').textContent).toBe('true');
      expect(screen.getByTestId('has-active-task').textContent).toBe('true');
      
      // Update mock data to processing
      act(() => {
        mockTaskData = mockProcessingTask;
      });
      
      // Rerender to pick up changes
      await waitFor(() => {
        expect(screen.getByTestId('task-status').textContent).toBe(TASK_STATUS.PROCESSING);
      });
      
      expect(screen.getByTestId('is-processing').textContent).toBe('true');
      expect(screen.getByTestId('has-active-task').textContent).toBe('true');
      
      // Update mock data to completed
      act(() => {
        mockTaskData = mockCompletedTask;
      });
      
      // Rerender to pick up changes
      await waitFor(() => {
        expect(screen.getByTestId('task-status').textContent).toBe(TASK_STATUS.COMPLETED);
      });
      
      expect(screen.getByTestId('is-completed').textContent).toBe('true');
      expect(screen.getByTestId('has-active-task').textContent).toBe('false');
      expect(screen.getByTestId('latest-result-id').textContent).toBe('result-456');
    });
    
    it('should handle failed tasks', async () => {
      // Set up initial failed task
      mockTaskData = mockFailedTask;
      
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Set a task to trigger subscription
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Wait for failed state
      await waitFor(() => {
        expect(screen.getByTestId('task-status').textContent).toBe(TASK_STATUS.FAILED);
      });
      
      expect(screen.getByTestId('is-failed').textContent).toBe('true');
      expect(screen.getByTestId('has-active-task').textContent).toBe('false');
    });
  });
  
  describe('Task cleared events', () => {
    it('should notify listeners when task is cleared', async () => {
      // Create a mock callback
      const mockCallback = vi.fn();
      
      render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
            <TestTaskClearedListener onClearedCallback={mockCallback} />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // First set a task
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Wait for state update
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('task-123');
      });
      
      // Then clear it
      act(() => {
        screen.getByTestId('clear-task').click();
      });
      
      // Wait for callback to be called
      await waitFor(() => {
        expect(mockCallback).toHaveBeenCalledTimes(1);
      });
    });
  });
  
  describe('Context selectors', () => {
    it('useActiveTaskId should return the active task ID', async () => {
      const { result } = renderHook(() => useActiveTaskId(), { wrapper: createWrapper(queryClient) });
      
      expect(result.current).toBeNull();
      
      // Update the task ID using a component in the provider tree
      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Set a task
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      // Rerender the hook to pick up the new value
      rerender();
      
      // The hook should see the updated value
      await waitFor(() => {
        expect(result.current).toBe('task-123');
      });
    });
    
    it('useTaskInitiating should return the initiating state', async () => {
      const { result } = renderHook(() => useTaskInitiating(), { wrapper: createWrapper(queryClient) });
      
      expect(result.current).toBe(false);
      
      // Update the initiating state using a component in the provider tree
      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Set initiating to true
      act(() => {
        screen.getByTestId('set-initiating').click();
      });
      
      // Rerender the hook to pick up the new value
      rerender();
      
      // The hook should see the updated value
      await waitFor(() => {
        expect(result.current).toBe(true);
      });
    });
    
    it('useOnTaskCleared should return the onTaskCleared function', async () => {
      const mockCallback = vi.fn();
      
      const { result } = renderHook(() => useOnTaskCleared(), { wrapper: createWrapper(queryClient) });
      
      // Subscribe to task cleared events
      let unsubscribe;
      act(() => {
        unsubscribe = result.current(mockCallback);
      });
      
      // Clear a task (we need to first set one)
      const { rerender } = render(
        <QueryClientProvider client={queryClient}>
          <TaskProvider>
            <TestTaskConsumer />
          </TaskProvider>
        </QueryClientProvider>
      );
      
      // Set and then clear a task
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('task-123');
      });
      
      act(() => {
        screen.getByTestId('clear-task').click();
      });
      
      // The callback should have been called
      await waitFor(() => {
        expect(mockCallback).toHaveBeenCalledTimes(1);
      });
      
      // Now unsubscribe
      act(() => {
        unsubscribe();
      });
      
      // Reset the mock to check it's not called again
      mockCallback.mockReset();
      
      // Set and clear again
      act(() => {
        screen.getByTestId('set-task').click();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('active-task-id').textContent).toBe('task-123');
      });
      
      act(() => {
        screen.getByTestId('clear-task').click();
      });
      
      // The callback should not have been called this time
      expect(mockCallback).not.toHaveBeenCalled();
    });
  });
  
  describe('Context errors', () => {
    it('should throw an error when used outside provider', () => {
      // Suppress console errors during this test
      const originalConsoleError = console.error;
      console.error = vi.fn();
      
      expect(() => {
        render(<TestTaskConsumer />);
      }).toThrow('useTaskContext must be used within a TaskProvider');
      
      // Restore console.error
      console.error = originalConsoleError;
    });
  });
}); 