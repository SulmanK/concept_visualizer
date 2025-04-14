


Okay, let's break down your existing TODO list into more granular, step-by-step plans.

---

**1. Prevent Concurrent Tasks (Backend)** [x] - Completed and merged in PR #1

*   **Goal:** Ensure a user cannot start a new generation or refinement task if one is already running.
*   **Target Files:**
    *   `backend/app/api/routes/concept/generation.py` (for `generate_concept_with_palettes`)
    *   `backend/app/api/routes/concept/refinement.py` (for `refine_concept`)
    *   `backend/app/services/task/service.py` (to use `get_tasks_by_user`)

*   **Steps:**
    1.  **Modify `generate_concept_with_palettes` (`generation.py`):**
        *   Inside the main `try` block, *before* calling `commons.task_service.create_task`.
        *   Get the `user_id` from `commons`.
        *   Call `active_tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status='pending')`.
        *   Call `processing_tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status='processing')`.
        *   Combine the lists: `all_active_tasks = active_tasks + processing_tasks`.
        *   Filter for tasks of the correct type: `active_generation_tasks = [task for task in all_active_tasks if task.get("type") == "concept_generation"]`.
        *   Check if `active_generation_tasks` is not empty.
        *   If it's not empty:
            *   Get the first task: `existing_task = active_generation_tasks[0]`.
            *   Log that an existing task was found (use `mask_id`).
            *   Set the response status code: `response.status_code = status.HTTP_409_CONFLICT`.
            *   Return a `TaskResponse` object populated with `existing_task` data and a relevant message.
        *   If it *is* empty, continue with the existing logic to create a new task.
    2.  **Modify `refine_concept` (`refinement.py`):**
        *   Repeat the logic from Step 1, but filter for `task.get("type") == "concept_refinement"`.
        *   Ensure the response message and type in the `TaskResponse` are appropriate for refinement.
    3.  **Testing:** Add integration tests (using `TestClient`) that attempt to create a second task while the first (mocked) one is still 'pending' or 'processing' and verify the 409 response and body. [SKIP for now]

---

**2. Prevent Concurrent Task UI (Frontend)** [x] - Completed in branch refactor/prevent-concurrent-tasks-ui

*   **Goal:** Disable submission and inform the user if a task is already running.
*   **Target Files:**
    *   `frontend/my-app/src/components/concept/ConceptForm.tsx`
    *   `frontend/my-app/src/components/concept/ConceptRefinementForm.tsx`
    *   `frontend/my-app/src/contexts/TaskContext.tsx` (to use the state)

*   **Steps:**
    1.  **Access Global Task State:**
        *   In both `ConceptForm.tsx` and `ConceptRefinementForm.tsx`, import and use the `useTaskContext` hook: `const { hasActiveTask, isTaskPending, isTaskProcessing } = useTaskContext();`.
    2.  **Disable Submit Button:**
        *   Locate the primary submit `<Button>` component in each form.
        *   Combine the existing `disabled` conditions (like `isSubmitting`, `isSuccess`) with the global task state: `disabled={isSubmitting || isSuccess || hasActiveTask || isTaskPending || isTaskProcessing}`. Adjust based on the exact prop names used for the component's own loading state (`status`).
    3.  **Display In-Progress Message:**
        *   In the `div` containing the submit button (likely using `flex justify-end`), add a conditional paragraph or div.
        *   Render this element only when `!isSubmitting && (hasActiveTask || isTaskPending || isTaskProcessing)`.
        *   Set the text content to "A generation/refinement task is already in progress".
        *   Apply appropriate styling (e.g., `text-amber-600 text-sm mr-4`).
    4.  **Testing:** Update unit tests for both forms. Mock `useTaskContext` to return states where `hasActiveTask`, `isTaskPending`, or `isTaskProcessing` are true. Verify the button is disabled and the message appears. [SKIP FOR NOW]

---

**3. Service Layer Granularity (Backend)** [x]

*   **Goal:** Ensure backend services follow the Single Responsibility Principle.

*   **Steps:**
    1.  **Review `ImageService` (`backend/app/services/image/service.py`):**
        *   Read through each method (`generate_and_store_image`, `refine_and_store_image`, `create_palette_variations`, `process_image`, `store_image`, etc.).
        *   **Ask:** Is this method *only* coordinating tasks related to images, or is it implementing complex *processing* logic itself?
        *   **Action:** If complex processing logic (e.g., detailed color manipulation beyond simple format conversion/resizing) is found, move that logic into dedicated functions within `backend/app/services/image/processing.py` or `conversion.py`. The service method should then call these functions. Ensure clear delegation to `JigsawStackClient` for generation/refinement and `ImageStorageService` for storage.
    2.  **Review `ConceptService` Components (`backend/app/services/concept/`):**
        *   Open `generation.py`, `refinement.py`, `palette.py`.
        *   **Ask:** Does `ConceptGenerator` only generate? Does `ConceptRefiner` only refine? Does `PaletteGenerator` only handle palettes? Do they delegate API calls correctly to `JigsawStackClient`?
        *   **Action:** If a class is performing tasks outside its core responsibility (e.g., `ConceptGenerator` doing complex palette manipulation), move that logic to the appropriate class or a utility function.
    3.  **Evaluate JigsawStack Service Split:**
        *   Open `backend/app/services/jigsawstack/client.py`.
        *   **Ask:** Does this class *only* contain methods that directly map to JigsawStack API endpoints, handling request formatting and basic response parsing? Or does it contain significant logic *before* or *after* the API call (e.g., complex prompt construction strategies, merging results from multiple calls)?
        *   **Action:** If it's just direct API wrappers, keep it as a `Client`. If complex logic exists or is anticipated, *consider* creating `backend/app/services/jigsawstack/service.py` with a `JigsawStackService` class that *uses* the `JigsawStackClient`. For now, the client structure seems sufficient.

---

**4. Rate Limiting Application (Backend)**[x]

*   **Goal:** Centralize rate limit application logic, removing it from route handlers.

*   **Steps:** (Assuming Option B - New Middleware - is preferred for cleaner separation)
    1.  **Refine Util Functions (`backend/app/utils/api_limits/endpoints.py`):**
        *   Ensure `apply_rate_limit` and `apply_multiple_rate_limits` are robust and correctly use the core `check_rate_limit`. *Note: These functions might become obsolete or internal helpers after creating the middleware.*
    2.  **Create Rate Limit Apply Middleware (`backend/app/api/middleware/rate_limit_apply.py`):**
        *   Define a new class `RateLimitApplyMiddleware(BaseHTTPMiddleware)`.
        *   Implement the `async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:` method.
        *   Inside `dispatch`, *before* `await call_next(request)`:
            *   Get the `request.url.path` and `request.method`.
            *   Determine the relevant rate limit rule(s) for this path/method (e.g., using a dictionary mapping paths to rules like `{"/api/concepts/generate-with-palettes": "10/month", ...}`). You might need a more sophisticated routing match if paths have parameters.
            *   If no rule applies, proceed to `await call_next(request)`.
            *   Get the user identifier using `get_user_id(request)`.
            *   Import and call the core `check_rate_limit` function (from `app.core.limiter`) for *each* applicable rule, with `check_only=False`.
            *   If *any* check returns `exceeded=True`, log the violation and `raise HTTPException(status_code=429, detail=..., headers=...)` immediately. Do *not* call `call_next`.
            *   If all checks pass, store the rate limit information from the *most restrictive* check (lowest remaining count) into `request.state.limiter_info = {...}`.
    3.  **Modify Rate Limit Headers Middleware (`backend/app/api/middleware/rate_limit_headers.py`):**
        *   Ensure this middleware *only* reads `request.state.limiter_info` *after* `await call_next(request)` and sets the `X-RateLimit-*` headers. Remove any rate limit *checking* logic from here.
    4.  **Register Middlewares (`backend/app/core/factory.py`):**
        *   In `create_app`, import both middlewares.
        *   Add them using `app.add_middleware()`. **Crucially, add `RateLimitApplyMiddleware` *before* `RateLimitHeadersMiddleware`.**
            ```python
            from app.api.middleware.rate_limit_apply import RateLimitApplyMiddleware
            # ... other imports ...
            app.add_middleware(RateLimitApplyMiddleware) # Check/Apply first
            app.add_middleware(RateLimitHeadersMiddleware) # Add headers later
            ```
    5.  **Remove Calls from Route Handlers:**
        *   Go through all route handlers in `backend/app/api/routes/` currently calling `apply_rate_limit` or `apply_multiple_rate_limits`.
        *   Delete these calls. The middleware now handles the application.
    6.  **Testing:** Update integration tests to verify that requests to rate-limited endpoints fail with 429 when limits are exceeded *without* the explicit call in the route handler. Verify the response headers are still set correctly on successful requests. [SKIP FOR NOW]

---

**5. Supabase Client & Storage (Backend)** [x]

*   **Goal:** Clean up client responsibilities and improve storage clarity.

*   **Steps:**
    1.  **Refocus `SupabaseClient` (`client.py`):**
        *   Review all methods. Ensure methods directly related to *storage* operations (like uploading, downloading, masking storage paths) are primarily in `ImageStorage` or `ConceptStorage`.
        *   Move helper methods like `_mask_path` to the classes that use them (e.g., `ImageStorage`). If used by both, potentially create a `supabase/utils.py`.
    2.  **Move `purge_all_data`:**
        *   Create `backend/scripts/admin/purge_data.py`.
        *   Copy the `purge_all_data` method's logic into a function within this script.
        *   Modify the script to import `SupabaseClient`, `settings`, necessary storage classes (`ConceptStorage`, `ImageStorage`, etc.), and potentially use `asyncio.run()` if needed.
        *   Add argument parsing (`argparse`) to allow specifying a session ID or `--all` flag.
        *   Remove the `purge_all_data` method from `SupabaseClient`.
        *   Update any documentation pointing to this functionality.
    3.  **Add Comments to `ImageStorage` (`image_storage.py`):**
        *   Add detailed docstrings and inline comments explaining:
            *   The purpose of using direct HTTP requests vs. SDK methods (JWT auth).
            *   Which methods expect storage paths vs. full URLs.
            *   The role of `create_supabase_jwt`.
            *   Assumptions made about path structures (e.g., `user_id/file.png`).
            *   The reason for using the service role key in specific methods (if applicable).

---

**6. DRY - Route Logic (Rate Limit Info Storage)** [x]

*   **Goal:** Remove redundant code setting `request.state.limiter_info`.
*   **Action:** This task is fully addressed by the plan for **Item 4 (Rate Limiting Application)**. Once the middleware handles applying limits and storing the info in `request.state`, the duplicated logic in routes will be removed. No separate steps needed here beyond completing Item 4.

---

**7. URL Handling Consistency (Backend)** [x]

*   **Goal:** Ensure services return full, ready-to-use, signed URLs.

*   **Steps:**
    1.  **Standardize `ImageStorageService.get_signed_url` (`image_storage.py`):**
        *   Open the `ImageStorageService` class (or potentially the underlying `ImageStorage` class if `get_signed_url` lives there).
        *   Find the `get_signed_url` method (or equivalent like `get_image_url`).
        *   Ensure it uses `supabase.storage.from_(...).create_signed_url(...)` with an appropriate expiration (e.g., 3600 seconds for 1 hour, or longer depending on use case).
        *   Check the return value from the Supabase SDK. If it's a *relative* URL (starts with `/`), prepend `settings.SUPABASE_URL` to make it absolute.
        *   Add robust error handling (e.g., `try...except`) and return a fallback (e.g., empty string or placeholder URL) or raise a specific `StorageError` if URL generation fails.
    2.  **Update Service Return Values:**
        *   Review methods in `ConceptStorageService` (`get_concept_detail`, `get_recent_concepts`, `get_concept_by_task_id`) and potentially `ImageService`.
        *   Identify where these methods fetch data that includes `image_path` fields (for concepts or variations).
        *   *After* fetching the raw data from the database, iterate through the results.
        *   For each concept/variation, call the standardized `get_signed_url` method (from Step 1) using the corresponding `image_path` and bucket type (`concept-images` or `palette-images`).
        *   Store the resulting signed URL in the `image_url` field of the data dictionary being returned.
        *   Remove any separate `get_image_url` calls from the API route handlers themselves. The service should return the complete data with URLs included.
    3.  **Testing:** Update tests for the services to mock `create_signed_url` and verify that the returned data structures contain absolute, signed URLs in the `image_url` fields. [SKIP FOR NOW]

---

**8. Legacy Code Cleanup (Backend)**[x]

*   **Goal:** Remove specified obsolete backend files.
*   **Pre-requisite:** Ensure functionality from these files has been migrated elsewhere (e.g., concept logic to `services/concept/`, storage logic to `services/storage/`, image processing to `services/image/`, API routing centralized via `api/router.py`).

*   **Steps:**
    1.  **Delete `backend/app/api/routes/api.py`:** Remove the file. Update `backend/app/api/router.py` if it imports anything from here (unlikely).
    2.  **Delete Old Model Files:**
        *   Delete `backend/app/models/concept.py`.
        *   Delete `backend/app/models/request.py`.
        *   Delete `backend/app/models/response.py`.
        *   Search for imports of these files and update them to point to the structured locations (e.g., `backend/app/models/concept/request.py`). Run linters/type checkers.

    5.  **Run Tests:** Execute the full backend test suite (`uv run pytest`) to confirm no regressions were introduced. [SKIP FOR NOW]

---

**9. Frontend State Management (Remove ConceptContext)**[x]

*   **Goal:** Simplify state by relying solely on React Query for concept data.

*   **Steps:**
    1.  **Identify Components:** Search the `frontend/my-app/src/` directory for `useConceptContext`. Note down the components (e.g., `RecentConceptsSection`, `ConceptList`).
    2.  **Refactor `RecentConceptsSection` (if using context):**
        *   Remove `import { useConceptContext } ...`.
        *   Import `import { useRecentConcepts } from '../../hooks/useConceptQueries';`.
        *   Import `import { useAuth } from '../../contexts/AuthContext';`.
        *   Get user: `const { user } = useAuth();`.
        *   Fetch data: `const { data: concepts, isLoading, error } = useRecentConcepts(user?.id);`.
        *   Adapt the rendering logic to use `isLoading`, `error`, and `concepts` (which is the `data` from the query).
    3.  **Refactor `ConceptList` (if using context):**
        *   Perform the same steps as for `RecentConceptsSection`.
    4.  **Refactor Other Components:** Repeat the refactoring process for any other component identified in Step 1.
    5.  **Remove Context File:** Delete `frontend/my-app/src/contexts/ConceptContext.tsx`.
    6.  **Remove Provider:** Open `frontend/my-app/src/App.tsx` (or wherever the provider is wrapped) and remove the `<ConceptProvider>...</ConceptProvider>` wrapper. Delete the import for `ConceptProvider`.
    7.  **Testing:** Update unit tests for the refactored components. Mock the React Query hooks (`useRecentConcepts`, etc.) instead of the context. Run E2E tests if available. [SKIP FOR NOW]

---

**10. React Query Cache Review**[x]

*   **Goal:** Optimize data fetching behavior and potentially remove unnecessary forced refetches.

*   **Steps:**
    1.  **Review Defaults (`frontend/my-app/src/main.tsx`):**
        *   Examine the `defaultOptions` for `queries` in the `QueryClient` constructor.
        *   Consider the current `staleTime` (10s). Is this appropriate globally? Maybe increase it slightly (e.g., 30s or 1min) if data doesn't change *that* rapidly.
        *   Confirm `refetchOnWindowFocus: false` is still desired. If data freshness is critical, enabling it (`true`) might be better, but can increase API calls.
    2.  **Evaluate `useFreshConceptDetail` (`useConceptQueries.ts`):**
        *   Analyze the `useFreshConceptDetail` hook (or the similar logic inside `useConceptDetail` if merged).
        *   **Question:** Why was the forced refetch (`staleTime: 0`, `refetchOnMount: true`, `invalidateQueries`) added? Was it due to caching issues during navigation or updates?
        *   **Action:**
            *   Temporarily *remove* or comment out the aggressive refetching logic (the `useEffect` doing `invalidateQueries` and `refetch`, and potentially the `staleTime: 0` override).
            *   Rely on standard React Query cache invalidation triggered by mutations (e.g., after refining or generating).
            *   Thoroughly test navigation scenarios: Does the detail page show fresh data after a refinement? Does the recent concepts list update correctly?
            *   If data appears stale without the forced refetch, investigate *why*. Is a mutation missing `queryClient.invalidateQueries`? Is the query key matching incorrect?
            *   If forced refetching *is* genuinely needed for specific cases (like immediately viewing a just-created concept), keep it but add clear comments explaining why. Consider using `queryClient.refetchQueries` triggered by an event rather than a blanket `useEffect` on mount.

---

**11. Component Consolidation (ConceptCard)** [x] - Completed

*   **Goal:** Maintain a single, reusable `ConceptCard` component.

*   **Steps:**
    1.  **Locate Cards:** Find all `ConceptCard.tsx` files (e.g., `components/ui/ConceptCard.tsx`, `features/concepts/recent/components/ConceptCard.tsx`).
    2.  **Analyze:** Compare their props (`ConceptCardProps`), internal state, rendering logic, and styling. List the differences.
    3.  **Select Base:** Choose `components/ui/ConceptCard.tsx` as the canonical component, as `ui` is typically for shared, reusable elements.
    4.  **Merge:**
        *   Identify props present in the `recent` card but not the `ui` card (e.g., `onEdit`, `onViewDetails`, specific data structure expectations).
        *   Add these props (make them optional) to the `ConceptCardProps` interface in `components/ui/ConceptCard.tsx`.
        *   Add the conditional rendering logic for the Edit/View Details buttons based on whether the `onEdit`/`onViewDetails` props are provided.
        *   Update the internal logic to handle the data structure provided by `RecentConceptsPage` (likely the `ConceptData` type). Ensure it can handle both detailed data and summary data gracefully. Add props if necessary to control display details (e.g., `displayMode: 'summary' | 'detail'`).
    5.  **Refactor Usage:**
        *   Go to `features/concepts/recent/components/ConceptList.tsx`.
        *   Change the import from `'./ConceptCard'` to `'../../../components/ui/ConceptCard'`.
        *   Ensure the props being passed match the updated interface of the UI card (pass `onEdit`, `onViewDetails` handlers).
    6.  **Delete Redundant File:** Delete `features/concepts/recent/components/ConceptCard.tsx`.
    7.  **Test:** Run unit tests for the UI `ConceptCard`. Manually test the Recent Concepts page and any other place the card was used. [SKIP FOR NOW]

**Additional Implementation:**
- Updated the ConceptCard UI to match the grid layout design from mockups
- Implemented a responsive grid layout in ConceptList component
- Added Material-UI icons for consistent styling
- Enhanced hover effects on cards
- Updated loading state with appropriate skeleton UI

---

**12. Component SRP/Import Review** [x]

*   **Goal:** Maintain clean component boundaries.

*   **Steps:**
    1.  **Scan `components/ui/`:**
        *   Check imports in each `.tsx` file within this directory.
        *   **Look for:** Imports starting with `../../features/`.
        *   **Action:** If found, refactor. The feature-specific logic/data should be passed down as props (data or callbacks) from the feature component that *uses* the UI component.
    2.  **Scan `features/`:**
        *   Check imports in components within *one* feature directory (e.g., `features/landing/components/`).
        *   **Look for:** Imports reaching into *another* feature directory (e.g., `import ... from '../../refinement/components/...'`).
        *   **Action:** If found, determine if the imported component/hook represents truly shared functionality.
            *   If yes, move the shared item to `components/ui/`, `components/common/`, or `hooks/`. Update imports in both features.
            *   If no, rethink the component structure. Perhaps the logic belongs in a shared parent or context.

---

**13. URL Handling Consistency (Frontend)** [x]

*   **Goal:** Rely on backend-provided URLs and simplify frontend logic.

*   **Steps:**
    1.  **Review `supabaseClient.ts` URL Functions:**
        *   Examine `getImageUrl`, `getSignedImageUrl`, `getAuthenticatedImageUrl`.
        *   **Action:** Simplify these. If the backend *always* returns full, signed URLs in the `image_url` fields of `ConceptData` and `ColorVariationData` (after Item 7 Backend Refactoring), these frontend functions might only need to:
            *   Handle potential `null` or `undefined` inputs gracefully (return fallback or empty string).
            *   Prepend the Supabase base URL *only* if a URL starts with `/` (as a safety check).
            *   Remove complex logic trying to generate signed URLs or token URLs.
        *   Deprecate or remove functions that are no longer needed. Keep one primary function (e.g., `formatImageUrl`) for consistency.
    2.  **Update Image Components:**
        *   Go to components displaying images (`ConceptCard`, `ConceptResult`, `ConceptDetailPage`, `EnhancedImagePreview`, `OptimizedImage`).
        *   Find where the `src` prop for `<img>` tags is set.
        *   Ensure it directly uses the `image_url` (or equivalent field like `base_image_url`) from the fetched concept/variation data object.
        *   Remove any calls to `getSignedImageUrl` or similar functions *within* these components. Pass the final URL directly as a prop if needed.
    3.  **Review `extractStoragePathFromUrl` (`utils/url.ts`):**
        *   Check where this function is used. Is it still needed for the `ExportOptions` component, or does the export mutation now handle path extraction on the backend/hook level?
        *   **Action:** If it's *only* used for export and the export hook (`useExportImageMutation`) now takes the `imageIdentifier` (path) directly, this utility can likely be removed. If it's still required, ensure it handles all possible URL formats correctly.

---

**14. Page Transitions**

*   **Goal:** Implement smooth page transitions using a standard library.

*   **Steps:**
    1.  **Remove Custom Component:** Delete `frontend/my-app/src/components/layout/PageTransition.tsx`. Update `frontend/my-app/src/components/layout/index.ts` to remove the export.
    2.  **Choose & Install Library:**
        *   Decision: Use `framer-motion` (popular and powerful).
        *   Run: `npm install framer-motion`.
    3.  **Implement in `App.tsx`:**
        *   Import `AnimatePresence` and `motion` from `framer-motion`.
        *   Import `useLocation` from `react-router-dom`.
        *   Get the `location` object: `const location = useLocation();`.
        *   Wrap the `<Suspense>` containing `<Routes>` with `<AnimatePresence mode="wait">`.
        *   Wrap the direct child *inside* `<Suspense>` (which is likely the `<Routes>` or a container div) with `<motion.div>`.
        *   Assign a `key={location.pathname}` to the `motion.div`.
        *   Define animation variants (e.g., `pageVariants`) for fade/slide effects.
        *   Add props to `motion.div`: `initial="initial"`, `animate="in"`, `exit="out"`, `variants={pageVariants}`, `transition={{ duration: 0.3 }}`.
            ```tsx
            import { AnimatePresence, motion } from 'framer-motion';
            // ... other imports

            const pageVariants = {
              initial: { opacity: 0, y: 20 },
              in: { opacity: 1, y: 0 },
              out: { opacity: 0, y: -20 },
            };

            const AppRoutes = () => {
              const location = useLocation();
              return (
                <AnimatePresence mode="wait">
                  <motion.div
                    key={location.pathname} // Key triggers animation on path change
                    initial="initial"
                    animate="in"
                    exit="out"
                    variants={pageVariants}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    style={{ height: '100%', width: '100%' }} // Ensure motion div takes space
                  >
                    <Suspense fallback={<LoadingFallback />}>
                      <Routes location={location}> // Pass location to Routes
                        {/* ... routes ... */}
                      </Routes>
                    </Suspense>
                  </motion.div>
                </AnimatePresence>
              );
            };
            ```
    4.  **Adjust Styling/Layout:** Ensure the `motion.div` and its parent containers have appropriate styling (e.g., `position: relative`, `height`, `width`) to allow the animation to work correctly without layout shifts. Remove the old `PageTransition` wrapper from `AppRoutes`.
    5.  **Test:** Navigate between different pages and verify the transition animation plays smoothly. [SKIP FOR NOW]

---

**15. API Client & Fetch Interceptor**

*   **Goal:** Centralize request/response handling in the Axios client.

*   **Steps:**
    1.  **Move Fetch Interceptor Logic:**
        *   Copy the rate limit header extraction logic from the `setupFetchInterceptor` function (currently in `App.tsx`).
        *   Copy the token refresh/401 handling logic (currently simulated or implemented in `apiClient.ts` interceptors).
        *   Open `frontend/my-app/src/services/apiClient.ts`.
        *   Implement the copied logic within `axiosInstance.interceptors.request.use()` and `axiosInstance.interceptors.response.use()`.
            *   *Request Interceptor:* Get token using `supabase.auth.getSession()` and add `Authorization` header.
            *   *Response Success Interceptor:* Call `extractRateLimitHeaders(response, response.config.url)`.
            *   *Response Error Interceptor:* Handle 401 (token refresh logic, retry original request, dispatch `auth-error-needs-logout`), handle 429 (create/throw `RateLimitError`, dispatch toast event).
    2.  **Remove `setupFetchInterceptor`:** Delete the function and its call from `App.tsx`.
    3.  **Confirm Axios Usage:** Verify that all API interactions throughout the app go through the `apiClient` methods (`get`, `post`, `exportImage`) which use the configured `axiosInstance`. Replace any remaining direct `fetch` calls.
    4.  **Testing:** Update/add tests for `apiClient.ts` (like `apiInterceptors.test.ts`) to specifically verify the interceptor logic for auth headers, rate limit extraction, 401 refresh, and 429 handling. [SKIP FOR NOW]

---

**16. Legacy Hooks Cleanup (Frontend)**

*   **Goal:** Standardize on React Query hooks.

*   **Steps:**
    1.  **Identify Usage:** Search for `useConceptGeneration`, `useConceptRefinement`, `useApi`. Likely places: `LandingPage.tsx`, `RefinementPage.tsx`.
    2.  **Replace `useConceptGeneration`:**
        *   In `LandingPage.tsx` (or wherever used):
        *   Remove the import and usage of `useConceptGeneration`.
        *   Import `useGenerateConceptMutation` from `useConceptMutations.ts`.
        *   Call the hook: `const { mutate: generateConcept, isPending, data: taskData, isSuccess, isError, error, reset } = useGenerateConceptMutation();`.
        *   Update the form submission handler (`handleGenerateConcept`) to call `generateConcept({ logo_description: ..., theme_description: ... });`.
        *   Update status checks to use `isPending`, `isSuccess`, `isError`, `taskData`, `error` from the mutation hook result.
        *   Update the reset handler to call `reset()` from the mutation hook.
    3.  **Replace `useConceptRefinement`:**
        *   In `RefinementPage.tsx` (or wherever used):
        *   Remove the import and usage of `useConceptRefinement`.
        *   Import `useRefineConceptMutation` from `useConceptMutations.ts`.
        *   Call the hook: `const { mutate: refineConcept, isPending, data: taskData, ... } = useRefineConceptMutation();`.
        *   Update the form submission handler (`handleRefineConcept`) to call `refineConcept({ original_image_url: ..., refinement_prompt: ..., ... });`.
        *   Update status checks similarly to the generation hook.
        *   Update the reset handler to call `reset()` from the mutation hook.
    4.  **Replace `useApi`:**
        *   Search for any remaining `useApi` usage.
        *   Replace `useApi().get(...)` calls with `useQuery` from `@tanstack/react-query`. Define appropriate query keys and query functions using `apiClient.get`.
        *   Replace `useApi().post(...)` calls with `useMutation` from `@tanstack/react-query`. Define mutation functions using `apiClient.post`.
    5.  **Delete Files:** Delete `useConceptGeneration.ts`, `useConceptRefinement.ts`, and `useApi.ts` from the `hooks` directory. Remove exports from `hooks/index.ts`.
    6.  **Testing:** Update unit/integration tests for the components that were modified. Ensure they correctly mock the new React Query mutation hooks. [SKIP FOR NOW]

---

**17. Backend Logging Cleanup**

*   **Goal:** Optimize backend logs for production clarity.

*   **Steps:**
    1.  **Systematic Review:** Go through each file listed in the TODO (middleware, routes, core, services, utils).
    2.  **Analyze `logger.info`:** Is this log essential for understanding the application flow in production (e.g., "Task started", "Concept stored")? If it's just confirming function entry/exit or intermediate steps useful only for debugging, change to `logger.debug` or remove.
    3.  **Analyze `logger.debug`:** Keep only if the information is highly valuable for diagnosing specific, hard-to-reproduce issues in production. Otherwise, remove.
    4.  **Analyze `logger.warning`:** Ensure these represent potentially problematic but non-fatal situations. Are they actionable?
    5.  **Analyze `logger.error` / `logger.critical`:** Ensure these are used for actual errors that require attention. Include relevant context (masked IDs, error details). Avoid logging full stack traces unless necessary (FastAPI's error handlers might already do this).
    6.  **Check for Sensitive Data:** Double-check that no unmasked IDs, keys, tokens, or full prompts/image data are being logged. Use the `mask_*` utilities.
    7.  **Test:** Run the backend locally (`uvicorn`) and perform common actions. Observe the log output. Is it concise but informative? [SKIP FOR NOW]

---

**18. Frontend Console Logging Cleanup**

*   **Goal:** Remove development noise from the browser console in production.

*   **Steps:**
    1.  **Global Search:** Use your IDE's search function to find all instances of `console.log`, `console.warn`, `console.debug`, `console.info` in the `frontend/my-app/src/` directory.
    2.  **Evaluate Each Log:**
        *   **Debug Logs:** If a `console.log` was added purely for temporary debugging, remove it.
        *   **Informational Logs:** If a `console.log` provides useful state information during development (e.g., "Component mounted", "State updated"), wrap it in an environment check: `if (import.meta.env.DEV) { console.log(...); }`.
        *   **Warnings/Errors:** Keep `console.warn` and `console.error` for issues that might still occur in production and are helpful for user bug reports (e.g., failed API calls *after* they've been handled by the UI error system, unexpected component state). Consider adding more context to these logs.
    3.  **Build & Verify:** Create a production build (`npm run build` and `npm run preview`) and check the browser console while using the app to ensure development logs are gone.

---

**19. DRY Code Refactoring**

*   **Steps:**
    1.  **Create `QueryResultHandler`:**
        *   Create the file `frontend/my-app/src/components/common/QueryResultHandler.tsx`.
        *   Define props: `isLoading: boolean`, `error: Error | null`, `data: T | null | undefined`, `loadingComponent?: ReactNode`, `errorComponent?: ReactNode`, `emptyComponent?: ReactNode`, `children: (data: T) => ReactNode`.
        *   Implement the component:
            ```tsx
            if (isLoading) return loadingComponent || <DefaultLoading />;
            if (error) return errorComponent || <DefaultError error={error} />;
            if (!data || (Array.isArray(data) && data.length === 0)) return emptyComponent || <DefaultEmpty />;
            return children(data);
            ```
        *   Create simple default components (`DefaultLoading`, `DefaultError`, `DefaultEmpty`) or use existing UI components like `SkeletonLoader` and `ErrorMessage`.
        *   Refactor components like `ConceptList`, `ConceptDetailPage`, `RefinementSelectionPage`: Replace their `if (isLoading)... else if (error)... else if (!data)...` blocks with `<QueryResultHandler isLoading={...} error={...} data={...}>{(data) => /* render actual content */}</QueryResultHandler>`.
    2.  **Refactor Backend Rate Limit Application:** Addressed by **Item 4**.
    3.  **Create Supabase Helpers (Backend):**
        *   In `backend/app/core/supabase/concept_storage.py` and `image_storage.py`.
        *   Identify repetitive query patterns (e.g., `select('*').eq('id', id).eq('user_id', user_id).single()`).
        *   Create private helper methods like `async def _get_record_by_id(self, table_name: str, record_id: str, user_id: str)` that encapsulate these patterns and include basic error handling/logging. Call these helpers from the public service methods.
    4.  **Centralize JigsawStack Handling (Backend):** Addressed by **Item 3**. Ensure all JigsawStack logic is within `services/concept/*` or `services/jigsawstack/*`.
    5.  **Consolidate Image Upload/Storage (Backend):**
        *   Review `backend/app/services/image/service.py` and `storage.py`.
        *   Ensure `ImageStorageService` handles: filename generation logic, content type determination, actual Supabase upload call (`storage.from_().upload()`), signed URL generation.
        *   Ensure `ImageService` handles: coordinating generation (calling JigsawStack), getting the image data, *calling* `ImageStorageService.store_image`, potentially applying processing *before* storing.

---

**20. UI Consistency**

*   **Goal:** Standardize styling using Tailwind utility classes.

*   **Steps:**
    1.  **Audit Components:** Go through `.tsx` files in `components/` and `features/`.
    2.  **Identify Non-Tailwind Styles:** Look for `<style>` tags, `style={{...}}` props used for layout/color/spacing/typography, and usage of CSS modules (`styles.*`) for basic styling.
    3.  **Replace with Tailwind:** Find the equivalent Tailwind utility class(es) for the identified styles.
        *   `style={{ color: 'red' }}` -> `className="text-red-500"`
        *   `style={{ fontSize: '16px' }}` -> `className="text-base"`
        *   `styles.container` with `padding: 1rem;` -> `<div className="p-4">`
        *   `styles.button` with complex styles -> Refactor into a reusable React `<Button>` component using Tailwind internally, or use `@apply` in `global.css` (`@layer components { .my-button { @apply px-4 py-2 ...; } }`). Prefer utility classes directly where possible.
    4.  **Use Theme Values:** Ensure colors (`text-primary`, `bg-indigo-100`), spacing (`p-4`, `m-2`), font sizes (`text-lg`) reference values configured in `tailwind.config.js`.
    5.  **Review Responsiveness:** Check for hardcoded pixel values that should be responsive units. Use Tailwind's `sm:`, `md:`, `lg:` prefixes for breakpoints.

---

**21. Backend Testing Enhancements**[SKIP FOR NOW]

*   **Goal:** Improve backend test coverage, especially for new/refactored areas.

*   **Steps:**
    1.  **Test Background Task Functions:** (If helpers were created for retry logic, etc.) Write unit tests in `tests/services/` or `tests/utils/` mocking their immediate dependencies.
    2.  **Test API Routes (Integration):** Create/update tests in `tests/routes/` using `TestClient`.
        *   For `generate`/`refine` endpoints: Mock the `BackgroundTasks.add_task` method. Verify the API returns 202, and that a task record *would* be created with the correct initial data (mock the `task_service.create_task` call).
    3.  **Test Refactored Services:** Update tests in `tests/services/`. Ensure mocks match the new dependencies and responsibilities. Verify return values and side effects (like calls to other services/clients).
    4.  **Test BG Task Error Handling:** Write integration tests where mocked service calls *within* the background task path (e.g., mock `image_service.generate_and_store_image` to raise an error) result in the task status being updated to 'failed' with the correct error message (mock `task_service.update_task_status` and check its arguments).
    5.  **Test Concurrent Task Prevention:** Write integration tests (see Item 1, Step 3).
    6.  **Test Stuck Task Cleanup:** Write unit tests for the *logic* within the Supabase Edge Function (`cleanup-old-data/index.ts`). Mock the `supabase` client methods (`from().select()`, `rpc()`, `storage.from().remove()`). Verify it correctly identifies tasks and calls the deletion methods with the right parameters.

---

**22. Frontend Testing Enhancements**[SKIP FOR NOW]

*   **Goal:** Ensure frontend tests align with refactored state management and components.

*   **Steps:**
    1.  **Update Component Tests (Context Removal):** Find tests for components previously using `useConceptContext`. Update them to mock the necessary React Query hooks (`useRecentConcepts`, `useConceptDetail`) instead. Use `vi.mock` to provide mock return values for `data`, `isLoading`, `error`.
    2.  **Test Consolidated Components:** Write comprehensive tests for the canonical `ConceptCard` (`components/ui/ConceptCard.tsx`), covering different props (`includeOriginal`, variations presence), interactions (button clicks, palette selection), and display modes.
    3.  **Test React Query Integration:** For components using `useQuery` or `useMutation`, write tests verifying:
        *   Correct rendering during `isLoading`.
        *   Correct rendering with `data`.
        *   Correct rendering of error states using `error`.
        *   Verify `mutate` functions are called with correct arguments on user interaction.
    4.  **Test Error Handling UI:** Write tests for `ErrorMessage` ensuring different `type` props render distinct styles/icons. Test the global error display mechanism added in Item 5 - mock `useErrorHandling` to have an error and verify the message appears. Test retry/dismiss actions.
    5.  **Test `useTaskPolling`:** Create unit tests for the hook in `hooks/__tests__/`. Mock `fetchTaskStatus`. Simulate different API responses ('pending', 'processing', 'completed', 'failed') over time and assert the hook's returned state (`data`, `isPending`, etc.) updates correctly. Verify callbacks (`onSuccess`, `onError`) are called.
    6.  **Test `TaskStatusBar`:** Write unit tests for the component. Mock `useTaskContext` to provide various states. Verify the rendered message, icon, and colors. Test the temporary display of the 'completed' state.
    7.  **Test Concurrent Task UI:** Write tests for `ConceptForm` and `RefinementForm`. Mock `useTaskContext` to return `{ hasActiveTask: true, isTaskPending: true }` (or similar) and verify the submit button is `disabled` and the "in progress" message is visible.

---

**23. Implementation Plan Steps**

*   **Goal:** Organize the execution of the refactoring.

    4.  **Branching:** Use descriptive branch names (e.g., `refactor/backend-error-handling`, `feature/task-concurrency-limit`, `chore/remove-concept-context`).
    5.  **Implement & Test:** Work on one ticket/branch at a time. Write code, update/write tests.
    6.  **Code Review:** Create Pull Requests. Ensure reviewers check code logic, adherence to the plan, and test coverage. Merge PRs frequently.

---

**24. Refine Backend Error Types**

*   **Goal:** More specific error handling in the service layer.

*   **Steps:**
    1.  **Define Specific Exceptions (`backend/app/core/exceptions.py`):**
        *   Open the file.
        *   Define new classes inheriting from `ApplicationError`. Examples:
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
        *   Add others as needed based on specific failure points you identify.

    2.  **Catch and Wrap Errors in Services (`backend/app/services/`):**
        *   Go through service files (e.g., `image/service.py`, `storage/concept_storage.py`, `jigsawstack/client.py`, `task/service.py`).
        *   Identify `try...except` blocks that handle external calls (e.g., `httpx` requests, `supabase` client calls, `redis` calls).
        *   Modify the `except` blocks:
            *   Catch *specific* external exceptions (e.g., `httpx.HTTPStatusError`, `httpx.RequestError`, `postgrest.exceptions.APIError`, `redis.RedisError`, `StorageException` from supabase-py if applicable).
            *   Inside the `except`, `raise` the corresponding *specific* custom exception defined in step 1. Pass relevant context (operation details, original error message, masked IDs/paths) into the `details` dictionary.
            *   Example in `JigsawStackClient`:
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
            *   Example in `ConceptStorageService`:
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
        *   Open the `application_error_handler` function.
        *   Add `elif isinstance(exc, NewSpecificError):` blocks for each new specific exception type created in step 1.
        *   Map each new exception to an appropriate HTTP status code (e.g., `DatabaseTransactionError` -> 500, `ConceptGenerationError` -> 503, `StorageOperationError` -> 503, `RateLimitRuleError` -> 500) and a distinct `error_code` string (e.g., `"DB_TRANSACTION_FAILED"`, `"CONCEPT_GEN_FAILED"`).
        *   Ensure the logging within the handler captures the specific exception type (`exc.__class__.__name__`) and any relevant details from `exc.details`.

---

**25. Transaction Management**

*   **Goal:** Ensure atomicity for multi-step DB/Storage operations.
*   **Target:** `ConceptStorageService.store_concept` (handles concept + variations).

*   **Steps:**
    1.  **Analyze `store_concept`:** Open `backend/app/services/storage/concept_storage.py` and `backend/app/core/supabase/concept_storage.py`. Review the `store_concept` and `store_color_variations` methods. Note the sequence: `store_concept` inserts into `concepts`, then `store_color_variations` inserts into `color_variations`.
    2.  **Implement Cleanup Logic:** Modify the service layer `store_concept` in `concept_storage.py`:
        *   Wrap the calls to `self.concept_storage.store_concept` and `self.concept_storage.store_color_variations` in a `try...except` block within the service method.
        *   Store the `concept_id` returned by `self.concept_storage.store_concept`.
        *   In the `except` block specifically catching errors during `store_color_variations`:
            *   Log the failure clearly.
            *   Attempt to delete the concept that was just created using the stored `concept_id`. Add a new method `delete_concept_by_id` to `ConceptStorage` if needed.
            *   Use a `try...except` around the deletion attempt and log whether cleanup was successful or failed.
            *   Reraise a `DatabaseTransactionError` or `StorageError` indicating the partial failure and failed/successful cleanup.
        *   If the initial `store_concept` call fails, just let the exception propagate (no cleanup needed).
    3.  **Logging:** Ensure all steps, failures, and cleanup attempts are logged with masked IDs.

---

**26. Background Task Robustness**

*   **Goal:** Make background tasks more resilient.

*   **Steps:**
    1.  **Detailed Error Logging (`backend/app/api/routes/concept/generation.py`, `refinement.py`):**
        *   Locate the main `except Exception as e:` block in `generate_concept_background_task` and `refine_concept_background_task`.
        *   Inside the `except` block, determine *which* service call failed (e.g., `image_service.generate_and_store_image`, `concept_service.generate_color_palettes`, `storage_service.store_concept`).
        *   Construct a more detailed `error_message` string including the failed step and the specific error from `e`. Example: `f"Failed at step 'generate_color_palettes': {str(e)}"`
        *   Update the call to `task_service.update_task_status` to pass this detailed `error_message`.
        *   *Optional:* If useful for debugging, add specific details (like masked IDs or prompt snippets) to the task's `metadata` field during the error update (requires modifying `update_task_status` to accept metadata updates on failure).

    2.  **Retry Mechanism (Optional - `tenacity`):**
        *   **Install:** `uv pip install tenacity` (add to `pyproject.toml` optional deps if preferred).
        *   **Import:** `from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type` in the route files (`generation.py`, `refinement.py`).
        *   **Identify Targets:** Calls prone to transient errors within the background tasks (e.g., `image_service.generate_and_store_image`, `concept_service.generate_color_palettes`, potentially `storage_service.store_concept`).
        *   **Apply Decorator:** Wrap the *calls* to these functions (or define small helper async functions to wrap the calls if needed) using the `@retry` decorator.
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
        *   **Adjust:** Configure `stop`, `wait`, and `retry` conditions based on the specific external service behavior.

    3.  **Stuck/Failed Task Cleanup (`backend/supabase/functions/cleanup-old-data/index.ts`):**
        *   Open the Edge Function code.
        *   **Query Failed Tasks:** Add a query similar to `cleanupStuckTasks` but filtering for `status = 'failed'` and `updated_at < NOW() - INTERVAL '7 days'` (or your desired retention period for failed tasks).
        *   **Identify Resources:** For each failed task retrieved, attempt to extract relevant resource identifiers from its `metadata` or `result_id` (e.g., `concept_id`, `image_path`). *This requires that the background tasks store useful identifiers in metadata upon failure.*
        *   **Attempt Deletion:** If identifiers are found, call appropriate Supabase Storage `remove` functions (like `deleteFromStorage`) to delete associated files (concept images, palette images).
        *   **Delete Task Record:** After attempting resource cleanup (regardless of success), delete the old 'failed' task record itself from the `tasks` table.
        *   **Logging:** Log which tasks are being processed for cleanup, which resources are identified, and the success/failure of deletion attempts.

---

**27. Configuration Validation**

*   **Goal:** Fail fast on missing critical configuration.

*   **Steps:**
    1.  **Enhance `validate_required_settings` (`backend/app/core/config.py`):**
        *   Open the `Settings` class.
        *   Add `if not self.VARIABLE_NAME:` checks for essential variables like:
            *   `SUPABASE_JWT_SECRET`
            *   `SUPABASE_SERVICE_ROLE` (crucial if service role calls are used)
            *   `STORAGE_BUCKET_CONCEPTS`
            *   `STORAGE_BUCKET_PALETTE`
        *   Conditionally check Redis variables if rate limiting is enabled:
            ```python
            if self.RATE_LIMITING_ENABLED:
                if not self.UPSTASH_REDIS_ENDPOINT:
                    raise EnvironmentVariableError(...)
                if not self.UPSTASH_REDIS_PASSWORD:
                    raise EnvironmentVariableError(...)
            ```
        *   Ensure each check raises `EnvironmentVariableError` with the correct `variable_name`.

---

**28. Frontend Global Error Handling Integration**

*   **Goal:** Centralize UI error handling.

*   **Steps:**
    1.  **Integrate `useErrorHandling` Hook:**
        *   Open `frontend/my-app/src/App.tsx`.
        *   Import `useErrorHandling` and the `ErrorMessage` component.
        *   Call the hook near the top of the `App` component: `const errorHandler = useErrorHandling();`.
        *   Render the `ErrorMessage` component conditionally based on `errorHandler.hasError` somewhere visible in the layout (e.g., fixed banner at the top/bottom, *outside* the main `Router`/`Outlet` area if it should persist across navigation).
            ```tsx
            // Inside App component return:
            {errorHandler.hasError && errorHandler.error && (
              <div style={{ position: 'fixed', top: '80px', left: '50%', transform: 'translateX(-50%)', zIndex: 1000, width: '90%', maxWidth: '600px' }}>
                <ErrorMessage
                  message={errorHandler.error.message}
                  details={errorHandler.error.details}
                  type={errorHandler.error.category as ErrorType} // Cast might be needed
                  onDismiss={errorHandler.clearError}
                />
              </div>
            )}
            {/* Rest of the app structure */}
            ```
        *   *Alternatively:* If using the `ErrorBoundary` component from `ui`, wrap `AppRoutes` with it and pass `onError={errorHandler.handleError}`.

    2.  **Review Error Propagation:**
        *   Examine custom hooks making API calls (e.g., `useConceptMutations`, `useConceptQueries`). Ensure they *re-throw* errors after logging or initial handling if they aren't meant to be fully handled locally.
        *   Check `apiClient.ts` interceptors. The current logic seems to re-throw most unhandled errors, which is good. Ensure the `auth-error-needs-logout` event path doesn't prevent errors from reaching the global handler if needed elsewhere.
        *   Remove `try...catch` blocks in components that simply log and swallow errors; let them bubble up.

---

**29. Frontend User Feedback for Errors**

*   **Goal:** Provide clear, actionable error feedback.

*   **Steps:**
    1.  **Enhance `ErrorMessage` Component (`components/ui/ErrorMessage.tsx`):**
        *   Add props to accept `error_code?: string` (passed via `details` object potentially).
        *   Inside the component, add conditional rendering:
            ```tsx
            {error_code && <span className="text-xs opacity-70 mr-2">Code: {error_code}</span>}
            {/* ... */}
            {category === 'network' && <p className="text-xs mt-1">Please check your internet connection.</p>}
            {category === 'validation' && <p className="text-xs mt-1">Please review the form fields.</p>}
            ```
        *   Modify the `props` interface and update calls to `ErrorMessage` where category/code info is available (e.g., from `useErrorHandling` state).

    2.  **Inline Rate Limit Handling:**
        *   Open mutation hooks (`useConceptMutations`, `useExportImageMutation`).
        *   In the `onError` callback:
            *   Check `if (error instanceof RateLimitError)`.
            *   If true, set a specific state variable in the hook's return value (e.g., `isRateLimited: true`, `rateLimitDetails: { message: error.getUserFriendlyMessage() }`).
            *   Trigger a rate limit refresh: `queryClient.invalidateQueries({ queryKey: ['rateLimits'] });`.
        *   In components using these hooks (e.g., `ConceptFormSection`, `ExportOptions`):
            *   Access the new rate limit state from the hook.
            *   Conditionally render an inline error message near the submit button using the `rateLimitDetails.message`.
            *   Consider disabling the button based on `isRateLimited`.
        *   Update `RateLimitsPanel` to potentially show a more prominent warning if a specific limit is hit (requires passing error state or using context).

    3.  **Actionable Task Failure Feedback (`components/TaskStatusBar.tsx`):**
        *   Modify the `failed` status rendering block.
        *   Display `activeTaskData.error_message` more clearly.
        *   Add a "Retry" button conditionally. Determine retry possibility:
            *   Check if the `error_message` indicates a transient issue (e.g., "Network Error", "API unavailable").
            *   *Requires backend enhancement:* The backend task could set a `retryable: true` flag in metadata upon failure.
        *   The "Retry" button's `onClick` should:
            *   Call `clearActiveTask()` from `useTaskContext`.
            *   Trigger the *original* mutation that created the task (this might require passing the mutation function down or using a different state management approach like Zustand/Redux if context becomes too complex).

---

**30. Frontend Network Status Integration**

*   **Goal:** Improve UI responsiveness to network state.

*   **Steps:**
    1.  **Integrate `useNetworkStatus` in Hooks:**
        *   Open hooks making API calls (e.g., `useConceptQueries.ts`, `useConceptMutations.ts`, `useTaskPolling.ts`).
        *   Import and call `useNetworkStatus`: `const networkStatus = useNetworkStatus();`.
        *   **Mutations:** Inside the main mutation function (`generateConceptMutation`, `refineConceptMutation`, etc.), add an early check:
            ```typescript
            if (!networkStatus.isOnline) {
              errorHandler.setError("You are offline. Cannot perform this action.", 'network');
              // Optionally throw an error to stop the mutation
              throw new Error("Offline");
              // Or return early if the mutation hook handles this state
            }
            ```
        *   **Queries (`useQuery`):** Modify the `enabled` option:
            ```typescript
            enabled: !!userId && networkStatus.isOnline, // Only enable fetching if online
            ```
            Consider adding `refetchOnReconnect: true` to automatically refetch when coming back online.
        *   **Polling (`useTaskPolling`):** Modify the `enabled` check:
            ```typescript
            const shouldPoll = Boolean(enabled && taskId && !cachedTask && networkStatus.isOnline);
            ```

    2.  **Review `OfflineStatus` Banner (`components/ui/OfflineStatus.tsx`):**
        *   Visually inspect the banner on different screen sizes and pages.
        *   Ensure the `position` prop (`top` or `bottom`) doesn't obstruct critical UI elements like the header or action buttons. Adjust `z-index` if necessary.
        *   Test the "Retry" button functionality. Ensure `isAnimating` state works correctly.
        *   Verify the messages (`offlineMessage`, `slowConnectionMessage`) are clear.

---

**31. Constants and Configuration Management**

*   **Goal:** Reduce magic strings, centralize config.

*   **Steps:**
    1.  **Backend Constants (`backend/app/core/constants.py`):**
        *   Create the file `backend/app/core/constants.py`.
        *   Define constants:
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
        *   **Refactor:** Go through backend code (`services/`, `api/routes/`, `core/limiter/`) and replace hardcoded strings (like `"pending"`, `"concept_generation"`, bucket names, rate limit strings/endpoints) with imports from `app.core.constants`.

    2.  **Frontend Constants:**
        *   **API Endpoints (`frontend/my-app/src/config/apiEndpoints.ts`):**
            *   Create the file.
            *   Define endpoint constants:
                ```typescript
                export const API_ENDPOINTS = {
                  GENERATE_CONCEPT: '/concepts/generate-with-palettes',
                  REFINE_CONCEPT: '/concepts/refine',
                  TASK_STATUS: (taskId: string) => `/tasks/${taskId}`,
                  EXPORT_IMAGE: '/export/process',
                  RECENT_CONCEPTS: '/storage/recent', // Check actual path
                  CONCEPT_DETAIL: (id: string) => `/storage/concept/${id}`, // Check actual path
                  RATE_LIMITS: '/health/rate-limits-status'
                };
                ```
            *   **Refactor:** Update `apiClient.ts`, mutation hooks (`useConceptMutations`, `useExportImageMutation`), query hooks (`useConceptQueries`), `task.ts`, and `rateLimitService.ts` to use these constants instead of hardcoded strings.
        *   **Query Keys (`frontend/my-app/src/config/queryKeys.ts`):**
            *   Create the file.
            *   Define query key factories:
                ```typescript
                export const queryKeys = {
                  concepts: {
                    all: () => ['concepts'] as const,
                    recent: (userId?: string, limit?: number) => [...queryKeys.concepts.all(), 'recent', userId, limit] as const,
                    detail: (id?: string, userId?: string) => [...queryKeys.concepts.all(), 'detail', id, userId] as const,
                  },
                  tasks: {
                    all: () => ['tasks'] as const,
                    detail: (id?: string) => [...queryKeys.tasks.all(), 'detail', id] as const,
                  },
                  rateLimits: () => ['rateLimits'] as const,
                };
                ```
            *   **Refactor:** Update all `useQuery`, `useMutation`, `queryClient.invalidateQueries`, `queryClient.setQueryData` calls throughout the hooks (`useConceptQueries`, `useTaskPolling`, `useRateLimitsQuery`, etc.) to use these key factories. Example: `queryKey: queryKeys.concepts.recent(userId, limit)`.

---
