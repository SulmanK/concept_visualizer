import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useTaskSubscription } from '../useTaskSubscription';
import { TASK_STATUS } from '../../config/apiEndpoints';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

// Mock dependencies
vi.mock('../../services/supabaseClient', () => {
  // Create mock channel object with fluent API
  const mockChannel = {
    on: vi.fn().mockImplementation(function() { return this; }),
    subscribe: vi.fn().mockImplementation((callback) => {
      // Store the callback so we can call it in tests
      mockSubscribeCallback = callback;
      return 'SUBSCRIBED';
    }),
  };
  
  return {
    supabase: {
      channel: vi.fn().mockReturnValue(mockChannel),
      removeChannel: vi.fn(),
    },
  };
});

// Mock task status query
vi.mock('../useTaskQueries', () => ({
  useTaskStatusQuery: vi.fn().mockImplementation(() => ({
    data: mockInitialTaskData,
    isError: mockIsError,
    error: mockError,
  })),
}));

// Mock variables to control the test behavior
let mockInitialTaskData = null;
let mockIsError = false;
let mockError = null;
let mockSubscribeCallback = null;

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

describe('useTaskSubscription', () => {
  let queryClient;

  beforeEach(() => {
    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    });

    // Reset the mocks
    vi.resetAllMocks();
    
    // Reset test variables
    mockInitialTaskData = null;
    mockIsError = false;
    mockError = null;
    mockSubscribeCallback = null;
  });

  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  it('should return null for taskData when taskId is null', async () => {
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result } = renderHook(() => useTaskSubscription(null), { wrapper });

    expect(result.current.taskData).toBeNull();
    expect(result.current.status).toBeNull();
    expect(result.current.error).toBeNull();
  });

  it('should use initial data from the query', async () => {
    // Set up mock initial data
    mockInitialTaskData = mockPendingTask;
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result } = renderHook(() => useTaskSubscription('task-123'), { wrapper });
    
    // Wait for the useEffect to run
    await waitFor(() => {
      expect(result.current.taskData).toEqual(mockPendingTask);
    });
    
    // Should have set up a subscription
    const { supabase } = require('../../services/supabaseClient');
    expect(supabase.channel).toHaveBeenCalledWith('task-updates-task-123');
  });
  
  it('should handle subscription events', async () => {
    // Set up mock initial data
    mockInitialTaskData = mockPendingTask;
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result } = renderHook(() => useTaskSubscription('task-123'), { wrapper });
    
    // Wait for the useEffect to run
    await waitFor(() => {
      expect(result.current.taskData).toBeTruthy();
    });
    
    // Get the postgres_changes handler
    const { supabase } = require('../../services/supabaseClient');
    const onArgs = supabase.channel().on.mock.calls;
    
    // Find the postgres_changes handler
    const postgresHandler = onArgs.find(call => 
      call[0] === 'postgres_changes' && 
      call[1].table === 'tasks'
    )[2];
    
    // Simulate a task update event
    act(() => {
      postgresHandler({
        new: mockProcessingTask,
        old: mockPendingTask,
      });
    });
    
    // Should have updated the task data
    expect(result.current.taskData).toEqual(mockProcessingTask);
    
    // Simulate another update to completed
    act(() => {
      postgresHandler({
        new: mockCompletedTask,
        old: mockProcessingTask,
      });
    });
    
    // Should have updated to completed
    expect(result.current.taskData).toEqual(mockCompletedTask);
  });
  
  it('should clean up subscription when unmounted', async () => {
    // Set up mock initial data
    mockInitialTaskData = mockPendingTask;
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result, unmount } = renderHook(() => useTaskSubscription('task-123'), { wrapper });
    
    // Wait for the useEffect to run
    await waitFor(() => {
      expect(result.current.taskData).toBeTruthy();
    });
    
    // Unmount the component
    unmount();
    
    // Should have called removeChannel
    const { supabase } = require('../../services/supabaseClient');
    expect(supabase.removeChannel).toHaveBeenCalled();
  });
  
  it('should handle subscription status changes', async () => {
    // Set up mock initial data
    mockInitialTaskData = mockPendingTask;
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result } = renderHook(() => useTaskSubscription('task-123'), { wrapper });
    
    // Wait for the useEffect to run
    await waitFor(() => {
      expect(result.current.taskData).toBeTruthy();
    });
    
    // Simulate the subscribe callback being called
    act(() => {
      mockSubscribeCallback('SUBSCRIBED');
    });
    
    // Should have updated the status
    expect(result.current.status).toBe('SUBSCRIBED');
    
    // Get the system event handler for connection_state_change
    const { supabase } = require('../../services/supabaseClient');
    const onArgs = supabase.channel().on.mock.calls;
    
    // Find the connection_state_change handler
    const connectionHandler = onArgs.find(call => 
      call[0] === 'system' && 
      call[1].event === 'connection_state_change'
    )[2];
    
    // Simulate a connection state change
    act(() => {
      connectionHandler({ event: 'CONNECTED' });
    });
    
    // Should have updated the status
    expect(result.current.status).toBe('CONNECTED');
  });
  
  it('should handle subscription errors', async () => {
    // Set up mock initial data
    mockInitialTaskData = mockPendingTask;
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result } = renderHook(() => useTaskSubscription('task-123'), { wrapper });
    
    // Wait for the useEffect to run
    await waitFor(() => {
      expect(result.current.taskData).toBeTruthy();
    });
    
    // Get the system event handler for error
    const { supabase } = require('../../services/supabaseClient');
    const onArgs = supabase.channel().on.mock.calls;
    
    // Find the error handler
    const errorHandler = onArgs.find(call => 
      call[0] === 'system' && 
      call[1].event === 'error'
    )[2];
    
    // Simulate an error
    act(() => {
      errorHandler(new Error('Subscription error'));
    });
    
    // Should have set the error and status
    expect(result.current.error).toEqual(new Error('Subscription error'));
    expect(result.current.status).toBe('error');
  });
  
  it('should handle query errors', async () => {
    // Set up mock error
    mockIsError = true;
    mockError = new Error('Failed to fetch task');
    
    const wrapper = ({ children }: { children: React.ReactNode }) => (
      <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
    );
    
    const { result } = renderHook(() => useTaskSubscription('task-123'), { wrapper });
    
    // Wait for the useEffect to run
    await waitFor(() => {
      expect(result.current.error).toBeTruthy();
    });
    
    // Should have set the error from the query
    expect(result.current.error).toEqual(new Error('Failed to fetch task'));
  });
}); 