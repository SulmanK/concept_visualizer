# terraform/variables.tf

variable "project_id" {
  description = "The GCP project ID to deploy resources into (dev or prod)."
  type        = string
}

variable "region" {
  description = "The primary GCP region for most resources."
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The primary GCP zone for zonal resources (VMs, PubSub Lite)."
  type        = string
  default     = "us-central1-a" # Ensure this aligns with region
}

variable "environment" {
  description = "The deployment environment ('dev' or 'prod')."
  type        = string
  validation {
    condition     = contains(["dev", "prod"], var.environment)
    error_message = "Environment must be either 'dev' or 'prod'."
  }
}

variable "naming_prefix" {
  description = "A prefix for resource names (e.g., 'concept-viz')."
  type        = string
  default     = "concept-viz"
}

variable "terraform_state_bucket_name" {
  description = "Name of the GCS bucket holding Terraform state."
  type        = string
}

variable "terraform_runner_user_emails" {
  description = "List of user emails (e.g., 'you@example.com') that run Terraform locally."
  type        = list(string)
  default     = []
}

variable "terraform_cicd_sa_email" {
  description = "Email of the Service Account used by CI/CD to run Terraform."
  type        = string
  default     = "" # Set in tfvars or CI/CD environment if used
}

variable "allow_ssh_ips" {
  description = "List of CIDR blocks allowed SSH access to API VMs."
  type        = list(string)
  default     = [] # Secure default: No SSH access
}

variable "api_vm_machine_type" {
  description = "Machine type for the API VM."
  type        = string
  default     = "e2-micro"
}

variable "worker_cpu" {
  description = "CPU allocation for the Cloud Function worker."
  type        = string
  default     = "1"
}

variable "worker_memory" {
  description = "Memory allocation for the Cloud Function worker."
  type        = string
  default     = "2048Mi"
}

variable "worker_min_instances" {
  description = "Minimum number of Cloud Function worker instances."
  type        = number
  default     = 0
}

variable "worker_max_instances" {
  description = "Maximum number of Cloud Function worker instances."
  type        = number
  default     = 5
}

variable "pubsub_lite_partition_count" {
  description = "Number of partitions for the Pub/Sub Lite topic."
  type        = number
  default     = 1
}

variable "pubsub_lite_publish_mib_per_sec" {
  description = "Publish capacity per partition (MiB/s)."
  type        = number
  default     = 1
}

variable "pubsub_lite_subscribe_mib_per_sec" {
  description = "Subscribe capacity per partition (MiB/s)."
  type        = number
  default     = 2
}

variable "github_repo" {
  description = "The full name of the GitHub repository in the format 'OWNER/REPO' (e.g., 'username/concept_visualizer'). Used for Workload Identity Federation."
  type        = string
  default     = ""
}

variable "alert_email_address" {
  description = "The email address to send monitoring alerts to."
  type        = string
}

variable "alert_alignment_period" {
  description = "The alignment period for the task failure alert (e.g., '300s' for 5 minutes)."
  type        = string
  default     = "300s" # 5 minutes
}

variable "alert_duration" {
  description = "How long the failure condition must persist before an alert is sent (e.g., '60s'). Use '0s' to alert on the first instance within an alignment period."
  type        = string
  default     = "0s" # Alert immediately on first failure in an alignment period
}

variable "api_startup_alert_delay" {
  description = "The duration (e.g., '600s') a failing health check condition must persist before an alert is triggered. Acts as an initial grace period after VM/API setup."
  type        = string
  default     = "600s" # Default to 10 minutes, adjust as needed
}
