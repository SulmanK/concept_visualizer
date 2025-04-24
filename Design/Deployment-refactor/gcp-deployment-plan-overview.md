---

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

---

**Phase 2: Setup GCP Infrastructure with Terraform (NEW)**

- **Goal:** Define and provision the core GCP infrastructure for `dev` and `prod` environments using Terraform.
- **Branch:** Can be done on `develop` or a dedicated `feature/infrastructure` branch off `develop`.

- **Files to Create/Modify:**

  1.  **Terraform Configuration:**
      - **Create:** Directory `terraform/`.
      - **Create:** `terraform/main.tf`: Define GCP provider, backend state configuration (e.g., GCS bucket - _note: state bucket itself might need manual creation or separate bootstrap_).
      - **Create:** `terraform/variables.tf`: Define input variables (project ID, region, environment name, naming prefixes).
      - **Create:** `terraform/outputs.tf`: Define outputs (VM IP/Name, Cloud Run Service Name, Pub/Sub Topic Name, Artifact Registry Repo name, etc.).
      - **Create:** `terraform/network.tf`: Define VPC (if not using default) and Firewall rules.
      - **Create:** `terraform/iam.tf`: Define Service Accounts (API, Worker) and IAM bindings (permissions for Secret Manager, Logging, Storage, Pub/Sub, Artifact Registry).
      - **Create:** `terraform/secrets.tf`: Define `google_secret_manager_secret` resources (placeholders for values to be added manually in GCP Console or via `gcloud`). Define `google_secret_manager_secret_iam_member` to grant access to service accounts.
      - **Create:** `terraform/artifact_registry.tf`: Define the Docker repository.
      - **Create:** `terraform/pubsub_lite.tf`: Define Pub/Sub Lite reservation, topics (`dev`, `prod`), and subscriptions.
      - **Create:** `terraform/cloud_run.tf`: Define `google_cloud_run_v2_service` resources for workers (`dev`, `prod`). Initially, you might use a simple public placeholder image (like `hello-world`) or skip setting the image. Configure triggers, environment variables (referencing secrets), CPU/memory (start low), scaling (min 0, max based on free tier/needs).
      - **Create:** `terraform/compute.tf`: Define `google_compute_instance_template` for the API VM (initially using a basic public image or OS image, configure service account, network, machine type `e2-micro`, region, basic startup script if needed). Define `google_compute_instance_group_manager` (size 1, using the template). Define `google_compute_address` for a static IP (optional, costs extra). Define Load Balancer resources (optional, costs extra).
      - **Create:** `terraform/environments/dev.tfvars` and `terraform/environments/prod.tfvars`: Define environment-specific variable values (e.g., `environment="dev"`, different naming prefixes).
      - **Create:** `.gitignore` inside `terraform/`: Ignore `.terraform/`, `*.tfstate`, `*.tfstate.backup`, `*.tfvars` (if not committing variables).
  2.  **README for Terraform:**
      - **Create:** `terraform/README.md`: Explain how to set up GCP credentials for Terraform, how to use workspaces (`terraform workspace new dev`), and the `init/plan/apply` workflow for each environment.
  3.  **Actions:**
      - Install Terraform.
      - Authenticate `gcloud` CLI.
      - Run `terraform init`.
      - Run `terraform workspace new dev` (and `prod`).
      - Run `terraform plan -var-file=environments/dev.tfvars` and `terraform apply -var-file=environments/dev.tfvars` (repeat for `prod`).
      - Manually populate secret values in GCP Secret Manager.

---

**Phase 3: Implement Deployment Architecture (Feature Branch)**

- **Goal:** Refactor backend to use Pub/Sub Lite + Cloud Run Worker.
- **Branch:** Create a new feature branch off `develop` (e.g., `feature/async-workers`).

- **Files to Create/Modify:**

  1.  **Dependencies:**

      - **Modify:** `backend/pyproject.toml`: Add `google-cloud-pubsub`. Remove `celery` if it was added previously.
      - **Action:** Run `uv pip install google-cloud-pubsub`.

  2.  **Configuration:**

      - **Modify:** `backend/app/core/config.py`: Add settings like `PUB_SUB_PROJECT_ID`, `PUB_SUB_TOPIC_ID_DEV`, `PUB_SUB_TOPIC_ID_PROD`. Add config for worker environment (e.g., reading Supabase keys from env vars).
      - **Modify:** `backend/.env.example` and `backend/.env`: Add new Pub/Sub variables.

  3.  **API Route Refactoring:**

      - **Modify:** `backend/app/api/routes/concept/generation.py` and `backend/app/api/routes/concept/refinement.py`:
        - Remove `BackgroundTasks` import and usage.
        - Import `pubsub_v1` from `google.cloud`.
        - Instantiate `pubsub_v1.PublisherClient()`.
        - Get the correct topic path based on `settings.ENVIRONMENT`.
        - After successfully creating the task record in the DB (using `TaskService`), construct a JSON payload (as bytes) with all necessary info (`task_id`, `user_id`, `logo_description`, `theme_description`, `original_image_url` etc.).
        - Use `publisher.publish(topic_path, data=json_payload_bytes)` to send the message.
        - Ensure the API endpoint returns `202 Accepted` status code along with the `task_id`.
      - **Pre-commit:** Apply code quality tools. Add/update docstrings explaining the new async flow.

  4.  **Worker Logic:**

      - **Create:** Directory `backend/cloud_run/worker/` (or `backend/cloud_functions/image_processor/`).
      - **Create:** `backend/cloud_run/worker/main.py`:
        - Define the main function triggered by Pub/Sub (e.g., `process_task(event, context)` for Cloud Functions, or a script that listens/processes if run as a service in Cloud Run).
        - Import necessary services (`TaskService`, `ConceptService`, `ImageService`, etc.) and utilities.
        - Add logic to parse the incoming Pub/Sub message data (decode JSON).
        - Add logic to **initialize services** needed by the worker _within the function scope_. Read necessary configurations (Supabase URL/Key, Jigsaw Key) from environment variables (these will be set during deployment).
        - Call `task_service.update_task_status` to set status to `processing`.
        - Include the core image generation/refinement logic (moved from the old `BackgroundTasks` functions). This involves calling JigsawStack, processing results, uploading to Supabase Storage.
        - Add robust `try...except...finally` blocks.
        - On success, call `task_service.update_task_status` with `completed` and the `result_id` (the ID of the newly created/updated `concepts` record).
        - On failure, call `task_service.update_task_status` with `failed` and the `error_message`.
      - **Create:** `backend/cloud_run/worker/requirements.txt`: List dependencies _only_ needed by the worker (e.g., `google-cloud-pubsub`, `supabase-py`, `httpx`, `Pillow`, `opencv-python`). _Do not include FastAPI, Uvicorn._
      - **Pre-commit:** Apply code quality tools to `main.py`. Add docstrings.

  5.  **Worker Dockerfile (If using Cloud Run):**
      - **Create:** `backend/Dockerfile.worker`:
        - Use a Python base image (e.g., `python:3.11-slim`).
        - Set working directory.
        - Copy `cloud_run/worker/requirements.txt`.
        - Install dependencies using `pip install -r requirements.txt --no-cache-dir`.
        - Copy the worker source code (`cloud_run/worker/`).
        - Define the `CMD` or `ENTRYPOINT` to run your `main.py` script.

---

**Phase 4: Update/Add Tests for New Architecture (Feature Branch)**

- **Goal:** Test the new async flow and worker logic.

- **Files to Create/Modify:**

  1.  **Backend Integration Tests (API):**

      - **Modify:** `backend/app/api/routes/__tests__/concept_test.py` (and refinement test):
        - Change assertions to expect `status_code == 202`.
        - Assert that the response body contains a `task_id`.
        - Remove assertions about the immediate return of concept data.
      - **Create/Modify:** `backend/app/api/routes/__tests__/task_test.py`: Add robust tests for the `GET /api/tasks/{task_id}` endpoint. Simulate different task statuses by mocking `TaskService.get_task`.

  2.  **Worker Tests:**

      - **Create:** `backend/cloud_run/worker/test_main.py` (or similar):
        - **Unit Tests:** Create mock Pub/Sub event data. Mock all external calls (`JigsawStackClient`, `SupabaseClient`, `TaskService`, `ImagePersistenceService`, `ConceptPersistenceService`). Call the worker's main handler function directly and assert that it calls the mocked services with correct arguments and updates task status appropriately for success and failure scenarios.
        - **(Advanced) Integration Tests:** Use `pytest`. Potentially use `google-cloud-pubsub[emulator]` to test against a local Pub/Sub emulator. Write tests that publish a message and assert that the worker function interacts correctly with a _test_ Supabase DB (requires careful setup/teardown or mocking at the DB client level) and mocked JigsawStack.
      - **Pre-commit:** Apply code quality tools.

  3.  **Frontend E2E Tests:**
      - **Modify:** `frontend/my-app/tests/e2e/concept-generation.spec.ts` and `concept-refinement.spec.ts`:
        - After submitting the form, assert that a "processing" state appears in the UI (e.g., check for the `TaskStatusBar` component).
        - _Instead of_ waiting for the `ConceptResult` component directly, implement a polling mechanism within the test (or wait for a specific UI element change triggered by polling/Realtime) that checks the `TaskStatusBar` until it shows "completed". You might need to add `data-testid` attributes to the status bar for reliable selection.
        - Once completed, assert that the final `ConceptResult` (or `ComparisonView`) is displayed with the expected image/data. Update `mockApi` fixtures to include handlers for the task status endpoint (`/api/tasks/{task_id}`).

---

**Phase 5: Full CI/CD Setup & Deployment (Merge to `develop`)**

- **Goal:** Automate building, testing, and deployment onto the Terraform-managed infrastructure.
- **Branch:** Merge `feature/async-workers` into `develop`.

- **Files to Create/Modify:**

  1.  **CI Pipeline:**
      - **Modify:** `.github/workflows/ci.yml` (or equivalent): Add steps to run worker tests. Add steps to build API and Worker Docker images (or package function code). Optionally add `terraform plan` check using the _dev_ workspace/vars.
      - **Pre-commit:** `check-yaml`.
  2.  **CD Pipeline:**
      - **Create:** `.github/workflows/deploy_dev.yml`, `.github/workflows/deploy_prod.yml`:
        - **Backend Deploy Job:** Authenticate to GCP. Retrieve secrets. Push images to Artifact Registry. Use `gcloud` commands to deploy:
          - `gcloud run deploy DEV/PROD_WORKER_SERVICE_NAME --image=... --update-env-vars=... --update-secrets=...` (Target the service name defined in Terraform).
          - `gcloud compute instances update-container DEV/PROD_VM_NAME --container-image=... --container-env=... --container-mount-secret=...` (Target the VM name defined in Terraform).
        - **Frontend Deploy Job:** Managed by Vercel. Ensure Vercel env vars are set for `develop` (preview) and `main` (production) branches.
      - **Pre-commit:** `check-yaml`.

---

**Phase 6: Update Documentation (on `develop` or `main`)**

- **Goal:** Document the final, deployed architecture.
- **Branch:** Update docs on `develop`, then merge to `main`.

- **Files to Create/Modify:**

  1.  **Architecture:**
      - **Modify:** `README.md` (root), `docs/README.md`, `docs/backend/README.md`: Update architecture descriptions and diagrams to show API VM, Pub/Sub, Cloud Run/Function worker.
  2.  **Backend Documentation:**
      - **Modify:** `docs/backend/api/routes/concept.md`: Update generation/refinement endpoints to reflect the `202 Accepted` response and task ID.
      - **Create/Modify:** `docs/backend/api/routes/tasks.md`: Document the task status endpoint (`GET /api/tasks/{task_id}`).
      - **Create:** `docs/backend/worker.md` (or similar): Document the Cloud Run/Function worker, its purpose, triggers, dependencies, and environment configuration.
      - **Create/Modify:** `docs/backend/core/task_queue.md`: Explain the Pub/Sub Lite setup and message format.
  3.  **Deployment Guide:**
      - **Create:** `docs/deployment.md`: Provide detailed steps on setting up the required GCP resources (VM, Pub/Sub Lite, Cloud Run/Function, IAM, Secrets, Firewall) and explain how the CI/CD pipeline works. Include instructions for configuring Vercel.
  4.  **Frontend Documentation:**
      - **Modify:** `docs/frontend/README.md`, `docs/frontend/hooks.md`: Explain how the frontend handles the asynchronous task flow (initiating state, polling or Realtime updates via TaskContext/hooks).

---
