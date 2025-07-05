# terraform/cloud_function.tf

resource "google_cloudfunctions2_function" "worker_function" {
  project     = var.project_id
  name        = "${var.naming_prefix}-worker-${var.environment}"
  location    = var.region
  description = "Worker function for processing Concept Visualizer tasks"

  build_config {
    # Runtime is required even when deploying a container
    runtime     = "python311"
    entry_point = "handle_pubsub" # Must match the function name in main.py

    # Use the real placeholder bucket and object
    source {
      storage_source {
        bucket = google_storage_bucket.function_source_placeholder.name
        object = google_storage_bucket_object.placeholder_source_zip.name
      }
    }

    # Optionally specify the repository here, although the deploy command will use the full image path
    docker_repository = google_artifact_registry_repository.docker_repo.id # Use the repo ID
  }

  service_config {
    max_instance_count  = var.worker_max_instances
    min_instance_count  = var.worker_min_instances
    available_memory    = var.worker_memory
    timeout_seconds     = 540 # Increased timeout to 18 minutes to accommodate longer tasks
    service_account_email = google_service_account.worker_service_account.email

    environment_variables = {
      ENVIRONMENT                    = var.environment
      GCP_PROJECT_ID                 = var.project_id
      CONCEPT_STORAGE_BUCKET_CONCEPT = "concept-images-${var.environment}"
      CONCEPT_STORAGE_BUCKET_PALETTE = "palette-images-${var.environment}"
      CONCEPT_DB_TABLE_TASKS         = "tasks_${var.environment}"
      CONCEPT_DB_TABLE_CONCEPTS      = "concepts_${var.environment}"
      CONCEPT_DB_TABLE_PALETTES      = "color_variations_${var.environment}"
      CONCEPT_LOG_LEVEL              = (var.environment == "prod" ? "INFO" : "DEBUG")
      CONCEPT_UPSTASH_REDIS_PORT     = "6379"
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
  }

  event_trigger {
    trigger_region = var.region
    event_type     = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic   = google_pubsub_topic.tasks_topic.id
    retry_policy   = "RETRY_POLICY_RETRY"
  }

  depends_on = [
    google_secret_manager_secret_iam_member.worker_sa_can_access_secrets,
    google_pubsub_topic.tasks_topic,
    google_artifact_registry_repository.docker_repo,
    google_artifact_registry_repository_iam_member.worker_sa_repo_reader, # Ensure worker can read from AR
    google_storage_bucket_object.placeholder_source_zip # Ensure the placeholder source exists
  ]
}

# Grant the Pub/Sub service account token creator role on the worker SA
# This allows Pub/Sub to create tokens to invoke the Cloud Function
resource "google_project_iam_member" "pubsub_sa_invoker" {
  project = var.project_id
  role    = "roles/iam.serviceAccountTokenCreator"
  member = "serviceAccount:service-${data.google_project.current.number}@gcp-sa-pubsub.iam.gserviceaccount.com"
  depends_on = [google_service_account.worker_service_account]
}
