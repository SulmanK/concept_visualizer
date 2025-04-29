import React, {
  useState,
  useEffect,
  useCallback,
  useRef,
  ReactNode,
} from "react";
import { createContext } from "use-context-selector";
import { TaskResponse } from "../types/api.types";
import { useTaskSubscription } from "../hooks/useTaskSubscription";
import { useQueryClient } from "@tanstack/react-query";
import { TASK_STATUS } from "../config/apiEndpoints";

// Event bus for task-related events
type TaskEventListener = () => void;

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

  /**
   * Subscribe to task cleared events
   */
  onTaskCleared: (listener: TaskEventListener) => () => void;
}

// Export the context so it can be imported by hooks
export const TaskContext = createContext<TaskContextType | undefined>(
  undefined,
);

interface TaskProviderProps {
  children: ReactNode;
}

/**
 * Provider component for managing the global task state.
 */
export const TaskProvider: React.FC<TaskProviderProps> = ({ children }) => {
  const [activeTaskId, setActiveTaskId] = useState<string | null>(null);
  const [isTaskInitiating, setIsTaskInitiating] = useState<boolean>(false);
  // Track when initiating state started
  const initiatingStartTimeRef = useRef<number | null>(null);
  // Track the latest result ID from completed tasks
  const [latestResultId, setLatestResultId] = useState<string | null>(null);
  // Task event listeners
  const taskClearedListenersRef = useRef<Set<TaskEventListener>>(new Set());
  const queryClient = useQueryClient();

  // Update initiatingStartTime when isTaskInitiating changes
  useEffect(() => {
    if (isTaskInitiating && initiatingStartTimeRef.current === null) {
      console.log("[TaskContext] Setting initiating start time");
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
        if (duration > 7000) {
          // 7 seconds is definitely too long for initiating without a task ID
          console.log(
            `[TaskContext] Auto-resetting stale initiating state after ${duration}ms`,
          );
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
  const setActiveTask = useCallback(
    (taskId: string | null) => {
      console.log(`[TaskContext] Setting active task to: ${taskId}`);

      // If we're setting a new task (and there was a previous one), ensure clean state
      if (taskId && taskId !== activeTaskId) {
        console.log(`[TaskContext] New task ID detected, ensuring clean state`);
        // No need to call clearActiveTask here as it would trigger listeners
        // Just make sure all internal state is reset properly
      }

      setActiveTaskId(taskId);
      if (taskId) {
        setIsTaskInitiating(false); // Reset initiating state when task ID is set
      }
    },
    [activeTaskId],
  );

  // Function to handle task success
  const handleTaskSuccess = useCallback(
    (taskData: TaskResponse) => {
      // When the task completes successfully, store result ID if it exists
      if (taskData.status === TASK_STATUS.COMPLETED) {
        console.log(`[TaskContext] Task ${taskData.id} completed successfully`);

        // Store the result_id if it exists
        if (taskData.result_id) {
          console.log(
            `[TaskContext] Setting latest result ID: ${taskData.result_id}`,
          );
          setLatestResultId(taskData.result_id);

          // Invalidate concept queries to ensure fresh data is displayed
          // This ensures that other components will see the updated data
          queryClient.invalidateQueries({
            queryKey: ["concepts", "detail", taskData.result_id],
            exact: false,
          });

          // Also invalidate recent concepts to ensure any lists get refreshed
          queryClient.invalidateQueries({
            queryKey: ["concepts", "recent"],
          });
        } else {
          console.log(
            `[TaskContext] Task completed but no result_id was found`,
          );
        }

        // DO NOT clear the active task here anymore. Let the status bar handle it.
      }
    },
    [setLatestResultId, queryClient],
  );

  // Function to handle task error
  const handleTaskError = useCallback((error: Error) => {
    console.error(`[TaskContext] Task failed:`, error);
    // DO NOT automatically clear the active task here.
    // The TaskStatusBar will show the error and auto-dismiss or allow manual dismissal.
  }, []);

  // Use the new useTaskSubscription hook to get real-time updates
  const { taskData: activeTaskData, error: subscriptionError } =
    useTaskSubscription(activeTaskId);

  // Set up derived state based on the task data
  const isTaskPending = activeTaskData?.status === TASK_STATUS.PENDING;
  const isTaskProcessing = activeTaskData?.status === TASK_STATUS.PROCESSING;
  const isTaskCompleted = activeTaskData?.status === TASK_STATUS.COMPLETED;
  const isTaskFailed =
    activeTaskData?.status === TASK_STATUS.FAILED ||
    activeTaskData?.status === TASK_STATUS.CANCELED;
  const hasActiveTask =
    Boolean(activeTaskId) && (isTaskPending || isTaskProcessing);

  // Process task data changes to call appropriate handlers
  useEffect(() => {
    if (!activeTaskData) return;

    if (activeTaskData.status === TASK_STATUS.COMPLETED) {
      handleTaskSuccess(activeTaskData);
    } else if (activeTaskData.status === TASK_STATUS.FAILED) {
      handleTaskError(new Error(activeTaskData.error_message || "Task failed"));
    }
  }, [activeTaskData, handleTaskSuccess, handleTaskError]);

  // Watch for result_id in task data even if onSuccess hasn't been called yet
  useEffect(() => {
    if (
      activeTaskData?.status === TASK_STATUS.COMPLETED &&
      activeTaskData.result_id
    ) {
      console.log(
        `[TaskContext] Detected result_id in task data: ${activeTaskData.result_id}`,
      );
      setLatestResultId(activeTaskData.result_id);
    }
  }, [activeTaskData]);

  // Log changes to task status for debugging
  useEffect(() => {
    if (activeTaskData) {
      console.log(
        `[TaskContext] Task status update - ID: ${activeTaskData.id}, Status: ${
          activeTaskData.status
        }, Result ID: ${activeTaskData.result_id || "none"}`,
      );
      console.log(
        `[TaskContext] Status flags - isPending: ${isTaskPending}, isProcessing: ${isTaskProcessing}, isCompleted: ${isTaskCompleted}, isFailed: ${isTaskFailed}`,
      );
    }
  }, [
    activeTaskData,
    isTaskPending,
    isTaskProcessing,
    isTaskCompleted,
    isTaskFailed,
  ]);

  // Handle subscription errors
  useEffect(() => {
    if (subscriptionError) {
      console.error("[TaskContext] Subscription error:", subscriptionError);
      // We don't need to implement fallback logic here as the useTaskSubscription
      // hook already manages errors properly and won't report successful subscriptions
      // as errors anymore
    }
  }, [subscriptionError]);

  const clearActiveTask = useCallback(() => {
    console.log(`[TaskContext] Manually clearing active task: ${activeTaskId}`);
    setActiveTaskId(null);
    setIsTaskInitiating(false);
    // Note: we don't clear the latestResultId here as it should persist

    // Notify listeners that task was cleared
    taskClearedListenersRef.current.forEach((listener) => {
      try {
        listener();
      } catch (e) {
        console.error("[TaskContext] Error in task cleared listener:", e);
      }
    });
  }, [activeTaskId]);

  // Function to register a task cleared event listener
  const onTaskCleared = useCallback((listener: TaskEventListener) => {
    console.log("[TaskContext] Adding task cleared listener");
    taskClearedListenersRef.current.add(listener);

    // Return an unsubscribe function
    return () => {
      console.log("[TaskContext] Removing task cleared listener");
      taskClearedListenersRef.current.delete(listener);
    };
  }, []);

  // Function to manually refresh task status (e.g. after the app comes back from background)
  const refreshTaskStatus = useCallback(() => {
    if (activeTaskId) {
      console.log(
        `[TaskContext] Manually refreshing task status for ${activeTaskId}`,
      );
      queryClient.invalidateQueries({
        queryKey: ["tasks", "detail", activeTaskId],
      });
    }
  }, [activeTaskId, queryClient]);

  // Create the context value object
  const contextValue: TaskContextType = {
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
    refreshTaskStatus,
    latestResultId,
    setLatestResultId,
    onTaskCleared,
  };

  return (
    <TaskContext.Provider value={contextValue}>{children}</TaskContext.Provider>
  );
};

// Hooks have been moved to src/hooks/useTask.ts
