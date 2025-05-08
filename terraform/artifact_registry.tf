# terraform/artifact_registry.tf

resource "google_artifact_registry_repository" "docker_repo" {
  project       = var.project_id
  location      = var.region
  repository_id = "${var.naming_prefix}-docker-repo" # Can be shared across envs if desired, or add ${var.environment}
  description   = "Docker repository for Concept Viz (${var.environment})"
  format        = "DOCKER"
}

resource "google_artifact_registry_repository_iam_member" "api_sa_repo_reader" {
  project    = google_artifact_registry_repository.docker_repo.project
  location   = google_artifact_registry_repository.docker_repo.location
  repository = google_artifact_registry_repository.docker_repo.name # Use name attribute
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.api_service_account.email}"
}

resource "google_artifact_registry_repository_iam_member" "worker_sa_repo_reader" {
  project    = google_artifact_registry_repository.docker_repo.project
  location   = google_artifact_registry_repository.docker_repo.location
  repository = google_artifact_registry_repository.docker_repo.name # Use name attribute
  role       = "roles/artifactregistry.reader"
  member     = "serviceAccount:${google_service_account.worker_service_account.email}"
}
