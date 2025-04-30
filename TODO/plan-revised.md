Okay, here is the consolidated, step-by-step Phase 2 plan incorporating all the details, HCL code, scripts, and workflow discussed.

---

**Consolidated Phase 2: Setup GCP Infrastructure and Secrets (Detailed Steps)**

- **Goal:** Define and provision core GCP infrastructure for **separate `dev` and `prod` GCP projects** using Terraform. Automate granting access to the manually created GCS state bucket within the Terraform run. Use branch-aware scripts for execution and a separate script for secret population. Pass non-secret configuration (like bucket/table names) via environment variables set by Terraform.
- **Branch:** Create and work on `feature/infrastructure` branch off `develop`.

**Step 2.1: Prerequisites & Initial Setup**

1.  **Install Terraform:** Ensure Terraform CLI (version >= 1.3 recommended) is installed locally. ([https://developer.hashicorp.com/terraform/downloads](https://developer.hashicorp.com/terraform/downloads))
2.  **Install `gcloud` CLI:** Ensure Google Cloud SDK is installed. ([https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install))
3.  **Authenticate `gcloud`:**
    - Run `gcloud auth login` to authenticate your primary user account.
    - Run `gcloud auth application-default login`.
4.  **Create GCP Projects:** Manually create two separate GCP Projects via the Cloud Console: one for `dev` (e.g., `yourproject-dev`) and one for `prod` (e.g., `yourproject-prod`). Note down their unique Project IDs.
5.  **Enable APIs:** For **both** the `dev` and `prod` projects, run the following `gcloud` command (replace `YOUR_PROJECT_ID_HERE` accordingly for each project):
    ```bash
    gcloud services enable \
      compute.googleapis.com \
      run.googleapis.com \
      secretmanager.googleapis.com \
      artifactregistry.googleapis.com \
      pubsub.googleapis.com \
      cloudresourcemanager.googleapis.com \
      iam.googleapis.com \
      logging.googleapis.com \
      monitoring.googleapis.com \
      cloudbuild.googleapis.com \
      --project=YOUR_PROJECT_ID_HERE
    ```
6.  **Create GCS Bucket for Terraform State (Manual/Bootstrap):**
    - **Action:** Choose **one** GCP project to host the state bucket (e.g., the `dev` project). Manually create a GCS bucket in that project using the Cloud Console or `gcloud`.
    - **Crucially:** **Enable Object Versioning** on this bucket.
    - **Example Name:** `yourproject-tfstate` (Replace with your globally unique name).
    - **Purpose:** Securely store Terraform state files for both `dev` and `prod` workspaces.
7.  **Grant Initial IAM Setter Permission:** Manually grant the identity running the _first_ `terraform apply` (likely your user account) the permission to _set IAM policies on the state bucket_. The `roles/storage.admin` role on the bucket is sufficient initially.
    ```bash
    gcloud storage buckets add-iam-policy-binding gs://yourproject-tfstate \
      --member="user:your-gcp-email@example.com" \
      --role="roles/storage.admin" \
      --project="project-hosting-tfstate-bucket" # Project where bucket lives
    ```
8.  **Create Project Directory Structure:**
    - `mkdir terraform`
    - `mkdir terraform/environments`
    - `mkdir terraform/scripts`
    - `mkdir scripts` (at the project root)
9.  **Add Terraform to `.gitignore` (Root):**
    ```gitignore
    # Terraform
    terraform/.terraform/
    terraform/*.tfstate
    terraform/*.tfstate.*
    terraform/*.tfplan
    terraform/crash.log
    terraform/crash.*.log
    # terraform/environments/*.tfvars # Keep commented unless you commit secrets!
    ```

**Step 2.2: Define Terraform Variables (`terraform/variables.tf`)**

```terraform
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
```

**Step 2.3: Configure Terraform Backend and Provider (`terraform/main.tf`)**

```terraform
# terraform/main.tf

terraform {
  required_version = ">= 1.3"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }

  backend "gcs" {
    # Bucket name passed via -backend-config during init
    prefix = "terraform/state/${terraform.workspace}" # Uses workspace name (dev/prod)
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
  zone    = var.zone
}

data "google_project" "current" {
  project_id = var.project_id
}
```

**Step 2.4: Define Environment Variable Files (`terraform/environments/*.tfvars`)**

- **`terraform/environments/dev.tfvars`**: (Ensure this file exists locally, **not committed**)
  ```tfvars
  project_id                      = "your-dev-project-id" # <-- REPLACE
  region                          = "us-central1"
  zone                            = "us-central1-a"
  environment                     = "dev"
  naming_prefix                   = "concept-viz-dev"
  terraform_state_bucket_name     = "your-unique-tf-state-bucket-name-here" # <-- REPLACE
  terraform_runner_user_emails    = ["your-gcp-email@example.com"] # <-- REPLACE
  terraform_cicd_sa_email         = "" # Set later if needed for CI/CD
  allow_ssh_ips                   = ["YOUR_HOME_OR_OFFICE_IP/32"] # Optional
  api_vm_machine_type             = "e2-micro"
  worker_min_instances            = 0
  worker_max_instances            = 3
  # Add other dev vars from variables.tf if needed
  ```
- **`terraform/environments/prod.tfvars`**: (Ensure this file exists locally, **not committed**)
  ```tfvars
  project_id                      = "your-prod-project-id" # <-- REPLACE
  region                          = "us-east1"
  zone                            = "us-east1-b"
  environment                     = "prod"
  naming_prefix                   = "concept-viz-prod"
  terraform_state_bucket_name     = "your-unique-tf-state-bucket-name-here" # <-- REPLACE (Same bucket)
  terraform_runner_user_emails    = ["your-gcp-email@example.com"] # <-- REPLACE
  terraform_cicd_sa_email         = "" # Set later if needed for CI/CD
  allow_ssh_ips                   = [] # Prod should not have SSH open generally
  api_vm_machine_type             = "e2-small"
  worker_min_instances            = 1
  worker_max_instances            = 10
  # Add other prod vars from variables.tf if needed
  ```
- **Create `.tfvars.example` files** for both `dev` and `prod` based on the above, using placeholders, and commit these example files.

**Step 2.5: Define Network and Firewall (`terraform/network.tf`)**

```terraform
# terraform/network.tf

data "google_compute_network" "default_network" {
  name = "default"
}

resource "google_compute_firewall" "allow_api_ingress" {
  name    = "${var.naming_prefix}-allow-api-ingress"
  network = data.google_compute_network.default_network.id
  allow { protocol = "tcp"; ports = ["80", "443"] }
  source_ranges = ["0.0.0.0/0"] # Adjust if using LB
  target_tags   = ["${var.naming_prefix}-api-vm-${var.environment}"]
}

resource "google_compute_firewall" "allow_ssh_ingress" {
  count   = length(var.allow_ssh_ips) > 0 ? 1 : 0
  name    = "${var.naming_prefix}-allow-ssh-ingress"
  network = data.google_compute_network.default_network.id
  allow { protocol = "tcp"; ports = ["22"] }
  source_ranges = var.allow_ssh_ips
  target_tags   = ["${var.naming_prefix}-api-vm-${var.environment}"]
}
```

**Step 2.6: Define IAM (`terraform/iam.tf`)**

```terraform
# terraform/iam.tf

resource "google_service_account" "api_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-api-sa-${var.environment}"
  display_name = "SA for Concept Viz API (${var.environment})"
}

resource "google_service_account" "worker_service_account" {
  project      = var.project_id
  account_id   = "${var.naming_prefix}-worker-sa-${var.environment}"
  display_name = "SA for Concept Viz Worker (${var.environment})"
}

# API SA Permissions
resource "google_project_iam_member" "api_sa_secret_accessor" { project = var.project_id; role = "roles/secretmanager.secretAccessor"; member = "serviceAccount:${google_service_account.api_service_account.email}" }
resource "google_project_iam_member" "api_sa_pubsub_publisher" { project = var.project_id; role = "roles/pubsub.publisher"; member = "serviceAccount:${google_service_account.api_service_account.email}" }
resource "google_project_iam_member" "api_sa_logging_writer" { project = var.project_id; role = "roles/logging.logWriter"; member = "serviceAccount:${google_service_account.api_service_account.email}" }
resource "google_project_iam_member" "api_sa_monitoring_writer" { project = var.project_id; role = "roles/monitoring.metricWriter"; member = "serviceAccount:${google_service_account.api_service_account.email}" }

# Worker SA Permissions
resource "google_project_iam_member" "worker_sa_secret_accessor" { project = var.project_id; role = "roles/secretmanager.secretAccessor"; member = "serviceAccount:${google_service_account.worker_service_account.email}" }
resource "google_project_iam_member" "worker_sa_pubsub_subscriber" { project = var.project_id; role = "roles/pubsub.subscriber"; member = "serviceAccount:${google_service_account.worker_service_account.email}" }
resource "google_project_iam_member" "worker_sa_logging_writer" { project = var.project_id; role = "roles/logging.logWriter"; member = "serviceAccount:${google_service_account.worker_service_account.email}" }
resource "google_project_iam_member" "worker_sa_monitoring_writer" { project = var.project_id; role = "roles/monitoring.metricWriter"; member = "serviceAccount:${google_service_account.worker_service_account.email}" }
resource "google_project_iam_member" "worker_sa_storage_admin" { project = var.project_id; role = "roles/storage.objectAdmin"; member = "serviceAccount:${google_service_account.worker_service_account.email}" }

# IAM for State Bucket (Managed within Terraform)
resource "google_storage_bucket_iam_member" "state_bucket_user_access" {
  for_each = toset(var.terraform_runner_user_emails)
  bucket   = var.terraform_state_bucket_name
  role     = "roles/storage.objectAdmin"
  member   = "user:${each.key}"
}

resource "google_storage_bucket_iam_member" "state_bucket_cicd_access" {
  count    = var.terraform_cicd_sa_email != "" ? 1 : 0
  bucket   = var.terraform_state_bucket_name
  role     = "roles/storage.objectAdmin"
  member   = "serviceAccount:${var.terraform_cicd_sa_email}"
}
```

**Step 2.7: Define Secret Containers and Access (`terraform/secrets.tf`)**

```terraform
# terraform/secrets.tf

resource "google_secret_manager_secret" "supabase_url" { project = var.project_id; secret_id = "${var.naming_prefix}-supabase-url-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }
resource "google_secret_manager_secret" "supabase_key" { project = var.project_id; secret_id = "${var.naming_prefix}-supabase-key-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }
resource "google_secret_manager_secret" "supabase_service_role" { project = var.project_id; secret_id = "${var.naming_prefix}-supabase-service-role-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }
resource "google_secret_manager_secret" "supabase_jwt_secret" { project = var.project_id; secret_id = "${var.naming_prefix}-supabase-jwt-secret-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }
resource "google_secret_manager_secret" "jigsaw_key" { project = var.project_id; secret_id = "${var.naming_prefix}-jigsawstack-api-key-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }
resource "google_secret_manager_secret" "redis_endpoint" { project = var.project_id; secret_id = "${var.naming_prefix}-redis-endpoint-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }
resource "google_secret_manager_secret" "redis_password" { project = var.project_id; secret_id = "${var.naming_prefix}-redis-password-${var.environment}"; replication { automatic = true }; labels = { environment = var.environment } }

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
  for_each  = local.secrets_in_project
  project   = each.value.project
  secret_id = each.value.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.api_service_account.email}"
  depends_on = [google_service_account.api_service_account]
}

resource "google_secret_manager_secret_iam_member" "worker_sa_can_access_secrets" {
  for_each  = local.secrets_in_project
  project   = each.value.project
  secret_id = each.value.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.worker_service_account.email}"
  depends_on = [google_service_account.worker_service_account]
}
```

**Step 2.8: Define Artifact Registry (`terraform/artifact_registry.tf`)**

```terraform
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
```

**Step 2.9: Define Pub/Sub Lite (`terraform/pubsub_lite.tf`)**

```terraform
# terraform/pubsub_lite.tf

resource "google_pubsub_lite_topic" "tasks_topic" {
  name    = "${var.naming_prefix}-tasks-${var.environment}"
  project = var.project_id
  zone    = var.zone
  partition_config { count = var.pubsub_lite_partition_count; capacity { publish_mib_per_sec = var.pubsub_lite_publish_mib_per_sec; subscribe_mib_per_sec = var.pubsub_lite_subscribe_mib_per_sec } }
  retention_config { per_partition_bytes = "30000000000"; period = "168h" }
}

resource "google_pubsub_lite_subscription" "worker_subscription" {
  name    = "${var.naming_prefix}-worker-sub-${var.environment}"
  project = var.project_id
  zone    = var.zone
  topic   = google_pubsub_lite_topic.tasks_topic.id
  delivery_config { delivery_requirement = "DELIVER_AFTER_STORED" }
}

data "google_project_service_identity" "run_agent" {
  provider = google-beta
  project  = var.project_id
  service  = "run.googleapis.com"
}

resource "google_pubsub_lite_subscription_iam_member" "run_subscriber_binding" {
  provider     = google-beta # Ensure beta provider used if needed for this resource
  project      = var.project_id
  zone         = google_pubsub_lite_subscription.worker_subscription.zone
  subscription = google_pubsub_lite_subscription.worker_subscription.name
  role         = "roles/pubsublite.subscriber"
  member       = "serviceAccount:${data.google_project_service_identity.run_agent.email}"
}
```

**Step 2.10: Define Cloud Run Worker (`terraform/cloud_run.tf`)**

```terraform
# terraform/cloud_run.tf

resource "google_cloud_run_v2_service" "worker" {
  name     = "${var.naming_prefix}-worker-${var.environment}"
  location = var.region
  project  = var.project_id
  launch_stage = "BETA"

  template {
    service_account = google_service_account.worker_service_account.email
    containers {
      image = "us-docker.pkg.dev/cloudrun/container/hello" # Placeholder - MUST BE UPDATED by CI/CD
      resources { limits = { cpu = var.worker_cpu; memory = var.worker_memory }; startup_cpu_boost = true }

      env { name = "ENVIRONMENT"; value = var.environment }
      env { name = "GCP_PROJECT_ID"; value = var.project_id }
      env { name = "CONCEPT_STORAGE_BUCKET_CONCEPT"; value = "${var.naming_prefix}-concept-images-${var.environment}" }
      env { name = "CONCEPT_STORAGE_BUCKET_PALETTE"; value = "${var.naming_prefix}-palette-images-${var.environment}" }
      env { name = "CONCEPT_DB_TABLE_TASKS"; value = "tasks_${var.environment}" }
      env { name = "CONCEPT_DB_TABLE_CONCEPTS"; value = "concepts_${var.environment}" }
      env { name = "CONCEPT_DB_TABLE_PALETTES"; value = "color_variations_${var.environment}" }
      env { name = "CONCEPT_LOG_LEVEL"; value = (var.environment == "prod" ? "INFO" : "DEBUG") } # Example conditional config

      # Secrets (reference all needed secrets)
      env { name = "CONCEPT_SUPABASE_URL"; value_source { secret_key_ref { secret = google_secret_manager_secret.supabase_url.secret_id; version = "latest" } } }
      env { name = "CONCEPT_SUPABASE_KEY"; value_source { secret_key_ref { secret = google_secret_manager_secret.supabase_key.secret_id; version = "latest" } } }
      env { name = "CONCEPT_SUPABASE_SERVICE_ROLE"; value_source { secret_key_ref { secret = google_secret_manager_secret.supabase_service_role.secret_id; version = "latest" } } }
      env { name = "CONCEPT_SUPABASE_JWT_SECRET"; value_source { secret_key_ref { secret = google_secret_manager_secret.supabase_jwt_secret.secret_id; version = "latest" } } }
      env { name = "CONCEPT_JIGSAWSTACK_API_KEY"; value_source { secret_key_ref { secret = google_secret_manager_secret.jigsaw_key.secret_id; version = "latest" } } }
      env { name = "CONCEPT_UPSTASH_REDIS_ENDPOINT"; value_source { secret_key_ref { secret = google_secret_manager_secret.redis_endpoint.secret_id; version = "latest" } } }
      env { name = "CONCEPT_UPSTASH_REDIS_PASSWORD"; value_source { secret_key_ref { secret = google_secret_manager_secret.redis_password.secret_id; version = "latest" } } }
      env { name = "CONCEPT_UPSTASH_REDIS_PORT"; value = "6379" } # Example non-secret config
    }
    scaling { min_instance_count = var.worker_min_instances; max_instance_count = var.worker_max_instances }
  }

  event_trigger {
    trigger_region  = google_pubsub_lite_subscription.worker_subscription.zone
    event_type      = "google.cloud.pubsub.topic.v1.messagePublished"
    pubsub_topic    = google_pubsub_lite_topic.tasks_topic.id
    retry_policy    = "RETRY_POLICY_RETRY"
    service_account = google_service_account.worker_service_account.email
  }

  ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"
  depends_on = [google_pubsub_lite_subscription.worker_subscription, google_pubsub_lite_subscription_iam_member.run_subscriber_binding]
}

resource "google_cloud_run_v2_service_iam_member" "worker_invoker" {
  project  = google_cloud_run_v2_service.worker.project
  location = google_cloud_run_v2_service.worker.location
  name     = google_cloud_run_v2_service.worker.name
  role     = "roles/run.invoker"
  member   = "serviceAccount:${google_service_account.worker_service_account.email}" # SA specified in trigger
}
```

**Step 2.11: Define Compute Engine API VM (`terraform/compute.tf`)**

```terraform
# terraform/compute.tf

resource "google_compute_address" "api_static_ip" {
  count   = var.environment == "prod" ? 1 : 0 # Only for prod in this example
  name    = "${var.naming_prefix}-api-ip-${var.environment}"
  project = var.project_id
  region  = var.region
}

resource "google_compute_instance_template" "api_template" {
  project      = var.project_id
  name_prefix  = "${var.naming_prefix}-api-tpl-${var.environment}-"
  machine_type = var.api_vm_machine_type
  region       = var.region

  disk { source_image = "debian-cloud/debian-11"; auto_delete = true; boot = true; disk_size_gb = 20 }

  network_interface {
    network = data.google_compute_network.default_network.id
    access_config {
      nat_ip       = try(google_compute_address.api_static_ip[0].address, null) # Assign static IP if it exists
      network_tier = "PREMIUM"
    }
  }

  service_account {
    email  = google_service_account.api_service_account.email
    scopes = ["cloud-platform"]
  }

  tags = ["${var.naming_prefix}-api-vm-${var.environment}", "http-server", "https-server"]

  metadata = {
    # Pass variables needed by startup script
    environment   = var.environment
    naming_prefix = var.naming_prefix
    region        = var.region
  }
  metadata_startup_script = file("${path.module}/scripts/startup-api.sh")

  lifecycle { create_before_destroy = true }
}

resource "google_compute_instance_group_manager" "api_igm" {
  project            = var.project_id
  name               = "${var.naming_prefix}-api-igm-${var.environment}"
  zone               = var.zone
  base_instance_name = "${var.naming_prefix}-api-vm-${var.environment}"
  target_size        = 1

  version { instance_template = google_compute_instance_template.api_template.id }
}

# Add optional Load Balancer resources here if needed for prod
```

**Step 2.12: Create API VM Startup Script (`terraform/scripts/startup-api.sh`)**

```bash
#!/bin/bash
set -euo pipefail # Exit on error, unset var error, pipefail

echo "Starting API VM startup script..."

# --- Install Prerequisites ---
install_pkg() {
    if ! command -v $1 &> /dev/null; then
        echo "Installing $1..."
        apt-get update -y && apt-get install -y $2 && echo "$1 installed."
    else
        echo "$1 already installed."
    fi
}

install_pkg "docker" "apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common docker-ce docker-ce-cli containerd.io docker-compose-plugin"
install_pkg "gcloud" "google-cloud-sdk"

# Configure Docker permissions (run docker commands as non-root if needed)
# usermod -aG docker your_user # Example

systemctl start docker
systemctl enable docker

# --- Fetch Metadata ---
echo "Fetching instance metadata..."
ENVIRONMENT=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/attributes/environment" -H "Metadata-Flavor: Google" || echo "dev")
NAMING_PREFIX=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/attributes/naming_prefix" -H "Metadata-Flavor: Google" || echo "concept-viz")
REGION=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | awk -F'/' '{print $NF}' | awk -F'-' '{print $1"-"$2}')
GCP_PROJECT_ID=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")

echo "Running startup for environment: $ENVIRONMENT in project: $GCP_PROJECT_ID, region: $REGION"

# --- Set Configuration Environment Variables ---
echo "Setting configuration environment variables..."
export ENVIRONMENT="$ENVIRONMENT"
export CONCEPT_STORAGE_BUCKET_CONCEPT="${NAMING_PREFIX}-concept-images-${ENVIRONMENT}"
export CONCEPT_STORAGE_BUCKET_PALETTE="${NAMING_PREFIX}-palette-images-${ENVIRONMENT}"
export CONCEPT_DB_TABLE_TASKS="tasks_${ENVIRONMENT}"
export CONCEPT_DB_TABLE_CONCEPTS="concepts_${ENVIRONMENT}"
export CONCEPT_DB_TABLE_PALETTES="color_variations_${ENVIRONMENT}"
export CONCEPT_LOG_LEVEL=$( [[ "$ENVIRONMENT" == "prod" ]] && echo "INFO" || echo "DEBUG" )
export CONCEPT_API_PREFIX="/api"
export CONCEPT_UPSTASH_REDIS_PORT="6379"
# Add other non-secret config vars needed by the backend app

# --- Fetch Secrets ---
echo "Fetching secrets..."
fetch_secret() {
    local secret_name_suffix=$1
    local env_var_name=$2
    local secret_id="${NAMING_PREFIX}-${secret_name_suffix}-${ENVIRONMENT}"
    local value=$(gcloud secrets versions access latest --secret="$secret_id" --project="$GCP_PROJECT_ID" 2>/dev/null || echo "SECRET_NOT_FOUND")

    if [[ "$value" == "SECRET_NOT_FOUND" ]]; then
        echo "Warning: Secret '$secret_id' not found or access denied."
    fi
    export "$env_var_name"="$value"
}

fetch_secret "supabase-url"                "CONCEPT_SUPABASE_URL"
fetch_secret "supabase-key"                "CONCEPT_SUPABASE_KEY"
fetch_secret "supabase-service-role"       "CONCEPT_SUPABASE_SERVICE_ROLE"
fetch_secret "supabase-jwt-secret"         "CONCEPT_SUPABASE_JWT_SECRET"
fetch_secret "jigsawstack-api-key"         "CONCEPT_JIGSAWSTACK_API_KEY"
fetch_secret "redis-endpoint"              "CONCEPT_UPSTASH_REDIS_ENDPOINT"
fetch_secret "redis-password"              "CONCEPT_UPSTASH_REDIS_PASSWORD"
echo "Secrets fetched (values hidden)."

# --- Configure Docker for Artifact Registry ---
echo "Configuring Docker for Artifact Registry: ${REGION}-docker.pkg.dev"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q
if [ $? -ne 0 ]; then echo "Warning: Failed to configure docker for Artifact Registry."; fi

# --- Pull API Image ---
# Construct image URL dynamically
ARTIFACT_REGISTRY_REPO="${NAMING_PREFIX}-docker-repo" # Matches terraform resource name pattern
API_IMAGE_URL="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/concept-api-${ENVIRONMENT}:latest" # Assumes :latest tag

echo "Pulling latest API image: $API_IMAGE_URL"
docker pull "$API_IMAGE_URL" || echo "Warning: Failed to pull image '$API_IMAGE_URL'. Maybe it hasn't been pushed yet?"

# --- Run API Container ---
CONTAINER_NAME="concept-api"
echo "Stopping existing container '$CONTAINER_NAME' if running..."
docker stop "$CONTAINER_NAME" || true
echo "Removing existing container '$CONTAINER_NAME' if present..."
docker rm "$CONTAINER_NAME" || true

echo "Starting API container '$CONTAINER_NAME'..."
# Pass ALL required env vars (config + secrets) to the container
# Using --env-file might be cleaner if many vars, requires creating a file
docker run -d --name "$CONTAINER_NAME" \
  -p 80:8000 \
  --env ENVIRONMENT \
  --env CONCEPT_STORAGE_BUCKET_CONCEPT \
  --env CONCEPT_STORAGE_BUCKET_PALETTE \
  --env CONCEPT_DB_TABLE_TASKS \
  --env CONCEPT_DB_TABLE_CONCEPTS \
  --env CONCEPT_DB_TABLE_PALETTES \
  --env CONCEPT_LOG_LEVEL \
  --env CONCEPT_API_PREFIX \
  --env CONCEPT_UPSTASH_REDIS_PORT \
  --env CONCEPT_SUPABASE_URL \
  --env CONCEPT_SUPABASE_KEY \
  --env CONCEPT_SUPABASE_SERVICE_ROLE \
  --env CONCEPT_SUPABASE_JWT_SECRET \
  --env CONCEPT_JIGSAWSTACK_API_KEY \
  --env CONCEPT_UPSTASH_REDIS_ENDPOINT \
  --env CONCEPT_UPSTASH_REDIS_PASSWORD \
  # Add other -e flags for any other needed vars
  --restart always \
  "$API_IMAGE_URL"

if [ $? -eq 0 ]; then
    echo "API container '$CONTAINER_NAME' started successfully."
else
    echo "Error: Failed to start API container '$CONTAINER_NAME'."
    # You might want to add more detailed error checking/logging here
fi

echo "Startup script finished."
```

**Step 2.13: Define Outputs (`terraform/outputs.tf`)**

```terraform
# terraform/outputs.tf

output "api_vm_external_ip" {
  description = "External IP address of the API VM."
  value       = try(google_compute_address.api_static_ip[0].address, google_compute_instance_group_manager.api_igm.instance_group != null ? tolist(google_compute_instance_group_manager.api_igm.status)[0].stateful.per_instance_configs["*"].network_interface[0].access_config[0].nat_ip : "N/A (Ephemeral or check IGM status)")
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
  description = "Name of the Pub/Sub Lite topic for tasks."
  value       = google_pubsub_lite_topic.tasks_topic.name
}

output "worker_subscription_name" {
  description = "Name of the Pub/Sub Lite subscription for the worker."
  value       = google_pubsub_lite_subscription.worker_subscription.name
}

output "api_service_account_email" {
  description = "Email of the API Service Account."
  value       = google_service_account.api_service_account.email
}

output "worker_service_account_email" {
  description = "Email of the Worker Service Account."
  value       = google_service_account.worker_service_account.email
}
```

**Step 2.14: Create `.gitignore` (`terraform/.gitignore`)**

    ```gitignore
    # Terraform
    terraform/.terraform/
    terraform/*.tfstate
    terraform/*.tfstate.*
    terraform/*.tfplan
    terraform/crash.log
    terraform/crash.*.log
    # Optional: Ignore tfvars if not committing sensitive defaults
    # terraform/environments/*.tfvars
    ```

**Step 2.15: Create Helper Scripts (`scripts/*.sh`)**

- Create `scripts/gcp_apply.sh`, `scripts/gcp_destroy.sh`, and `scripts/gcp_populate_secrets.sh` exactly as provided in the previous answers (the versions that are branch-aware and handle secret population separately). Ensure the `TERRAFORM_DIR` and environment file paths within the scripts are correct relative to your project root where you'll run them. Modify the `terraform init` command in the scripts to pass the backend configuration.

  - **Modify `scripts/gcp_apply.sh` & `scripts/gcp_destroy.sh`:**
    - Replace `terraform init -input=false -no-color` with:
    ```bash
    TF_STATE_BUCKET=$(grep 'terraform_state_bucket_name' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
    if [[ -z "$TF_STATE_BUCKET" ]]; then
        echo "Error: terraform_state_bucket_name not found in $TFVARS_FILE."
        exit 1
    fi
    echo "Initializing Terraform with backend bucket: $TF_STATE_BUCKET"
    terraform init -input=false -no-color \
        -backend-config="bucket=$TF_STATE_BUCKET"
    if [ $? -ne 0 ]; then echo "Error: Terraform init failed."; exit 1; fi
    ```

**Step 2.16: Update `terraform/README.md`**

- Document the two-project structure, prerequisites, **manual GCS state bucket creation & versioning**, **initial IAM grant**, **branch-aware scripts**, and **two-step workflow** (`gcp_apply` then `gcp_populate_secrets`).
- Clarify that bucket/table names are **not** secrets and are passed via environment variables defined in Terraform.
- Warn about production secret handling in `.env.main` for the `gcp_populate_secrets.sh` script.

**Step 2.17: Final Execution Workflow**

1.  Complete all actions from Step 2.1.
2.  Populate `terraform/environments/dev.tfvars` and `terraform/environments/prod.tfvars` with your specific project IDs, state bucket name, user emails, etc.
3.  Navigate to the `terraform/` directory.
4.  Run `terraform fmt` to format your code.
5.  Run `terraform init` **manually once** to download providers. Although the script runs init, doing it manually first helps catch backend config issues early. Ensure it configures the GCS backend correctly using the bucket name from `dev.tfvars` (or pass `-backend-config="bucket=your-bucket-name"` explicitly this first time if needed).
6.  Run `terraform workspace new dev` and `terraform workspace new prod`.
7.  Navigate back to the project root (`cd ..`).
8.  Make scripts executable: `chmod +x scripts/*.sh`.
9.  **Deploy Dev:**
    - `git checkout develop`
    - Ensure `backend/.env.develop` is populated with **development secrets**.
    - Run `scripts/gcp_apply.sh`.
    - Run `scripts/gcp_populate_secrets.sh`.
10. **Deploy Prod:**
    - `git checkout main`
    - Ensure `backend/.env.main` is populated with **production secrets** (handle securely!).
    - Run `scripts/gcp_apply.sh`.
    - Run `scripts/gcp_populate_secrets.sh` (confirm the prompt).
11. **Destroy:** Run `scripts/gcp_destroy.sh` _only_ when needed, while on the corresponding branch (`develop` for dev, `main` for prod), and confirm carefully.

**Step 2.18: Application Code Update (`backend/app/core/config.py`)**

- Ensure your `Settings` class in `config.py` reads `STORAGE_BUCKET_*` and `DB_TABLE_*` variables from the environment, as they will be provided by the deployment (VM startup script / Cloud Run env vars). Provide sensible defaults for local development if the environment variables aren't set.

  ```python
  import os
  from pydantic_settings import BaseSettings, SettingsConfigDict

  class Settings(BaseSettings):
      # ... (API_PREFIX, CORS_ORIGINS, JIGSAWSTACK_*, SUPABASE_*, REDIS_*, etc.)

      # Read bucket/table names from env vars set by deployment
      # Provide defaults that match your local/dev setup or Supabase defaults
      STORAGE_BUCKET_PALETTE: str = os.getenv("CONCEPT_STORAGE_BUCKET_PALETTE", "palette-images-dev")
      STORAGE_BUCKET_CONCEPT: str = os.getenv("CONCEPT_STORAGE_BUCKET_CONCEPT", "concept-images-dev")
      DB_TABLE_TASKS: str = os.getenv("CONCEPT_DB_TABLE_TASKS", "tasks_dev")
      DB_TABLE_CONCEPTS: str = os.getenv("CONCEPT_DB_TABLE_CONCEPTS", "concepts_dev")
      DB_TABLE_PALETTES: str = os.getenv("CONCEPT_DB_TABLE_PALETTES", "color_variations_dev")

      model_config = SettingsConfigDict(
          env_file=".env", # Still read local .env for other vars like keys
          env_file_encoding="utf-8",
          env_prefix="CONCEPT_",
          case_sensitive=True,
          extra='ignore'
      )
      # ... (Rest of Settings class and validation)

  settings = Settings()
  ```

---

This complete plan details each Terraform file, the startup script, helper scripts, and the necessary manual steps, addressing the separation of secrets and configuration.
