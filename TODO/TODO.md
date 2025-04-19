Okay, here is a detailed breakdown of the files to be created or modified for implementing the frontend testing strategy, focusing on unit and integration tests using Vitest and React Testing Library (RTL).

**Legend:**

*   `[CREATE]` - A new test file needs to be created.
*   `[MODIFY]` - An existing test file needs to be updated or expanded.
*   `[DONE]` - Task has been completed.

---

### 1. `src/api/`

*   **File to Create:** `src/api/__tests__/task.test.ts` `[CREATE]` `[DONE]`
    *   **Purpose:** Verify deprecated API call functions interact correctly with the `apiClient`.
    *   **Key Tests:**
        *   Mock `apiClient` using `vi.mock('../../services/apiClient')`.
        *   Test `fetchTaskStatus`: Ensure it calls `apiClient.get` with the correct formatted URL (`tasks/${taskId}`). Check taskId validation.
        *   Test `cancelTask`: Ensure it calls `apiClient.post` with the correct formatted URL (`tasks/${taskId}/cancel`). Check taskId validation.
    *   **Note:** Low priority due to deprecation; focus on testing the corresponding hooks (`useTaskQueries`).
    *   **Status:** Implemented unit tests for both `fetchTaskStatus` and `cancelTask` functions with validation checks.

---

### 2. `src/components/`

*   **`common/`**
    *   **File to Create:** `src/components/common/__tests__/QueryResultHandler.test.tsx` `[CREATE]` `[DONE]`
        *   **Purpose:** Test conditional rendering based on query state props.
        *   **Key Tests:**
            *   Render with `isLoading={true}` -> Assert `loadingComponent` or default `LoadingIndicator` is shown.
            *   Render with `error` -> Assert `errorComponent` or default `ErrorMessage` is shown with the correct message.
            *   Render with `data={null}` or `data={[]}` -> Assert `emptyComponent` or default empty message is shown.
            *   Render with valid `data` -> Assert `children` function is called with data and its output is rendered.
        *   **Status:** Implemented all test cases for each condition (loading, error, empty, data) including custom component variants.

*   **`concept/`**
    *   **File to Modify:** `src/components/concept/__tests__/ConceptForm.test.tsx` `[MODIFY]` `[DONE]`
        *   **Purpose:** Enhance existing tests for the concept generation form.
        *   **Key Tests (Add/Verify):**
            *   Simulate input changes using `fireEvent.change` and verify state updates (if applicable, or check controlled component behavior).
            *   Test validation logic thoroughly (empty fields, min length) and assert error messages appear.
            *   Mock `onSubmit` and verify it's called with correct `logoDescription` and `themeDescription` on valid submission.
            *   Test rendering based on `status` prop ('submitting', 'error', 'success'): check button disabled state, loading indicator visibility, error message display.
            *   Test `onReset` callback invocation.
            *   Verify snapshot is up-to-date.
        *   **Status:** Implemented all required tests, fixed mocks for dependencies, and added tests for error states and reset functionality.
    *   **File to Create:** `src/components/concept/__tests__/ConceptImage.test.tsx` `[CREATE]`
        *   **Purpose:** Test the wrapper around `OptimizedImage`.
        *   **Key Tests:**
            *   Render with `url` prop -> Assert `OptimizedImage` receives the `url`.
            *   Render with `path` prop -> Assert `OptimizedImage` receives the `path` (check if URL conversion happens if needed).
            *   Render without `url` or `path` -> Assert placeholder text is shown.
            *   Simulate `onError` from `OptimizedImage` -> Assert error message is displayed.
    *   **File to Modify:** `src/components/concept/__tests__/ConceptRefinementForm.test.tsx` `[MODIFY]`
        *   **Purpose:** Enhance existing tests for the refinement form.
        *   **Key Tests (Add/Verify):**
            *   Render with initial props (`originalImageUrl`, `initialLogoDescription`, `initialThemeDescription`) -> Assert image is shown and textareas have correct initial values.
            *   Test validation (empty/short refinement prompt) -> Assert error message appears.
            *   Simulate input changes in textareas.
            *   Simulate checkbox clicks for `preserveAspects` -> Verify internal state updates (if possible) or check form submission arguments.
            *   Mock `onSubmit` -> Simulate valid submission, assert callback is called with correct prompt, descriptions, and selected aspects.
            *   Mock `onCancel` -> Simulate cancel button click, assert callback is called.
            *   Test rendering based on `status` prop ('submitting', 'error', 'success') -> Check disabled states, loading indicators, error messages.
            *   Verify snapshot is up-to-date.
    *   **File to Modify:** `src/components/concept/__tests__/ConceptResult.test.tsx` `[MODIFY]`
        *   **Purpose:** Enhance existing tests for displaying generation results.
        *   **Key Tests (Add/Verify):**
            *   Render with `concept` data -> Assert image (`imageUrl`), palette (`ColorPaletteComponent`), and date are displayed correctly.
            *   Render with `variations` -> Assert variation thumbnails/selectors are rendered. Simulate variation selection and check if main image/palette updates.
            *   Mock `onRefineRequest` -> Simulate button click, assert callback called.
            *   Mock `onDownload` -> Simulate button click, assert callback called (or test default `window.open` mock if no prop passed).
            *   Mock `onColorSelect` -> Simulate clicking on a color swatch in `ColorPaletteComponent`, assert callback called with correct color/role.
            *   Render without `onRefineRequest` prop -> Assert refine button is not present.
            *   Verify snapshot is up-to-date.

*   **`layout/`**
    *   **File to Modify:** `src/components/layout/__tests__/Footer.test.tsx` `[MODIFY]`
        *   **Purpose:** Verify footer rendering and links.
        *   **Key Tests (Add/Verify):**
            *   Render within `MemoryRouter`.
            *   Assert all text content (title, tagline, headings, copyright) is present.
            *   Assert all links (`<Link>` and `<a>`) have the correct `href` attributes.
            *   Test `year` prop (default vs. custom).
            *   Verify snapshot is up-to-date.
    *   **File to Modify:** `src/components/layout/__tests__/Header.test.tsx` `[MODIFY]`
        *   **Purpose:** Verify header rendering, navigation links, and active state highlighting.
        *   **Key Tests (Add/Verify):**
            *   Render within `MemoryRouter`.
            *   Assert logo and title are present and link to '/'.
            *   Assert navigation links ("Create", "Recent", "Refine") are present with correct `href`.
            *   Test `activeRoute` prop: Render with different `activeRoute` values (`/`, `/create`, `/recent`, `/refine`, `/refine/123`) and assert the correct link has the active CSS class (`styles.activeNavLink`) and others have the inactive class.
            *   Test mobile menu: Simulate screen size change (if possible with testing setup, otherwise assume mobile view), simulate clicking the hamburger button, assert mobile links become visible, simulate clicking a mobile link, assert menu closes.
            *   Verify snapshot is up-to-date.
    *   **File to Create:** `src/components/layout/__tests__/MainLayout.test.tsx` `[CREATE]`
        *   **Purpose:** Test the main structure of the application layout.
        *   **Key Tests:**
            *   Render within `MemoryRouter`, `QueryClientProvider`, `AuthProvider`, `ToastProvider`, `RateLimitProvider`, `TaskProvider`.
            *   Mock `useLocation` to provide a pathname.
            *   Assert that `Header` and `Footer` components are rendered.
            *   Assert that the `Outlet`'s container (`<main>`) exists. (Testing the *content* of the outlet is done in feature/routing tests).
            *   Assert `RateLimitsPanel` and its toggle button are rendered. Simulate toggle click and check visibility/state change (may need to mock `useRateLimitsQuery`).

*   **`RateLimitsPanel/`**
    *   **File to Create:** `src/components/RateLimitsPanel/__tests__/RateLimitsPanel.test.tsx` `[CREATE]`
        *   **Purpose:** Test rendering of rate limit information.
        *   **Key Tests:**
            *   Mock `useRateLimitsQuery` hook.
            *   Render with `isLoading: true` -> Assert loading state is shown.
            *   Render with `error` -> Assert error message is shown.
            *   Render with `data` -> Assert correct limit categories are displayed with correct `remaining`/`limit` values and progress bars reflect the percentage. Test `formatTimeRemaining` is used for tooltips.
            *   Simulate clicking the 'Refresh' button -> Assert `refetch` function from mocked hook is called. Test cooldown logic disables the button.

*   **`ui/`** (Create/Modify test files for each component)
    *   **Files:** `Button.test.tsx` `[MODIFY]`, `Card.test.tsx` `[MODIFY]`, `ColorPalette.test.tsx` `[MODIFY]`, `Input.test.tsx` `[MODIFY]`, `TextArea.test.tsx` `[MODIFY]`, `ApiToastListener.test.tsx` `[CREATE]`, `ConceptCard.test.tsx` `[CREATE]`, `ErrorBoundary.test.tsx` `[CREATE]`, `ErrorMessage.test.tsx` `[CREATE]`, `FeatureSteps.test.tsx` `[CREATE]`, `LoadingIndicator.test.tsx` `[CREATE]`, `OfflineStatus.test.tsx` `[CREATE]`, `OptimizedImage.test.tsx` `[CREATE]`, `SkeletonLoader.test.tsx` `[CREATE]`, `Spinner.test.tsx` `[CREATE]`, `Toast.test.tsx` `[CREATE]`, `ToastContainer.test.tsx` `[CREATE]`
    *   **Purpose:** Unit test individual, reusable UI components.
    *   **Key Tests (General):** Basic rendering, prop variations (variants, sizes, text, data), interaction handling (`onClick`, `onChange`), state handling (`disabled`, `selected`), accessibility attributes, snapshots.
    *   **Specifics:**
        *   `ApiToastListener`: Mock `useToast`. Dispatch `show-api-toast` custom events on `document`, assert the correct `useToast` function (`showSuccess`, `showError`, etc.) is called.
        *   `ConceptCard`: Test rendering with `concept` prop vs individual props. Test initials generation. Test color variation dots and selection (`onClick`). Mock `onEdit`/`onViewDetails` and test button clicks. Test `preventNavigation`.
        *   `ErrorBoundary`: Render with a child component that throws an error. Assert the fallback UI (default or custom `fallback` prop) is displayed. Test `onError` callback. Test retry button functionality.
        *   `ErrorMessage`: Render with different `type` props, assert correct styling/icon. Test rendering `details`, `validationErrors`, `rateLimitData`. Test `onRetry`/`onDismiss` callbacks.
        *   `FeatureSteps`: Render with `title` and `steps` props, assert correct text/numbers. Mock action handlers and test button clicks.
        *   `LoadingIndicator`/`Spinner`: Test rendering different `size` props and classes. Test `showLabel`.
        *   `OfflineStatus`: Mock `useNetworkStatus`. Render with different states (`isOnline`, `isSlowConnection`) and assert correct message/styling. Test retry button calls `checkConnection`.
        *   `OptimizedImage`: Mock `IntersectionObserver`. Test lazy loading (image `src` initially null/placeholder, then updates). Test `onLoad`, `onError` handlers. Test `placeholder` rendering.
        *   `SkeletonLoader`: Render different `type` props (`text`, `circle`, `card`, etc.) and assert correct structure/classes. Test `lines` prop for text.
        *   `Toast`: Test rendering different `type` props. Test `onDismiss` callback after `duration` or close button click.
        *   `ToastContainer`: Render with multiple `toasts`. Test `position` prop results in correct classes. Test `onDismiss` callback passes correct ID.

*   **`TaskStatusBar.tsx`**
    *   **File to Create:** `src/components/__tests__/TaskStatusBar.test.tsx` `[CREATE]`
        *   **Purpose:** Test rendering based on task context state.
        *   **Key Tests:**
            *   Wrap in mock `TaskProvider`.
            *   Simulate different context values (`activeTaskId`, `activeTaskData` with various statuses, `isTaskInitiating`, etc.) -> Assert correct message, icon, and style are rendered. Assert visibility based on state.
            *   Simulate dismiss button click -> Assert `clearActiveTask` from context is called.
            *   Simulate refresh button click -> Assert `refreshTaskStatus` from context is called.
            *   Test auto-dismiss logic (might need timer mocks).

---

### 3. `src/config/`

*   **File to Create:** `src/config/__tests__/apiEndpoints.test.ts` `[CREATE]`
    *   **Purpose:** Verify API endpoint constants and functions.
    *   **Key Tests:** Assert string constants match expected values. Call functions like `API_ENDPOINTS.TASK_STATUS_BY_ID('test-id')` and assert the returned string is correct.
*   **File to Create:** `src/config/__tests__/queryKeys.test.ts` `[CREATE]`
    *   **Purpose:** Verify React Query key factory functions.
    *   **Key Tests:** Call factory functions (e.g., `queryKeys.concepts.detail('test-id')`) and assert the returned array structure and contents are correct. Test with and without optional parameters.

---

### 4. `src/contexts/`

*   **File to Create:** `src/contexts/__tests__/AuthContext.test.tsx` `[CREATE]`
    *   **Purpose:** Test `AuthProvider` state and `useAuth` hooks.
    *   **Key Tests:** Render provider + consumer hook. Assert initial state (`isLoading`, `user`, `isAnonymous`). Mock `supabase.auth.getSession`, `supabase.auth.onAuthStateChange`, `initializeAnonymousAuth`. Simulate auth state changes (`SIGNED_IN`, `SIGNED_OUT`, token refresh), assert context state updates correctly. Test `signOut` and `linkEmail` call the underlying Supabase functions. Test selector hooks (`useUserId`, `useIsAnonymous`, etc.).
*   **File to Create:** `src/contexts/__tests__/RateLimitContext.test.tsx` `[CREATE]`
    *   **Purpose:** Test `RateLimitProvider` state and `useRateLimitContext` hooks.
    *   **Key Tests:** Render provider + consumer hook. Mock `useRateLimitsQuery`. Assert initial state. Simulate query loading, success, error states and verify context updates. Call `decrementLimit` within `act()` and verify optimistic update via `useRateLimitsData`. Test `refetch` function calls the underlying query refetch. Test selector hooks.
*   **File to Create:** `src/contexts/__tests__/TaskContext.test.tsx` `[CREATE]`
    *   **Purpose:** Test `TaskProvider` state management and hooks.
    *   **Key Tests:** Render provider + consumer hook. Assert initial state. Call `setActiveTask`, `clearActiveTask`, `setIsTaskInitiating` within `act()` and assert state updates (`activeTaskId`, `hasActiveTask`, etc.). Mock `useTaskSubscription`, simulate subscription updates (different statuses, `result_id`), assert `activeTaskData`, `latestResultId` update correctly. Test `onTaskCleared` subscription/unsubscription. Test `refreshTaskStatus` invalidates query cache (mock `queryClient`).

---

### 5. `src/features/`

*   **`concepts/detail/`**
    *   **File to Modify:** `src/features/concepts/detail/__tests__/ConceptDetailPage.test.tsx` `[MODIFY]`
        *   **Purpose:** Integration test for the concept detail view.
        *   **Key Tests (Add/Verify):** Use `MemoryRouter` with `:conceptId`. Mock `useConceptDetail`. Test loading state (skeletons). Test error state (not found, general error). Test successful rendering of concept data (image using `OptimizedImage`, descriptions, `ColorPalette`). Test variation selection updates the main image and palette display. Test clicking 'Refine' calls `navigate`. Test clicking 'Export Selected' in `ExportOptions` calls the appropriate handler/mutation. Test `showExport` query param functionality.
    *   **File to Modify:** `src/features/concepts/detail/components/__tests__/EnhancedImagePreview.test.tsx` `[MODIFY]`
        *   **Purpose:** Test the modal image preview component.
        *   **Key Tests (Add/Verify):** Render with `isOpen=true`. Assert modal content is visible. Mock Material UI components if not already done. Test close button calls `onClose`. Simulate mouse events (mouseDown, mouseMove, mouseUp, wheel) for pan/zoom and ensure no errors (state testing is difficult here, focus on interaction).
    *   **File to Create:** `src/features/concepts/detail/components/__tests__/ExportOptions.test.tsx` `[CREATE]`
        *   **Purpose:** Test the export options component.
        *   **Key Tests:** Render with props (`imageUrl`, etc.). Simulate clicking format/size buttons and verify internal state/selection updates. Mock `useExportImageMutation`. Simulate 'Preview' click -> assert preview mutation called, test modal opening on success. Simulate 'Download' click -> assert export mutation called, test `downloadBlob` helper called on success. Simulate 'Copy Link' click -> test `navigator.clipboard.writeText` called, test success state UI. Test error handling for mutations.

*   **`concepts/recent/`**
    *   **File to Modify:** `src/features/concepts/recent/__tests__/RecentConceptsPage.test.tsx` `[MODIFY]`
        *   **Purpose:** High-level test ensuring the recent concepts page structure.
        *   **Key Tests (Add/Verify):** Render with `MemoryRouter`. Assert `RecentConceptsHeader` and `ConceptList` components are rendered.
    *   **File to Modify:** `src/features/concepts/recent/components/__tests__/ConceptList.test.tsx` `[MODIFY]`
        *   **Purpose:** Enhance tests for displaying the list of concepts.
        *   **Key Tests (Add/Verify):** Use `MemoryRouter`. Mock `useRecentConcepts`. Test loading state (skeletons). Test error state (error message, 'Try Again' button calls `refetch`). Test empty state (message, 'Create New' link navigates). Test rendering `ConceptCard` for each concept in mock data. Test clicking 'Refine'/'View Details' on a card calls the correct handler (`handleEdit`/`handleViewDetails`) which should call `navigate` with correct URL (including variation ID if selected within the card).
    *   **File to Create:** `src/features/concepts/recent/components/__tests__/RecentConceptsHeader.test.tsx` `[CREATE]`
        *   **Purpose:** Test the header specific to the recent concepts page.
        *   **Key Tests:** Render component. Assert title and description text are present.

*   **`landing/`**
    *   **File to Modify:** `src/features/landing/__tests__/LandingPage.test.tsx` `[MODIFY]`
        *   **Purpose:** Integration test for the main landing page flow.
        *   **Key Tests (Add/Verify):** Use `MemoryRouter`. Mock `useGenerateConceptMutation` and `useRecentConcepts`. Assert initial rendering of `ConceptHeader`, `HowItWorks`, `ConceptFormSection`, `RecentConceptsSection`. Simulate form submission -> verify `mutate` called. Simulate mutation `isPending` -> verify loading UI in form/results. Simulate mutation `isSuccess` -> verify `ResultsSection` displayed with data. Simulate mutation `isError` -> verify error message in form. Test 'Start Over' button resets state. Test clicking 'Get Started' scrolls to form. Test clicking cards in `RecentConceptsSection` calls `navigate`.
    *   **File to Create:** `src/features/landing/components/__tests__/HowItWorks.test.tsx` `[CREATE]`
        *   **Purpose:** Test the 'How It Works' steps component.
        *   **Key Tests:** Render with `steps` prop. Assert all step numbers, titles, and descriptions are displayed. Mock `onGetStarted` and test button click.
    *   **File to Create:** `src/features/landing/components/__tests__/RecentConceptsSection.test.tsx` `[CREATE]`
        *   **Purpose:** Test the section displaying recent concepts on the landing page.
        *   **Key Tests:** Render with `concepts` prop. Assert `ConceptCard` is rendered for each concept. Mock `onEdit`/`onViewDetails` and verify calls when card buttons are clicked. Test `isLoading` prop shows skeletons. Test 'View All' link navigates to `/recent`.
    *   **File to Create:** `src/features/landing/components/__tests__/ResultsSection.test.tsx` `[CREATE]`
        *   **Purpose:** Test the section displaying generation results.
        *   **Key Tests:** Render with `conceptData`. Assert main image and variations grid are displayed correctly. Simulate variation selection and assert main image updates. Mock `onExportSelected` and test 'Export Selected' button click passes correct concept/variation ID. Test `onStartOver` button callback. Test `isLoading` prop shows skeleton.
    *   **File to Create:** `src/features/landing/components/__tests__/ConceptFormSection.test.tsx` `[CREATE]`
        *   **Purpose:** Test the wrapper section for the concept form.
        *   **Key Tests:** Render with props. Assert `ConceptForm` is rendered and receives the correct props (`onSubmit`, `status`, `errorMessage`, `onReset`, `isProcessing`, `processingMessage`).
    *   **File to Create:** `src/features/landing/components/__tests__/ConceptHeader.test.tsx` `[CREATE]`
        *   **Purpose:** Test the header specific to the landing page.
        *   **Key Tests:** Render component. Assert title and description text are present. Mock `onGetStarted` and test button click.

*   **`refinement/`**
    *   **File to Modify:** `src/features/refinement/__tests__/RefinementPage.test.tsx` `[MODIFY]`
        *   **Purpose:** Integration test for the concept refinement flow.
        *   **Key Tests (Add/Verify):** Use `MemoryRouter` with route params (`:conceptId`, `?colorId`). Mock `useConceptDetail` and `useRefineConceptMutation`. Test loading state. Test error state (concept not found). Test rendering `RefinementHeader` and `RefinementForm` with initial concept data. Simulate form submission -> verify `mutate` called. Simulate success -> verify `ComparisonView` and `RefinementActions` rendered. Test `onReset` and `onCreateNew` calls from `RefinementActions`.
    *   **File to Modify:** `src/features/refinement/__tests__/RefinementSelectionPage.test.tsx` `[MODIFY]`
        *   **Purpose:** Integration test for the page where users select a concept to refine.
        *   **Key Tests (Add/Verify):** Use `MemoryRouter`. Mock `useRecentConcepts`. Test loading, error, and empty states. Render with mock concept data -> assert concepts are listed correctly (image, title). Simulate clicking a concept row/button -> assert `navigate` is called with the correct `/refine/:conceptId` URL. Test variation selection within the expanded view calls `navigate` with the correct `?colorId`.
    *   **File to Create:** `src/features/refinement/components/__tests__/ComparisonView.test.tsx` `[CREATE]`
        *   **Purpose:** Test the side-by-side comparison component.
        *   **Key Tests:** Render with `originalImageUrl` and `refinedConceptId`. Mock `useConceptDetail` for the refined concept. Test loading/error states for the refined concept fetch. Assert both original and refined images are displayed. Assert `ConceptResult` is rendered for the refined concept.
    *   **File to Create:** `src/features/refinement/components/__tests__/RefinementActions.test.tsx` `[CREATE]`
        *   **Purpose:** Test the action buttons shown after refinement.
        *   **Key Tests:** Render component. Mock `onReset` and `onCreateNew`. Simulate button clicks and verify callbacks.
    *   **File to Create:** `src/features/refinement/components/__tests__/RefinementForm.test.tsx` `[CREATE]`
        *   **Purpose:** Test the wrapper around the main refinement form component.
        *   **Key Tests:** Render with props. Assert `ConceptRefinementForm` is rendered. Verify props are passed correctly, especially `refinementPlaceholder` and `defaultPreserveAspects` based on `colorVariation` prop.
    *   **File to Create:** `src/features/refinement/components/__tests__/RefinementHeader.test.tsx` `[CREATE]`
        *   **Purpose:** Test the header specific to the refinement page.
        *   **Key Tests:** Render component. Assert correct title/description based on `isVariation` and `variationName` props.

---

### 6. `src/hooks/`

*   **`animation/`**
    *   **File to Create:** `src/hooks/animation/__tests__/useAnimatedMount.test.tsx` `[CREATE]`
        *   **Purpose:** Test mount/unmount animation state transitions.
        *   **Key Tests:** Use `renderHook`. Test initial `isMounted`/`animationState`. Update `isVisible` prop -> use `waitFor` to assert state transitions (`entering` -> `entered`, `exiting` -> `exited`) happen after correct `enterDuration`/`exitDuration` (use timer mocks). Test callbacks (`onEntering`, etc.) are called. Test `prefersReducedMotion` skips animation.
    *   **File to Create:** `src/hooks/animation/__tests__/useAnimatedValue.test.tsx` `[CREATE]`
        *   **Purpose:** Test value interpolation over time.
        *   **Key Tests:** Use `renderHook`. Test initial value. Update `endValue` prop -> use `waitFor` to assert the value animates correctly over `duration` using the specified `easing`. Test `delay`. Test `onComplete` callback. Test `isActive` prop. Test `prefersReducedMotion`.
    *   **File to Create:** `src/hooks/animation/__tests__/usePrefersReducedMotion.test.tsx` `[CREATE]`
        *   **Purpose:** Test detection of reduced motion preference.
        *   **Key Tests:** Use `renderHook`. Mock `window.matchMedia`. Simulate media query changes and assert hook returns the correct boolean value. Test initial state.

*   **Hook Files:**
    *   **File to Create:** `src/hooks/__tests__/useConceptMutations.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useConceptQueries.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useConfigQuery.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useErrorHandling.test.tsx` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useExportImageMutation.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useNetworkStatus.test.tsx` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useRateLimitsQuery.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useSessionQuery.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useTaskQueries.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useTaskSubscription.test.ts` `[CREATE]`
    *   **File to Create:** `src/hooks/__tests__/useToast.test.tsx` `[CREATE]`
        *   **Purpose (General):** Isolate and test the logic, state, side effects, and return values of each custom hook.
        *   **Key Tests (General):** Use `renderHook`. Mock dependencies (`apiClient`, `supabase`, contexts, other hooks). Test initial state. Trigger actions/updates using `act()`. Test async logic with `waitFor`. Verify correct state updates and return values. Test error handling. Test cleanup logic on `unmount`. See specific hook examples in the previous strategy document.

---

### 7. `src/services/`

*   **File to Modify:** `src/services/__tests__/apiClient.test.ts` `[MODIFY]` (`apiInterceptors.test.ts` likely needs renaming/merging)
    *   **Purpose:** Test the Axios instance, interceptors, and custom error classes.
    *   **Key Tests (Add/Verify):** Mock `axios`. Test request interceptor adds/removes Auth header correctly (mock `supabase.auth.getSession`). Test response interceptor handles 401 (mock `supabase.auth.refreshSession`, test retry), 429 (test `RateLimitError` creation, event dispatch), rate limit header extraction, and general error categorization into custom error classes (`AuthError`, `ServerError`, etc.). Test `exportImage` function sets correct `responseType`.
*   **File to Create:** `src/services/__tests__/conceptService.test.ts` `[CREATE]`
    *   **Purpose:** Verify functions call `apiClient` correctly for concept endpoints.
    *   **Key Tests:** Mock `apiClient`. Call `fetchRecentConceptsFromApi`, `fetchConceptDetailFromApi`. Assert `apiClient.get` is called with the correct URLs and parameters. Test handling of 404 for detail fetch.
*   **File to Create:** `src/services/__tests__/configService.test.ts` `[CREATE]`
    *   **Purpose:** Test configuration fetching and access.
    *   **Key Tests:** Mock `fetch`. Call `fetchConfig`, assert correct URL. Test `getConfig` returns default, then fetched config. Test `getBucketName`. Test `useConfig` hook (render, check loading/data/error).
*   **File to Create:** `src/services/__tests__/eventService.test.ts` `[CREATE]`
    *   **Purpose:** Test the simple event emitter.
    *   **Key Tests:** Test `subscribe` adds handler. Test `emit` calls correct handlers. Test unsubscribe function removes handler. Test `clearListeners`.
*   **File to Create:** `src/services/__tests__/rateLimitService.test.ts` `[CREATE]`
    *   **Purpose:** Test rate limit helper functions.
    *   **Key Tests:** Test `mapEndpointToCategory` with various endpoint strings. Test `extractRateLimitHeaders` (mock `AxiosResponse`, mock `queryClient.setQueryData` and assert it's called with correct update). Test `formatTimeRemaining` with different seconds values. Test `decrementRateLimit` (mock `queryClient.getQueryData`/`setQueryData`).
*   **File to Create:** `src/services/__tests__/supabaseClient.test.ts` `[CREATE]`
    *   **Purpose:** Test interactions with the Supabase JS library.
    *   **Key Tests:** Mock `supabase-js` (`createClient`, `auth` methods). Test `initializeAnonymousAuth` checks session and calls `signInAnonymously` if needed. Test `getUserId`, `signOut`, `isAnonymousUser`, `linkEmailToAnonymousUser` call the correct underlying methods. Test `getAuthenticatedImageUrl` calls `createSignedUrl`.

---

### 8. `src/utils/`

*   **File to Create:** `src/utils/__tests__/dev-logging.test.ts` `[CREATE]`
*   **File to Create:** `src/utils/__tests__/errorUtils.test.ts` `[CREATE]`
*   **File to Modify:** `src/utils/__tests__/formatUtils.test.ts` `[MODIFY]`
*   **File to Create:** `src/utils/__tests__/logger.test.ts` `[CREATE]`
*   **File to Modify:** `src/utils/__tests__/stringUtils.test.ts` `[MODIFY]`
*   **File to Create:** `src/utils/__tests__/url.test.ts` `[CREATE]`
*   **File to Modify:** `src/utils/__tests__/validationUtils.test.ts` `[MODIFY]`
    *   **Purpose (General):** Unit test pure utility functions for correctness and edge cases.
    *   **Key Tests (General):** Import functions. For each function, provide various valid inputs, invalid inputs, edge cases (empty, null, boundary values), and assert the output is exactly as expected using `expect`.

---

### 9. `src/App.tsx`

*   **File to Create:** `src/App.test.tsx` `[CREATE]`
    *   **Purpose:** High-level integration test to ensure the app mounts and renders the default route.
    *   **Key Tests:** Render `<App />` within `QueryClientProvider` and `MemoryRouter`. Assert a key element from `LandingPage` (e.g., the main H1 title) is present. Check that providers (`ToastProvider`, `AuthProvider`, etc.) are wrapping the content correctly (though their internal logic is tested elsewhere).

---

This detailed list provides a clear roadmap for implementing the frontend testing strategy, ensuring comprehensive coverage across different layers and functionalities. Remember to keep tests focused and avoid testing implementation details where possible, favoring tests that verify the component's behavior from a user's perspective.