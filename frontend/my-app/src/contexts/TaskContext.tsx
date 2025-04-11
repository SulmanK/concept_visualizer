import React, { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';
import { TaskResponse } from '../types/api.types';
import { useTaskPolling } from '../hooks/useTaskPolling';

interface TaskContextType {
  /**
   * The current active task ID
   */
  activeTaskId: string | null;
  
  /**
   * The latest task response data from polling
   */
  activeTaskData: TaskResponse | null;
  
  /**
   * Sets a new active task ID to be polled
   */
  setActiveTask: (taskId: string | null) => void;
  
  /**
   * Clears the current active task
   */
  clearActiveTask: () => void;
  
  /**
   * Whether there is an active task in progress (pending or processing)
   */
  hasActiveTask: boolean;
  
  /**
   * Whether the task is in pending state
   */
  isTaskPending: boolean;
  
  /**
   * Whether the task is in processing state
   */
  isTaskProcessing: boolean;
  
  /**
   * Whether the task has completed
   */
  isTaskCompleted: boolean;
  
  /**
   * Whether the task has failed
   */
  isTaskFailed: boolean;
  
  /**
   * Whether a task is being initiated (before the first API response)
   */
  isTaskInitiating: boolean;
  
  /**
   * Set the initiating state
   */
  setIsTaskInitiating: (isInitiating: boolean) => void;
  
  /**
   * Force a manual refresh of the task status
   */
  refreshTaskStatus: () => void;

  /**
   * The result ID from the most recently completed task
   */
  latestResultId: string | null;
  
  /**
   * Set the result ID manually (for cases where the result_id isn't coming from the task)
   */
  setLatestResultId: (resultId: string | null) => void;
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

interface TaskProviderProps {
  children: ReactNode;
  pollingInterval?: number;
}

interface TaskContextData {
  activeTaskId: string | null;
  setActiveTask: (taskId: string | null) => void;
}

/**
 * Provider component for managing the global task state.
 */
export const TaskProvider: React.FC<TaskProviderProps> = ({ 
  children, 
  pollingInterval = 2000 
}) => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [isTaskInitiating, setIsTaskInitiating] = useState<boolean>(false);
  // Track when initiating state started
  const initiatingStartTimeRef = useRef<number | null>(null);
  // Track the latest result ID from completed tasks
  const [latestResultId, setLatestResultId] = useState<string | null>(null);
  
  // Update initiatingStartTime when isTaskInitiating changes
  useEffect(() => {
    if (isTaskInitiating && initiatingStartTimeRef.current === null) {
      console.log('[TaskContext] Setting initiating start time');
      initiatingStartTimeRef.current = Date.now();
    } else if (!isTaskInitiating) {
      initiatingStartTimeRef.current = null;
    }
  }, [isTaskInitiating]);
  
  // Auto-reset initiating state if it's been active too long without a task ID
  useEffect(() => {
    let timeoutId: NodeJS.Timeout | null = null;
    
    if (isTaskInitiating && !activeTaskId && initiatingStartTimeRef.current) {
      timeoutId = setTimeout(() => {
        const duration = Date.now() - initiatingStartTimeRef.current!;
        if (duration > 7000) { // 7 seconds is definitely too long for initiating without a task ID
          console.log(`[TaskContext] Auto-resetting stale initiating state after ${duration}ms`);
          setIsTaskInitiating(false);
        }
      }, 7000);
    }
    
    return () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    };
  }, [isTaskInitiating, activeTaskId]);
  
  // Create a callback for setting the task ID that we can pass to useTaskPolling
  const setActiveTask = useCallback((taskId: string | null) => {
    console.log(`[TaskContext] Setting active task to: ${taskId}`);
    setActiveTaskId(taskId);
    if (taskId) {
      setIsTaskInitiating(false); // Reset initiating state when task ID is set
    }
  }, []);
  
  // Create task context data object to avoid circular dependency
  const taskContextData: TaskContextData = {
    activeTaskId,
    setActiveTask
  };
  
  // Function to handle task success
  const handleTaskSuccess = (taskData: TaskResponse) => {
    // When the task completes successfully, store result ID if it exists
    if (taskData.status === 'completed') {
      console.log(`[TaskContext] Task ${taskData.id} completed successfully`);
      
      // Store the result_id if it exists
      if (taskData.result_id) {
        console.log(`[TaskContext] Setting latest result ID: ${taskData.result_id}`);
        setLatestResultId(taskData.result_id);
      } else {
        console.log(`[TaskContext] Task completed but no result_id was found`);
      }
      
      // Note: We no longer auto-clear completed tasks
      // Let the TaskStatusBar handle the temporary display of completed status
    }
  };
  
  // Function to handle task error
  const handleTaskError = (error: Error) => {
    console.error(`[TaskContext] Task failed:`, error);
    // When the task fails, we might want to keep it in the state
    // so the user can see the error, but auto-clear after a while
    const timer = setTimeout(() => {
      console.log(`[TaskContext] Auto-clearing failed task after timeout`);
      setActiveTaskId(null);
    }, 8000); // Auto-clear failed tasks after 8 seconds
    
    return () => clearTimeout(timer);
  };
  
  // Pass taskContextData directly to useTaskPolling to avoid circular dependency
  const { 
    data: activeTaskData,
    isPending,
    isProcessing,
    isCompleted,
    isFailed,
    isLoading: isPollingLoading,
    refresh: refreshTaskStatus
  } = useTaskPolling({
    taskId: activeTaskId,
    pollingInterval,
    enabled: true,
    onSuccess: handleTaskSuccess,
    onError: handleTaskError
  });
  
  // Watch for result_id in task data even if onSuccess hasn't been called yet
  useEffect(() => {
    if (activeTaskData?.status === 'completed' && activeTaskData.result_id) {
      console.log(`[TaskContext] Detected result_id in task data: ${activeTaskData.result_id}`);
      setLatestResultId(activeTaskData.result_id);
    }
  }, [activeTaskData]);
  
  // Log changes to task status for debugging
  useEffect(() => {
    if (activeTaskData) {
      console.log(`[TaskContext] Task status update - ID: ${activeTaskData.id}, Status: ${activeTaskData.status}, Result ID: ${activeTaskData.result_id || 'none'}`);
      console.log(`[TaskContext] Status flags - isPending: ${isPending}, isProcessing: ${isProcessing}, isCompleted: ${isCompleted}, isFailed: ${isFailed}`);
    }
  }, [activeTaskData, isPending, isProcessing, isCompleted, isFailed]);
  
  const clearActiveTask = useCallback(() => {
    console.log(`[TaskContext] Manually clearing active task: ${activeTaskId}`);
    setActiveTaskId(null);
    setIsTaskInitiating(false);
    // Note: we don't clear the latestResultId here as it should persist
  }, [activeTaskId]);
  
  // Simplified hasActiveTask logic
  const hasActiveTask = Boolean(
    activeTaskId && (isPending || isProcessing)
  );
  
  // Provide the task context
  const value: TaskContextType = {
    activeTaskId,
    activeTaskData: activeTaskData || null,
    setActiveTask,
    clearActiveTask,
    hasActiveTask,
    isTaskPending: isPending || false,
    isTaskProcessing: isProcessing || false,
    isTaskCompleted: isCompleted || false,
    isTaskFailed: isFailed || false,
    isTaskInitiating,
    setIsTaskInitiating,
    refreshTaskStatus,
    latestResultId,
    setLatestResultId
  };
  
  return (
    <TaskContext.Provider value={value}>
      {children}
    </TaskContext.Provider>
  );
};

/**
 * Hook for accessing the task context.
 * Must be used within a TaskProvider component.
 */
export const useTaskContext = (): TaskContextType => {
  const context = useContext(TaskContext);
  
  if (context === undefined) {
    throw new Error('useTaskContext must be used within a TaskProvider');
  }
  
  return context;
};

export default TaskContext; 