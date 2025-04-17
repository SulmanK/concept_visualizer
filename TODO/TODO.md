**Phase 1: Stabilize and Document Existing Code (+ Basic CI)**

*   **Goal:** Test and document the *current* FastAPI application with `BackgroundTasks`. Set up basic quality checks.
*   **Branch:** Start by creating a `develop` branch from your `main` branch. All work in this phase happens on `develop` or feature branches off it.

*   **Files to Create/Modify:**

    1.  **Backend Unit Tests:**
        *   **Create:**
            *   `backend/tests/services/test_concept_service.py`: Test core logic of `ConceptService` (mock Jigsaw, Supabase).
            *   `backend/tests/services/test_image_service.py`: Test image processing/storage logic (mock Supabase Storage, Pillow/CV2 if used directly).
            *   `backend/tests/services/test_task_service.py`: Test task creation/update logic (mock Supabase DB interactions).
            *   `backend/tests/services/test_persistence/test_concept_persistence_service.py`: Test DB interactions (mock Supabase client methods).
            *   `backend/tests/services/test_persistence/test_image_persistence_service.py`: Test Storage interactions (mock Supabase storage methods).
            *   `backend/tests/utils/test_*.py`: Test individual utility functions.
        *   **Tools:** `pytest`, `unittest.mock`.
        *   **Pre-commit:** Ensure tests pass `flake8`, `black`, `isort`, `mypy`. Add docstrings.

    2.  **Backend Integration Tests (API Level):**
        *   **Modify/Expand:**
            *   `backend/app/api/routes/__tests__/concept_test.py`: Test `POST /concepts/generate-with-palettes` and `POST /concepts/refine`. Verify they accept correct input and return `202 Accepted` (or the immediate result if not using BackgroundTasks yet). Mock the service layer (`ConceptService`).
            *   `backend/app/api/routes/__tests__/health_test.py`: Ensure health checks work.
            *   `backend/app/api/routes/__tests__/concept_storage_test.py` (if exists): Test storage routes.
            *   `backend/app/api/routes/__tests__/task_test.py` (if exists): Test task status routes.
        *   **Create:** Tests for any routes not yet covered.
        *   **Tools:** `pytest`, `fastapi.TestClient`.
        *   **Pre-commit:** Apply code quality tools.

    3.  **Frontend Tests:**
        *   **Unit/Integration (Vitest):**
            *   **Create/Modify:** `frontend/my-app/src/**/__tests__/*.test.tsx?`: Add tests for components rendering correctly, handling props, user interactions. Test hooks (`frontend/my-app/src/hooks/__tests__/*.test.ts`) with mocked API calls (using `mockApiService` or `vi.mock`).
        *   **E2E (Playwright):**
            *   **Modify/Expand:** `frontend/my-app/tests/e2e/*.spec.ts`: Ensure existing tests cover core flows (generation, maybe simple refinement stub). Use `mockApi` fixture to simulate backend responses *as they currently are*.
        *   **Pre-commit:** Ensure tests pass `eslint`, `prettier`, `tsc`.

    4.  **Documentation (Backend):**
        *   **Modify:** *All* `backend/app/**/*.py` files: Add/improve Google-style docstrings for modules, classes, methods, functions. Explain parameters, returns, raises.
        *   **Create/Modify:**
            *   `docs/backend/README.md`: High-level overview.
            *   `docs/backend/api/README.md`: Overview of API structure.
            *   `docs/backend/api/routes/*.md`: Detailed descriptions for *current* endpoints (concept, storage, health, tasks, auth, export). Include request/response examples.
            *   `docs/backend/services/*.md`: Explain the purpose and methods of each service (`concept`, `image`, `task`, `persistence`, `jigsaw`).
            *   `docs/backend/core/*.md`: Document configuration (`config.py`), exceptions (`exceptions.py`), core Supabase client (`client.py`), rate limiting (`limiter/`).
            *   `docs/backend/models/*.md`: Document key Pydantic models.
        *   **Pre-commit:** Ensure Markdown files are well-formed.

    5.  **Documentation (Frontend):**
        *   **Modify:** `frontend/my-app/src/**/*.ts(x)`: Add/improve JSDoc comments for component props, hooks, complex functions.
        *   **Create/Modify:**
            *   `docs/frontend/README.md`: High-level overview.
            *   `docs/frontend/components.md`: Document key UI components.
            *   `docs/frontend/hooks.md`: Document custom hooks.
            *   `docs/frontend/services.md`: Document `apiClient` and other service functions.
            *   `docs/frontend/state.md`: Explain state management (Contexts, React Query).
        *   **Pre-commit:** Ensure Markdown files are well-formed.

    6.  **Basic CI Setup:**
        *   **Create:** `.github/workflows/ci.yml` (or separate `backend_ci.yml`, `frontend_ci.yml`).
        *   **Content:** Define jobs for backend and frontend.
            *   Backend Job: Checkout code, setup Python/uv, install deps, run `flake8`, `black --check`, `isort --check`, `mypy`, `pytest` (unit & integration tests).
            *   Frontend Job: Checkout code, setup Node/npm, install deps (`npm ci`), run `eslint`, `tsc --noEmit`, `vitest run`.
        *   **Trigger:** On push/pull_request to `develop` branch.
        *   **Pre-commit:** Ensure YAML syntax is correct (`check-yaml`).