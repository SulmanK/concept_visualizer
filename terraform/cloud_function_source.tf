# terraform/cloud_function_source.tf

# 1. Create a bucket to hold the dummy source zip
resource "google_storage_bucket" "function_source_placeholder" {
  project       = var.project_id
  name          = "${var.naming_prefix}-func-source-${var.environment}-${var.bucket_unique_suffix}"
  location      = var.region
  force_destroy = true  # Allows easy cleanup during destroy

  uniform_bucket_level_access = true

  lifecycle_rule {
    condition {
      age = 30 // Delete objects older than 30 days (it's just a placeholder)
    }
    action {
      type = "Delete"
    }
  }
}

# 2. Upload the placeholder zip file to the bucket
# Note: The placeholder.zip file should be in the terraform/placeholder directory
# You can create it with these commands:
# 1. mkdir -p placeholder && echo "placeholder" > placeholder/placeholder.txt
# 2. Compress placeholder/placeholder.txt to placeholder/placeholder.zip
resource "google_storage_bucket_object" "placeholder_source_zip" {
  name   = "placeholder-source.zip" # Name of the object in the bucket
  bucket = google_storage_bucket.function_source_placeholder.name
  source = "${path.module}/placeholder/placeholder.zip" # Path to the zip file in terraform/placeholder directory

  # Ensure the bucket exists before uploading
  depends_on = [google_storage_bucket.function_source_placeholder]
}
