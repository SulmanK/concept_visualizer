# terraform/outputs.tf

output "api_vm_external_ip" {
  description = "External IP address of the API VM."
  value       = try(google_compute_address.api_static_ip[0].address, "Check the IP of the VM created by the Instance Group Manager")
}

output "worker_service_name" {
  description = "Name of the Cloud Run worker service."
  value       = google_cloud_run_v2_service.worker.name
}

output "worker_service_url" {
  description = "URL of the Cloud Run worker service (internal)."
  value       = google_cloud_run_v2_service.worker.uri
}

output "artifact_registry_repository_url" {
  description = "URL of the Artifact Registry repository."
  value       = "${google_artifact_registry_repository.docker_repo.location}-docker.pkg.dev/${var.project_id}/${google_artifact_registry_repository.docker_repo.repository_id}"
}

output "tasks_topic_name" {
  description = "Name of the Pub/Sub topic for tasks."
  value       = google_pubsub_topic.tasks_topic.name
}

output "worker_subscription_name" {
  description = "Name of the Pub/Sub subscription for the worker."
  value       = google_pubsub_subscription.worker_subscription.name
}

output "api_service_account_email" {
  description = "Email of the API Service Account."
  value       = google_service_account.api_service_account.email
}

output "worker_service_account_email" {
  description = "Email of the Worker Service Account."
  value       = google_service_account.worker_service_account.email
}
