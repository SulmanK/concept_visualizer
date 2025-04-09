# Concept Visualizer - Project TODO

## Production-Ready Rate Limit Enhancements (@design/rate_limit_production_enhancements.md)

- [x] Refactor `rateLimitService.ts`: Implement central caching based on headers and reset timestamps. Expose functions to get cached data.
- [x] Refactor `useRateLimits.ts`: Remove internal cache, consume data from `rateLimitService`, trigger status endpoint calls only when necessary.
- [x] Update `RateLimitContext.tsx`: Add `decrementLimit` function and integrate it with the service cache for optimistic updates.
- [x] Update `apiClient.ts` / Fetch Interceptor: Implement 429 error handling, specific error reporting (using toasts), and header extraction on 429s.
- [x] Update UI Components:
    - [x] Call `decrementLimit` before relevant actions (e.g., Generate, SVG Export).
    - [x] Add proactive warnings (e.g., low remaining count) in `RateLimitsPanel`.
    - [ ] ~~Add visual indicators (e.g., bars/gauges) to `RateLimitsPanel`.~~ (Skipped)
    - [x] Ensure UI handles specific rate limit error toasts gracefully.
    - [x] Add cooldown to `RateLimitsPanel` refresh button.

## Frontend State Management Refactor (@design/frontend_state_management_refactor.md)

### Phase 1: Context Optimization
- [x] Implement selectors or optimize `useRateLimitContext` hook.
  - Implemented `use-context-selector` library
  - Created individual selector hooks for specific context values
  - Maintained backward compatibility with the original hook
- [x] Implement selectors or optimize `useConceptContext` hook.
  - Added selector hooks for fine-grained context consumption
  - Minimized re-renders for components that only need specific parts of the context
- [x] Review and ensure memoization in `RateLimitProvider` and `ConceptProvider`.
  - Added proper `useMemo` for context values
  - Memoized callback functions to prevent unnecessary re-renders
- [x] Profile and verify performance improvements using React DevTools.

### Phase 2: React Query Simplification
- [x] Refactor `ConceptContext` to rely directly on React Query state (remove redundant loading/error state).
  - Eliminated duplicate state management
  - Directly exposed React Query state through context
- [x] Expose `refetch` and other necessary functions directly from React Query via context.
  - Added direct access to the `refetch` function from React Query
  - Combined with cache invalidation for more reliable refreshing

### Phase 3: Error Handling Standardization
- [x] Audit async operations (`apiClient`, `useConceptQueries`, `AuthContext`) for error handling consistency.
  - Created utility functions in `errorUtils.ts` for standardized error handling
- [x] Integrate `useErrorHandling` hook consistently across audited operations.
  - Added `createAsyncErrorHandler` and `createQueryErrorHandler` utilities
  - Implemented in `useConceptQueries` and `useConceptGeneration`
- [x] Ensure `ErrorMessage`/`RateLimitErrorMessage` components are used universally for displaying errors.
  - Standardized error display through the error handling utilities

### Phase 4: Event Service Refinement
- [x] Review current uses of `eventService` for state synchronization.
  - Identified redundant event subscriptions in `ConceptContext`
- [x] Replace event-driven refreshing with `queryClient.invalidateQueries` where suitable.
  - Removed event listeners from `ConceptContext` 
  - Implemented direct cache invalidation in data mutation operations
- [x] Retain `eventService` only for necessary decoupling scenarios.
  - Eliminated unnecessary event-based refreshing
  - More direct and traceable data flow using React Query's cache invalidation

## Client-Side State & Data Synchronization Enhancement (@design/fixing_SRA.md)

### Step 1: React Query Configuration
- [x] Adjust React Query defaults in `src/main.tsx`
  - Set `refetchOnWindowFocus: true` (or use default `true`)
  - Reduced staleTime from 5 minutes to 10 seconds for faster data refresh
  - Test navigation scenarios to verify improvements

### Step 2: Diagnose PageTransition Component
- [x] Temporarily bypass `PageTransition` component in `src/App.tsx` for testing
  - Commented out the PageTransition wrapper to test without transitions
  - Kept Suspense for lazy-loaded components

### Step 3: Authentication & Loading State Handling
- [x] Add detailed logging to authentication processes
  - [x] Log auth state changes in `apiClient.ts` -> `getAuthHeaders`
  - [x] Log session checks and refresh attempts in `AuthContext.tsx`
- [x] Review components using data dependent on `userId`
  - [x] Ensure they handle loading states from both `useAuth()` and the query

### Step 4: Data Refetching on Navigation
- [x] Identify key pages that must show latest data upon navigation
  - [x] Add explicit `refetch` calls in `useEffect` hooks on critical pages
  - [x] Created custom `useFreshConceptDetail` and `useFreshRecentConcepts` hooks that force staleTime:0
  - [x] Added React Query Devtools for better visibility of cache state
  - Critical pages identified: ConceptDetailPage, ConceptList (Recent Concepts)

### Step 5: Verify Query Invalidation
- [x] Review mutation hooks in `useConceptMutations.ts`
  - [x] Add consistent userId to query keys for proper cache identity
  - [x] Add detailed logging of invalidation process
  - [x] Test actions and navigation to verify data updates correctly

### Step 6: Standardize Error Handling
- [x] Audit all `try...catch` blocks in data fetching code
  - [x] Enhance errorUtils.ts with better logging for debugging
  - [x] Add context information to error logging
  - [x] Add specific detection for auth-related errors

### Step 7: Enhanced Debugging (Additional)
- [x] Add React Query DevTools for better cache debugging
- [x] Enhanced logging in data fetching hooks
  - Added detailed timestamp and query key information
  - Added cache hit/miss logging
  - Added timing information to track performance

# Frontend State Management Refactor - TODO

## Phase 1: Core React Query Integration (1-2 Sprints)

-   [x] Refactor `useRateLimits` to `useRateLimitsQuery` using `useQuery`.
-   [x] Integrate `useRateLimitsQuery` into `RateLimitProvider`.
-   [x] Refactor `useConceptGeneration` to `useGenerateConceptMutation` using `useMutation`.
-   [x] Refactor `useConceptRefinement` to `useRefineConceptMutation` using `useMutation`.
-   [x] Update components (`LandingPage`, `RefinementPage`, etc.) to use refactored React Query hooks.
-   [x] Implement query invalidation in mutation `onSuccess` callbacks.
-   [x] Establish standard React Query query keys (e.g., `['concepts', 'recent', userId]`).

## Phase 2: Context & Optimistic Update Refinement (1 Sprint)

-   [x] Refactor `RateLimitContext` to provide `decrementLimit` function that uses `queryClient.setQueryData`.
-   [x] Implement optimistic updates for rate limits in UI components.
-   [x] Simplify or remove `ConceptContext`, relying more on direct query hook usage.
-   [x] Update components currently using `ConceptContext` to use direct query hooks/selectors.
-   [x] Replace `eventService` refresh triggers with `queryClient.invalidateQueries`.

## Phase 3: API Hook & Error Handling Cleanup (1 Sprint)

-   [x] Update `RateLimitsPanel` component to use React Query directly instead of context.
-   [x] Update `ConceptList` component to use React Query directly instead of context.
-   [x] Update `LandingPage` component to use React Query directly instead of context.
-   [x] Fix TypeScript errors in hook return types with proper typing for React Query.
-   [x] Fix TypeScript errors in remaining components refactored to use React Query directly.
-   [x] Add `useSvgConversionMutation` hook for SVG conversion operations.
-   [x] Update `ExportOptions` component to use React Query mutation for SVG conversion.
-   [x] Remove `ConceptProvider` from `App.tsx` after all components are migrated to React Query.
-   [x] Simplify or remove the generic `useApi` hook, relying on `apiClient` within query/mutation functions.
-   [x] Ensure consistent error handling using `createQueryErrorHandler` in all `useQuery`/`useMutation` instances.
-   [x] Audit `ErrorMessage`/`RateLimitErrorMessage` components for proper handling of categorized errors.
-   [x] Remove manual loading/error state management from components where React Query now handles it.
-   [x] Update tests that mock `useConceptContext` to mock the React Query hooks instead.
-   [x] Update documentation in `frontend_state_refactor_progress.md` to reflect all changes.

## Components Still Using ConceptContext

- [x] **RefinementPage**: Confirmed not using `ConceptContext`, already using direct hooks.
- [x] **RefinementSelectionPage**: Confirmed not using `ConceptContext`, already migrated.
- [x] **RateLimitsPanel**: Confirmed using React Query directly via `useRateLimitsQuery`.
- [x] **RecentConceptsPage**: Using `useRecentConcepts` directly instead of context.
- [x] **ConceptDetailPage**: Using `useConceptDetail` directly instead of context.
- [x] **Fix TypeScript errors**: 
    - [x] `LandingPage.tsx`: Fixed typing issues with `recentConcepts`.
    - [x] `ConceptList.tsx`: Fixed typing issues with `recentConcepts`.

## Final Steps for ConceptContext Removal

-   [x] Identify any remaining components using `ConceptContext` and update them to use React Query directly.
-   [x] Remove `ConceptContext` and `ConceptProvider` entirely from the codebase.
-   [x] Verify application functions correctly with React Query replacing all context-based state management.


---