# terraform/iam.tf

resource "google_service_account" "api_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-api-${var.environment}"
  display_name = "SA for Concept Viz API (${var.environment})"
}

resource "google_service_account" "worker_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-worker-${var.environment}"
  display_name = "SA for Concept Viz Worker (${var.environment})"
}

# Create dedicated CI/CD service account
resource "google_service_account" "cicd_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-cicd-${var.environment}"
  display_name = "CI/CD Service Account for Concept Visualizer (${var.environment})"
  description  = "Used by GitHub Actions for CI/CD operations"
}

# Create Workload Identity Pool for GitHub Actions
resource "google_iam_workload_identity_pool" "github_pool" {
  project                   = var.project_id
  workload_identity_pool_id = "gh-pool-${var.environment}-${random_string.pool_suffix.result}"
  display_name              = "GitHub Pool (${var.environment})"
  description               = "Identity pool for GitHub Actions CI/CD pipelines"

  lifecycle {
    create_before_destroy = true
    prevent_destroy       = false
  }
}

# Create GitHub Provider for the Workload Identity Pool
resource "google_iam_workload_identity_pool_provider" "github_provider" {
  project                            = var.project_id
  workload_identity_pool_id          = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
  workload_identity_pool_provider_id = "gh-provider-${var.environment}"
  display_name                       = "GitHub Provider (${var.environment})"

  # Configure the provider to accept tokens from GitHub's OIDC token issuer
  oidc {
    issuer_uri = "https://token.actions.githubusercontent.com"
  }

  # Configure attribute mapping to map claims in the GitHub Actions OIDC token to Google Cloud attributes
  attribute_mapping = {
    "google.subject"       = "assertion.sub"              # GitHub's subject
    "attribute.repository" = "assertion.repository"       # GitHub repo name
    "attribute.owner"      = "assertion.repository_owner" # GitHub repo owner
    "attribute.workflow"   = "assertion.workflow"         # GitHub workflow name
    "attribute.ref"        = "assertion.ref"              # GitHub ref (e.g., refs/heads/main)
  }

  # Set attribute condition to limit which repositories can use this provider
  attribute_condition = var.github_repo != "" ? "attribute.repository == \"${var.github_repo}\"" : null
}

# Allow the CI/CD service account to be impersonated by the GitHub Actions workload
resource "google_service_account_iam_binding" "workload_identity_binding" {
  service_account_id = google_service_account.cicd_service_account.name
  role               = "roles/iam.workloadIdentityUser"

  members = [
    "principalSet://iam.googleapis.com/${google_iam_workload_identity_pool.github_pool.name}/attribute.repository/${var.github_repo}"
  ]

  depends_on = [
    google_iam_workload_identity_pool.github_pool,
    google_iam_workload_identity_pool_provider.github_provider
  ]
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

# CI/CD Service Account Permissions
resource "google_project_iam_member" "cicd_sa_artifact_registry_writer" {
  project = var.project_id
  role    = "roles/artifactregistry.writer"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

resource "google_project_iam_member" "cicd_sa_compute_admin" {
  project = var.project_id
  role    = "roles/compute.admin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

resource "google_project_iam_member" "cicd_sa_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

resource "google_project_iam_member" "cicd_sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

resource "google_project_iam_member" "cicd_sa_logging_admin" {
  project = var.project_id
  role    = "roles/logging.admin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# Add Monitoring Admin role to CI/CD service account
resource "google_project_iam_member" "cicd_sa_monitoring_admin" {
  project = var.project_id
  role    = "roles/monitoring.admin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# Add Cloud Functions Admin role to CI/CD service account
resource "google_project_iam_member" "cicd_sa_cloudfunctions_admin" {
  project = var.project_id
  role    = "roles/cloudfunctions.admin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# Add Workload Identity Pool Admin role to CI/CD service account
resource "google_project_iam_member" "cicd_sa_workload_identity_admin" {
  project = var.project_id
  role    = "roles/iam.workloadIdentityPoolAdmin"
  member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# Add IAM binding for CI/CD service account to impersonate Compute Engine default service account
resource "google_service_account_iam_member" "cicd_sa_compute_service_account_user" {
  service_account_id = "projects/${var.project_id}/serviceAccounts/${data.google_project.current.number}-compute@developer.gserviceaccount.com"
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# Add IAM binding for CI/CD service account to impersonate the worker service account
resource "google_service_account_iam_member" "cicd_sa_worker_service_account_user" {
  service_account_id = google_service_account.worker_service_account.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# Add IAM binding for CI/CD service account to impersonate the API service account
resource "google_service_account_iam_member" "cicd_sa_api_service_account_user" {
  service_account_id = google_service_account.api_service_account.name
  role               = "roles/iam.serviceAccountUser"
  member             = "serviceAccount:${google_service_account.cicd_service_account.email}"
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

# --- IAM for Manually Created Terraform State Bucket ---
# This bucket is used by the main Terraform configuration AND for storing dynamic monitoring IDs.

# Data source to reference the manually created GCS bucket for Terraform state
data "google_storage_bucket" "manual_tf_state_bucket" {
  name = var.manual_tf_state_bucket_name
}

# Grant the CI/CD service account permissions to manage objects in the manually created TF state bucket
# This is needed by the deploy_backend.yml workflow to write the dynamic monitoring resource IDs.
resource "google_storage_bucket_iam_member" "cicd_sa_manual_tfstate_bucket_object_admin" {
  bucket = data.google_storage_bucket.manual_tf_state_bucket.name
  role   = "roles/storage.objectAdmin" # Allows listing, creating, reading, deleting objects
  member = "serviceAccount:${google_service_account.cicd_service_account.email}"
}

# --- End of IAM for Manually Created Terraform State Bucket ---
