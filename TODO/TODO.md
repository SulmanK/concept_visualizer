Okay, let's outline a design plan to switch your worker architecture from Cloud Run Service to **Cloud Functions (2nd Gen, container-based)**, focusing on simplicity and aligning with your "run-to-completion" goal.

**Goal:** Replace the long-running Cloud Run Service worker with an event-driven Cloud Function (2nd Gen) that processes one Pub/Sub message per invocation and then terminates.

**I. Backend Code Changes (`backend/cloud_run/worker/`)**

1.  **Modify `requirements.txt`:**

    - **Add:** `functions-framework` (e.g., `functions-framework>=3.0.0`)
    - **Keep:** Existing dependencies (`google-cloud-pubsub`, `supabase`, `httpx`, `Pillow`, `opencv-python`, etc.)

2.  **Refactor `main.py`:**

    - **Remove:** The `if __name__ == "__main__":` block that starts the `subscriber.subscribe()` loop.
    - **Import:** `import functions_framework`.
    - **Define Entry Point:** Create a function decorated with `@functions_framework.cloud_event`. This function will be triggered by Pub/Sub messages.

      ```python
      import base64
      import json
      import logging
      import asyncio
      import functions_framework
      # ... other imports ...

      # Keep initialize_services() and process_pubsub_message()

      @functions_framework.cloud_event
      def handle_pubsub(cloud_event):
          """
          Cloud Function entry point triggered by Pub/Sub CloudEvents.
          """
          logger = logging.getLogger("concept-worker-function")
          try:
              # Extract and decode the Pub/Sub message data
              if 'message' not in cloud_event.data or 'data' not in cloud_event.data['message']:
                  logger.error("Invalid CloudEvent format: Missing message data.")
                  # Acknowledge implicitly by returning, or raise to potentially trigger retry
                  return

              message_data_base64 = cloud_event.data['message']['data']
              message_data_bytes = base64.b64decode(message_data_base64)
              message = json.loads(message_data_bytes.decode('utf-8'))
              task_id = message.get('task_id', 'UNKNOWN')
              logger.info(f"Processing Pub/Sub message for task ID: {task_id}")

              # Initialize services *per invocation*
              services = initialize_services()

              # Run the async processing logic
              # Using asyncio.run is suitable for Cloud Functions entry points
              asyncio.run(process_pubsub_message(message, services))

              logger.info(f"Successfully processed task ID: {task_id}")
              # Function completes, execution environment terminates

          except Exception as e:
              task_id = message.get('task_id', 'UNKNOWN') if 'message' in locals() else 'UNKNOWN'
              logger.error(f"FATAL error processing task {task_id}: {e}", exc_info=True)
              # Re-raising signals failure to the platform for potential retries
              raise
      ```

    - **Ensure:** `initialize_services()` reads configuration (API keys, URLs) from _environment variables_ set during deployment, not from `.env` files.

**II. Worker Dockerfile Changes (`backend/Dockerfile.worker`)**

1.  **Install Dependencies:** Ensure `functions-framework` is installed via `requirements.txt`.
2.  **Set Entry Point (Optional but Recommended):** While Cloud Functions often infers it, explicitly setting the entry point via environment variables can be clearer. The deployment command (`gcloud functions deploy`) is usually the primary way to set the entry point.
3.  **`CMD` Instruction:** The standard `CMD` for the Python Functions Framework is recommended. This starts the framework's web server which listens for invocation requests.

    ```dockerfile
    # ... (FROM, WORKDIR, apt-get installs, COPY requirements.txt, RUN pip install) ...

    COPY app/ app/ # Make sure necessary shared code is copied if needed
    COPY cloud_run/worker/ worker/ # Copy the worker code

    # Set environment variable for the framework (optional but good practice)
    # Replace 'handle_pubsub' if your function name is different
    ENV FUNCTION_TARGET=handle_pubsub
    ENV FUNCTION_SIGNATURE_TYPE=cloudevent

    # Run the Functions Framework entry point
    # Default port is 8080, which Cloud Functions expects
    CMD ["functions-framework", "--target=${FUNCTION_TARGET}", "--signature-type=${FUNCTION_SIGNATURE_TYPE}"]
    ```

    _Note: Double-check the exact `CMD` required by the specific version of `functions-framework` and the GCP Python runtime environment._

**III. Terraform Configuration Changes (`terraform/`)**

1.  **Remove Cloud Run Service (`cloud_run.tf`):**

    - Delete the `google_cloud_run_v2_service.worker` resource.
    - Delete the `google_cloud_run_v2_service_iam_member.worker_invoker` resource.

2.  **Remove Eventarc Trigger (`cloud_run.tf` or `pubsub.tf`):**

    - Delete the `google_eventarc_trigger.worker_trigger` resource.
    - Delete the `google_project_service_identity.run_agent` if it's only used by Eventarc for the Run service.

3.  **Add Cloud Function Resource (e.g., in `cloud_function.tf` or reuse `cloud_run.tf`):**

    ```terraform
    # terraform/cloud_function.tf (or similar)

    resource "google_cloudfunctions2_function" "worker_function" {
      project  = var.project_id
      name     = "${var.naming_prefix}-worker-${var.environment}"
      location = var.region

      build_config {
        runtime     = "python311" # Match your Dockerfile base
        entry_point = "handle_pubsub" # Must match the function name in main.py
        # We'll deploy using a pre-built container image from Artifact Registry
        # Source block is omitted when using docker_repository/docker_image
      }

      service_config {
        max_instance_count = var.worker_max_instances # Use existing vars
        min_instance_count = var.worker_min_instances # Use existing vars
        available_memory   = var.worker_memory        # Use existing vars
        # available_cpu      = var.worker_cpu # Uncomment if you need specific CPU
        timeout_seconds    = 300 # Adjust as needed (max 540 for HTTP, 3600 for event)
        service_account_email = google_service_account.worker_service_account.email

        environment_variables = {
          # Copy necessary non-secret ENV VARS from the old cloud_run.tf
          ENVIRONMENT                     = var.environment
          GCP_PROJECT_ID                  = var.project_id
          CONCEPT_STORAGE_BUCKET_CONCEPT  = "${var.naming_prefix}-concept-images-${var.environment}"
          CONCEPT_STORAGE_BUCKET_PALETTE  = "${var.naming_prefix}-palette-images-${var.environment}"
          CONCEPT_DB_TABLE_TASKS          = "tasks_${var.environment}"
          CONCEPT_DB_TABLE_CONCEPTS       = "concepts_${var.environment}"
          CONCEPT_DB_TABLE_PALETTES       = "color_variations_${var.environment}"
          CONCEPT_LOG_LEVEL               = (var.environment == "prod" ? "INFO" : "DEBUG")
          CONCEPT_UPSTASH_REDIS_PORT      = "6379"
        }

        secret_environment_variables {
          key        = "CONCEPT_SUPABASE_URL"
          project_id = var.project_id
          secret     = google_secret_manager_secret.supabase_url.secret_id
          version    = "latest"
        }
        secret_environment_variables {
          key        = "CONCEPT_SUPABASE_KEY"
          project_id = var.project_id
          secret     = google_secret_manager_secret.supabase_key.secret_id
          version    = "latest"
        }
        secret_environment_variables {
          key        = "CONCEPT_SUPABASE_SERVICE_ROLE"
          project_id = var.project_id
          secret     = google_secret_manager_secret.supabase_service_role.secret_id
          version    = "latest"
        }
         secret_environment_variables {
          key        = "CONCEPT_SUPABASE_JWT_SECRET"
          project_id = var.project_id
          secret     = google_secret_manager_secret.supabase_jwt_secret.secret_id
          version    = "latest"
        }
        secret_environment_variables {
          key        = "CONCEPT_JIGSAWSTACK_API_KEY"
          project_id = var.project_id
          secret     = google_secret_manager_secret.jigsaw_key.secret_id
          version    = "latest"
        }
        secret_environment_variables {
          key        = "CONCEPT_UPSTASH_REDIS_ENDPOINT"
          project_id = var.project_id
          secret     = google_secret_manager_secret.redis_endpoint.secret_id
          version    = "latest"
        }
        secret_environment_variables {
          key        = "CONCEPT_UPSTASH_REDIS_PASSWORD"
          project_id = var.project_id
          secret     = google_secret_manager_secret.redis_password.secret_id
          version    = "latest"
        }
        # Note: No ingress settings needed for Pub/Sub trigger
      }

      event_trigger {
        trigger_region = var.region # Or "global" if appropriate
        event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
        pubsub_topic   = google_pubsub_topic.tasks_topic.id # Use .id for full path
        retry_policy   = "RETRY_POLICY_RETRY" # Or RETRY_POLICY_DO_NOT_RETRY
        # service_account_email = google_service_account.worker_service_account.email # SA for trigger
      }

      depends_on = [
         google_secret_manager_secret_iam_member.worker_sa_can_access_secrets,
         google_pubsub_topic.tasks_topic
         # Add other dependencies if needed (e.g., Artifact Registry repo)
         google_artifact_registry_repository.docker_repo
      ]
    }

    # Grant the Pub/Sub service account token creator role on the worker SA
    # This allows Pub/Sub to create tokens to invoke the Cloud Function
    resource "google_project_iam_member" "pubsub_sa_invoker" {
      project = var.project_id
      role    = "roles/iam.serviceAccountTokenCreator"
      # This member format is specific to the Pub/Sub service agent
      member  = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
    }
    ```

4.  **Update IAM (`iam.tf` - Verify):**

    - The `worker_service_account` still needs roles like `secretmanager.secretAccessor`, `storage.objectAdmin`, `logging.logWriter`, `monitoring.metricWriter`. These should already be present.
    - The Pub/Sub Subscriber role (`roles/pubsub.subscriber` for the worker SA) might no longer be strictly necessary if the function uses the push subscription implicitly managed by the trigger, but it doesn't hurt to leave it.
    - **Add** the `roles/iam.serviceAccountTokenCreator` role for the _Pub/Sub Service Agent_ (`service-${PROJECT_NUMBER}@gcp-sa-pubsub.iam.gserviceaccount.com`) on the _worker service account_ (`worker_service_account`) as shown in the Terraform snippet above. This is crucial for Pub/Sub triggered functions.

5.  **Update Outputs (`outputs.tf`):**

    - Remove outputs related to the Cloud Run Service (`worker_service_name`, `worker_service_region`, `worker_service_url`).
    - Add outputs for the Cloud Function:

      ```terraform
      output "worker_function_name" {
        description = "Name of the Cloud Function worker."
        value       = google_cloudfunctions2_function.worker_function.name
      }

      output "worker_function_region" {
        description = "Region of the Cloud Function worker."
        value       = google_cloudfunctions2_function.worker_function.location
      }
      # Add other relevant outputs if needed
      ```

**IV. GitHub Actions Workflow Changes**

1.  **`ci-tests.yml`:**

    - The `build-push-images` job remains essentially the same. It builds the `Dockerfile.worker` and pushes the image to Artifact Registry tagged with the SHA and `latest`. This image will be used by the Cloud Function deployment.

2.  **`deploy_backend.yml`:**

    - **Trigger (`workflow_run`):** Remains the same.
    - **Deployment Step for Worker:** Replace the `gcloud run deploy` step for the worker with `gcloud functions deploy`.

      ```yaml
      # --- REMOVE THIS Cloud Run Worker Deployment Step ---
      # - name: Deploy Cloud Run Worker
      #   run: |
      #     IMAGE_URL="${{ env.ARTIFACT_REGISTRY_REPO_NAME }}/concept-worker-${{ env.ENVIRONMENT }}:${{ github.sha }}"
      #     SERVICE_NAME="${{ env.NAMING_PREFIX }}-worker"
      #     gcloud run deploy "$SERVICE_NAME" --image="$IMAGE_URL" --region="${{ env.REGION }}" --project="${{ env.GCP_PROJECT_ID }}" --quiet

      # --- ADD THIS Cloud Function Deployment Step ---
      - name: Deploy Cloud Function Worker
        run: |
          FUNCTION_NAME="${{ env.NAMING_PREFIX }}-worker-${{ env.ENVIRONMENT }}"
          WORKER_IMAGE_URL="${{ env.ARTIFACT_REGISTRY_REPO_NAME }}/concept-worker-${{ env.ENVIRONMENT }}:${{ github.sha }}"
          TASKS_TOPIC_NAME="${{ env.NAMING_PREFIX }}-tasks-${{ env.ENVIRONMENT }}"
          WORKER_SA_EMAIL="${{ env.WORKER_SERVICE_ACCOUNT_EMAIL }}" # Need to add WORKER_SERVICE_ACCOUNT_EMAIL to secrets/env vars

          echo "Deploying Function: $FUNCTION_NAME"
          echo "Using Image: $WORKER_IMAGE_URL"
          echo "Trigger Topic: $TASKS_TOPIC_NAME"
          echo "Service Account: $WORKER_SA_EMAIL"

          # Construct --set-secrets argument dynamically
          SECRETS_ARG=""
          SECRETS_ARG+="CONCEPT_SUPABASE_URL=${{ env.NAMING_PREFIX }}-supabase-url-${{ env.ENVIRONMENT }}:latest,"
          SECRETS_ARG+="CONCEPT_SUPABASE_KEY=${{ env.NAMING_PREFIX }}-supabase-key-${{ env.ENVIRONMENT }}:latest,"
          SECRETS_ARG+="CONCEPT_SUPABASE_SERVICE_ROLE=${{ env.NAMING_PREFIX }}-supabase-service-role-${{ env.ENVIRONMENT }}:latest,"
          SECRETS_ARG+="CONCEPT_SUPABASE_JWT_SECRET=${{ env.NAMING_PREFIX }}-supabase-jwt-secret-${{ env.ENVIRONMENT }}:latest,"
          SECRETS_ARG+="CONCEPT_JIGSAWSTACK_API_KEY=${{ env.NAMING_PREFIX }}-jigsawstack-api-key-${{ env.ENVIRONMENT }}:latest,"
          SECRETS_ARG+="CONCEPT_UPSTASH_REDIS_ENDPOINT=${{ env.NAMING_PREFIX }}-redis-endpoint-${{ env.ENVIRONMENT }}:latest,"
          SECRETS_ARG+="CONCEPT_UPSTASH_REDIS_PASSWORD=${{ env.NAMING_PREFIX }}-redis-password-${{ env.ENVIRONMENT }}:latest"
          # Remove trailing comma if necessary

          gcloud functions deploy "$FUNCTION_NAME" \
            --gen2 \
            --region="${{ env.REGION }}" \
            --project="${{ env.GCP_PROJECT_ID }}" \
            --runtime=python311 `# Optional if using custom container` \
            --entry-point=handle_pubsub \
            --source=. `# This might need adjustment if source isn't needed with --image` \
            --image="$WORKER_IMAGE_URL" \
            --trigger-topic="$TASKS_TOPIC_NAME" \
            --service-account="$WORKER_SA_EMAIL" \
            --timeout=300s \
            --memory=512Mi `# Adjust as needed` \
            --min-instances=${{ env.WORKER_MIN_INSTANCES }} `# Need WORKER_MIN_INSTANCES env var` \
            --max-instances=${{ env.WORKER_MAX_INSTANCES }} `# Need WORKER_MAX_INSTANCES env var` \
            --set-env-vars="ENVIRONMENT=${{ env.ENVIRONMENT }},GCP_PROJECT_ID=${{ env.GCP_PROJECT_ID }},CONCEPT_STORAGE_BUCKET_CONCEPT=${{ env.NAMING_PREFIX }}-concept-images-${{ env.ENVIRONMENT }},CONCEPT_STORAGE_BUCKET_PALETTE=${{ env.NAMING_PREFIX }}-palette-images-${{ env.ENVIRONMENT }},CONCEPT_DB_TABLE_TASKS=tasks_${{ env.ENVIRONMENT }},CONCEPT_DB_TABLE_CONCEPTS=concepts_${{ env.ENVIRONMENT }},CONCEPT_DB_TABLE_PALETTES=color_variations_${{ env.ENVIRONMENT }},CONCEPT_LOG_LEVEL=$([[ "${{ env.ENVIRONMENT }}" == "prod" ]] && echo "INFO" || echo "DEBUG"),CONCEPT_UPSTASH_REDIS_PORT=6379" \
            --set-secrets="$SECRETS_ARG" \
            --quiet
        env:
          # Add variables needed for this step from the 'Set Environment Specifics' step
          WORKER_SERVICE_ACCOUNT_EMAIL: ${{ env.WORKER_SERVICE_ACCOUNT_EMAIL }} # Make sure this env var is set in the previous step
          WORKER_MIN_INSTANCES: ${{ env.WORKER_MIN_INSTANCES }} # Set this too
          WORKER_MAX_INSTANCES: ${{ env.WORKER_MAX_INSTANCES }} # Set this too
      ```

    - **Environment Variables:** Ensure the `Set Environment Specifics` step in `deploy_backend.yml` also sets `WORKER_SERVICE_ACCOUNT_EMAIL`, `WORKER_MIN_INSTANCES`, and `WORKER_MAX_INSTANCES` from secrets or defaults, similar to how you set other environment variables. You'll need the worker SA email for the `gcloud functions deploy` command.

**V. Scripts Changes**

- No direct changes needed to `gcp_apply.sh`, `gcp_destroy.sh`, or `gcp_populate_secrets.sh` as they operate on Terraform and environment files, which are being updated in step III.

This plan shifts your worker to a more appropriate architecture for its intended purpose, resolving the health check issue and aligning better with serverless best practices for event-driven tasks. Remember to test the Terraform changes (`terraform plan`) carefully before applying.

## Implementation Progress

The following changes have been implemented to migrate from Cloud Run Service to Cloud Functions (2nd Gen):

### Completed Tasks

- [x] Added `functions-framework>=3.0.0` to `backend/cloud_run/worker/requirements.txt`
- [x] Refactored `backend/cloud_run/worker/main.py` to remove the Cloud Run subscriber loop and add the Cloud Function handler
- [x] Updated the worker's `backend/Dockerfile.worker` to work with the Functions Framework
- [x] Created a new Terraform file for Cloud Functions configuration (`terraform/cloud_function.tf`)
- [x] Updated the outputs in `terraform/outputs.tf` to replace Cloud Run outputs with Cloud Function outputs
- [x] Modified `terraform/cloud_run.tf` to remove Cloud Run worker service and associated resources
- [x] Updated the GitHub Actions workflow file to deploy the Cloud Function instead of Cloud Run

### Remaining Tasks

- [ ] Test the Terraform changes using `terraform plan`
- [ ] Apply the Terraform changes
- [ ] Verify the Cloud Function is working correctly by checking logs and testing the functionality
- [ ] Clean up any remaining references to the old Cloud Run worker service

These changes have successfully migrated the worker architecture from a long-running Cloud Run Service to an event-driven Cloud Function (2nd Gen), which should resolve the health check issues and better align with serverless best practices for event-driven tasks.
