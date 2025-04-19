Okay, here is the prioritized implementation order for your frontend tests, based on dependencies and building from the foundation upwards. The original descriptions for each file are retained.

**Phase 1: Foundational Utilities & Core UI**

1.  **`src/utils/__tests__/formatUtils.test.ts` `[MODIFY]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
2.  **`src/utils/__tests__/stringUtils.test.ts` `[MODIFY]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
3.  **`src/utils/__tests__/validationUtils.test.ts` `[MODIFY]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
4.  **`src/utils/__tests__/url.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
5.  **`src/utils/__tests__/logger.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
6.  **`src/utils/__tests__/dev-logging.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
7.  **`src/utils/__tests__/errorUtils.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases. Test `createAsyncErrorHandler`, `createQueryErrorHandler` structures, maybe with mock error handler.
8.  **`src/config/__tests__/apiEndpoints.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Verify API endpoint constants and functions.
    *   **Key Tests:** Assert string constants match expected values. Call functions like `API_ENDPOINTS.TASK_STATUS_BY_ID('test-id')` and assert the returned string is correct.
9.  **`src/config/__tests__/queryKeys.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Verify React Query key factory functions.
    *   **Key Tests:** Call factory functions (e.g., `queryKeys.concepts.detail('test-id')`) and assert the returned array structure and contents are correct. Test with and without optional parameters.
10. **`src/components/ui/__tests__/Button.test.tsx` `[MODIFY]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components.
11. **`src/components/ui/__tests__/Card.test.tsx` `[MODIFY]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components.
12. **`src/components/ui/__tests__/Input.test.tsx` `[MODIFY]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components.
13. **`src/components/ui/__tests__/TextArea.test.tsx` `[MODIFY]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components.
14. **`src/components/ui/__tests__/LoadingIndicator.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Test rendering different `size` props and classes. Test `showLabel`.
15. **`src/components/ui/__tests__/Spinner.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Test rendering different `size` props and classes.
16. **`src/components/ui/__tests__/SkeletonLoader.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Render different `type` props (`text`, `circle`, `card`, etc.) and assert correct structure/classes. Test `lines` prop for text.
17. **`src/components/ui/__tests__/OptimizedImage.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Mock `IntersectionObserver`. Test lazy loading (image `src` initially null/placeholder, then updates). Test `onLoad`, `onError` handlers. Test `placeholder` rendering.

**Phase 2: Services & Core Logic**

18. **`src/services/__tests__/apiClient.test.ts` `[MODIFY]` `[DONE]`**
    *   **Purpose:** Test the Axios instance, interceptors, and custom error classes.
    *   **Key Tests (Add/Verify):** Mock `axios`. Test request interceptor adds/removes Auth header correctly (mock `supabase.auth.getSession`). Test response interceptor handles 401 (mock `supabase.auth.refreshSession`, test retry), 429 (test `RateLimitError` creation, event dispatch), rate limit header extraction, and general error categorization into custom error classes (`AuthError`, `ServerError`, etc.). Test `exportImage` function sets correct `responseType`.
19. **`src/services/__tests__/supabaseClient.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Test interactions with the Supabase JS library.
    *   **Key Tests:** Mock `supabase-js` (`createClient`, `auth` methods). Test `initializeAnonymousAuth` checks session and calls `signInAnonymously` if needed. Test `getUserId`, `signOut`, `isAnonymousUser`, `linkEmailToAnonymousUser` call the correct underlying methods. Test `getAuthenticatedImageUrl` calls `createSignedUrl`.
20. **`src/services/__tests__/rateLimitService.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Test rate limit helper functions.
    *   **Key Tests:** Test `mapEndpointToCategory` with various endpoint strings. Test `extractRateLimitHeaders` (mock `AxiosResponse`, mock `queryClient.setQueryData` and assert it's called with correct update). Test `formatTimeRemaining` with different seconds values. Test `decrementRateLimit` (mock `queryClient.getQueryData`/`setQueryData`).
21. **`src/services/__tests__/conceptService.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Verify functions call `apiClient` correctly for concept endpoints.
    *   **Key Tests:** Mock `apiClient`. Call `fetchRecentConceptsFromApi`, `fetchConceptDetailFromApi`. Assert `apiClient.get` is called with the correct URLs and parameters. Test handling of 404 for detail fetch.
22. **`src/services/__tests__/configService.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Test configuration fetching and access.
    *   **Key Tests:** Mock `fetch`. Call `fetchConfig`, assert correct URL. Test `getConfig` returns default, then fetched config. Test `getBucketName`. Test `useConfig` hook (render, check loading/data/error).
23. **`src/services/__tests__/eventService.test.ts` `[CREATE]` `[DONE]`**
    *   **Purpose:** Test the simple event emitter.
    *   **Key Tests:** Test `subscribe` adds handler. Test `emit` calls correct handlers. Test unsubscribe function removes handler. Test `clearListeners`.
24. **`src/hooks/__tests__/useErrorHandling.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Test state updates based on `setError`, `handleError`.
25. **`src/hooks/__tests__/useToast.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Test functions trigger state changes correctly within the provider.
26. **`src/hooks/__tests__/useNetworkStatus.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock browser APIs (`navigator.onLine`, `navigator.connection`), test state updates and callbacks.

**Phase 3: Contexts & Data Hooks**

27. **`src/contexts/__tests__/AuthContext.test.tsx` `[CREATE]`**
    *   **Purpose:** Test `AuthProvider` state and `useAuth` hooks.
    *   **Key Tests:** Render provider + consumer hook. Assert initial state (`isLoading`, `user`, `isAnonymous`). Mock `supabase.auth.getSession`, `supabase.auth.onAuthStateChange`, `initializeAnonymousAuth`. Simulate auth state changes (`SIGNED_IN`, `SIGNED_OUT`, token refresh), assert context state updates correctly. Test `signOut` and `linkEmail` call the underlying Supabase functions. Test selector hooks (`useUserId`, `useIsAnonymous`, etc.).
28. **`src/hooks/__tests__/useRateLimitsQuery.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `rateLimitService.fetchRateLimits`. Test query states.
29. **`src/contexts/__tests__/RateLimitContext.test.tsx` `[CREATE]`**
    *   **Purpose:** Test `RateLimitProvider` state and `useRateLimitContext` hooks.
    *   **Key Tests:** Render provider + consumer hook. Mock `useRateLimitsQuery`. Assert initial state. Simulate query loading, success, error states and verify context updates. Call `decrementLimit` within `act()` and verify optimistic update via `useRateLimitsData`. Test `refetch` function calls the underlying query refetch. Test selector hooks.
30. **`src/hooks/__tests__/useTaskQueries.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `apiClient`. Test `useTaskStatusQuery` states. Test `useTaskCancelMutation`.
31. **`src/hooks/__tests__/useTaskSubscription.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `supabase.channel`. Test hook updates `taskData` based on simulated channel messages.
32. **`src/contexts/__tests__/TaskContext.test.tsx` `[CREATE]`**
    *   **Purpose:** Test `TaskProvider` state management and hooks.
    *   **Key Tests:** Render provider + consumer hook. Assert initial state. Call `setActiveTask`, `clearActiveTask`, `setIsTaskInitiating` within `act()` and assert state updates (`activeTaskId`, `hasActiveTask`, etc.). Mock `useTaskSubscription`, simulate subscription updates (different statuses, `result_id`), assert `activeTaskData`, `latestResultId` update correctly. Test `onTaskCleared` subscription/unsubscription. Test `refreshTaskStatus` invalidates query cache (mock `queryClient`).
33. **`src/hooks/__tests__/useConceptQueries.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock services (`conceptService`). Test `useRecentConcepts`, `useConceptDetail` query states (loading, data, error). Use `QueryClientProvider`. Test `enabled` option.
34. **`src/hooks/__tests__/useConceptMutations.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `apiClient`/`conceptService`. Test `useGenerateConceptMutation`, `useRefineConceptMutation` states (`isPending`, `isSuccess`, `isError`, `data`, `error`). Verify `mutate` calls the underlying service. Test optimistic updates (`decrementLimit`) and query invalidation (mock `queryClient`). Test `onError`, `onSuccess` callbacks.
35. **`src/hooks/__tests__/useExportImageMutation.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `apiClient.exportImage`. Test mutation states. Test `downloadBlob` helper (might need DOM mocks).
36. **`src/hooks/__tests__/useSessionQuery.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `apiClient.post`. Test mutation states.
37. **`src/hooks/__tests__/useConfigQuery.test.ts` `[CREATE]`**
    *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook. Mock `apiClient.get`. Test query states.

**Phase 4: Component Integration & Features**

38. **`src/components/ui/__tests__/ErrorMessage.test.tsx` `[CREATE]` `[DONE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Render with different `type` props, assert correct styling/icon. Test rendering `details`, `validationErrors`, `rateLimitData`. Test `onRetry`/`onDismiss` callbacks.
39. **`src/components/ui/__tests__/ColorPalette.test.tsx` `[MODIFY]`**
    *   **Purpose:** Unit test individual, reusable UI components. Test rendering correct colors based on `palette` prop. Test `onColorSelect` callback when `selectable={true}`. Test `selectedColor` highlighting. Test `showLabels` prop.
40. **`src/components/ui/__tests__/ConceptCard.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Test rendering with `concept` prop vs individual props. Test initials generation. Test color variation dots and selection (`onClick`). Mock `onEdit`/`onViewDetails` and test button clicks. Test `preventNavigation`.
41. **`src/components/ui/__tests__/Toast.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Test rendering different `type` props. Test `onDismiss` callback after `duration` or close button click.
42. **`src/components/ui/__tests__/ToastContainer.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Render with multiple `toasts`. Test `position` prop results in correct classes. Test `onDismiss` callback passes correct ID.
43. **`src/components/ui/__tests__/ErrorBoundary.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Render with a child component that throws an error. Assert the fallback UI (default or custom `fallback` prop) is displayed. Test `onError` callback. Test retry button functionality.
44. **`src/components/ui/__tests__/OfflineStatus.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Mock `useNetworkStatus`. Render with different states (`isOnline`, `isSlowConnection`) and assert correct message/styling. Test retry button calls `checkConnection`.
45. **`src/components/ui/__tests__/FeatureSteps.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Render with `title` and `steps` props, assert correct text/numbers. Mock action handlers and test button clicks.
46. **`src/components/ui/__tests__/ApiToastListener.test.tsx` `[CREATE]`**
    *   **Purpose:** Unit test individual, reusable UI components. Mock `useToast`. Dispatch `show-api-toast` custom events on `document`, assert the correct `useToast` function (`showSuccess`, `showError`, etc.) is called.
47. **`src/components/layout/__tests__/Header.test.tsx` `[MODIFY]`**
    *   **Purpose:** Verify header rendering, navigation links, and active state highlighting.
48. **`src/components/layout/__tests__/Footer.test.tsx` `[MODIFY]`**
    *   **Purpose:** Verify footer rendering and links.
49. **`src/components/layout/__tests__/MainLayout.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the main structure of the application layout.
50. **`src/components/common/__tests__/QueryResultHandler.test.tsx` `[MODIFY]`** *(Already marked DONE, but review if needed)*
    *   **Purpose:** Test conditional rendering based on query state props.
51. **`src/components/RateLimitsPanel/__tests__/RateLimitsPanel.test.tsx` `[CREATE]`**
    *   **Purpose:** Test rendering of rate limit information.
52. **`src/components/__tests__/TaskStatusBar.test.tsx` `[CREATE]`**
    *   **Purpose:** Test rendering based on task context state.
53. **`src/components/concept/__tests__/ConceptForm.test.tsx` `[MODIFY]`** *(Already marked DONE, but review if needed)*
    *   **Purpose:** Enhance existing tests for the concept generation form.
54. **`src/components/concept/__tests__/ConceptRefinementForm.test.tsx` `[MODIFY]`**
    *   **Purpose:** Enhance existing tests for the refinement form.
55. **`src/components/concept/__tests__/ConceptResult.test.tsx` `[MODIFY]`**
    *   **Purpose:** Enhance existing tests for displaying generation results.
56. **`src/components/concept/__tests__/ConceptImage.test.tsx` `[MODIFY]`** *(Already marked DONE, but review if needed)*
    *   **Purpose:** Test the wrapper around `OptimizedImage`.
57. **`src/features/landing/components/__tests__/HowItWorks.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the 'How It Works' steps component.
58. **`src/features/landing/components/__tests__/RecentConceptsSection.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the section displaying recent concepts on the landing page.
59. **`src/features/landing/components/__tests__/ResultsSection.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the section displaying generation results.
60. **`src/features/landing/components/__tests__/ConceptFormSection.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the wrapper section for the concept form.
61. **`src/features/landing/components/__tests__/ConceptHeader.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the header specific to the landing page.
62. **`src/features/concepts/detail/components/__tests__/EnhancedImagePreview.test.tsx` `[MODIFY]`**
    *   **Purpose:** Test the modal image preview component.
63. **`src/features/concepts/detail/components/__tests__/ExportOptions.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the export options component.
64. **`src/features/concepts/recent/components/__tests__/RecentConceptsHeader.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the header specific to the recent concepts page.
65. **`src/features/concepts/recent/components/__tests__/ConceptList.test.tsx` `[MODIFY]`**
    *   **Purpose:** Enhance tests for displaying the list of concepts.
66. **`src/features/refinement/components/__tests__/ComparisonView.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the side-by-side comparison component.
67. **`src/features/refinement/components/__tests__/RefinementActions.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the action buttons shown after refinement.
68. **`src/features/refinement/components/__tests__/RefinementForm.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the wrapper around the main refinement form component.
69. **`src/features/refinement/components/__tests__/RefinementHeader.test.tsx` `[CREATE]`**
    *   **Purpose:** Test the header specific to the refinement page.
70. **`src/features/landing/__tests__/LandingPage.test.tsx` `[MODIFY]`**
    *   **Purpose:** Integration test for the main landing page flow.
71. **`src/features/concepts/detail/__tests__/ConceptDetailPage.test.tsx` `[MODIFY]`**
    *   **Purpose:** Integration test for the concept detail view.
72. **`src/features/concepts/recent/__tests__/RecentConceptsPage.test.tsx` `[MODIFY]`**
    *   **Purpose:** High-level test ensuring the recent concepts page structure.
73. **`src/features/refinement/__tests__/RefinementPage.test.tsx` `[MODIFY]`**
    *   **Purpose:** Integration test for the concept refinement flow.
74. **`src/features/refinement/__tests__/RefinementSelectionPage.test.tsx` `[MODIFY]`**
    *   **Purpose:** Integration test for the page where users select a concept to refine.
75. **`src/hooks/animation/__tests__/useAnimatedMount.test.tsx` `[CREATE]`**
    *   **Purpose:** Test mount/unmount animation state transitions.
76. **`src/hooks/animation/__tests__/useAnimatedValue.test.tsx` `[CREATE]`**
    *   **Purpose:** Test value interpolation over time.
77. **`src/hooks/animation/__tests__/usePrefersReducedMotion.test.tsx` `[CREATE]`**
    *   **Purpose:** Test detection of reduced motion preference.
78. **`src/api/__tests__/task.test.ts` `[MODIFY]`** *(Already marked DONE, low priority)*
    *   **Purpose:** Verify deprecated API call functions.
79. **`src/App.test.tsx` `[CREATE]`**
    *   **Purpose:** High-level integration test to ensure the app mounts and renders the default route.

This order prioritizes foundational elements, then services/logic, then hooks/contexts, and finally integrates everything into components and feature pages.