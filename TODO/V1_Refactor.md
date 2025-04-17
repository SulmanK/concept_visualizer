# Concept Visualizer - Project TODO

## Backend Refactoring

### 1. Background Tasks Implementation
- [x] Remove `backend/app/core/middleware/prioritization.py` and its registration in `backend/app/core/factory.py`
- [x] Modify API routes to use FastAPI's `BackgroundTasks`:
  - [x] Inject `BackgroundTasks` into relevant routes in `generation.py` and `refinement.py`
  - [x] Update `POST /concepts/generate-with-palettes` handler to use background tasks
  - [x] Update `POST /concepts/refine` handler to use background tasks
- [x] Implement the task management system:
  - [x] Create a TaskService to handle task CRUD operations
  - [x] Update background task functions to use dedicated tasks table
  - [x] Add endpoints to retrieve task status
  - [x] Add support for error handling and state persistence
- [x] Update frontend to handle the asynchronous task workflow

## Frontend Task Workflow Integration

**Goal:** Update the frontend to handle the asynchronous task workflow introduced in the backend for concept generation and refinement.

### 1. API Client & Types
- [x] **Update API Types (`src/types/api.types.ts`)**:
  - [x] Define the `TaskResponse` interface matching the backend response model (id, status, type, result_id, error_message, etc.).
  - [x] Update the return types for API client functions related to generation/refinement to expect `TaskResponse` instead of `GenerationResponse`.
- [x] **Update API Client (`src/services/apiClient.ts`)**:
  - [x] Add new functions or update existing ones to call the task status endpoints (`/api/tasks/{task_id}`, `/api/tasks`).
  - [x] Ensure request/response handling is correct for task-related endpoints.

### 2. Hooks & State Management
- [x] **Update Mutation Hooks (`src/hooks/useConceptMutations.ts`)**:
  - [x] Modify `useGenerateConceptMutation`:
    - [x] Change the `mutationFn` to call the `/concepts/generate-with-palettes` endpoint.
    - [x] Update the expected return type to `TaskResponse`.
    - [x] Implement logic in `onSuccess` (or elsewhere) to handle the `TaskResponse` (e.g., store `task_id`, initiate polling).
  - [x] Modify `useRefineConceptMutation`:
    - [x] Change the `mutationFn` to call the `/concepts/refine` endpoint (which now returns a TaskResponse).
    - [x] Update the expected return type to `TaskResponse`.
    - [x] Implement logic in `onSuccess` to handle the `TaskResponse`.
- [x] **Create Task Polling Hook (`src/hooks/useTaskPolling.ts` - New Hook)**:
  - [x] Create a new hook responsible for polling the `/api/tasks/{task_id}` endpoint.
  - [x] Input: `task_id` and polling interval.
  - [x] Output: Current task status (`pending`, `processing`, `completed`, `failed`), result data (`result_id`, `error_message`).
  - [x] Implement logic to stop polling when task reaches a terminal state (`completed`, `failed`).
  - [x] Handle potential errors during polling.

### 3. Component Updates
- [x] **Landing Page (`src/features/landing/LandingPage.tsx`)**:
  - [x] Modify `handleGenerateConcept` (or the mutation trigger) to handle the `TaskResponse`.
  - [x] Store the returned `task_id`.
  - [x] Display a "Processing" or similar state while the task is `pending` or `processing` (use the new polling hook).
  - [x] When the task status is `completed`, use the `result_id` to fetch the final `GenerationResponse` (perhaps using `useConceptDetail` or a dedicated fetch).
  - [x] Update `ResultsSection` to potentially display processing state before showing the final result.
  - [x] Handle task `failed` status by displaying an appropriate error message.
- [x] **Refinement Page (`src/features/refinement/RefinementPage.tsx`)**:
  - [x] Modify `handleRefineConcept` (or the mutation trigger) to handle the `TaskResponse`.
  - [x] Store the returned `task_id`.
  - [x] Display a "Processing" state while the task runs.
  - [x] Fetch the refined concept details using the `result_id` upon task completion.
  - [x] Update `ComparisonView` or surrounding logic to show the refined concept only after the task is `completed`.
  - [x] Handle task `failed` status.
- [x] **Concept Forms (`ConceptForm.tsx`, `ConceptRefinementForm.tsx`)**:
  - [x] Update UI feedback during submission to indicate task queuing/processing rather than immediate result generation.
  - [x] Potentially disable form fields while a task is actively processing.
- [x] **Loading/Progress Indicators (`LoadingIndicator.tsx`, etc.)**:
  - [x] Use loading indicators to show task processing status clearly in relevant UI sections.
- [x] **Error Display (`ErrorMessage.tsx`)**:
  - [x] Ensure error messages from failed tasks (`error_message` field) can be displayed effectively.

### 4. Cache Management (React Query)
- [x] Review query invalidation logic in mutation hooks (`useConceptMutations.ts`):
  - [x] Invalidate relevant queries (e.g., `recentConcepts`, `conceptDetail`) only *after* a task successfully completes and the final result is available/fetched.
  - [x] Consider adding query invalidation for task lists if a task details page is added.

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


