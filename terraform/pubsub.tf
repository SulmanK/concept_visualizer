# terraform/pubsub.tf

resource "google_pubsub_topic" "tasks_topic" {
  name    = "${var.naming_prefix}-tasks-${var.environment}"
  project = var.project_id

  message_retention_duration = "604800s"  # 7 days in seconds
}

resource "google_pubsub_subscription" "worker_subscription" {
  name    = "${var.naming_prefix}-worker-sub-${var.environment}"
  project = var.project_id
  topic   = google_pubsub_topic.tasks_topic.name

  # Configure acknowledgement deadline
  ack_deadline_seconds = 60

  # Configure message retention
  message_retention_duration = "604800s"  # 7 days retention

  # Configure retry policy
  retry_policy {
    minimum_backoff = "10s"
    maximum_backoff = "600s"  # 10 minutes
  }

  # Enable exactly once delivery if needed
  enable_exactly_once_delivery = true
}

# Using resource for service identity
resource "google_project_service_identity" "run_agent" {
  provider = google-beta
  project  = var.project_id
  service  = "run.googleapis.com"
}

# Grant publisher role to API service account
resource "google_pubsub_topic_iam_member" "api_sa_publisher" {
  project = var.project_id
  topic   = google_pubsub_topic.tasks_topic.name
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_service_account.email}"
}

# Grant subscriber role to worker service account
resource "google_pubsub_subscription_iam_member" "worker_sa_subscriber" {
  project      = var.project_id
  subscription = google_pubsub_subscription.worker_subscription.name
  role         = "roles/pubsub.subscriber"
  member       = "serviceAccount:${google_service_account.worker_service_account.email}"
}
