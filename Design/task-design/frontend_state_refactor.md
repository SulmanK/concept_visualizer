# Frontend State Management Refactor Design Document

## Current Context

- **Existing System:** The frontend uses a mix of state management strategies: React Context API (`AuthContext`, `ConceptContext`, `RateLimitContext` with `use-context-selector`), local component state (`useState`), custom hooks managing API state (`useApi`, `useConceptGeneration`, `useConceptRefinement`, `useRateLimits`), TanStack React Query (`useConceptQueries`), and a simple event service (`eventService`).
- **Key Components:**
  - Context Providers (`AuthProvider`, `ConceptProvider`, `RateLimitProvider`)
  - API hooks (`useApi`, `useConceptGeneration`, etc.)
  - React Query hooks (`useRecentConcepts`, `useConceptDetail`)
  - UI components consuming state from contexts or hooks.
  - `apiClient` for making requests.
  - `eventService` for cross-component communication/refresh triggers.
- **Pain Points/Gaps:**
  - **Inconsistent Server State Management:** Some server data is managed via React Query, while other data (generation results, rate limits) is managed manually within custom hooks using `useState` and `useEffect`. This leads to duplicated logic for loading/error states and difficulty managing caching/refetching consistently.
  - **Context Complexity:** `ConceptContext` potentially duplicates state managed by React Query, increasing complexity and potential for unnecessary re-renders, even with `use-context-selector`.
  - **Optimistic Update Implementation:** While `useRateLimits` has an optimistic update mechanism (`decrementLimit`), it's manually managed and not tied into a central caching layer like React Query.
  - **Event-Driven Data Flow:** Using `eventService` to trigger data refreshes (e.g., after concept creation) obscures the direct relationship between actions and data updates.
  - **Manual API State in Hooks:** Custom hooks like `useApi`, `useConceptGeneration`, etc., manually manage `loading`, `error`, and `result` states, which is boilerplate code already handled well by libraries like React Query.

## Requirements

### Functional Requirements

1.  **Centralized Server State:** All data fetched from or sent to the backend API (concepts, rate limits, generation results) should be managed consistently.
2.  **API Call Status:** Provide clear and consistent loading, success, and error states for all API interactions.
3.  **Caching:** Implement intelligent caching for server data (concepts, rate limits) to reduce redundant API calls and improve perceived performance.
4.  **Background Updates:** Support background refetching of stale data (e.g., recent concepts, rate limits).
5.  **Optimistic Updates:** Support optimistic UI updates for actions like rate limit consumption.
6.  **Automatic UI Updates:** UI components should automatically re-render when relevant server data changes (e.g., concept list updates after generation).
7.  **Error Handling:** Provide categorized and user-friendly error feedback for API failures, including rate limit specifics.

### Non-Functional Requirements

1.  **Performance:** Minimize unnecessary component re-renders caused by state changes. Improve perceived performance through caching and background updates.
2.  **Maintainability:** Establish consistent patterns for data fetching, mutation, and state management across the application. Reduce boilerplate code.
3.  **Scalability:** The state management approach should easily accommodate new data types and API endpoints.
4.  **Testability:** State logic, especially around API interactions, should be easily testable in isolation.
5.  **Developer Experience:** Provide clear data flow, simplify state logic, and leverage library features effectively.

## Design Decisions

### 1. Primary Server State Management Tool

- **Decision:** Adopt **TanStack React Query (`@tanstack/react-query`)** as the primary tool for managing _all_ server state, including concepts, generation/refinement results, and rate limits.
- **Rationale:**
  - Provides built-in caching, background updates, stale-while-revalidate logic.
  - Simplifies handling of loading, error, and success states for data fetching and mutations.
  - Offers robust features like query invalidation, optimistic updates, and pagination/infinite scrolling support.
  - Reduces boilerplate code compared to manual state management with `useState`/`useEffect`.
  - Already partially used (`useConceptQueries`), allowing for consolidation onto a single pattern.
- **Trade-offs:** Requires refactoring existing custom hooks (`useConceptGeneration`, `useConceptRefinement`, `useRateLimits`, `useApi`). Team needs familiarity with React Query concepts.

### 2. Role of React Context API

- **Decision:** **Reduce the scope of Context API.** Use Context primarily for:
  1.  **Global, non-server state:** Authentication status (`AuthContext`), potentially UI theme or settings.
  2.  **Dependency Injection:** Providing stable instances of services or functions (like the `queryClient` or toast functions).
  3.  **Stable Derived State:** Providing heavily memoized, derived state if absolutely necessary, leveraging `use-context-selector`.
- **Rationale:**
  - Avoids duplicating server state already managed by React Query.
  - Improves performance by minimizing context-related re-renders.
  - Separates concerns: React Query for server state, Context for global UI/auth state.
- **Alternatives Considered:**
  - _Zustand/Jotai:_ Powerful but adds another state management library. React Query + minimal Context is likely sufficient.
  - _Redux:_ Generally overkill for this application's likely complexity.

### 3. Data Synchronization Strategy

- **Decision:** Primarily use **React Query's cache invalidation (`queryClient.invalidateQueries`)** for data synchronization after mutations.
- **Rationale:**
  - Creates a clear link between an action (mutation) and its effect on related data (query invalidation).
  - Leverages React Query's core mechanism for keeping data fresh.
  - Reduces the need for the custom `eventService` for simple data refresh scenarios.
- **Keep Event Service For:** Global UI notifications (like toasts triggered from non-React `apiClient`), or scenarios where direct coupling via invalidation is not feasible.

### 4. Refactoring Custom API Hooks

- **Decision:** Refactor existing custom API hooks:
  - `useConceptGeneration` and `useConceptRefinement` will be rewritten using `useMutation`.
  - `useRateLimits` will be rewritten using `useQuery`.
  - `useApi` will be simplified to a basic fetch utility focusing on auth headers and base URL, or potentially removed if components/hooks use React Query's `queryFn`/`mutationFn` directly with `apiClient`.
- **Rationale:**
  - Leverages the dedicated state management capabilities of `useQuery` and `useMutation`.
  - Removes manual `loading`, `error`, `status`, `result` state management from these hooks.
  - Integrates seamlessly with React Query's caching and invalidation system.

## Technical Design

### 1. Core Components (React Query Hooks)

```typescript
// src/hooks/useConceptMutations.ts (Example - could be split further)
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { GenerationResponse, PromptRequest, RefinementRequest } from '../types';
import { useAuth } from '../contexts/AuthContext'; // Assuming user ID needed for invalidation key

export function useGenerateConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth(); // Needed for invalidation key

  return useMutation<GenerationResponse, Error, PromptRequest>({
    mutationFn: (data) => apiClient.post<GenerationResponse>('/concepts/generate-with-palettes', data).then(res => res.data),
    onSuccess: (data) => {
      // Invalidate recent concepts list on success
      queryClient.invalidateQueries({ queryKey: ['concepts', 'recent', user?.id] });
      // Optionally pre-populate the detail view cache
      if (data?.id) {
         queryClient.setQueryData(['concepts', 'detail', data.id, user?.id], data);
      }
    },
    // Add onError for standardized error handling
  });
}

export function useRefineConceptMutation() {
  const queryClient = useQueryClient();
  const { user } = useAuth();

  return useMutation<GenerationResponse, Error, RefinementRequest>({
    mutationFn: (data) => apiClient.post<GenerationResponse>('/concepts/refine', data).then(res => res.data),
    onSuccess: (data, variables) => {
      // Invalidate specific concept detail and recent list
      queryClient.invalidateQueries({ queryKey: ['concepts', 'detail', variables.originalConceptId, user?.id] }); // Assuming originalConceptId is passed
      queryClient.invalidateQueries({ queryKey: ['concepts', 'recent', user?.id] });
    },
    // Add onError
  });
}

// src/hooks/useRateLimitsQuery.ts
import { useQuery } from '@tanstack/react-query';
import { fetchRateLimits, RateLimitsResponse } from '../services/rateLimitService';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';

export function useRateLimitsQuery(options: { enabled?: boolean } = {}) {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler, { showToast: false }); // Don't show toast for background refresh errors

  return useQuery<RateLimitsResponse, Error>({
    queryKey: ['rateLimits'],
    queryFn: () => fetchRateLimits(false), // Fetch uses internal caching logic
    enabled: options.enabled ?? true,
    staleTime: 1000 * 30, // Consider stale after 30 seconds
    refetchInterval: 1000 * 60, // Refetch every minute in the background
    refetchOnWindowFocus: true, // Refresh when window regains focus
    onError: onQueryError,
  });
}

// src/hooks/useOptimisticRateLimitUpdate.ts (Example utility or part of context)
import { useQueryClient } from '@tanstack/react-query';
import { RateLimitCategory, RateLimitsResponse } from '../services/rateLimitService';

export function useOptimisticRateLimitUpdate() {
  const queryClient = useQueryClient();

  const decrementLimit = (category: RateLimitCategory, amount = 1) => {
    queryClient.setQueryData<RateLimitsResponse>(['rateLimits'], (oldData) => {
      if (!oldData) return oldData;

      const categoryData = oldData.limits[category];
      if (!categoryData) return oldData;

      // Create a deep copy to avoid mutation
      const newData = JSON.parse(JSON.stringify(oldData)) as RateLimitsResponse;

      newData.limits[category] = {
        ...categoryData,
        remaining: Math.max(0, categoryData.remaining - amount),
      };
      return newData;
    });
  };

  return { decrementLimit };
}

2. Data Models

Existing types (ApiResponse, ApiError, GenerationResponse, ConceptData, etc.) will be maintained and used.

React Query's hook results (data, error, status) will become the primary way components access server state and status.

3. Integration Points

UI Components: Will primarily use the refactored hooks (useGenerateConceptMutation, useRateLimitsQuery, useRecentConcepts, etc.) to get data and trigger actions.

Contexts:

RateLimitContext: Will consume state from useRateLimitsQuery. Its value will provide memoized data slices and the decrementLimit function (which now interacts with queryClient).

ConceptContext: Will be simplified. It might only provide the refreshConcepts function (which calls queryClient.invalidateQueries). Components needing concept data will use useRecentConcepts or useConceptDetail directly.

API Client: apiClient will be used by React Query's queryFn and mutationFn. It will handle auth header injection and potentially basic error formatting, but not loading/error state management.

Optimistic Updates: Components initiating rate-limited actions will call the decrementLimit function (provided by RateLimitContext or useOptimisticRateLimitUpdate) before triggering the mutation. React Query's onError will handle reverting the optimistic update if the mutation fails.

Data Invalidation: Mutations (useGenerateConceptMutation, etc.) will call queryClient.invalidateQueries in their onSuccess callbacks to trigger refetches of relevant data (e.g., recent concepts list).

Implementation Plan

Phase 1: Core React Query Integration (1-2 Sprints)

Refactor useRateLimits to useRateLimitsQuery using useQuery.

Integrate useRateLimitsQuery into RateLimitProvider.

Refactor useConceptGeneration to useGenerateConceptMutation using useMutation.

Refactor useConceptRefinement to useRefineConceptMutation using useMutation.

Update components using these hooks (LandingPage, RefinementPage) to use the new mutation hooks.

Implement basic query invalidation in mutation onSuccess callbacks.

Establish standard React Query query keys.

Phase 2: Context & Optimistic Update Refinement (1 Sprint)

Refactor RateLimitContext to provide decrementLimit function that uses queryClient.setQueryData.

Implement optimistic updates in UI components calling rate-limited mutations.

Simplify ConceptContext – remove redundant state, focus on providing stable actions/selectors if still needed, or remove entirely.

Update components consuming ConceptContext to use direct query hooks or simplified context selectors.

Replace eventService-based refreshing with queryClient.invalidateQueries.

Phase 3: API Hook & Error Handling Cleanup (1 Sprint)

Refactor or remove the generic useApi hook. Decide if a simple apiClient wrapper is sufficient.

Ensure all useQuery and useMutation instances use the standardized onError handling (createQueryErrorHandler).

Audit error display components (ErrorMessage, RateLimitErrorMessage) to ensure they handle categorized errors effectively.

Remove redundant loading/error state management from components now handled by React Query.




Security Considerations

Ensure React Query cache does not inadvertently store sensitive user-specific data that shouldn't be persisted long-term (React Query cache is in memory).

Verify that query keys incorporating user IDs or other identifiers do not expose sensitive information if logged or used improperly.

Authentication token handling within apiClient remains critical and should be reviewed for security alongside this refactor.
```
