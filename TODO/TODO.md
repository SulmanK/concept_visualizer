# Concept Visualizer - Project TODO

## Production-Ready Rate Limit Enhancements (@design/rate_limit_production_enhancements.md)

- [x] Refactor `rateLimitService.ts`: Implement central caching based on headers and reset timestamps. Expose functions to get cached data.
- [x] Refactor `useRateLimits.ts`: Remove internal cache, consume data from `rateLimitService`, trigger status endpoint calls only when necessary.
- [x] Update `RateLimitContext.tsx`: Add `decrementLimit` function and integrate it with the service cache for optimistic updates.
- [x] Update `apiClient.ts` / Fetch Interceptor: Implement 429 error handling, specific error reporting (using toasts), and header extraction on 429s.
- [ ] Update UI Components:
    - [x] Call `decrementLimit` before relevant actions (e.g., Generate, SVG Export).
    - [x] Add proactive warnings (e.g., low remaining count) in `RateLimitsPanel`.
    - [ ] ~~Add visual indicators (e.g., bars/gauges) to `RateLimitsPanel`.~~ (Skipped)
    - [x] Ensure UI handles specific rate limit error toasts gracefully.
    - [x] Add cooldown to `RateLimitsPanel` refresh button.

## Frontend State Management Refactor (@design/frontend_state_management_refactor.md)

### Phase 1: Context Optimization
- [ ] Implement selectors or optimize `useRateLimitContext` hook.
- [ ] Implement selectors or optimize `useConceptContext` hook.
- [ ] Review and ensure memoization in `RateLimitProvider` and `ConceptProvider`.
- [ ] Profile and verify performance improvements using React DevTools.

### Phase 2: React Query Simplification
- [ ] Refactor `ConceptContext` to rely directly on React Query state (remove redundant loading/error state).
- [ ] Expose `refetch` and other necessary functions directly from React Query via context.

### Phase 3: Error Handling Standardization
- [ ] Audit async operations (`apiClient`, `useConceptQueries`, `AuthContext`) for error handling consistency.
- [ ] Integrate `useErrorHandling` hook consistently across audited operations.
- [ ] Ensure `ErrorMessage`/`RateLimitErrorMessage` components are used universally for displaying errors.

### Phase 4: Event Service Refinement
- [ ] Review current uses of `eventService` for state synchronization.
- [ ] Replace event-driven refreshing with `queryClient.invalidateQueries` where suitable.
- [ ] Retain `eventService` only for necessary decoupling scenarios.

