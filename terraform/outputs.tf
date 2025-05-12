# terraform/outputs.tf

output "api_vm_external_ip" {
  description = "External IP address of the API VM."
  value       = google_compute_address.api_static_ip[0].address
}

output "api_igm_name" {
  description = "Name of the Managed Instance Group for the API."
  value       = google_compute_instance_group_manager.api_igm.name
}

output "api_igm_zone" {
  description = "Zone of the API Instance Group Manager."
  value       = google_compute_instance_group_manager.api_igm.zone
}

output "worker_function_name" {
  description = "Name of the Cloud Function worker."
  value       = google_cloudfunctions2_function.worker_function.name
}

output "worker_function_region" {
  description = "Region of the Cloud Function worker."
  value       = google_cloudfunctions2_function.worker_function.location
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

output "cicd_service_account_email" {
  description = "Email of the CI/CD Service Account for GitHub Actions."
  value       = google_service_account.cicd_service_account.email
}

output "workload_identity_provider" {
  description = "Workload Identity Provider ID for GitHub Actions."
  value       = "projects/${var.project_id}/locations/global/workloadIdentityPools/${google_iam_workload_identity_pool.github_pool.workload_identity_pool_id}/providers/${google_iam_workload_identity_pool_provider.github_provider.workload_identity_pool_provider_id}"
}

output "github_pool_name" {
  description = "GitHub Workload Identity Pool Name."
  value       = google_iam_workload_identity_pool.github_pool.name
}

output "github_pool_id" {
  description = "GitHub Workload Identity Pool ID with suffix."
  value       = google_iam_workload_identity_pool.github_pool.workload_identity_pool_id
}

output "github_provider_id" {
  description = "GitHub Workload Identity Provider ID."
  value       = google_iam_workload_identity_pool_provider.github_provider.workload_identity_pool_provider_id
}

output "workload_identity_full_provider_name" {
  description = "The full resource name of the workload identity provider."
  value       = google_iam_workload_identity_pool_provider.github_provider.name
}

output "project_id" {
  description = "GCP Project ID."
  value       = var.project_id
}

# Monitoring outputs
output "log_metric_name" {
  description = "The name of the log-based metric for task failures"
  value       = google_logging_metric.concept_task_failures.name
}

output "alert_policy_name" {
  description = "The name of the alert policy for task failures"
  value       = google_monitoring_alert_policy.concept_task_failure_alert.display_name
}

output "notification_channel_name" {
  description = "The name of the notification channel for alerts"
  value       = google_monitoring_notification_channel.email_alert_channel.display_name
}

output "notification_channel_verification_note" {
  description = "Important note about verifying the notification channel"
  value       = "IMPORTANT: Check your email (${var.alert_email_address}) for a verification link from Google Cloud Monitoring. You must click this link to activate the notification channel!"
}
