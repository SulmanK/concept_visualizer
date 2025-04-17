# [How-To] Enhance Client-Side State & Data Synchronization

## Current Context

-   **System Overview:** The frontend is a React Single Page Application (SPA) using Vite, TypeScript, `react-router-dom` for navigation, `@tanstack/react-query` for server state management, `AuthContext` for authentication, and custom hooks (`useApi`, `useConceptGeneration`, etc.) interacting with a FastAPI backend via an `apiClient`.
-   **Key Components:**
    -   `App.tsx`: Main application structure, includes Router, Providers (`QueryClientProvider`, `AuthProvider`, `RateLimitProvider`, `ToastProvider`).
    *   `PageTransition.tsx`: Custom component handling animated transitions between routes.
    *   React Query Hooks (`useConceptQueries`, `useConceptMutations`, `useRateLimitsQuery`): Manage fetching, caching, and updating server state.
    *   `apiClient.ts`: Centralized fetch wrapper handling authentication and basic error structure.
    *   Contexts (`AuthContext`, `RateLimitContext`): Provide global state.
    *   Page Components (e.g., `LandingPage`, `ConceptDetailPage`): Consume data via hooks and context.
-   **Pain Point:** State and data fetched via React Query sometimes appear stale or "lost" during client-side navigation (using `<Link>` or `navigate()`). A hard browser refresh (F5) correctly reloads the state and data, indicating the issue lies within the client-side data fetching, caching, or state management lifecycle during transitions, not backend data loss.

## Requirements

### Functional Requirements

1.  **Data Freshness:** Data displayed on pages must reflect the latest available server state after client-side navigation, respecting React Query's caching strategy.
2.  **State Persistence:** Local component state and global context state should not be unintentionally lost during navigation transitions.
3.  **Smooth Transitions:** Page transitions should be visually smooth and not introduce visual glitches or flashes of stale content.
4.  **Accurate Loading States:** Correct loading indicators should be displayed while data is being fetched or re-fetched during navigation.
5.  **Consistent Authentication:** Authentication status and tokens must remain valid and be correctly applied to API requests made immediately after navigation.

### Non-Functional Requirements

1.  **Performance:** Minimize unnecessary data re-fetching while ensuring freshness. Page transitions should remain performant. Avoid layout shifts caused by late-loading data.
2.  **Reliability:** State and data fetching should be consistent and predictable across different navigation scenarios.
3.  **User Experience:** Users should not perceive data loss or see inconsistent states between pages. Transitions should feel seamless.
4.  **Maintainability:** Solutions should be easy to understand and maintain within the existing architecture (React Query, Context).

## Design Decisions

### 1. React Query Configuration Review & Adjustment

-   **Approach:** Enable `refetchOnWindowFocus` and potentially adjust `staleTime` to better align with user expectations for data freshness during typical app usage. Explicitly trigger refetches where necessary.
-   **Rationale:**
    -   The current global `refetchOnWindowFocus: false` is a common cause of seeing stale data, as React Query won't automatically check for updates when the user navigates back to the app/tab. Enabling it leverages RQ's built-in freshness mechanism.
    -   Adjusting `staleTime` controls how quickly data is considered "old," influencing refetch behavior on mount.
    -   Explicit refetches guarantee data is fresh for critical views after navigation.
-   **Trade-offs:** Enabling more refetching might slightly increase API calls, but ensures data accuracy. Explicit refetches add minor code complexity but provide precise control.

### 2. Page Transition Strategy Diagnosis & Refinement

-   **Approach:** Systematically diagnose the custom `PageTransition` component by temporarily removing it. If it's implicated, simplify its implementation or replace it with a more standard library (`Framer Motion`, `react-transition-group`).
-   **Rationale:** Custom transition logic, especially involving timeouts, refs, and state manipulation (`isContentReady`, child swapping), can easily conflict with React's rendering lifecycle and data fetching timings, leading to perceived state loss or flashes of old content. Standard libraries often handle these complexities more robustly.
-   **Trade-offs:** Removing/replacing the transition component might alter the desired visual effect but simplifies debugging and ensures core functionality. Using a library adds a dependency but reduces custom code maintenance.

### 3. Authentication Robustness during Transitions

-   **Approach:** Add detailed logging within token refresh logic (`apiClient`, `AuthContext`) and ensure components relying on authentication correctly handle loading states from both `useAuth` and relevant React Query hooks.
-   **Rationale:** While less likely, transient auth failures during navigation could lead to failed data fetches on the destination page. Robust logging helps pinpoint this, and proper loading state handling prevents rendering with incomplete auth info.
-   **Trade-offs:** Adds log noise, requires careful implementation of loading state checks in components.

### 4. Standardized Error Handling & Diagnostics

-   **Approach:** Ensure the `useErrorHandling` hook and associated utilities (`createQueryErrorHandler`) are consistently used for all data fetching (React Query) and API interactions to provide uniform error feedback and simplify debugging.
-   **Rationale:** Consistent error handling makes it easier to identify *why* data might be missing (e.g., a 404 error vs. a 500 error vs. a network error) rather than just observing missing state.
-   **Trade-offs:** Requires minor refactoring in places where error handling might be inconsistent.

## Technical Design (How-To Steps)

### Step 1: Adjust React Query Defaults

1.  **Locate:** Open `src/main.tsx`.
2.  **Modify:** Find the `QueryClient` instantiation.
3.  **Change:** Set `refetchOnWindowFocus: true` (or remove the line to use the default `true`).
    ```typescript
    // src/main.tsx
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          staleTime: 1000 * 60 * 5, // Keep 5 minutes for now
          cacheTime: 1000 * 60 * 30,
          // refetchOnWindowFocus: false, // REMOVE or change to true
          refetchOnWindowFocus: true, // ADD or ensure it's true (default)
          retry: 1,
        },
      },
    });
    ```
4.  **Test:** Thoroughly test navigation scenarios (browser back/forward, link clicks, tab switching) to see if this resolves the stale data issue. Observe network requests and React Query DevTools.

### Step 2: Diagnose `PageTransition` Component

1.  **Locate:** Open `src/App.tsx`.
2.  **Modify:** Find the `AppRoutes` component where `PageTransition` wraps the `<Suspense>` and `<Routes>`.
3.  **Bypass:** Temporarily comment out or remove the `<PageTransition>` wrapper:
    ```typescript
    // src/App.tsx (inside AppRoutes)
    // <PageTransition transitionType={getTransitionType(location.pathname)}> // COMMENT OUT
      <Suspense fallback={<LoadingFallback />}>
        <Routes location={location}>
          {/* ... routes ... */}
        </Routes>
      </Suspense>
    // </PageTransition> // COMMENT OUT
    ```
4.  **Test:** Repeat the navigation scenarios that previously caused state loss.
    *   If the problem *disappears*, `PageTransition` is the primary cause. Proceed to Step 2a.
    *   If the problem *persists*, `PageTransition` is likely not the main issue (though it could still exacerbate it). Restore the component and focus on other steps (especially Step 1 & 4).

### Step 2a: Refine or Replace `PageTransition` (If Implicated)

1.  **Simplify:** Review `src/components/layout/PageTransition.tsx`. Can the logic around `isContentReady`, `useLayoutEffect`, and `requestAnimationFrame` be removed or simplified? Start by removing the initial hiding logic in `useLayoutEffect`. Test if a basic CSS fade transition applied to the container achieves a similar-enough effect with less complex state management.
2.  **Consider Alternatives:** If simplification doesn't work or the effect is lost, evaluate libraries:
    *   **`Framer Motion`:** Powerful animation library, integrates well with React.
    *   **`react-transition-group`:** Lower-level library providing transition state management, often used with CSS transitions/animations.
3.  **Implement:** Replace the custom `PageTransition` with the chosen alternative, ensuring it correctly handles component mounting/unmounting based on `react-router-dom`'s location changes.

### Step 3: Enhance Authentication & Loading State Handling

1.  **Add Logging:**
    *   In `src/services/apiClient.ts` -> `getAuthHeaders`: Log when checking session, when refreshing, success/failure of refresh.
    *   In `src/contexts/AuthContext.tsx`: Log auth state changes, session expiry checks, and refresh triggers/results.
2.  **Review Components:** Check components that use data dependent on `userId` (e.g., `useRecentConcepts`, `useConceptDetail`). Ensure they correctly handle the `isLoading` state from `useAuth()` *in addition to* the query's `isLoading` state. Example:
    ```typescript
    // Example in a component using userId-dependent query
    const { user, isLoading: authLoading } = useAuth();
    const { data, isLoading: queryLoading } = useRecentConcepts(user?.id);

    if (authLoading || queryLoading) {
      return <LoadingIndicator />;
    }
    // ... render data
    ```

### Step 4: Ensure Consistent Data Refetching on Navigation (If Needed)

*If Step 1 wasn't sufficient:*

1.  **Identify Key Pages:** Determine which pages *must* show the absolute latest data immediately upon navigation (e.g., `RecentConceptsPage`, `ConceptDetailPage` after refinement).
2.  **Implement `useEffect`:** In those identified page components, add a `useEffect` hook to explicitly call the `refetch` function from the relevant React Query hook when the component mounts or critical parameters (like `conceptId` or `location.pathname`) change.
    ```typescript
    // src/features/concepts/recent/RecentConceptsPage.tsx
    import { useEffect } from 'react';
    import { useRecentConcepts } from '...';
    import { useAuth } from '...';

    function RecentConceptsPage() {
      const { user } = useAuth();
      const { data, refetch, isLoading } = useRecentConcepts(user?.id);

      useEffect(() => {
        // Refetch whenever the user ID changes or the component mounts
        // The `enabled: !!userId` in the hook already handles the initial load
        // This ensures refetch on subsequent visits if data is stale
        console.log('[RecentConceptsPage] Triggering refetch due to mount/userId change.');
        refetch();
      }, [user?.id, refetch]); // Include userId and refetch in dependency array

      // ... rest of component
    }
    ```
3.  **Review Query Keys:** Double-check that all query keys include every variable the query depends on (e.g., user ID, concept ID, filters, page numbers).

### Step 5: Verify Query Invalidation

1.  **Review Mutations:** Examine `src/hooks/useConceptMutations.ts` and any other mutation hooks.
2.  **Confirm Invalidation:** Ensure that the `onSuccess` or `onSettled` callbacks correctly call `queryClient.invalidateQueries` with the precise query keys for the data that needs refreshing (e.g., `['concepts', 'recent', userId]` after generation/refinement).
3.  **Test:** Perform actions (generate, refine) and navigate immediately to pages displaying related data to confirm they show the updated information without needing a hard refresh. Use React Query DevTools to watch invalidation and refetching.

### Step 6: Standardize Error Handling

1.  **Audit:** Review all `try...catch` blocks involved in data fetching or API calls (`apiClient.ts`, query hooks, mutation hooks, `AuthContext`).
2.  **Implement:** Ensure errors are passed to `errorHandler.handleError` or use `createQueryErrorHandler`.
3.  **Display:** Make sure relevant components use `ErrorMessage` or `RateLimitErrorMessage` to display errors derived from the `errorHandler` state or React Query's `error` state.

By following these steps, starting with the most likely cause (React Query config) and methodically diagnosing the transition component, you should be able to isolate and fix the root cause of the state and data synchronization issues during client-side navigation. Remember to use browser DevTools (Network tab, Console) and React Query DevTools extensively throughout the process.