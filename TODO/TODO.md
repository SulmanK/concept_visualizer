Okay, let's break down the issues with the `TaskStatusBar` and refactor it step-by-step to behave more like a standard production status indicator.

The core problems you identified are:
1.  **Stays Visible:** The "Completed" status doesn't disappear automatically after its timeout.
2.  **Stale Status:** When a new task starts, the "Completed" status from the *previous* task might still be showing.

The root cause likely lies in how the visibility and state (`shouldShowCompleted`, `isDismissed`) interact with the global task context flags (`isTaskCompleted`, `activeTaskId`) and potentially flawed timer management.

Here’s a refactoring strategy focusing on making the `TaskStatusBar` react directly to the *current* `activeTaskData` and manage its own display lifecycle more reliably.

**Refactoring Plan:**

1.  **Simplify State Management:** Rely primarily on `activeTaskData` from `TaskContext` to determine the display status. Remove the local `shouldShowCompleted` state.
2.  **Improve Visibility Logic:** The bar should be visible only when there's an active task (`pending` or `processing`) or when a task has *just* finished (`completed` or `failed`) for a short duration, and only if not manually dismissed *for that specific task completion/failure*.
3.  **Reliable Auto-Dismiss:** Implement a robust `useEffect`-based timer that triggers when the status changes to `completed` or `failed`, and automatically hides the bar after a set duration.
4.  **Reset on New Task:** Ensure the bar correctly resets its dismissed state and timers when a *new* `activeTaskId` is set in the context.

---

**Step 1: Refactor `TaskStatusBar.tsx`**

This is the main component to change. We'll simplify its state and logic.

```tsx
// frontend/my-app/src/components/TaskStatusBar.tsx
import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useTaskContext } from '../contexts/TaskContext';
import { LoadingIndicator } from './ui/LoadingIndicator';
import { TASK_STATUS } from '../config/apiEndpoints'; // Import task statuses

// How long to show success/failure messages before auto-dismissing (in milliseconds)
const AUTO_DISMISS_DELAY = 5000; // 5 seconds

/**
 * Displays the current task status as a floating bar.
 * Refactored for more reliable state management and auto-dismissal.
 */
const TaskStatusBar: React.FC = () => {
  // Get task state from the global context
  const {
    activeTaskId,
    activeTaskData,
    refreshTaskStatus,
    clearActiveTask, // Use clearActiveTask to dismiss permanently for a session
  } = useTaskContext();

  // Local state to track manual dismissal *for the current task ID*
  const [isManuallyDismissed, setIsManuallyDismissed] = useState(false);
  // Store the task ID for which the dismissal applies
  const dismissedTaskIdRef = useRef<string | null>(null);
  // Ref for the auto-dismiss timer
  const dismissTimerRef = useRef<NodeJS.Timeout | null>(null);

  const status = activeTaskData?.status;
  const taskId = activeTaskData?.id || activeTaskData?.task_id || activeTaskId; // Use ID from data if available

  // --- Auto-Dismiss Logic ---
  useEffect(() => {
    // Clear existing timer whenever status or task ID changes
    if (dismissTimerRef.current) {
      clearTimeout(dismissTimerRef.current);
      dismissTimerRef.current = null;
    }

    // If the task is completed or failed, set a timer to dismiss it
    if (status === TASK_STATUS.COMPLETED || status === TASK_STATUS.FAILED) {
      console.log(`[TaskStatusBar] Setting auto-dismiss timer for task ${taskId} (status: ${status})`);
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
    // Optionally, clear the task globally immediately on manual dismiss
    // clearActiveTask();
  }, [taskId]); // Dependency is taskId

  // --- Reset Dismissal State for New Tasks ---
  useEffect(() => {
    // If the active Task ID changes (and is not null), reset the manual dismissal state
    if (taskId && taskId !== dismissedTaskIdRef.current) {
      console.log(`[TaskStatusBar] New task detected (${taskId}), resetting dismissal state.`);
      setIsManuallyDismissed(false);
      dismissedTaskIdRef.current = null; // Clear the remembered dismissed ID
    }
  }, [taskId]); // Rerun only when taskId changes

  // --- Visibility Logic ---
  // Show if there's active task data AND (it's pending/processing OR it's completed/failed AND not manually dismissed for *this specific task*)
  const isVisible =
    !!activeTaskData &&
    (
      status === TASK_STATUS.PENDING ||
      status === TASK_STATUS.PROCESSING ||
      ((status === TASK_STATUS.COMPLETED || status === TASK_STATUS.FAILED) && (!isManuallyDismissed || dismissedTaskIdRef.current !== taskId))
    );

  // --- Render Logic ---
  if (!isVisible) {
    // Optional: Log why it's not visible for debugging
    // console.log(`[TaskStatusBar] Not visible. TaskData: ${!!activeTaskData}, Status: ${status}, Dismissed: ${isManuallyDismissed}, DismissedID: ${dismissedTaskIdRef.current}, CurrentID: ${taskId}`);
    return null;
  }

  let statusMessage = "Task status unknown";
  let statusColor = "bg-gray-100 border-gray-300";
  let statusIcon = null;

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
        <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7"></path>
        </svg>
      );
      break;
    case TASK_STATUS.FAILED:
      statusMessage = activeTaskData?.error_message || "Task failed";
      statusColor = "bg-red-100 border-red-300";
      statusIcon = (
        <svg className="w-5 h-5 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
        </svg>
      );
      break;
  }

  console.log(`[TaskStatusBar] Rendering. Visible: ${isVisible}, Status: ${status}, Message: ${statusMessage}`);

  return (
    <div className={`fixed top-6 right-6 min-w-[320px] z-50 p-3 rounded-lg shadow-2xl border-2 ${statusColor} transition-all duration-300 transform ${isVisible ? 'translate-x-0 opacity-100' : 'translate-x-full opacity-0'}`}>
      <div className="flex items-center">
        <div className="mr-3 flex-shrink-0">
          {statusIcon}
        </div>
        <div className="flex-grow">
          <p className="text-sm font-medium">{statusMessage}</p>
          {taskId && (
            <p className="text-xs opacity-60">Task ID: {taskId.substring(0, 8)}...</p>
          )}
        </div>
        <div className="flex ml-2">
          {/* Refresh button is less useful now with polling, could be removed */}
          {/* <button
            onClick={refreshTaskStatus}
            className="text-gray-500 hover:text-gray-700 mr-2"
            aria-label="Refresh status"
            title="Refresh Status"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path></svg>
          </button> */}
          <button
            onClick={handleManualDismiss}
            className="text-gray-500 hover:text-gray-700"
            aria-label="Close status"
            title="Dismiss Status"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TaskStatusBar;
```

**Key Changes in `TaskStatusBar.tsx`:**

1.  **Removed `shouldShowCompleted` State:** Visibility is now directly tied to the `activeTaskData`'s status and the new `isManuallyDismissed` state.
2.  **Simplified `isVisible` Logic:** The bar shows if there's task data and the status is relevant (`pending`, `processing`, `completed`, `failed`), *unless* it has been manually dismissed for the *current* task ID.
3.  **Added Auto-Dismiss `useEffect`:** When the status becomes `completed` or `failed`, a `setTimeout` is created using `dismissTimerRef`. After `AUTO_DISMISS_DELAY`, it calls `clearActiveTask` from the context (if the task ID still matches) to hide the bar globally. The timer is cleared if the status changes again or the component unmounts.
4.  **Improved Manual Dismissal:** `handleManualDismiss` now sets `isManuallyDismissed` to `true`, remembers *which* task was dismissed using `dismissedTaskIdRef`, and clears the auto-dismiss timer.
5.  **Reset Dismissal on New Task:** A new `useEffect` watches `taskId`. If `taskId` changes (a new task starts), it resets `isManuallyDismissed` to `false`, ensuring the bar shows up for the new task.
6.  **Relies on Context for Task Data:** It consistently uses `activeTaskData` for status, error messages, and task ID.

---

**Step 2: Adjust `TaskContext.tsx` (Minor Change)**

The main change here is to *remove* any logic within the `onSuccess` or `onError` callbacks (passed to `useTaskPolling`) that automatically clears the `activeTaskId`. The context should simply reflect the latest polled state. The `TaskStatusBar` (or potentially other components) will decide when to call `clearActiveTask`.

```tsx
// frontend/my-app/src/contexts/TaskContext.tsx
// ... other imports ...
import { useTaskPolling } from '../hooks/useTaskPolling'; // Ensure this is imported
import { TASK_STATUS } from '../config/apiEndpoints'; // Import TASK_STATUS

// ... (rest of the component code) ...

  // Function to handle task success (SIMPLIFIED)
  const handleTaskSuccess = useCallback((taskData: TaskResponse) => {
    // When the task completes successfully, store result ID if it exists
    if (taskData.status === TASK_STATUS.COMPLETED) {
      console.log(`[TaskContext] Task ${taskData.id} completed successfully`);

      if (taskData.result_id) {
        console.log(`[TaskContext] Setting latest result ID: ${taskData.result_id}`);
        setLatestResultId(taskData.result_id);

        // Invalidate concept queries to ensure fresh data is displayed
        queryClient.invalidateQueries({ queryKey: ['concepts', 'detail', taskData.result_id], exact: false });
        queryClient.invalidateQueries({ queryKey: ['concepts', 'recent'] });
      } else {
        console.log(`[TaskContext] Task completed but no result_id was found`);
      }
      // DO NOT clear the active task here anymore. Let the status bar handle it.
    }
  }, [setLatestResultId, queryClient]); // Dependencies updated

  // Function to handle task error (SIMPLIFIED)
  const handleTaskError = useCallback((error: Error) => {
    console.error(`[TaskContext] Task failed:`, error);
    // DO NOT automatically clear the active task here.
    // The TaskStatusBar will show the error and auto-dismiss or allow manual dismissal.
  }, []); // No dependencies needed if just logging

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
    enabled: true, // Polling is always enabled when there's an activeTaskId
    onSuccess: handleTaskSuccess,
    onError: handleTaskError
  });

  // ... (rest of the component code, including clearActiveTask and context value) ...

  const clearActiveTask = useCallback(() => {
    console.log(`[TaskContext] Manually clearing active task: ${activeTaskId}`);
    setActiveTaskId(null);
    setIsTaskInitiating(false);
    // Clear latestResultId when task is explicitly cleared? Maybe not, depends on desired behavior.
    // setLatestResultId(null);
  }, [activeTaskId]); // Dependency updated

  const value: TaskContextType = {
    // ... other properties ...
    clearActiveTask, // Make sure clearActiveTask is included
    // ... rest of the properties ...
    isTaskPending: isPending || false, // Use derived flags from useTaskPolling
    isTaskProcessing: isProcessing || false,
    isTaskCompleted: isCompleted || false,
    isTaskFailed: isFailed || false,
  };

// ... (rest of the component code) ...
```

**Key Changes in `TaskContext.tsx`:**

1.  **Simplified Callbacks:** Removed logic from `handleTaskSuccess` and `handleTaskError` that automatically cleared the `activeTaskId`. The context now focuses on reflecting the state fetched by polling.
2.  **Dependency on `clearActiveTask`:** The `TaskStatusBar` now calls `clearActiveTask` from the context when it auto-dismisses or is manually dismissed (if that behavior is desired for manual dismissal).

---

**Step 3: Verify `useTaskPolling.ts` and Task Initiation**

*   **`useTaskPolling.ts`:** The existing logic seems generally sound. It uses React Query (`useTaskStatusQuery`) which handles caching and refetching. The `useEffect` that stops polling when `isTaskCompleted` becomes true is correct. The key is that it *reports* the final status correctly via its returned `data`.
*   **`useConceptMutations.ts`:** The logic for setting `isTaskInitiating` and then calling `setActiveTask` upon receiving the initial task response seems correct and should work well with the refactored `TaskStatusBar`.

---

**Summary of Changes:**

1.  **`TaskStatusBar.tsx`:** Overhauled to manage its own visibility based on `activeTaskData` and a new `isManuallyDismissed` state tied to the specific `taskId`. Implemented a reliable auto-dismiss timer using `useEffect`. Reset dismissal state when a new task starts.
2.  **`TaskContext.tsx`:** Simplified the callbacks passed to `useTaskPolling` by removing the automatic clearing of the active task. The context now purely reflects the polled state.

**Benefits of this Refactor:**

1.  **Correct State Handling:** The status bar now reliably shows the status of the *current* active task. When a new task starts, the bar resets and shows the new task's status.
2.  **Reliable Auto-Dismiss:** The `completed` and `failed` states will show for a defined duration (`AUTO_DISMISS_DELAY`) and then the bar will disappear by clearing the global task state.
3.  **Clearer Logic:** State management within the `TaskStatusBar` is simplified and more directly tied to the `activeTaskData`.
4.  **Improved User Experience:** Provides consistent feedback without lingering completed/failed messages interfering with new tasks.
5.  **Robustness:** Handles edge cases like starting a new task while the previous completion message is still visible.

Remember to test these changes thoroughly across different scenarios to ensure the desired behavior.