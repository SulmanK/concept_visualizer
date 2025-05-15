# Concept Visualizer GCP Infrastructure

This directory contains Terraform configurations for setting up the Google Cloud Platform (GCP) infrastructure for the Concept Visualizer project. The project follows a two-project structure with separate environments for development and production.

## Environment Structure

- **Development Environment**: Project ID: `proj-dev`
- **Production Environment**: Project ID: `proj-prod`
- **Terraform State Storage**: Project ID: `proj-managed`, Bucket: `proj-tfstate`

## Prerequisites

Before using these Terraform configurations, ensure you have:

1. **Terraform CLI** (>= v1.3) installed on your local machine
2. **Google Cloud SDK** installed and configured
3. **GCP Projects** created in the GCP Console:
   - Development project: `proj-dev`
   - Production project: `proj-prod`
4. **GCP APIs Enabled** in both projects:
   ```
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
      cloudresourcemanager.googleapis.com \
      eventarc.googleapis.com \
      cloudfunctions.googleapis.com
   ```
5. **GCS Bucket for Terraform State** created manually with versioning enabled:
   - Bucket name: `proj-tfstate`
   - Created in project: `proj-managed`
6. **Initial IAM Permissions** granted on the state bucket:
   ```bash
   gcloud storage buckets add-iam-policy-binding gs://concept-visualizer-tfstate-1 \
     --member="user:username@email.com" \
     --role="roles/storage.admin" \
     --project="proj-managed"
   ```

## Configuration Files

- `variables.tf`: Defines all input variables
- `main.tf`: Configures Terraform providers and backend
- `network.tf`: Network and firewall configuration
- `iam.tf`: IAM roles and permissions
- `secrets.tf`: Secret Manager configuration (container setup only, no values)
- `artifact_registry.tf`: Artifact Registry setup
- `pubsub.tf`: Pub/Sub topics and subscriptions
- `cloud_function.tf`: Cloud Functions (2nd Gen) worker configuration
- `compute.tf`: Compute Engine VM for API service
- `outputs.tf`: Output values after deployment
- `environments/dev.tfvars`: Development environment variables (not committed)
- `environments/prod.tfvars`: Production environment variables (not committed)
- `environments/*.tfvars.example`: Example environment variable files (committed)
- `scripts/startup-api.sh`: VM startup script to configure the API VM

## Helper Scripts

The following helper scripts are located in the `scripts/` directory at the project root:

- `gcp_apply.sh`: Branch-aware script to apply Terraform configuration
- `gcp_destroy.sh`: Branch-aware script to destroy Terraform resources
- `gcp_populate_secrets.sh`: Script to populate secrets in Secret Manager

## Workflow

1. Ensure all prerequisites are met
2. Populate environment variable files:
   - `terraform/environments/dev.tfvars`
   - `terraform/environments/prod.tfvars`
3. Initialize Terraform:
   ```bash
   cd terraform
   terraform init -backend-config="bucket=concept-visualizer-tfstate-1"
   terraform workspace new dev
   terraform workspace new prod
   cd ..
   ```
4. Deploy infrastructure using the branch-aware scripts:
   - For development environment:
     ```bash
     git checkout develop
     scripts/gcp_apply.sh
     ```
   - For production environment:
     ```bash
     git checkout main
     scripts/gcp_apply.sh
     ```

## Important Notes

- **Secrets Management**: This setup keeps secrets out of Terraform state files by:

  1. Using Terraform to create empty secret containers and permissions
  2. Using a separate script to populate secret values after Terraform apply

- **Configuration vs. Secrets**:

  - Non-sensitive configuration values (bucket/table names) are passed via environment variables defined in Terraform
  - Sensitive values (API keys, credentials) are stored in Secret Manager

- **Environment-Based Deployment**:

  - The scripts detect which environment to work with based on the git branch:
    - `develop` branch → `dev` environment
    - `main` branch → `prod` environment

- **Production Deployments**:
  - Production deployments require additional confirmation
  - Handle the production secret file (`backend/.env.main`) securely

## Troubleshooting

- **State Bucket Access**: If you encounter access issues with the Terraform state bucket, ensure your user has the correct IAM permissions.
- **API Enabling**: If you encounter "API not enabled" errors, make sure all required APIs are enabled in both GCP projects.
- **Secret Population**: If the secret population script fails, check if Terraform has successfully created the secret containers.
- **Docker Image**: The API VM requires a Docker image to be pushed to Artifact Registry. This is typically handled by CI/CD after the infrastructure is set up.
