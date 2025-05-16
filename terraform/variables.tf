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
  default     = "2700s" # Default to 45 minutes, adjust as needed
}

variable "initial_frontend_hostname_placeholder" {
  description = "A placeholder hostname for the frontend uptime check. This will be updated by CI/CD. Can be an empty string or a generic domain if Terraform requires a value."
  type        = string
  default     = "placeholder.vercel.app" # Or your main custom domain if relatively stable
}

variable "frontend_startup_alert_delay" {
  description = "The duration a failing frontend health check must persist before alerting."
  type        = string
  default     = "2700s" # 45 minutes, Vercel deployments are usually fast
}

variable "alert_notification_channel_email" {
  description = "Email address for the alert notification channel. If not provided, one will be created with a default name."
  type        = string
  default     = ""
}

variable "initial_frontend_hostname" {
  description = "Initial placeholder hostname for the frontend uptime check. This will be updated by the deployment workflow."
  type        = string
  default     = "placeholder.example.com"
}

variable "frontend_uptime_check_period" {
  description = "How often the frontend uptime check is performed (e.g., '300s' for 5 minutes)."
  type        = string
  default     = "300s"
}

variable "manual_tf_state_bucket_name" {
  description = "The name of the manually created GCS bucket used for Terraform state and other shared resources (like dynamic monitoring IDs)."
  type        = string
  # No default, this should be explicitly set in tfvars
}

# --- Optional Variables for Worker Autoscaling (Cloud Function 2nd Gen) ---
