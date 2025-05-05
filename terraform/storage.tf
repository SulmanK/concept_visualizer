# terraform/storage.tf

# Create a storage bucket for startup scripts and other assets
resource "google_storage_bucket" "assets_bucket" {
  name     = "${var.naming_prefix}-assets-${var.environment}"
  project  = var.project_id
  location = var.region

  # Use standard storage class (cheaper than multi-regional)
  storage_class = "STANDARD"

  # Ensure uniform bucket-level access
  uniform_bucket_level_access = true

  # Set reasonable defaults for lifecycle rules
  lifecycle_rule {
    condition {
      age = 365  # Objects older than 1 year
    }
    action {
      type = "Delete"
    }
  }

  # Force destroy allows Terraform to delete the bucket even if it contains objects
  force_destroy = true
}

# IAM: Grant the API service account access to the bucket
resource "google_storage_bucket_iam_member" "api_sa_storage_object_viewer" {
  bucket = google_storage_bucket.assets_bucket.name
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_service_account.api_service_account.email}"
}
