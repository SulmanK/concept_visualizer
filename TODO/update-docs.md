Okay, I've reviewed the codebase structure and the content of the files provided. Based on that, here's a list of documentation files in `docs/` that likely need updates, along with the reasons:

**I. Backend Documentation (`docs/backend/`)**

1.  **`docs/backend/api/routes/auth/auth_routes.md`**

    - **Reason:** The `AuthResponse` model described in the doc (with `user_id`, `token`, `expires_at`) is not the primary response type for the `/login` endpoint in `backend/app/api/routes/auth/auth_routes.py`. The code returns a `JSONResponse` with `{"authenticated": True, "user": UserObject}` and relies on session cookies implicitly handled by Supabase/FastAPI middleware. The `/session` endpoint is a GET, not a POST as might be implied by some auth flows.
    - **Update Needed:** Adjust the response model description for `/login` and clarify the session management mechanism. Ensure the `/session` endpoint description is accurate.

2.  **`docs/backend/api/routes/concept/generation.md`**

    - **Reason:** The `GenerationResponse` model described in the doc for the `/generate` endpoint has `color_palette: Optional[Dict[str, Any]] = None` (deprecated) and `variations: List[Dict[str, Any]] = []`. The actual code model `app.models.concept.response.GenerationResponse` uses `color_palette: Optional[ColorPalette]` (typed object) and `variations: List[PaletteVariation]` (typed list).
    - **Update Needed:** Update the type definition for `color_palette` and `variations` in the `GenerationResponse` section to match the Pydantic models in the code.

3.  **`docs/backend/api/routes/concept/refinement.md`**

    - **Reason:** Similar to generation, the document should accurately reflect the _final result structure_ of the refinement task. While the immediate response is `TaskResponse`, the task eventually produces a result whose structure (likely a `RefinementResponse` or `GenerationResponse`) should be documented.
    - **Update Needed:** Clarify the structure of the _completed task's result_ for the `/refine` endpoint.

4.  **`docs/backend/api/routes/concept_storage/storage_routes.md`**

    - **Reason:** The `/store` endpoint's `GenerationResponse` example in the doc might be too simplistic. The code (`backend/app/api/routes/concept_storage/storage_routes.py`) calls `concept_service.generate_concept`, then `concept_service.generate_color_palettes`, and `image_service.create_palette_variations`. The actual `GenerationResponse` model supports a `variations` list.
    - **Update Needed:** Update the response example for the `/store` endpoint to include the `variations: List[PaletteVariation]` field and ensure the description accurately reflects what this endpoint does regarding variations.

5.  **`docs/backend/api/routes/export/export_routes.md`**

    - **Reason:** The doc describes the response of `/export/process` as a dictionary. The code (`backend/app/api/routes/export/export_routes.py`) returns a `StreamingResponse`.
    - **Update Needed:** Change the response description to `StreamingResponse` and mention relevant headers like `Content-Disposition` for file download.

6.  **`docs/backend/api/middleware/rate_limit_apply.md`**

    - **Reason:** The `RATE_LIMIT_RULES` dictionary defined in the code (`backend/app/api/middleware/rate_limit_apply.py`) has more/different entries than what's listed in the documentation.
      - Doc: `/concepts/generate-with-palettes: "10/month"`, `/concepts/refine: "10/month"`, `/concepts/store: "10/month"`, `/storage/store: "10/month"`, `/storage/recent: "30/minute"`, `/storage/concept: "30/minute"`, `/export/process: "50/hour"`
      - Code: `/concepts/generate: "10/month"`, `/concepts/generate-with-palettes: "10/month"`, `/concepts/refine: "10/month"`, `/concepts/store: "10/month"`, `/storage/store: "10/month"`, `/storage/recent: "60/minute"`, `/storage/concept: "30/minute"`, `/export/process: "50/hour"`.
    - **Update Needed:** Update the `RATE_LIMIT_RULES` section to accurately reflect the rules defined in the code. Specifically, add `/concepts/generate` and correct the `/storage/recent` limit.

7.  **`docs/backend/models/concept/response.md`**

    - **Reason:**
      - The `GenerationResponse` model's `color_palette` field is typed as `Optional[Dict[str, Any]]` (deprecated) in the doc, but `Optional[ColorPalette]` (Pydantic model) in `app.models.concept.response.py`. The `variations` field is `List[Dict[str, Any]]` in doc vs `List[PaletteVariation]` in code.
      - The `ConceptSummary` and `ConceptDetail` models described in this doc might differ from what the API routes actually construct and return if they perform transformations on the domain models (`app/models/concept/domain.py`). The doc's `ConceptSummary` includes `color_variations: List[PaletteVariation]`, while the domain model `ConceptSummary` uses `List[ColorPalette]`.
    - **Update Needed:**
      - Correct the types for `color_palette` and `variations` in `GenerationResponse`.
      - Review and clarify the structure of `ConceptSummary` and `ConceptDetail` as _returned by API endpoints_. Ensure they accurately reflect the fields and types. For example, `ConceptSummary` in the doc has `has_variations` and `variations_count` which aren't directly in the Pydantic model and are likely computed.

8.  **`docs/backend/models/task/response.md`**

    - **Reason:** The `TaskResponse` model in the doc lists `type: Optional[str]`. In the code (`app/models/task/response.py`), it's `type: str`.
    - **Update Needed:** Change `type` to `str` in the documentation for consistency.

9.  **`docs/backend/services/concept/service.md`** (and potentially `generation.md`, `refinement.md`, `palette.md` which are more detailed)

    - **Reason:** The documentation for `ConceptService` methods like `generate_concept` often implies returning complex Pydantic objects (e.g., `Concept` or `GenerationResponse` directly from the models). However, the actual implementation in `app.services.concept.service.py` (and its sub-modules like `generation.py`) often returns `Dict[str, Any]`. For example, `generate_concept` returns a dict with `image_url`, `image_path`, `concept_id`, and `image_data`.
    - **Update Needed:** Revise the return type descriptions for methods in `ConceptService` and its constituent parts (`ConceptGenerator`, `ConceptRefiner`, `PaletteGenerator`) to reflect that they often return dictionaries, and detail the structure of these dictionaries.

10. **`docs/backend/services/image/service.md`**

    - **Reason:** Similar to `ConceptService`, the documented return types might not perfectly match the actual dictionary structures or primitive types returned by the methods in `app.services.image.service.py`. For instance, `store_image` returns `Tuple[str, str]`.
    - **Update Needed:** Review method signatures and return type descriptions, ensuring they match the code's behavior (e.g., `Tuple[str, str]` for `store_image`).

11. **`docs/backend/cloud_run/worker/main.md`** and **`docs/backend/cloud_run/worker/README.md`**
    - **Reason:** The backend deployment workflow (`.github/workflows/deploy_backend.yml`) uses `gcloud functions deploy ... --source="./backend"`. This means the worker is deployed as a Google Cloud Function (2nd Gen) using the source code from the entire `./backend` directory. The entry point is specified as `handle_pubsub` which is in `backend/cloud_run/worker/main.py` (re-exported by `backend/main.py`). The `Dockerfile.worker`, `wsgi.py`, and `Procfile` in `backend/cloud_run/worker/` seem to be for a different deployment method (perhaps older, or for local Gunicorn testing) and are not directly used by the GitHub Actions deployment command for the worker.
    - **Update Needed:** Clarify that the worker is deployed as a Cloud Function using source deployment. Explain the role of `backend/cloud_run/worker/main.py::handle_pubsub` as the entry point. The purpose of `Dockerfile.worker`, `wsgi.py`, and `Procfile` should be clarified (e.g., "for local testing with Gunicorn" or "for alternative Cloud Run service deployment").

**II. Frontend Documentation (`docs/frontend/`)**

1.  **`docs/frontend/api/task.md`**

    - **Reason:** The doc describes `getTask`, `getTaskStatus`, `cancelTask`, `getTaskResult`. The actual code in `frontend/my-app/src/api/task.ts` exports `fetchTaskStatus` and `cancelTask`. The type for tasks in the doc is `Task` interface, while the code uses `TaskResponse` from `api.types.ts`.
    - **Update Needed:** Update the described API functions to match `fetchTaskStatus` and `cancelTask`. Use the `TaskResponse` type definition.

2.  **`docs/frontend/services/conceptService.md`**

    - **Reason:** The document describes `fetchRecentConceptsFromApi` and `fetchConceptDetailFromApi`. The `ConceptData` type these functions use is defined in `frontend/my-app/src/services/supabaseClient.ts` and includes `color_variations`. The logging in the code confirms this.
    - **Update Needed:** Ensure the `ConceptData` structure, especially `color_variations`, is accurately described or referenced in this document.

3.  **`docs/frontend/contexts/AuthContext.md`**

    - **Reason:** The custom hooks (`useAuth`, `useAuthUser`, etc.) are now defined in `frontend/my-app/src/hooks/useAuth.ts`.
    - **Update Needed:** Update the "Exposed Hooks" section or usage examples to point to `hooks/useAuth.ts` as the source of these hooks.

4.  **`docs/frontend/contexts/TaskContext.md`**

    - **Reason:** The custom hooks for task context are now in `frontend/my-app/src/hooks/useTask.ts`.
    - **Update Needed:** Update the "Exposed Hooks" section or usage examples to point to `hooks/useTask.ts`.

5.  **`docs/frontend/hooks/useConceptMutations.md`**

    - **Reason:**
      - Hook names differ: Doc mentions `useCreateConcept`, `useRefineConcept`, `useDeleteConcept`, `useUpdateConcept`. Code in `useConceptMutations.ts` exports `useGenerateConceptMutation` and `useRefineConceptMutation`.
      - Request/Response types: Doc uses `CreateConceptRequest`, `RefineConceptRequest`, etc. Code uses `PromptRequest`, `RefinementRequest` (from `api.types.ts`) as input and `TaskResponse` as output for these mutations because they initiate backend tasks.
    - **Update Needed:** Update hook names to `useGenerateConceptMutation` and `useRefineConceptMutation`. Update the "Parameters" and "Return Value" sections for these hooks to use `PromptRequest`/`RefinementRequest` as input and `TaskResponse` as the direct mutation result. Explain that the `TaskResponse` will then be used to track the async operation. Remove or update descriptions for `useDeleteConcept` and `useUpdateConcept` if they are not implemented or have different names.

6.  **`docs/frontend/hooks/useConceptQueries.md`**

    - **Reason:**
      - `useRecentConcepts`: Doc says it returns `ConceptsResponse` (paginated). Code's `useRecentConcepts` in `useConceptQueries.ts` directly returns `ConceptData[]` (from `supabaseClient.ts`). Pagination might be handled differently or not in this specific hook.
      - `useConceptById`: Doc says it returns `Concept`. Code's `useConceptDetail` returns `ConceptData | null`.
      - `useConceptVersionHistory`: Mentioned in doc, but its implementation is not immediately obvious in the provided code scan for `useConceptQueries.ts`.
    - **Update Needed:** Adjust return types for `useRecentConcepts` and `useConceptById` to `ConceptData[]` and `ConceptData | null` respectively. Clarify if pagination is part of `useRecentConcepts`. Verify or remove `useConceptVersionHistory`.

7.  **`docs/frontend/components/ui/Button.md`**

    - **Reason:** The component in `frontend/my-app/src/components/ui/Button.tsx` is a custom Tailwind CSS-based button. The documentation describes props like `variant: 'primary' | 'secondary' | 'text'` and mentions MUI Button, which is not what's in the code. The code's variants are `primary`, `secondary`, `outline`, `ghost`.
    - **Update Needed:** Rewrite the documentation to accurately reflect the props, styling (Tailwind), and features of the custom `Button.tsx` component.

8.  **`docs/frontend/components/ui/Card.md`**

    - **Reason:** The component in `frontend/my-app/src/components/ui/Card.tsx` is a custom Tailwind CSS-based card. The documentation describes props like `elevation`, `hoverEffect`, `variant: 'outlined' | 'elevation'` and mentions MUI Card. The code's variants are `default`, `gradient`, `elevated` and hover effects are controlled differently.
    - **Update Needed:** Rewrite the documentation for the custom `Card.tsx` component, detailing its Tailwind-based styling and props.

9.  **`docs/frontend/components/ui/Input.md`** and **`docs/frontend/components/ui/TextArea.md`**
    - **Reason:** These components in the codebase (`Input.tsx`, `TextArea.tsx`) are custom Tailwind CSS components. The documentation seems to describe standard HTML inputs or MUI-like components.
    - **Update Needed:** Rewrite the documentation for these custom components, detailing their props (e.g., `startIcon`, `endIcon`, `animated` for `Input.tsx`) and Tailwind-based styling.

**III. Infrastructure Documentation (`terraform/` and root `README.md`)**

1.  **`terraform/README.md`**

    - **Reason:**
      - Mentions "Pub/Sub Lite" but `terraform/pubsub.tf` defines `google_pubsub_topic` and `google_pubsub_subscription`, which are standard Pub/Sub.
      - Mentions "Cloud Run worker service" but `terraform/cloud_function.tf` defines `google_cloudfunctions2_function`. `cloud_run.tf` is empty.
    - **Update Needed:** Change "Pub/Sub Lite" to "Pub/Sub". Change "Cloud Run worker service" to "Cloud Function (2nd Gen) worker".

2.  **Root `README.md`**
    - **Tech Stack section:**
      - Mentions "Cloud Run (Worker)". This should be "Google Cloud Functions (Gen 2) (Worker)".
    - **Deployment section (Backend):**
      - Mentions "Cloud Run (Worker)". Should be "Cloud Functions (Worker)".
    - **Infrastructure section:**
      - Mentions "Cloud Run (Worker)". Should be "Cloud Functions (Worker)".
    - **Update Needed:** Correct the "Cloud Run" references to "Google Cloud Functions (Gen 2)" for the worker component.

This list covers the most apparent discrepancies. A more in-depth, line-by-line review of each doc file against its corresponding code would likely reveal further minor areas for polish and accuracy. Focus on ensuring that props, return types, endpoint paths, and key architectural descriptions are current.
