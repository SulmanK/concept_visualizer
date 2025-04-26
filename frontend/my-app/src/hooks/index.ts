// API Hooks
export { useConceptDetail, useRecentConcepts } from "./useConceptQueries";
export {
  useGenerateConceptMutation,
  useRefineConceptMutation,
} from "./useConceptMutations";
export {
  useRateLimitsQuery,
  useOptimisticRateLimitUpdate,
} from "./useRateLimitsQuery";
export { useExportImageMutation, downloadBlob } from "./useExportImageMutation";
export { useTaskStatusQuery, useTaskCancelMutation } from "./useTaskQueries";
export { useTaskSubscription } from "./useTaskSubscription";
export { useSessionSyncMutation } from "./useSessionQuery";
export { useConfigQuery } from "./useConfigQuery";

// Auth Hooks
export {
  useAuth,
  useAuthUser,
  useUserId,
  useIsAnonymous,
  useAuthIsLoading,
} from "./useAuth";

// Rate Limit Hooks
export {
  useRateLimitsData,
  useRateLimitsLoading,
  useRateLimitsError,
  useRateLimitsRefetch,
  useRateLimitsDecrement,
  useRateLimitContext,
  useDecrementRateLimit,
} from "./useRateLimits";

// Task Hooks
export {
  useTaskContext,
  useHasActiveTask,
  useIsTaskProcessing,
  useIsTaskPending,
  useIsTaskCompleted,
  useIsTaskFailed,
  useLatestResultId,
  useTaskInitiating,
  useActiveTaskId,
  useOnTaskCleared,
  useActiveTaskData,
  useClearActiveTask,
} from "./useTask";

// Error and Loading Hooks
export { useToast } from "./useToast";
export { ToastProvider } from "./toast/ToastContext";
export { useErrorHandling } from "./useErrorHandling";
export { useNetworkStatus } from "./useNetworkStatus";

// Animation Hooks
export {
  useAnimatedMount,
  useAnimatedValue,
  usePrefersReducedMotion,
} from "./animation";

// Animation Types (re-exported)
export type {
  AnimationState,
  AnimatedMountOptions,
  AnimatedValueOptions,
} from "./animation";
