import { useContextSelector } from "use-context-selector";
import type { TaskResponse } from "../types/api.types";
import { TaskContext } from "../contexts/TaskContext";

/**
 * Hook to access the task context
 * @returns Task context value
 * @throws Error if used outside of TaskProvider
 */
export const useTaskContext = () => {
  // Use useContextSelector for consistency with other selector hooks
  const context = useContextSelector(TaskContext, (state) => state);
  if (context === undefined) {
    throw new Error("useTaskContext must be used within a TaskProvider");
  }
  return context;
};

/**
 * Hook to access the hasActiveTask state from task context
 */
export const useHasActiveTask = () =>
  useContextSelector(TaskContext, (state) => state?.hasActiveTask);

/**
 * Hook to access the isTaskProcessing state from task context
 */
export const useIsTaskProcessing = () =>
  useContextSelector(TaskContext, (state) => state?.isTaskProcessing);

/**
 * Hook to access the isTaskPending state from task context
 */
export const useIsTaskPending = () =>
  useContextSelector(TaskContext, (state) => state?.isTaskPending);

/**
 * Hook to access the isTaskCompleted state from task context
 */
export const useIsTaskCompleted = () =>
  useContextSelector(TaskContext, (state) => state?.isTaskCompleted);

/**
 * Hook to access the isTaskFailed state from task context
 */
export const useIsTaskFailed = () =>
  useContextSelector(TaskContext, (state) => state?.isTaskFailed);

/**
 * Hook to access the latestResultId from task context
 */
export const useLatestResultId = () =>
  useContextSelector(TaskContext, (state) => state?.latestResultId);

/**
 * Hook to access the isTaskInitiating state from task context
 */
export const useTaskInitiating = () =>
  useContextSelector(TaskContext, (state) => state?.isTaskInitiating);

/**
 * Hook to access the activeTaskId from task context
 */
export const useActiveTaskId = () =>
  useContextSelector(TaskContext, (state) => state?.activeTaskId);

/**
 * Hook to access the onTaskCleared event subscription function from task context
 */
export const useOnTaskCleared = () =>
  useContextSelector(TaskContext, (state) => state?.onTaskCleared);

/**
 * Hook to access the active task data
 */
export const useActiveTaskData = (): TaskResponse | null =>
  useContextSelector(TaskContext, (state) => state?.activeTaskData || null);

/**
 * Hook to get a function that clears the current active task
 */
export const useClearActiveTask = () =>
  useContextSelector(TaskContext, (state) => state?.clearActiveTask);
