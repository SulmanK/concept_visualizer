# terraform/cloud_run.tf

resource "google_cloud_run_v2_service" "worker" {
  name         = "${var.naming_prefix}-worker-${var.environment}"
  location     = var.region
  project      = var.project_id
  launch_stage = "BETA"

  template {
    service_account = google_service_account.worker_service_account.email
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder - MUST BE UPDATED by CI/CD
      resources {
        limits = {
          cpu    = var.worker_cpu
          memory = var.worker_memory
        }
        startup_cpu_boost = true
      }

      env {
        name  = "ENVIRONMENT"
        value = var.environment
      }
      env {
        name  = "GCP_PROJECT_ID"
        value = var.project_id
      }
      env {
        name  = "CONCEPT_STORAGE_BUCKET_CONCEPT"
        value = "${var.naming_prefix}-concept-images-${var.environment}"
      }
      env {
        name  = "CONCEPT_STORAGE_BUCKET_PALETTE"
        value = "${var.naming_prefix}-palette-images-${var.environment}"
      }
      env {
        name  = "CONCEPT_DB_TABLE_TASKS"
        value = "tasks_${var.environment}"
      }
      env {
        name  = "CONCEPT_DB_TABLE_CONCEPTS"
        value = "concepts_${var.environment}"
      }
      env {
        name  = "CONCEPT_DB_TABLE_PALETTES"
        value = "color_variations_${var.environment}"
      }
      env {
        name  = "CONCEPT_LOG_LEVEL"
        value = (var.environment == "prod" ? "INFO" : "DEBUG")
      }

      # Secrets (reference all needed secrets)
      env {
        name = "CONCEPT_SUPABASE_URL"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_url.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CONCEPT_SUPABASE_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CONCEPT_SUPABASE_SERVICE_ROLE"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_service_role.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CONCEPT_SUPABASE_JWT_SECRET"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.supabase_jwt_secret.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CONCEPT_JIGSAWSTACK_API_KEY"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.jigsaw_key.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CONCEPT_UPSTASH_REDIS_ENDPOINT"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_endpoint.secret_id
            version = "latest"
          }
        }
      }
      env {
        name = "CONCEPT_UPSTASH_REDIS_PASSWORD"
        value_source {
          secret_key_ref {
            secret  = google_secret_manager_secret.redis_password.secret_id
            version = "latest"
          }
        }
      }
      env {
        name  = "CONCEPT_UPSTASH_REDIS_PORT"
        value = "6379"
      }
    }
    scaling {
      min_instance_count = var.worker_min_instances
      max_instance_count = var.worker_max_instances
    }
  }

  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  depends_on = [
    google_pubsub_subscription.worker_subscription,
    google_secret_manager_secret_iam_member.worker_sa_can_access_secrets
  ]
}

# Create an Eventarc trigger for the worker service
resource "google_eventarc_trigger" "worker_trigger" {
  name     = "${var.naming_prefix}-worker-trigger-${var.environment}"
  location = var.region
  project  = var.project_id

  matching_criteria {
    attribute = "type"
    value     = "google.cloud.pubsub.topic.v1.messagePublished"
  }

  destination {
    cloud_run_service {
      service = google_cloud_run_v2_service.worker.name
      region  = google_cloud_run_v2_service.worker.location
    }
  }

  transport {
    pubsub {
      topic = google_pubsub_topic.tasks_topic.name
    }
  }

  service_account = google_service_account.worker_service_account.email

  depends_on = [
    google_cloud_run_v2_service.worker,
    google_pubsub_subscription.worker_subscription,
    google_pubsub_subscription_iam_member.worker_sa_subscriber
  ]
}

resource "google_cloud_run_v2_service_iam_member" "worker_invoker" {
  project  = google_cloud_run_v2_service.worker.project
  location = google_cloud_run_v2_service.worker.location
  name     = google_cloud_run_v2_service.worker.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.worker_service_account.email}" # SA specified in trigger
}
