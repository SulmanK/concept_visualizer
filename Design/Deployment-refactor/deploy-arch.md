**Phase 3: Implement Deployment Architecture (Feature Branch)**

- **Goal:** Refactor backend to use Pub/Sub Lite + Cloud Run Worker.
- **Branch:** Create a new feature branch off `develop` (e.g., `feature/async-workers`).

- **Files to Create/Modify:**

  1.  **Dependencies:**

      - **Modify:** `backend/pyproject.toml`: Add `google-cloud-pubsub`. Remove `celery` if it was added previously.
      - **Action:** Run `uv pip install google-cloud-pubsub`.

  2.  **Configuration:**

      - **Modify:** `backend/app/core/config.py`: Add settings like `PUB_SUB_TOPIC_ID": reading from the .env file calling CONCEPT_PUB_SUB_TOPIC_ID
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
