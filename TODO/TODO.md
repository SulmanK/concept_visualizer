**Phase 1: Stabilize and Document Existing Code (+ Basic CI)**

*   **Goal:** Test and document the *current* FastAPI application with `BackgroundTasks`. Set up basic quality checks.
*   **Branch:** Start by creating a `develop` branch from your `main` branch. All work in this phase happens on `develop` or feature branches off it.

*   **Files to Create/Modify:**

Okay, let's expand Phase 1 with a detailed list of test files to create/modify, organized using the recommended mirrored directory structure (`tests/app/...`). This covers unit and API integration tests for the existing codebase (before the Pub/Sub + Cloud Run refactor).

**Phase 1: Stabilize and Document Existing Code (+ Basic CI) - Expanded Test Plan**

*   **Goal:** Achieve solid test coverage and documentation for the current FastAPI application using `BackgroundTasks`.
*   **Branch:** Work on `develop` or feature branches off `develop`.
*   **Tools:** `pytest`, `unittest.mock`, `fastapi.TestClient`.
*   **Pre-commit:** Ensure all created/modified `.py` files pass `flake8`, `black`, `isort`, `mypy`, and have Google-style docstrings where appropriate. Ensure `.md` files are well-formed. Ensure `.yml` files pass `check-yaml`.

---

**A. Backend Unit Tests (Isolation & Mocking)**

*   **Location:** `backend/tests/app/...` mirroring `backend/app/...`
*   **Focus:** Test individual classes/functions, mocking external dependencies.

*   **Files to Create/Modify:**

    1.  **`tests/app/services/concept/test_concept_service.py`**:
        *   [x] Test `ConceptService.generate_concept`: Mock `JigsawStackClient.generate_image`, `ImagePersistenceService.store_image`, `ConceptPersistenceService.store_concept`, `_download_image`. Verify correct calls and data flow. Test `skip_persistence=True`. Test error handling from mocks.
        *   [x] Test `ConceptService.generate_concept_with_palettes`: Mock `generate_concept` (self-call), `PaletteGenerator.generate_palettes`, `ImageService.create_palette_variations`, `_download_image`. Verify logic flow and calls.
        *   [x] Test `ConceptService.refine_concept`: Mock `ConceptRefiner.refine`, `ImagePersistenceService.store_image`, `ConceptPersistenceService.store_concept`, `_download_image`. Verify calls and data flow.
        *   [x] Test `ConceptService.generate_color_palettes`: Mock `PaletteGenerator.generate_palettes`. Verify it delegates correctly.
        *   [x] Test `ConceptService.apply_palette_to_concept`: Mock `ImageService.apply_palette_to_image`, `ImagePersistenceService.store_image`, `_download_image`. Verify calls.
        *   [x] Test `ConceptService._download_image`: Mock `httpx.AsyncClient` and `os.path/open`. Test both URL and `file://` paths, test error handling.

    2.  **`tests/app/services/concept/test_generation.py`**:
        *   [x] Test `ConceptGenerator.generate`: Mock `JigsawStackClient.generate_image`, `JigsawStackClient.generate_color_palette`. Verify prompt construction (if any), API calls, response mapping to `GenerationResponse`. Test error handling.
        *   [x] Test `ConceptGenerator.generate_with_palettes`: Mock `JigsawStackClient.generate_multiple_palettes`, `JigsawStackClient.generate_image_with_palette`. Verify logic, calls, error handling (e.g., when image gen fails for one palette).

    3.  **`tests/app/services/concept/test_refinement.py`**:
        *   [x] Test `ConceptRefiner.refine`: Mock `JigsawStackClient.refine_image`, `JigsawStackClient.generate_color_palette`. Verify prompt construction, API calls, response mapping. Test error handling.

    4.  **`tests/app/services/concept/test_palette.py`**:
        *   [x] Test `PaletteGenerator.generate_palettes`: Mock `JigsawStackClient.generate_multiple_palettes`. Verify calls, response handling.
        *   [x] Test `PaletteGenerator.generate_single_palette`: Mock `JigsawStackClient.generate_color_palette`. Verify calls, response handling.

    5.  **`tests/app/services/export/test_export_service.py`**:
        *   [x] Test `ExportService.process_export`: Mock `ImageProcessingService.process_image`, `ImageProcessingService.convert_to_format`, `vtracer` library functions, `tempfile`, `os.unlink`. Test logic for different formats (`png`, `jpg`, `svg`) and sizes. Verify filename generation, content types. Test SVG parameter handling. Test error cases.

    6.  **`tests/app/services/image/test_image_service.py`**:
        *   [x] Test `ImageService.process_image`: Mock `ImageProcessingService.process_image`. Verify delegation.
        *   [x] Test `ImageService.store_image`: Mock `ImagePersistenceService.store_image`. Verify delegation.
        *   [x] Test `ImageService.convert_to_format`: Mock `ImageProcessingService.convert_to_format`. Verify delegation.
        *   [x] Test `ImageService.generate_thumbnail`: Mock `ImageProcessingService.generate_thumbnail`. Verify delegation.
        *   [x] Test `ImageService.extract_color_palette`: Mock `ImageProcessingService.extract_color_palette`. Verify delegation.
        *   [x] Test `ImageService.create_palette_variations`: Mock `ImageProcessingService.process_image` (for applying palette), `ImagePersistenceService.store_image`. Test loop logic, filename generation, metadata creation. Test error handling during loop.
        *   [x] Test `ImageService.apply_palette_to_image`: Mock `ImageProcessingService.process_image` (apply_palette operation).
        *   [x] Test `ImageService.get_image_async`: Mock `httpx.AsyncClient` and `ImagePersistenceService.get_image_async`. Test URL fetching and path fetching logic. Test caching logic if implemented.

    7.  **`tests/app/services/image/test_image_processing_service.py`**:
        *   [x] Test `ImageProcessingService.process_image`: Mock underlying `conversion` and `processing` functions. Test routing logic based on `operations` list.
        *   [x] Test `ImageProcessingService.convert_to_format`: Mock `conversion.convert_image_format`.
        *   [x] Test `ImageProcessingService.resize_image`: Mock `PIL.Image.open`, `resize`, `save`. Test logic for different aspect ratio scenarios.
        *   [x] Test `ImageProcessingService.generate_thumbnail`: Mock `conversion.generate_thumbnail`.
        *   [x] Test `ImageProcessingService.extract_color_palette`: Mock `processing.extract_dominant_colors`.
        *   [x] Test `ImageProcessingService.get_image_metadata`: Mock `conversion.get_image_metadata`.
        *   [x] Test `ImageProcessingService.apply_palette`: Mock `processing.apply_palette_with_masking_optimized`.

    8.  **`tests/app/services/image/test_conversion.py`**:
        *   [x] Test `detect_image_format`: Use sample image bytes of different types.
        *   [x] Test `convert_image_format`: Use sample image bytes, test conversions between PNG, JPG, WEBP. Check quality parameter effect.
        *   [x] Test `generate_thumbnail`: Use sample image bytes, test different sizes, aspect ratio preservation.
        *   [x] Test `get_image_metadata`: Use sample image bytes, verify extracted metadata.
        *   [x] Test `optimize_image`: Use sample image bytes, check output size, quality parameter.

    9.  **`tests/app/services/image/test_processing.py`**:
        *   [x] Test `hex_to_bgr`, `bgr_to_hex`, `hex_to_lab`.
        *   [x] Test `find_dominant_colors`: Use sample images (numpy arrays), mock `cv2.kmeans`. Verify color/percentage output.
        *   [x] Test `extract_dominant_colors`: Mock `PIL.Image.open`, `cv2.cvtColor`, `find_dominant_colors`. Verify end-to-end flow.
        *   [x] Test `create_color_mask`: Use sample images, test mask creation with different target colors and thresholds.
        *   [x] Test `apply_palette_with_masking_optimized`: Mock `cv2` functions, `download_image`. Test the complex logic of clustering, color mapping, blending.

    10. **`tests/app/services/jigsawstack/test_jigsawstack_service.py`**:
        *    [x] Test `JigsawStackService.generate_image`: Mock `JigsawStackClient.generate_image`. Verify correct arguments passed and result returned. Test error wrapping.
        *    [x] Test `JigsawStackService.refine_image`: Mock `JigsawStackClient.refine_image`. Verify args/result/errors.
        *    [x] Test `JigsawStackService.generate_color_palettes`: Mock `JigsawStackClient.generate_color_palettes` or `generate_multiple_palettes`. Verify args/result/errors.

    11. **`tests/app/services/jigsawstack/test_client.py`**:
        *    [x] Test `JigsawStackClient.generate_image`: Mock `httpx.AsyncClient.post`. Test payload construction, header usage, handling of success (JSON/binary), different error status codes (401, 429, 500), connection errors, timeouts. Test prompt enhancement logic.
        *    [x] Test `JigsawStackClient.refine_image`: Mock `httpx.AsyncClient.post`. Test payload, headers, success/error/timeout handling.
        *    [x] Test `JigsawStackClient.generate_multiple_palettes`: Mock `httpx.AsyncClient.post`. Test payload, headers, success/error/timeout handling. Test response parsing and fallback logic.
        *    [x] Test `JigsawStackClient.generate_image_with_palette`: Mock `generate_image`. Test prompt construction. Test handling of binary data vs URL.

    12. **`tests/app/services/persistence/test_concept_persistence_service.py`**:
        *    [x] Test `ConceptPersistenceService.store_concept`: Mock `ConceptStorage.store_concept`, `ConceptStorage.store_color_variations`. Test data preparation, calls to storage component. Test transaction logic (mock `_delete_concept`, test cleanup on variation storage failure).
        *    [x] Test `ConceptPersistenceService.get_concept_detail`: Mock `ConceptStorage.get_concept_detail`. Verify delegation and error handling (`NotFoundError`).
        *    [x] Test `ConceptPersistenceService.get_recent_concepts`: Mock `ConceptStorage.get_recent_concepts`, `ConceptStorage.get_variations_by_concept_ids`. Verify batch fetching logic.
        *    [x] Test `ConceptPersistenceService.delete_all_concepts`: Mock `ConceptStorage.delete_all_concepts`.
        *    [x] Test `ConceptPersistenceService.get_concept_by_task_id`: Mock `ConceptStorage.get_concept_by_task_id`.
        *    [x] Test `ConceptPersistenceService._delete_concept`: Mock `requests.delete`. Test deletion logic via service role key.

    13. **`tests/app/services/persistence/test_image_persistence_service.py`**:
        *   Test `ImagePersistenceService.store_image`: Mock `ImageStorage.upload_image`, `ImageStorage.create_signed_url`. Test path generation, content type detection, metadata handling, calls to storage component.
        *   Test `ImagePersistenceService.get_image`: Mock `ImageStorage.download_image`. Verify delegation and error handling (`ImageNotFoundError`).
        *   Test `ImagePersistenceService.delete_image`: Mock `ImageStorage.remove_image`.
        *   Test `ImagePersistenceService.get_signed_url`: Mock `ImageStorage.create_signed_url`.
        *   Test `ImagePersistenceService.get_image_url`: Test logic for handling existing URLs vs generating signed URLs.
        *   Test `ImagePersistenceService.get_image_async`: Mock `httpx.AsyncClient`, `get_image`. Test URL vs path logic, caching if implemented.

    14. **`tests/app/services/task/test_task_service.py`**:
        *   Test `TaskService.create_task`: Mock Supabase `client.table().insert().execute()`. Verify data inserted, ID generation, return value. Test using service role vs regular client.
        *   Test `TaskService.update_task_status`: Mock `client.table().update().eq().execute()`. Test different statuses, `result_id`, `error_message`. Test `TaskNotFoundError`.
        *   Test `TaskService.get_task`: Mock `client.table().select().eq().execute()`. Test found/not found cases.
        *   Test `TaskService.get_tasks_by_user`: Mock `client.table().select().eq().order().limit().execute()`. Test filtering by status, limit.
        *   Test `TaskService.delete_task`: Mock `get_task`, `client.table().delete().eq().execute()`. Test found/not found, deletion logic.
        *   Test `TaskService.get_task_by_result_id`: Mock `client.table().select().eq().execute()`.

    15. **`tests/app/core/limiter/test_redis_store.py`**:
        *   Test `RedisStore._make_key`.
        *   Test `RedisStore.increment`: Mock `redis.Redis.pipeline`. Verify INCRBY and EXPIRE calls. Test error handling.
        *   Test `RedisStore.get`: Mock `redis.Redis.get`. Test found/not found/error cases.
        *   Test `RedisStore.get_with_expiry`: Mock `redis.Redis.pipeline` (GET, TTL). Test value/ttl logic.
        *   Test `RedisStore.get_quota`: Mock `get_with_expiry`. Test quota calculation.
        *   Test `RedisStore.check_rate_limit`: Mock `get`, `increment`, `get_quota`. Test logic for allowed, denied, check_only. Test error handling.
        *   Test `RedisStore.reset`: Mock `redis.Redis.delete`.
        *   Test `RedisStore.clear_all`: Mock `redis.Redis.scan`, `redis.Redis.delete`.

    16. **`tests/app/core/limiter/test_keys.py`**:
        *   Test `get_user_id`: Mock `Request` with state, headers, remote address. Verify correct key (user vs ip).
        *   Test `get_endpoint_key`: Mock `Request` with/without route scope.
        *   Test `combine_keys`.
        *   Test `calculate_ttl`.
        *   Test `generate_rate_limit_keys`.

    17. **`tests/app/core/supabase/test_client.py`**:
        *   Test `SupabaseClient` init (mock `create_client`).
        *   Test `get_service_role_client` (mock `settings`, `create_client`).
        *   Test `SupabaseAuthClient` init.
        *   Test `verify_token` (mock `jwt.decode`, test valid, expired, invalid cases).
        *   Test `get_user_from_request` (mock `Request`, `verify_token`).

    18. **`tests/app/core/supabase/test_concept_storage.py`**:
        *   Test `ConceptStorage.store_concept`: Mock `client.table().insert().execute()` and `_store_concept_with_service_role`. Test data preparation, ID removal.
        *   Test `ConceptStorage._store_concept_with_service_role`: Mock `settings`, `requests.post`. Test direct API call logic.
        *   Test `ConceptStorage.store_color_variations`: Mock `client.table().insert().execute()` and `_store_variations_with_service_role`. Test data cleaning.
        *   Test `ConceptStorage._store_variations_with_service_role`: Mock `settings`, `requests.post`.
        *   Test `ConceptStorage.get_recent_concepts`: Mock client/service role methods. Verify filtering, ordering, limit. Ensure variations aren't fetched initially.
        *   Test `ConceptStorage._get_recent_concepts_with_service_role`: Mock `settings`, `requests.get`.
        *   Test `ConceptStorage.get_concept_detail`: Mock client/service role methods. Verify select includes variations.
        *   Test `ConceptStorage._get_concept_detail_with_service_role`: Mock `settings`, `requests.get` (for concept and variations).
        *   Test `ConceptStorage.delete_all_concepts`: Mock client method.
        *   Test `ConceptStorage.get_concept_by_task_id`: Mock client/service role methods.
        *   Test `ConceptStorage.get_variations_by_concept_ids`: Mock client/service role methods. Test grouping logic.
        *   Test `ConceptStorage._get_variations_by_concept_ids_with_service_role`: Mock `settings`, `requests.get`.

    19. **`tests/app/core/supabase/test_image_storage.py`**:
        *   Test `ImageStorage.upload_image_from_url`: Mock `requests.get`, `PIL.Image.open`, `client.storage.from_().upload`.
        *   Test `ImageStorage.get_image_url`: Mock `get_signed_url`.
        *   Test `ImageStorage.apply_color_palette`: Mock image download/upload logic, test path generation.
        *   Test `ImageStorage.delete_all_storage_objects`: Mock `client.storage.from_().list`, `remove`. Test user_id vs all logic.
        *   Test `ImageStorage.store_image`: Mock `create_supabase_jwt`, `requests.post`. Test path/content-type generation.
        *   Test `ImageStorage.upload_image`: Mock `create_supabase_jwt`, `requests.post`.
        *   Test `ImageStorage.download_image`: Mock `create_supabase_jwt`, `requests.get`.
        *   Test `ImageStorage.create_signed_url`: Mock `create_supabase_jwt`, `requests.post`. Test URL formatting fixes.

    20. **`tests/app/models/**/*.py`**:
        *   Create test files like `tests/app/models/concept/test_requests.py`.
        *   Test any custom Pydantic validators (e.g., `RefinementRequest.validate_preserve_aspects`).
        *   Test field constraints (min/max length, format).

    21. **`tests/app/utils/api_limits/test_*.py`**:
        *   Test `apply_rate_limit`, `apply_multiple_rate_limits` (mock `Request`, `settings`, limiter state/`check_rate_limit`). Verify logic and `HTTPException` raising.
        *   Test `store_rate_limit_info` decorator (mock `Request`, `check_rate_limit`). Verify state is updated.

    22. **`tests/app/utils/auth/test_user.py`**:
        *   Test `get_current_user_id`: Mock `Request` (state, headers, session).
        *   Test `get_current_user_auth`: Mock `HTTPAuthorizationCredentials`, `decode_token`.
        *   Test `get_current_user`.

    23. **`tests/app/utils/logging/test_setup.py`**:
        *   Test `setup_logging`: Mock `logging` module, `Path.mkdir`. Verify handlers and levels are set.
        *   Test `is_health_check`.

    24. **`tests/app/utils/security/test_mask.py`**:
        *   Test `mask_id`, `mask_path`, `mask_ip`, `mask_url`, `mask_key` with various valid and edge-case inputs.

    25. **`tests/app/utils/test_http_utils.py`**:
        *   Test `download_image`: Mock `httpx.AsyncClient`. Test success, HTTP errors, empty content.

    26. **`tests/app/utils/test_jwt_utils.py`**:
        *   Test `create_supabase_jwt`: Mock `settings`, `jose.jwt.encode`. Verify payload structure, expiry.
        *   Test `verify_jwt`: Mock `settings`, `jose.jwt.decode`. Test success, expired, invalid signature cases.
        *   Test `extract_user_id_from_token`: Mock `verify_jwt`, `decode_token`. Test different claim locations.
        *   Test `create_supabase_jwt_for_storage`: Mock `settings`, `jose.jwt.encode`. Verify payload.
        *   Test `decode_token`: Test valid/invalid base64, JSON parsing.

---

**B. Backend Integration Tests (API Level)**

*   **Location:** `backend/tests/app/api/routes/...`
*   **Focus:** Test API endpoints using `TestClient`, mocking the *immediate* service dependencies.

*   **Files to Create/Modify:**

    1.  **`tests/app/api/routes/concept/test_concept_endpoints.py`**:
        *   Test `POST /concepts/generate-with-palettes`: Use `TestClient`. Mock `CommonDependencies` (or `TaskService`, `ConceptService`). Verify 422 for invalid input. Verify 202 response with `task_id`. Check `TaskService.create_task` was called. *For Phase 1 with BackgroundTasks: Check if the background task function was added to the `BackgroundTasks` object.*
        *   Test `POST /concepts/refine`: Similar setup, test 202 response, task creation. *Phase 1: Check background task.*
        *   Test `GET /tasks/{task_id}`: Mock `TaskService.get_task`. Test 200, 404 responses. Check response structure matches `TaskResponse`. Test authentication requirement.

    2.  **`tests/app/api/routes/concept_storage/test_storage_endpoints.py`**:
        *   Test `GET /storage/recent`: Mock `ConceptPersistenceService.get_recent_concepts`. Use `TestClient` with auth headers/cookies. Verify response structure (`List[ConceptSummary]`), limit parameter handling.
        *   Test `GET /storage/concept/{concept_id}`: Mock `ConceptPersistenceService.get_concept_detail`. Test 200 (found) and 404 (not found). Verify response structure (`ConceptDetail`). Test auth/ownership logic by mocking the service to return data for a different user ID.

    3.  **`tests/app/api/routes/export/test_export_endpoints.py`**:
        *   Test `POST /export/process`: Mock `get_current_user`, `ExportService.process_export`, `ImagePersistenceService.get_image_async`. Use `TestClient`. Verify input validation (422). Verify correct content type and filename in headers. Test authentication and ownership check logic (mock `current_user`, provide path with different user ID).

    4.  **`tests/app/api/routes/health/test_health_endpoints.py`**:
        *   Test `GET /health/ping`.
        *   Test `GET /health/config`.
        *   Test `GET /health/rate-limits-status`: Mock limiter state or `check_rate_limit`. Verify response structure. Test authenticated vs unauthenticated responses.

    5.  **`tests/app/api/routes/auth/test_auth_endpoints.py`**:
        *   Test `/auth/signin-anonymous`, `/auth/refresh`, `/auth/signout` if they exist. Mock `SupabaseAuthClient`. Verify response structure and status codes.

    6.  **`tests/app/api/middleware/test_*.py`**:
        *   **`test_auth_middleware.py`**: Create a dummy FastAPI app with the middleware. Use `TestClient`. Test requests to public/protected paths with/without valid/invalid/expired auth headers. Verify `request.state.user` is set. Verify 401/500 responses.
        *   **`test_rate_limit_middleware.py`**: Test `RateLimitApplyMiddleware` and `RateLimitHeadersMiddleware`. Mock `check_rate_limit` or limiter state. Test requests to rate-limited endpoints. Verify 429 responses when limit exceeded. Verify `X-RateLimit-*` headers are correctly added by `RateLimitHeadersMiddleware` based on `request.state.limiter_info`. Test public path skipping.

---

This comprehensive list covers the key areas for testing in Phase 1, ensuring your existing code is robust before you introduce the architectural changes for deployment.