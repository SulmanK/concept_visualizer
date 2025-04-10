# Concept Visualizer - Project TODO

## Backend Refactoring

### 1. Background Tasks Implementation
- [x] Remove `backend/app/core/middleware/prioritization.py` and its registration in `backend/app/core/factory.py`
- [x] Modify API routes to use FastAPI's `BackgroundTasks`:
  - [x] Inject `BackgroundTasks` into relevant routes in `generation.py` and `refinement.py`
  - [x] Update `POST /concepts/generate-with-palettes` handler to use background tasks
  - [x] Update `POST /concepts/refine` handler to use background tasks
- [x] Create task logic in appropriate service modules or new `tasks` module

### 2. Service Layer Granularity
- [ ] Review and refine `ImageService` (`backend/app/services/image/service.py`)
- [ ] Ensure `ConceptService` components maintain single responsibilities
- [ ] Consider splitting JigsawStack interactions into a separate service if needed

### 3. Rate Limiting Application
- [ ] Refine `backend/app/utils/api_limits/endpoints.py` functions
- [ ] Replace direct calls to rate limiting functions in route handlers with:
  - [ ] Option A: Enhance `RateLimitHeadersMiddleware` or create new middleware
- [ ] Extract rate limit info storage logic into reusable dependency function

### 4. Supabase Client & Storage
- [ ] Refocus `backend/app/core/supabase/client.py` on client creation only
- [ ] Move `purge_all_data` to a dedicated admin service or script
- [ ] Add clear comments to `backend/app/core/supabase/image_storage.py` about API usage
- [ ] Review Supabase client library for potential SDK updates

### 5. DRY - Route Logic
- [ ] Extract duplicated logic for storing rate limit info in routes to a reusable function

### 6. URL Handling Consistency
- [ ] Ensure services that return concept/image data always include ready-to-use URLs
- [ ] Standardize URL generation using `ImageStorageService.get_signed_url`

### 7. Legacy Code Cleanup
- [ ] Review and remove:
  - [ ] `backend/app/api/routes/api.py`
  - [ ] `backend/app/models/concept.py`, `request.py`, `response.py`
  - [ ] `backend/app/services/concept_service.py`
  - [ ] `backend/app/services/image_processing.py`
  - [ ] `backend/app/services/image_service.py`
- [ ] Consolidate `backend/app/services/concept_storage_service.py` into `backend/app/services/storage/concept_storage.py`

## Frontend Refactoring

### 1. State Management
- [ ] Remove `frontend/my-app/src/contexts/ConceptContext.tsx`
- [ ] Update components importing `useConceptContext` to use React Query hooks directly
- [ ] Review React Query caching settings in `frontend/my-app/src/main.tsx`
- [ ] Evaluate necessity of `useFreshConceptDetail`'s forced refetch in `useConceptQueries.ts`

### 2. Component Consolidation
- [ ] Consolidate `ConceptCard` components from different features into a single reusable component
- [ ] Review UI components to ensure adherence to Single Responsibility Principle
- [ ] Review feature components to minimize direct cross-feature imports

### 3. URL Handling Consistency
- [ ] Simplify URL logic in `frontend/my-app/src/services/supabaseClient.ts`
- [ ] Update components to use ready-to-use URLs from backend
- [ ] Simplify or remove `extractStoragePathFromUrl` in `frontend/my-app/src/utils/url.ts` if no longer needed

### 4. Page Transitions
- [ ] Remove `PageTransition` component in `frontend/my-app/src/components/layout/PageTransition.tsx`
- [ ] Implement a performant packaged animation library for page transitions
- [ ] Update `frontend/my-app/src/App.tsx` for proper page transition handling

### 5. API Client & Fetch Interceptor
- [ ] Move fetch interceptor logic from `App.tsx` to `frontend/my-app/src/services/apiClient.ts`
- [ ] Consider switching to Axios with interceptors for more robust API client

### 6. Legacy Hooks Cleanup
- [ ] Remove and replace:
  - [ ] `frontend/my-app/src/hooks/useConceptGeneration.ts`
  - [ ] `frontend/my-app/src/hooks/useConceptRefinement.ts`
  - [ ] `frontend/my-app/src/hooks/useApi.ts`
- [ ] Update components to use React Query-based hooks

## Code Quality Improvements

### 1. Backend Logging Cleanup
- [ ] Review and clean up logger statements in:
  - [ ] API middleware files
  - [ ] API route handlers
  - [ ] Core configuration modules
  - [ ] Service implementations
  - [ ] Utility functions
- [ ] Keep essential error logs while removing/reducing debug-only logs

### 2. Frontend Console Logging Cleanup
- [ ] Review and clean up console.log statements in:
  - [ ] Context providers
  - [ ] Service implementations
  - [ ] React Query hooks
  - [ ] UI components
- [ ] Guard remaining console statements with environment checks

### 3. DRY Code Refactoring
- [ ] Create reusable components for common UI patterns:
  - [ ] Create `QueryResultHandler` component for loading/error/empty states
  - [ ] Update list and detail components to use the handler
- [ ] Refactor backend rate limit application logic
- [ ] Create helper methods for common Supabase operations
- [ ] Centralize JigsawStack API request handling
- [ ] Consolidate image upload/storage logic

### 4. UI Consistency
- [ ] Ensure consistent use of Tailwind CSS classes across the entire frontend
- [ ] Review and update all component styling to follow Tailwind best practices
- [ ] Create common utility classes for frequently used styling patterns

## Testing Strategy

### 1. Backend Testing
- [ ] Add unit tests for new background task functions
- [ ] Add integration tests for API routes with background tasks
- [ ] Enhance tests for refactored services
- [ ] Test error handling for background tasks

### 2. Frontend Testing
- [ ] Update tests for components after context removal
- [ ] Add tests for consolidated components
- [ ] Test React Query integration
- [ ] Verify error handling UI components



## Implementation Plan

- [ ] Review and approve this design plan
- [ ] Break down plan into smaller tasks
- [ ] Prioritize implementation order
- [ ] Create development branches for each major change
- [ ] Implement changes incrementally with testing
- [ ] Conduct code reviews for all changes


