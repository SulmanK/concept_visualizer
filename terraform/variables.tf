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
  description = "CPU allocation for the Cloud Run worker."
  type        = string
  default     = "1"
}

variable "worker_memory" {
  description = "Memory allocation for the Cloud Run worker."
  type        = string
  default     = "512Mi"
}

variable "worker_min_instances" {
  description = "Minimum number of Cloud Run worker instances."
  type        = number
  default     = 0
}

variable "worker_max_instances" {
  description = "Maximum number of Cloud Run worker instances."
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
