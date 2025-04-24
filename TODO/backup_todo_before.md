# Concept Visualizer - Project TODO

Backend

- [] **Prevent Concurrent Tasks:**
  - [ ] **Backend:** Modify `POST /concepts/generate-with-palettes` and `POST /concepts/refine` route handlers in `backend/app/api/routes/concept/` to query for existing 'pending' or 'processing' tasks for the user before creating a new one.
  - [ ] **Backend:** Return an appropriate response (e.g., HTTP 200/202 with existing task details or HTTP 409 Conflict) if an active task is found.

Frontend

- [ ] **Prevent Concurrent Task UI:**
  - [ ] In `ConceptForm.tsx` and `RefinementForm.tsx`, disable the submit button if the global task state indicates a task is already `pending` or `processing`.
  - [ ] Display a message like "A generation/refinement is already in progress..." near the disabled button.

---

## **_EXISTING TASKS CONTINUE BELOW_**

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
- [ ] Test concurrent task prevention logic
- [ ] Test stuck task cleanup logic

### 2. Frontend Testing

- [ ] Update tests for components after context removal
- [ ] Add tests for consolidated components
- [ ] Test React Query integration
- [ ] Verify error handling UI components
- [ ] Add tests for task polling hook (`useTaskPolling`)
- [ ] Add tests for the global task status bar component
- [ ] Test UI state when a task is already in progress (disabled buttons, messages)

## Implementation Plan

- [ ] Review and approve this design plan
- [ ] Break down plan into smaller tasks
- [ ] Prioritize implementation order
- [ ] Create development branches for each major change
- [ ] Implement changes incrementally with testing
- [ ] Conduct code reviews for all changes

---

**I. Refine Backend Error Types**

- **Goal:** More specific error handling in the service layer.

- **Steps:**

  1.  **Define Specific Exceptions (`backend/app/core/exceptions.py`):**

      - Open the file.
      - Define new classes inheriting from `ApplicationError`. Examples:

        ```python
        class ConceptGenerationError(ApplicationError):
            """Error during the concept generation process."""
            def __init__(self, message: str = "Concept generation failed", details: Optional[Dict[str, Any]] = None):
                super().__init__(message, details)

        class DatabaseTransactionError(DatabaseError):
            """Error during a multi-step database operation."""
            def __init__(self, message: str = "Database transaction failed", details: Optional[Dict[str, Any]] = None):
                super().__init__(message, operation="transaction", details=details)

        class RateLimitRuleError(ApplicationError):
            """Error related to rate limit configuration or application."""
            def __init__(self, message: str = "Rate limit rule error", details: Optional[Dict[str, Any]] = None):
                super().__init__(message, details)

        class ExternalServiceError(ApplicationError):
            """Error communicating with an external service like JigsawStack."""
            def __init__(self, service_name: str, message: str = "External service error", details: Optional[Dict[str, Any]] = None):
                details = details or {}
                details["service_name"] = service_name
                super().__init__(message, details)

        class StorageOperationError(StorageError):
             """Specific error during a storage operation."""
             def __init__(self, message: str = "Storage operation failed", operation: Optional[str] = None, bucket: Optional[str] = None, path: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
                 super().__init__(message, operation, bucket, path, details)
        ```

      - Add others as needed based on specific failure points you identify.

  2.  **Catch and Wrap Errors in Services (`backend/app/services/`):**

      - Go through service files (e.g., `image/service.py`, `storage/concept_storage.py`, `jigsawstack/client.py`, `task/service.py`).
      - Identify `try...except` blocks that handle external calls (e.g., `httpx` requests, `supabase` client calls, `redis` calls).
      - Modify the `except` blocks:

        - Catch _specific_ external exceptions (e.g., `httpx.HTTPStatusError`, `httpx.RequestError`, `postgrest.exceptions.APIError`, `redis.RedisError`, `StorageException` from supabase-py if applicable).
        - Inside the `except`, `raise` the corresponding _specific_ custom exception defined in step 1. Pass relevant context (operation details, original error message, masked IDs/paths) into the `details` dictionary.
        - Example in `JigsawStackClient`:
          ```python
          except httpx.RequestError as e:
              logger.error(f"Connection error to JigsawStack: {e}")
              raise ExternalServiceError(service_name="JigsawStack", message=f"Connection error: {e}", details={"endpoint": endpoint})
          except httpx.HTTPStatusError as e:
               logger.error(f"JigsawStack API error {e.response.status_code}")
               # Map to specific JigsawStack errors or a general ExternalServiceError
               if e.response.status_code in (401, 403):
                    raise JigsawStackAuthenticationError(...) # Keep existing specific errors
               else:
                    raise ExternalServiceError(service_name="JigsawStack", message=f"API error: {e.response.status_code}", details={"endpoint": endpoint, "response": str(e.response.text[:100])})
          ```
        - Example in `ConceptStorageService`:

          ```python
           except PostgrestAPIError as e:
                logger.error(f"Supabase DB error storing concept: {e}")
                raise DatabaseError(message=f"Database error: {e}", operation="insert", table="concepts", details={"error_code": e.code})
           except Exception as e:
                # Catch broader storage/client errors if specific ones aren't available
                logger.error(f"Unexpected error storing concept: {e}")
                raise StorageOperationError(message=f"Storage error: {e}", operation="insert", bucket="concepts")

          ```

  3.  **Update API Error Handlers (`backend/app/api/errors.py`):**
      - Open the `application_error_handler` function.
      - Add `elif isinstance(exc, NewSpecificError):` blocks for each new specific exception type created in step 1.
      - Map each new exception to an appropriate HTTP status code (e.g., `DatabaseTransactionError` -> 500, `ConceptGenerationError` -> 503, `StorageOperationError` -> 503, `RateLimitRuleError` -> 500) and a distinct `error_code` string (e.g., `"DB_TRANSACTION_FAILED"`, `"CONCEPT_GEN_FAILED"`).
      - Ensure the logging within the handler captures the specific exception type (`exc.__class__.__name__`) and any relevant details from `exc.details`.

---

**II. Transaction Management**

- **Goal:** Ensure atomicity for multi-step DB/Storage operations.
- **Target:** `ConceptStorageService.store_concept` (handles concept + variations).

- **Steps:**
  1.  **Analyze `store_concept`:** Open `backend/app/services/storage/concept_storage.py` and `backend/app/core/supabase/concept_storage.py`. Review the `store_concept` and `store_color_variations` methods. Note the sequence: `store_concept` inserts into `concepts`, then `store_color_variations` inserts into `color_variations`.
  2.  **Implement Cleanup Logic:** Modify the service layer `store_concept` in `concept_storage.py`:
      - Wrap the calls to `self.concept_storage.store_concept` and `self.concept_storage.store_color_variations` in a `try...except` block within the service method.
      - Store the `concept_id` returned by `self.concept_storage.store_concept`.
      - In the `except` block specifically catching errors during `store_color_variations`:
        - Log the failure clearly.
        - Attempt to delete the concept that was just created using the stored `concept_id`. Add a new method `delete_concept_by_id` to `ConceptStorage` if needed.
        - Use a `try...except` around the deletion attempt and log whether cleanup was successful or failed.
        - Reraise a `DatabaseTransactionError` or `StorageError` indicating the partial failure and failed/successful cleanup.
      - If the initial `store_concept` call fails, just let the exception propagate (no cleanup needed).
  3.  **Logging:** Ensure all steps, failures, and cleanup attempts are logged with masked IDs.

---

**III. Background Task Robustness**

- **Goal:** Make background tasks more resilient.

- **Steps:**

  1.  **Detailed Error Logging (`backend/app/api/routes/concept/generation.py`, `refinement.py`):**

      - Locate the main `except Exception as e:` block in `generate_concept_background_task` and `refine_concept_background_task`.
      - Inside the `except` block, determine _which_ service call failed (e.g., `image_service.generate_and_store_image`, `concept_service.generate_color_palettes`, `storage_service.store_concept`).
      - Construct a more detailed `error_message` string including the failed step and the specific error from `e`. Example: `f"Failed at step 'generate_color_palettes': {str(e)}"`
      - Update the call to `task_service.update_task_status` to pass this detailed `error_message`.
      - _Optional:_ If useful for debugging, add specific details (like masked IDs or prompt snippets) to the task's `metadata` field during the error update (requires modifying `update_task_status` to accept metadata updates on failure).

  2.  **Retry Mechanism (Optional - `tenacity`):**

      - **Install:** `uv pip install tenacity` (add to `pyproject.toml` optional deps if preferred).
      - **Import:** `from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type` in the route files (`generation.py`, `refinement.py`).
      - **Identify Targets:** Calls prone to transient errors within the background tasks (e.g., `image_service.generate_and_store_image`, `concept_service.generate_color_palettes`, potentially `storage_service.store_concept`).
      - **Apply Decorator:** Wrap the _calls_ to these functions (or define small helper async functions to wrap the calls if needed) using the `@retry` decorator.

        ```python
        from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
        import httpx # Assuming httpx exceptions are relevant

        @retry(
            stop=stop_after_attempt(3), # Retry 3 times
            wait=wait_exponential(multiplier=1, min=2, max=10), # Wait 2s, 4s, 8s,... up to 10s
            retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError, ExternalServiceError)), # Retry on specific errors
            before_sleep=lambda retry_state: logger.warning(f"Retrying {retry_state.fn.__name__} due to {retry_state.outcome.exception()}, attempt {retry_state.attempt_number}")
        )
        async def attempt_generate_image(*args, **kwargs):
             # Make the actual call inside this helper
             return await image_service.generate_and_store_image(*args, **kwargs)

        # In the background task:
        # Replace: image_path, image_url = await image_service.generate_and_store_image(...)
        # With:    image_path, image_url = await attempt_generate_image(...)
        ```

      - **Adjust:** Configure `stop`, `wait`, and `retry` conditions based on the specific external service behavior.

  3.  **Stuck/Failed Task Cleanup (`backend/supabase/functions/cleanup-old-data/index.ts`):**
      - Open the Edge Function code.
      - **Query Failed Tasks:** Add a query similar to `cleanupStuckTasks` but filtering for `status = 'failed'` and `updated_at < NOW() - INTERVAL '7 days'` (or your desired retention period for failed tasks).
      - **Identify Resources:** For each failed task retrieved, attempt to extract relevant resource identifiers from its `metadata` or `result_id` (e.g., `concept_id`, `image_path`). _This requires that the background tasks store useful identifiers in metadata upon failure._
      - **Attempt Deletion:** If identifiers are found, call appropriate Supabase Storage `remove` functions (like `deleteFromStorage`) to delete associated files (concept images, palette images).
      - **Delete Task Record:** After attempting resource cleanup (regardless of success), delete the old 'failed' task record itself from the `tasks` table.
      - **Logging:** Log which tasks are being processed for cleanup, which resources are identified, and the success/failure of deletion attempts.

---

**IV. Configuration Validation**

- **Goal:** Fail fast on missing critical configuration.

- **Steps:**
  1.  **Enhance `validate_required_settings` (`backend/app/core/config.py`):**
      - Open the `Settings` class.
      - Add `if not self.VARIABLE_NAME:` checks for essential variables like:
        - `SUPABASE_JWT_SECRET`
        - `SUPABASE_SERVICE_ROLE` (crucial if service role calls are used)
        - `STORAGE_BUCKET_CONCEPT`
        - `STORAGE_BUCKET_PALETTE`
      - Conditionally check Redis variables if rate limiting is enabled:
        ```python
        if self.RATE_LIMITING_ENABLED:
            if not self.UPSTASH_REDIS_ENDPOINT:
                raise EnvironmentVariableError(...)
            if not self.UPSTASH_REDIS_PASSWORD:
                raise EnvironmentVariableError(...)
        ```
      - Ensure each check raises `EnvironmentVariableError` with the correct `variable_name`.

---

**V. Frontend Global Error Handling Integration**

- **Goal:** Centralize UI error handling.

- **Steps:**

  1.  **Integrate `useErrorHandling` Hook:**

      - Open `frontend/my-app/src/App.tsx`.
      - Import `useErrorHandling` and the `ErrorMessage` component.
      - Call the hook near the top of the `App` component: `const errorHandler = useErrorHandling();`.
      - Render the `ErrorMessage` component conditionally based on `errorHandler.hasError` somewhere visible in the layout (e.g., fixed banner at the top/bottom, _outside_ the main `Router`/`Outlet` area if it should persist across navigation).
        ```tsx
        // Inside App component return:
        {
          errorHandler.hasError && errorHandler.error && (
            <div
              style={{
                position: "fixed",
                top: "80px",
                left: "50%",
                transform: "translateX(-50%)",
                zIndex: 1000,
                width: "90%",
                maxWidth: "600px",
              }}
            >
              <ErrorMessage
                message={errorHandler.error.message}
                details={errorHandler.error.details}
                type={errorHandler.error.category as ErrorType} // Cast might be needed
                onDismiss={errorHandler.clearError}
              />
            </div>
          );
        }
        {
          /* Rest of the app structure */
        }
        ```
      - _Alternatively:_ If using the `ErrorBoundary` component from `ui`, wrap `AppRoutes` with it and pass `onError={errorHandler.handleError}`.

  2.  **Review Error Propagation:**
      - Examine custom hooks making API calls (e.g., `useConceptMutations`, `useConceptQueries`). Ensure they _re-throw_ errors after logging or initial handling if they aren't meant to be fully handled locally.
      - Check `apiClient.ts` interceptors. The current logic seems to re-throw most unhandled errors, which is good. Ensure the `auth-error-needs-logout` event path doesn't prevent errors from reaching the global handler if needed elsewhere.
      - Remove `try...catch` blocks in components that simply log and swallow errors; let them bubble up.

---

**VI. Frontend User Feedback for Errors**

- **Goal:** Provide clear, actionable error feedback.

- **Steps:**

  1.  **Enhance `ErrorMessage` Component (`components/ui/ErrorMessage.tsx`):**

      - Add props to accept `error_code?: string` (passed via `details` object potentially).
      - Inside the component, add conditional rendering:
        ```tsx
        {
          error_code && (
            <span className="text-xs opacity-70 mr-2">Code: {error_code}</span>
          );
        }
        {
          /* ... */
        }
        {
          category === "network" && (
            <p className="text-xs mt-1">
              Please check your internet connection.
            </p>
          );
        }
        {
          category === "validation" && (
            <p className="text-xs mt-1">Please review the form fields.</p>
          );
        }
        ```
      - Modify the `props` interface and update calls to `ErrorMessage` where category/code info is available (e.g., from `useErrorHandling` state).

  2.  **Inline Rate Limit Handling:**

      - Open mutation hooks (`useConceptMutations`, `useExportImageMutation`).
      - In the `onError` callback:
        - Check `if (error instanceof RateLimitError)`.
        - If true, set a specific state variable in the hook's return value (e.g., `isRateLimited: true`, `rateLimitDetails: { message: error.getUserFriendlyMessage() }`).
        - Trigger a rate limit refresh: `queryClient.invalidateQueries({ queryKey: ['rateLimits'] });`.
      - In components using these hooks (e.g., `ConceptFormSection`, `ExportOptions`):
        - Access the new rate limit state from the hook.
        - Conditionally render an inline error message near the submit button using the `rateLimitDetails.message`.
        - Consider disabling the button based on `isRateLimited`.
      - Update `RateLimitsPanel` to potentially show a more prominent warning if a specific limit is hit (requires passing error state or using context).

  3.  **Actionable Task Failure Feedback (`components/TaskStatusBar.tsx`):**
      - Modify the `failed` status rendering block.
      - Display `activeTaskData.error_message` more clearly.
      - Add a "Retry" button conditionally. Determine retry possibility:
        - Check if the `error_message` indicates a transient issue (e.g., "Network Error", "API unavailable").
        - _Requires backend enhancement:_ The backend task could set a `retryable: true` flag in metadata upon failure.
      - The "Retry" button's `onClick` should:
        - Call `clearActiveTask()` from `useTaskContext`.
        - Trigger the _original_ mutation that created the task (this might require passing the mutation function down or using a different state management approach like Zustand/Redux if context becomes too complex).

---

**VII. Frontend Network Status Integration**

- **Goal:** Improve UI responsiveness to network state.

- **Steps:**

  1.  **Integrate `useNetworkStatus` in Hooks:**

      - Open hooks making API calls (e.g., `useConceptQueries.ts`, `useConceptMutations.ts`, `useTaskPolling.ts`).
      - Import and call `useNetworkStatus`: `const networkStatus = useNetworkStatus();`.
      - **Mutations:** Inside the main mutation function (`generateConceptMutation`, `refineConceptMutation`, etc.), add an early check:
        ```typescript
        if (!networkStatus.isOnline) {
          errorHandler.setError(
            "You are offline. Cannot perform this action.",
            "network",
          );
          // Optionally throw an error to stop the mutation
          throw new Error("Offline");
          // Or return early if the mutation hook handles this state
        }
        ```
      - **Queries (`useQuery`):** Modify the `enabled` option:
        ```typescript
        enabled: !!userId && networkStatus.isOnline, // Only enable fetching if online
        ```
        Consider adding `refetchOnReconnect: true` to automatically refetch when coming back online.
      - **Polling (`useTaskPolling`):** Modify the `enabled` check:
        ```typescript
        const shouldPoll = Boolean(
          enabled && taskId && !cachedTask && networkStatus.isOnline,
        );
        ```

  2.  **Review `OfflineStatus` Banner (`components/ui/OfflineStatus.tsx`):**
      - Visually inspect the banner on different screen sizes and pages.
      - Ensure the `position` prop (`top` or `bottom`) doesn't obstruct critical UI elements like the header or action buttons. Adjust `z-index` if necessary.
      - Test the "Retry" button functionality. Ensure `isAnimating` state works correctly.
      - Verify the messages (`offlineMessage`, `slowConnectionMessage`) are clear.

---

**VIII. Constants and Configuration Management**

- **Goal:** Reduce magic strings, centralize config.

- **Steps:**

  1.  **Backend Constants (`backend/app/core/constants.py`):**

      - Create the file `backend/app/core/constants.py`.
      - Define constants:

        ```python
        # Task Statuses
        TASK_STATUS_PENDING = "pending"
        TASK_STATUS_PROCESSING = "processing"
        # ... etc.

        # Task Types
        TASK_TYPE_GENERATION = "concept_generation"
        TASK_TYPE_REFINEMENT = "concept_refinement"
        # ... etc.

        # Bucket Names (Reference settings but provide constant names)
        from .config import settings
        BUCKET_NAME_CONCEPTS = settings.STORAGE_BUCKET_CONCEPT
        BUCKET_NAME_PALETTES = settings.STORAGE_BUCKET_PALETTE

        # Rate Limit Keys/Strings
        RATE_LIMIT_ENDPOINT_GENERATE = "/concepts/generate-with-palettes" # Use the actual endpoint used by limiter
        RATE_LIMIT_STRING_GENERATE = "10/month"
        # ... etc. for refine, store, export
        ```

      - **Refactor:** Go through backend code (`services/`, `api/routes/`, `core/limiter/`) and replace hardcoded strings (like `"pending"`, `"concept_generation"`, bucket names, rate limit strings/endpoints) with imports from `app.core.constants`.

  2.  **Frontend Constants:**
      - **API Endpoints (`frontend/my-app/src/config/apiEndpoints.ts`):**
        - Create the file.
        - Define endpoint constants:
          ```typescript
          export const API_ENDPOINTS = {
            GENERATE_CONCEPT: "/concepts/generate-with-palettes",
            REFINE_CONCEPT: "/concepts/refine",
            TASK_STATUS: (taskId: string) => `/tasks/${taskId}`,
            EXPORT_IMAGE: "/export/process",
            RECENT_CONCEPTS: "/storage/recent", // Check actual path
            CONCEPT_DETAIL: (id: string) => `/storage/concept/${id}`, // Check actual path
            RATE_LIMITS: "/health/rate-limits-status",
          };
          ```
        - **Refactor:** Update `apiClient.ts`, mutation hooks (`useConceptMutations`, `useExportImageMutation`), query hooks (`useConceptQueries`), `task.ts`, and `rateLimitService.ts` to use these constants instead of hardcoded strings.
      - **Query Keys (`frontend/my-app/src/config/queryKeys.ts`):**
        - Create the file.
        - Define query key factories:
          ```typescript
          export const queryKeys = {
            concepts: {
              all: () => ["concepts"] as const,
              recent: (userId?: string, limit?: number) =>
                [...queryKeys.concepts.all(), "recent", userId, limit] as const,
              detail: (id?: string, userId?: string) =>
                [...queryKeys.concepts.all(), "detail", id, userId] as const,
            },
            tasks: {
              all: () => ["tasks"] as const,
              detail: (id?: string) =>
                [...queryKeys.tasks.all(), "detail", id] as const,
            },
            rateLimits: () => ["rateLimits"] as const,
          };
          ```
        - **Refactor:** Update all `useQuery`, `useMutation`, `queryClient.invalidateQueries`, `queryClient.setQueryData` calls throughout the hooks (`useConceptQueries`, `useTaskPolling`, `useRateLimitsQuery`, etc.) to use these key factories. Example: `queryKey: queryKeys.concepts.recent(userId, limit)`.

---
