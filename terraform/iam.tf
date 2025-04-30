# terraform/iam.tf

resource "google_service_account" "api_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-api-sa-${var.environment}"
  display_name = "SA for Concept Viz API (${var.environment})"
}

resource "google_service_account" "worker_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-worker-sa-${var.environment}"
  display_name = "SA for Concept Viz Worker (${var.environment})"
}

# API SA Permissions
resource "google_project_iam_member" "api_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.api_service_account.email}"
}

resource "google_project_iam_member" "api_sa_pubsub_publisher" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_service_account.email}"
}

resource "google_project_iam_member" "api_sa_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.api_service_account.email}"
}

resource "google_project_iam_member" "api_sa_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.api_service_account.email}"
}

# Worker SA Permissions
resource "google_project_iam_member" "worker_sa_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.worker_service_account.email}"
}

resource "google_project_iam_member" "worker_sa_pubsub_subscriber" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.worker_service_account.email}"
}

resource "google_project_iam_member" "worker_sa_logging_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.worker_service_account.email}"
}

resource "google_project_iam_member" "worker_sa_monitoring_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.worker_service_account.email}"
}

resource "google_project_iam_member" "worker_sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.objectAdmin"
  member  = "serviceAccount:${google_service_account.worker_service_account.email}"
}

# IAM for State Bucket (Managed within Terraform)
resource "google_storage_bucket_iam_member" "state_bucket_user_access" {
  for_each = toset(var.terraform_runner_user_emails)
  bucket   = var.terraform_state_bucket_name
  role     = "roles/storage.objectAdmin"
  member   = "user:${each.key}"
}

resource "google_storage_bucket_iam_member" "state_bucket_cicd_access" {
  count  = var.terraform_cicd_sa_email != "" ? 1 : 0
  bucket = var.terraform_state_bucket_name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.terraform_cicd_sa_email}"
}
