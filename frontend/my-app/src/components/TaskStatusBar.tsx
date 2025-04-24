import React, { useEffect, useState, useRef, useCallback } from "react";
import { useTaskContext } from "../contexts/TaskContext";
import { LoadingIndicator } from "./ui/LoadingIndicator";
import { TASK_STATUS } from "../config/apiEndpoints"; // Import task statuses

// How long to show success/failure messages before auto-dismissing (in milliseconds)
const AUTO_DISMISS_DELAY = 30000; // 30 seconds

/**
 * Displays the current task status as a floating bar.
 * Updated to work with Supabase Realtime subscriptions.
 */
const TaskStatusBar: React.FC = () => {
  // Get task state from the global context
  const {
    activeTaskId,
    activeTaskData,
    refreshTaskStatus,
    clearActiveTask,
    isTaskInitiating,
    isTaskPending,
    isTaskProcessing,
  } = useTaskContext();

  // Local state to track manual dismissal *for the current task ID*
  const [isManuallyDismissed, setIsManuallyDismissed] = useState(false);
  // Store the task ID for which the dismissal applies
  const dismissedTaskIdRef = useRef<string | null>(null);
  // Ref for the auto-dismiss timer
  const dismissTimerRef = useRef<NodeJS.Timeout | null>(null);
  // Ref to track the previously shown task ID
  const prevTaskIdRef = useRef<string | null>(null);

  const status = activeTaskData?.status;
  const taskId = activeTaskData?.id || activeTaskData?.task_id || activeTaskId; // Use ID from data if available

  // Log state changes for debugging
  useEffect(() => {
    console.log(
      `[TaskStatusBar] State update - activeTaskId: ${activeTaskId}, status: ${status}, isInitiating: ${isTaskInitiating}`,
    );
    console.log(
      `[TaskStatusBar] Flags - isTaskPending: ${isTaskPending}, isTaskProcessing: ${isTaskProcessing}`,
    );
  }, [activeTaskId, status, isTaskInitiating, isTaskPending, isTaskProcessing]);

  // Refresh task status periodically when in pending state (as fallback)
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;

    // Set up a fallback polling mechanism in case Realtime subscription fails
    if ((isTaskPending || isTaskProcessing) && activeTaskId) {
      intervalId = setInterval(() => {
        console.log(
          `[TaskStatusBar] Fallback refresh for task ${activeTaskId}`,
        );
        refreshTaskStatus();
      }, 10000); // Every 10 seconds as fallback
    }

    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isTaskPending, isTaskProcessing, activeTaskId, refreshTaskStatus]);

  // --- Auto-Dismiss Logic ---
  useEffect(() => {
    // Clear existing timer whenever status or task ID changes
    if (dismissTimerRef.current) {
      clearTimeout(dismissTimerRef.current);
      dismissTimerRef.current = null;
    }

    // If the task is completed or failed, set a timer to dismiss it
    if (status === TASK_STATUS.COMPLETED || status === TASK_STATUS.FAILED) {
      console.log(
        `[TaskStatusBar] Setting auto-dismiss timer for task ${taskId} (status: ${status})`,
      );
      dismissTimerRef.current = setTimeout(() => {
        console.log(`[TaskStatusBar] Auto-dismissing task ${taskId}`);
        // Instead of local dismiss, clear the task from the global context
        // Only clear if it's still the same task shown
        if (activeTaskId === taskId) {
          clearActiveTask();
        }
      }, AUTO_DISMISS_DELAY);
    }

    // Cleanup function to clear timer on unmount or dependency change
    return () => {
      if (dismissTimerRef.current) {
        clearTimeout(dismissTimerRef.current);
        dismissTimerRef.current = null;
      }
    };
  }, [status, taskId, clearActiveTask, activeTaskId]); // Rerun when status or taskId changes

  // --- Manual Dismiss Logic ---
  const handleManualDismiss = useCallback(() => {
    console.log(`[TaskStatusBar] Manually dismissing task ${taskId}`);
    setIsManuallyDismissed(true);
    dismissedTaskIdRef.current = taskId; // Remember which task was dismissed

    // Clear any pending auto-dismiss timer
    if (dismissTimerRef.current) {
      clearTimeout(dismissTimerRef.current);
      dismissTimerRef.current = null;
    }

    // Clear the task globally immediately on manual dismiss
    clearActiveTask();
  }, [taskId, clearActiveTask]); // Dependencies include clearActiveTask

  // --- Reset Dismissal State for New Tasks ---
  useEffect(() => {
    // If the active Task ID changes (and is not null), reset the manual dismissal state
    if (
      taskId &&
      taskId !== dismissedTaskIdRef.current &&
      taskId !== prevTaskIdRef.current
    ) {
      console.log(
        `[TaskStatusBar] New task detected (${taskId}), resetting dismissal state.`,
      );
      setIsManuallyDismissed(false);
      dismissedTaskIdRef.current = null; // Clear the remembered dismissed ID
      prevTaskIdRef.current = taskId; // Remember this task ID
    }
  }, [taskId]); // Rerun only when taskId changes

  // --- Visibility Logic ---
  // Show if there's active task data OR task is initiating
  // AND (it's pending/processing OR it's completed/failed AND not manually dismissed for *this specific task*)
  const isVisible =
    (!!activeTaskData ||
      isTaskInitiating ||
      isTaskPending ||
      isTaskProcessing) &&
    (isTaskInitiating ||
      isTaskPending ||
      isTaskProcessing ||
      status === TASK_STATUS.PENDING ||
      status === TASK_STATUS.PROCESSING ||
      ((status === TASK_STATUS.COMPLETED || status === TASK_STATUS.FAILED) &&
        (!isManuallyDismissed || dismissedTaskIdRef.current !== taskId)));

  // --- Render Logic ---
  if (!isVisible) {
    // Log why it's not visible for debugging
    console.log(`[TaskStatusBar] Not visible. TaskData: ${!!activeTaskData}, Status: ${status},
      isInitiating: ${isTaskInitiating}, isPending: ${isTaskPending}, isProcessing: ${isTaskProcessing},
      Dismissed: ${isManuallyDismissed}, DismissedID: ${
        dismissedTaskIdRef.current
      }, CurrentID: ${taskId}`);
    return null;
  }

  let statusMessage = "Task status unknown";
  let statusColor = "bg-gray-100 border-gray-300";
  let statusIcon = null;

  // Handle initiating state (before we have a task status)
  if (isTaskInitiating) {
    statusMessage = "Preparing your request...";
    statusColor = "bg-yellow-100 border-yellow-300";
    statusIcon = <LoadingIndicator size="small" />;
  } else {
    switch (status) {
      case TASK_STATUS.PENDING:
        statusMessage = "Request queued...";
        statusColor = "bg-yellow-100 border-yellow-300";
        statusIcon = <LoadingIndicator size="small" />;
        break;
      case TASK_STATUS.PROCESSING:
        statusMessage = "Processing your request...";
        statusColor = "bg-blue-100 border-blue-300";
        statusIcon = <LoadingIndicator size="small" />;
        break;
      case TASK_STATUS.COMPLETED:
        statusMessage = "Task completed successfully!";
        statusColor = "bg-green-100 border-green-300";
        statusIcon = (
          <svg
            className="w-5 h-5 text-green-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M5 13l4 4L19 7"
            ></path>
          </svg>
        );
        break;
      case TASK_STATUS.FAILED:
        statusMessage = activeTaskData?.error_message || "Task failed";
        statusColor = "bg-red-100 border-red-300";
        statusIcon = (
          <svg
            className="w-5 h-5 text-red-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        );
        break;
      case TASK_STATUS.CANCELED:
        statusMessage = "Task was canceled";
        statusColor = "bg-gray-100 border-gray-300";
        statusIcon = (
          <svg
            className="w-5 h-5 text-gray-600"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth="2"
              d="M6 18L18 6M6 6l12 12"
            ></path>
          </svg>
        );
        break;
    }
  }

  console.log(
    `[TaskStatusBar] Rendering. Visible: ${isVisible}, Status: ${
      status || "initiating"
    }, Message: ${statusMessage}`,
  );

  return (
    <div
      className={`fixed top-6 right-6 min-w-[320px] z-50 p-3 rounded-lg shadow-2xl border-2 ${statusColor} transition-all duration-300 transform ${
        isVisible ? "translate-x-0 opacity-100" : "translate-x-full opacity-0"
      }`}
    >
      <div className="flex items-center">
        <div className="mr-3 flex-shrink-0">{statusIcon}</div>
        <div className="flex-grow">
          <p className="text-sm font-medium">{statusMessage}</p>
          {taskId && (
            <p className="text-xs opacity-60">
              Task ID: {taskId.substring(0, 8)}...
            </p>
          )}
        </div>
        <div className="flex ml-2">
          {/* When processing, add a manual refresh button */}
          {(isTaskPending || isTaskProcessing) && (
            <button
              onClick={refreshTaskStatus}
              className="text-gray-500 hover:text-gray-700 mr-2"
              aria-label="Refresh status"
              title="Refresh Status"
            >
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                ></path>
              </svg>
            </button>
          )}
          <button
            onClick={handleManualDismiss}
            className="text-gray-500 hover:text-gray-700"
            aria-label="Close status"
            title="Dismiss Status"
          >
            <svg
              className="w-4 h-4"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth="2"
                d="M6 18L18 6M6 6l12 12"
              ></path>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskStatusBar;
