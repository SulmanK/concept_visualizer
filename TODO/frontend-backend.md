Okay, here are the implementation steps from the refactoring plan, broken down into actionable tasks. We'll skip the testing tasks for now as requested.

---

**Phase 1: Backend API Endpoint Creation**

**[x] Task 1: Create `GET /api/storage/concepts/recent` Endpoint**

- **File:** `backend/app/api/routes/concept_storage/storage_routes.py`
- **Action:** Define a new FastAPI route function (e.g., `get_recent_concepts_api`).
- **Decorator:** Use `@router.get("/recent", response_model=List[ConceptSummary])` (or an adapted `ConceptData` model for response).
- **Input:**
  - Accept an optional `limit: int = Query(10, ge=1, le=50)` query parameter.
  - Get `user_id: str = Depends(get_current_user_id)` from the authenticated request.
- **Dependencies:** Inject `ConceptPersistenceServiceInterface` and `ImagePersistenceServiceInterface`.
- **Logic:**
  1.  Call `concept_persistence_service.get_recent_concepts(user_id, limit)`.
  2.  Iterate through the returned concepts.
  3.  For each concept's `image_path`, call `image_persistence_service.get_signed_url(path, is_palette=False)` to get the base image URL. Store this in an `image_url` field.
  4.  Iterate through each concept's `color_variations`.
  5.  For each variation's `image_path`, call `image_persistence_service.get_signed_url(path, is_palette=True)` to get the variation image URL. Store this in the variation's `image_url` field.
  6.  Return the list of concepts with populated `image_url` fields.
- **Response Model:** Ensure the Pydantic response model used (e.g., `ConceptSummary` or a similar `ConceptData` adaptation) includes `image_url` for the base concept and nested `image_url` for variations.
- **Authentication:** Ensure the route is protected by the existing auth setup for the `/storage` router.

**[x] Task 2: Create `GET /api/storage/concept/{concept_id}` Endpoint**

- **File:** `backend/app/api/routes/concept_storage/storage_routes.py`
- **Action:** Define a new FastAPI route function (e.g., `get_concept_detail_api`).
- **Decorator:** Use `@router.get("/concept/{concept_id}", response_model=ConceptDetail)` (or an adapted `ConceptData` model).
- **Input:**
  - Accept `concept_id: str` as a path parameter.
  - Get `user_id: str = Depends(get_current_user_id)` from the authenticated request.
- **Dependencies:** Inject `ConceptPersistenceServiceInterface` and `ImagePersistenceServiceInterface`.
- **Logic:**
  1.  Call `concept_persistence_service.get_concept_detail(concept_id, user_id)`.
  2.  If the concept is not found (returns `None` or raises `NotFoundError`), raise an appropriate `HTTPException` (e.g., 404 Not Found).
  3.  If found, get the signed URL for the concept's `image_path` using `image_persistence_service.get_signed_url(path, is_palette=False)` and store it in `image_url`.
  4.  Iterate through the concept's `color_variations`.
  5.  For each variation's `image_path`, get the signed URL using `image_persistence_service.get_signed_url(path, is_palette=True)` and store it in the variation's `image_url`.
  6.  Return the processed concept data.
- **Response Model:** Ensure the Pydantic response model includes `image_url` for the base concept and variations.
- **Authentication:** Ensure the route is protected.

**[x] Task 3: Verify/Update Backend Persistence Services**

- **Files:**
  - `backend/app/services/persistence/concept_persistence_service.py`
  - `backend/app/services/persistence/image_persistence_service.py`
- **Action:**
  1.  **Concept Service:** Review `get_recent_concepts` and `get_concept_detail`. Confirm they primarily return data containing `image_path` (and `color_variations[].image_path`). They should _not_ be generating the final URLs themselves.
  2.  **Image Service:** Review `get_signed_url` in `ImagePersistenceService`. Ensure it correctly accepts `path` and `is_palette` (or equivalent logic to determine the bucket) and reliably returns a valid, usable signed URL with appropriate expiry.

---

**Phase 2: Frontend Refactoring**

**[x] Task 4: Create Frontend Service Functions**

- **File:** Create `src/services/conceptService.ts` (or modify `src/services/supabaseClient.ts`).
- **Action:**
  1.  Implement `fetchRecentConceptsFromApi(userId: string, limit: number = 10): Promise<ConceptData[]>`.
      - Inside, call `apiClient.get<ConceptData[]>(API_ENDPOINTS.RECENT_CONCEPTS, { params: { limit } })`.
      - Return `response.data`.
  2.  Implement `fetchConceptDetailFromApi(conceptId: string): Promise<ConceptData | null>`.
      - Inside, call `apiClient.get<ConceptData>(API_ENDPOINTS.CONCEPT_DETAIL(conceptId))`.
      - Handle potential 404s (maybe Axios throws, or check response status) and return `null` in that case.
      - Return `response.data` on success.
- **Update Config:** Add the new endpoint paths to `src/config/apiEndpoints.ts`:
  - `RECENT_CONCEPTS: '/storage/recent'` (Adjust path if different in backend)
  - `CONCEPT_DETAIL: (id: string) => \`/storage/concept/${id}\`` (Adjust path if different)

**[x] Task 5: Refactor `supabaseClient.ts` Functions**

- **File:** `src/services/supabaseClient.ts`
- **Action:**
  1.  Modify the existing `fetchRecentConcepts` function: Remove its current Supabase logic and replace it with a call to the new `fetchRecentConceptsFromApi` function created in Task 4.
  2.  Modify the existing `fetchConceptDetail` function: Remove its current Supabase logic and replace it with a call to the new `fetchConceptDetailFromApi` function.
  3.  **Crucially:** Remove the `batchProcessConceptsUrls` function entirely.
  4.  Remove any imports or direct `supabase.from(...)` calls related to the `concepts` or `color_variations` tables within these modified functions.

**[x] Task 6: Update React Query Hooks**

- **File:** `src/hooks/useConceptQueries.ts`
- **Action:**
  1.  **`useRecentConcepts`:** Verify its `queryFn` now correctly calls the refactored `fetchRecentConcepts` from `supabaseClient.ts` (which internally uses `apiClient`). No other changes should be strictly necessary, but consider updating the `queryKey` to maybe `['api', 'concepts', 'recent', userId, limit]` for clarity if desired.
  2.  **`useConceptDetail`:** Verify its `queryFn` now correctly calls the refactored `fetchConceptDetail` from `supabaseClient.ts`. Keep `userId` in the `queryKey` (`['concepts', 'detail', conceptId, userId]`).
  3.  Remove any post-fetch logic within these hooks that manually processes URLs (like calling `getSignedImageUrl` or similar). Trust the data coming from the (refactored) fetch functions.

**[x] Task 7: Update Frontend Components**

- **Files:** Review components like `ConceptCard.tsx`, `ConceptDetailPage.tsx`, `RecentConceptsSection.tsx`, `ResultsSection.tsx`, `OptimizedImage.tsx`, etc.
- **Action:**
  1.  Search the codebase for any remaining instances where `getSignedImageUrl` or `formatImageUrl` (or similar manual URL processing) is used for concept or variation images sourced from `useRecentConcepts` or `useConceptDetail`. Remove this logic.
  2.  Ensure these components directly use the `image_url` property (for both base concepts and variations) provided in the data fetched by the hooks.
  3.  Verify that `OptimizedImage` and standard `<img>` tags work correctly when passed the potentially long signed URLs returned by the backend.

---

**Phase 3: Cleanup (To be done after testing)**

**[x] Task 8: Code Cleanup**

- **File:** `src/services/supabaseClient.ts`
- **Action:** Once the new approach is verified and stable, completely remove the implementation of `batchProcessConceptsUrls` and any orphaned helper functions related to the old direct Supabase fetching logic for concepts.

---

This breakdown provides concrete steps for each part of the refactor. Remember to commit changes incrementally after completing related tasks.
