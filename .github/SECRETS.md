# GitHub Secrets for CI/CD

This document lists all the GitHub secrets required for the CI/CD workflows to function properly. All secrets follow a consistent naming convention: environment prefix (`DEV_` or `PROD_`) followed by the service/purpose.

## Complete List of Required GitHub Secrets

Add these secrets to your GitHub repository under Settings > Secrets and variables > Actions:

```
# GCP Authentication (shared between environments)
GCP_REGION

# Development Environment
DEV_GCP_PROJECT_ID
DEV_GCP_ZONE
DEV_ARTIFACT_REGISTRY_REPO_NAME
DEV_NAMING_PREFIX
DEV_WORKLOAD_IDENTITY_PROVIDER  # From Terraform output: workload_identity_provider
DEV_CICD_SERVICE_ACCOUNT_EMAIL  # From Terraform output: cicd_service_account_email
DEV_WORKER_SERVICE_ACCOUNT_EMAIL # From Terraform output
DEV_API_SERVICE_ACCOUNT_EMAIL   # From Terraform output
DEV_SUPABASE_URL
DEV_SUPABASE_ANON_KEY
DEV_SUPABASE_SERVICE_ROLE
DEV_SUPABASE_JWT_SECRET
DEV_JIGSAWSTACK_API_KEY

# Production Environment
PROD_GCP_PROJECT_ID
PROD_GCP_ZONE
PROD_ARTIFACT_REGISTRY_REPO_NAME
PROD_NAMING_PREFIX
PROD_WORKLOAD_IDENTITY_PROVIDER  # From Terraform output: workload_identity_provider
PROD_CICD_SERVICE_ACCOUNT_EMAIL  # From Terraform output: cicd_service_account_email
PROD_WORKER_SERVICE_ACCOUNT_EMAIL # From Terraform output
PROD_API_SERVICE_ACCOUNT_EMAIL  # From Terraform output
PROD_SUPABASE_URL
PROD_SUPABASE_ANON_KEY
PROD_SUPABASE_SERVICE_ROLE
PROD_SUPABASE_JWT_SECRET
PROD_JIGSAWSTACK_API_KEY
```

## Terraform-Managed Resources

Several secrets are automatically created and managed by Terraform. After applying your Terraform configuration for each environment, use the outputs to populate these GitHub secrets:

1. For Development environment:

   ```bash
   # After applying Terraform to the dev environment (terraform workspace select dev && terraform apply)
   export DEV_WORKLOAD_IDENTITY_PROVIDER=$(terraform output -raw workload_identity_provider)
   export DEV_CICD_SERVICE_ACCOUNT_EMAIL=$(terraform output -raw cicd_service_account_email)
   export DEV_WORKER_SERVICE_ACCOUNT_EMAIL=$(terraform output -raw worker_service_account_email)
   export DEV_API_SERVICE_ACCOUNT_EMAIL=$(terraform output -raw api_service_account_email)

   # You can then add these as GitHub secrets
   # (either manually or using the GitHub CLI)
   ```

2. For Production environment:

   ```bash
   # After applying Terraform to the prod environment (terraform workspace select prod && terraform apply)
   export PROD_WORKLOAD_IDENTITY_PROVIDER=$(terraform output -raw workload_identity_provider)
   export PROD_CICD_SERVICE_ACCOUNT_EMAIL=$(terraform output -raw cicd_service_account_email)
   export PROD_WORKER_SERVICE_ACCOUNT_EMAIL=$(terraform output -raw worker_service_account_email)
   export PROD_API_SERVICE_ACCOUNT_EMAIL=$(terraform output -raw api_service_account_email)

   # You can then add these as GitHub secrets
   # (either manually or using the GitHub CLI)
   ```

## Details of GitHub Secrets

## Development Environment

### GCP Development Configuration

- `DEV_GCP_PROJECT_ID`: The GCP project ID for the development environment
- `DEV_GCP_ZONE`: The GCP zone for the development environment (e.g., us-central1-a)
- `DEV_GCP_REGION`: The GCP region for the development environment (e.g., us-central1)
- `DEV_ARTIFACT_REGISTRY_REPO_NAME`: The name of the Artifact Registry repository for the development environment (e.g., concept-viz-dev-docker-repo)
- `DEV_NAMING_PREFIX`: The naming prefix for development resources (e.g., concept-viz-dev)
- `DEV_WORKLOAD_IDENTITY_PROVIDER`: The full path of the Workload Identity Federation provider for the development environment. Get this from Terraform output.
- `DEV_CICD_SERVICE_ACCOUNT_EMAIL`: Email address of the service account used for CI/CD in the development environment. Get this from Terraform output.
- `DEV_WORKER_SERVICE_ACCOUNT_EMAIL`: Email address of the service account used for the worker (Cloud Function) in the development environment. Get this from Terraform output.
- `DEV_API_SERVICE_ACCOUNT_EMAIL`: Email address of the service account used for the API VM in the development environment. Get this from Terraform output.

### Supabase Development

- `DEV_SUPABASE_URL`: The Supabase URL for the development environment
- `DEV_SUPABASE_ANON_KEY`: The Supabase anonymous key for the development environment
- `DEV_SUPABASE_SERVICE_ROLE`: The Supabase service role key for the development environment
- `DEV_SUPABASE_JWT_SECRET`: The JWT secret for the development environment

### JigsawStack Development

- `DEV_JIGSAWSTACK_API_KEY`: The JigsawStack API key for the development environment

## Production Environment

### GCP Production Configuration

- `PROD_GCP_PROJECT_ID`: The GCP project ID for the production environment
- `PROD_GCP_ZONE`: The GCP zone for the production environment (e.g., us-east1-b)
- `PROD_GCP_REGION`: The GCP region for the production environment (e.g., us-east1)
- `PROD_ARTIFACT_REGISTRY_REPO_NAME`: The name of the Artifact Registry repository for the production environment (e.g., concept-viz-prod-docker-repo)
- `PROD_NAMING_PREFIX`: The naming prefix for production resources (e.g., concept-viz-prod)
- `PROD_WORKLOAD_IDENTITY_PROVIDER`: The full path of the Workload Identity Federation provider for the production environment. Get this from Terraform output.
- `PROD_CICD_SERVICE_ACCOUNT_EMAIL`: Email address of the service account used for CI/CD in the production environment. Get this from Terraform output.
- `PROD_WORKER_SERVICE_ACCOUNT_EMAIL`: Email address of the service account used for the worker (Cloud Function) in the production environment. Get this from Terraform output.
- `PROD_API_SERVICE_ACCOUNT_EMAIL`: Email address of the service account used for the API VM in the production environment. Get this from Terraform output.

### Supabase Production

- `PROD_SUPABASE_URL`: The Supabase URL for the production environment
- `PROD_SUPABASE_ANON_KEY`: The Supabase anonymous key for the production environment
- `PROD_SUPABASE_SERVICE_ROLE`: The Supabase service role key for the production environment
- `PROD_SUPABASE_JWT_SECRET`: The JWT secret for the production environment

### JigsawStack Production

- `PROD_JIGSAWSTACK_API_KEY`: The JigsawStack API key for the production environment

## Testing Environment Variables

These environment variables are used during CI testing but are hardcoded in the workflows (not GitHub secrets):

- `CONCEPT_UPSTASH_REDIS_ENDPOINT`: The Redis endpoint used for caching tests
- `CONCEPT_UPSTASH_REDIS_PASSWORD`: The Redis password for testing
- `CONCEPT_UPSTASH_REDIS_PORT`: The Redis port for testing
- `CONCEPT_STORAGE_BUCKET_CONCEPT`: The name of the GCS bucket for storing concepts during tests
- `CONCEPT_STORAGE_BUCKET_PALETTE`: The name of the GCS bucket for storing palettes during tests

## Adding Secrets to GitHub

1. Navigate to your GitHub repository
2. Go to Settings > Secrets and variables > Actions
3. Click on "New repository secret"
4. Add each secret with its corresponding name and value
5. Ensure all secrets listed in this document are added before running any workflows

## Naming Convention

All secrets should follow a consistent naming pattern:

- Development environment: `DEV_` prefix (e.g., `DEV_SUPABASE_URL`)
- Production environment: `PROD_` prefix (e.g., `PROD_SUPABASE_URL`)
- Testing mock values: Used directly in the workflow files, not as secrets
