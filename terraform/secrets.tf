# terraform/secrets.tf

resource "google_secret_manager_secret" "supabase_url" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-supabase-url-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret" "supabase_key" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-supabase-key-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret" "supabase_service_role" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-supabase-service-role-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret" "supabase_jwt_secret" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-supabase-jwt-secret-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret" "jigsaw_key" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-jigsawstack-api-key-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret" "redis_endpoint" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-redis-endpoint-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

resource "google_secret_manager_secret" "redis_password" {
  project   = var.project_id
  secret_id = "${var.naming_prefix}-redis-password-${var.environment}"
  replication {
    auto {}
  }
  labels = {
    environment = var.environment
  }
}

locals {
  secrets_in_project = {
    "supabase_url"          = google_secret_manager_secret.supabase_url
    "supabase_key"          = google_secret_manager_secret.supabase_key
    "supabase_service_role" = google_secret_manager_secret.supabase_service_role
    "supabase_jwt_secret"   = google_secret_manager_secret.supabase_jwt_secret
    "jigsaw_key"            = google_secret_manager_secret.jigsaw_key
    "redis_endpoint"        = google_secret_manager_secret.redis_endpoint
    "redis_password"        = google_secret_manager_secret.redis_password
  }
}

resource "google_secret_manager_secret_iam_member" "api_sa_can_access_secrets" {
  for_each   = local.secrets_in_project
  project    = each.value.project
  secret_id  = each.value.secret_id
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.api_service_account.email}"
  depends_on = [google_service_account.api_service_account]
}

resource "google_secret_manager_secret_iam_member" "worker_sa_can_access_secrets" {
  for_each   = local.secrets_in_project
  project    = each.value.project
  secret_id  = each.value.secret_id
  role       = "roles/secretmanager.secretAccessor"
  member     = "serviceAccount:${google_service_account.worker_service_account.email}"
  depends_on = [google_service_account.worker_service_account]
}
