import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';
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
}

const TaskContext = createContext<TaskContextType | undefined>(undefined);

interface TaskProviderProps {
  children: ReactNode;
  pollingInterval?: number;
}

/**
 * Provider component for managing the global task state.
 */
export const TaskProvider: React.FC<TaskProviderProps> = ({ 
  children, 
  pollingInterval = 2000 
}) => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  
  // Create a callback for setting the task ID that we can pass to useTaskPolling
  const setActiveTask = useCallback((taskId: string | null) => {
    setActiveTaskId(taskId);
  }, []);
  
  // Pass taskContextData directly to useTaskPolling to avoid circular dependency
  const { 
    data: activeTaskData,
    isPending,
    isProcessing,
    isCompleted,
    isFailed
  } = useTaskPolling(activeTaskId, { 
    pollingInterval,
    // Provide the context data directly to avoid circular reference
    taskContextData: {
      activeTaskId,
      setActiveTask
    },
    onSuccess: (taskData) => {
      // When the task completes successfully, we might keep the data
      // but we could automatically clear the active task after a delay
      if (taskData.status === 'completed') {
        const timer = setTimeout(() => {
          setActiveTaskId(null);
        }, 5000); // Auto-clear completed tasks after 5 seconds
        
        return () => clearTimeout(timer);
      }
    },
    onError: () => {
      // When the task fails, we might want to keep it in the state
      // so the user can see the error, but auto-clear after a while
      const timer = setTimeout(() => {
        setActiveTaskId(null);
      }, 8000); // Auto-clear failed tasks after 8 seconds
      
      return () => clearTimeout(timer);
    }
  });
  
  const clearActiveTask = useCallback(() => {
    setActiveTaskId(null);
  }, []);
  
  // Derive whether there's currently an active task
  const hasActiveTask = Boolean(activeTaskId && (isPending || isProcessing));
  
  // Provide the task context
  const value: TaskContextType = {
    activeTaskId,
    activeTaskData,
    setActiveTask,
    clearActiveTask,
    hasActiveTask,
    isTaskPending: isPending,
    isTaskProcessing: isProcessing,
    isTaskCompleted: isCompleted,
    isTaskFailed: isFailed
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