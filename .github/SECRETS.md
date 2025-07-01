# GitHub Secrets for CI/CD

This document lists all the GitHub secrets required for the CI/CD workflows to function properly. Many of these secrets are now automatically populated by the `scripts/gh_populate_secrets.sh` script, which is called at the end of `scripts/gcp_apply.sh`. Ensure you have the GitHub CLI (`gh`) installed and authenticated for this automation to work.

All secrets follow a consistent naming convention: environment prefix (`DEV_` or `PROD_`) followed by the service/purpose, or global if not prefixed.

## Overview of GitHub Secrets

### Automatically Populated Secrets (via `scripts/gcp_apply.sh`)

The following secrets are automatically set in your GitHub repository by the `scripts/gh_populate_secrets.sh` script. Values are sourced from Terraform outputs or active `.tfvars` files.

```
# Global (from .tfvars)
GCP_REGION

# Development Environment (from Terraform outputs)
DEV_GCP_PROJECT_ID
DEV_GCP_ZONE
DEV_NAMING_PREFIX
DEV_API_SERVICE_ACCOUNT_EMAIL
DEV_WORKER_SERVICE_ACCOUNT_EMAIL
DEV_CICD_SERVICE_ACCOUNT_EMAIL
DEV_WORKLOAD_IDENTITY_PROVIDER
DEV_ARTIFACT_REGISTRY_REPO_NAME
DEV_FRONTEND_UPTIME_CHECK_CONFIG_ID
DEV_FRONTEND_ALERT_POLICY_ID
DEV_ALERT_NOTIFICATION_CHANNEL_FULL_ID
DEV_FRONTEND_STARTUP_ALERT_DELAY
DEV_ALERT_ALIGNMENT_PERIOD
DEV_WORKER_MIN_INSTANCES
DEV_WORKER_MAX_INSTANCES

# Production Environment (from Terraform outputs)
PROD_GCP_PROJECT_ID
PROD_GCP_ZONE
PROD_NAMING_PREFIX
PROD_API_SERVICE_ACCOUNT_EMAIL
PROD_WORKER_SERVICE_ACCOUNT_EMAIL
PROD_CICD_SERVICE_ACCOUNT_EMAIL
PROD_WORKLOAD_IDENTITY_PROVIDER
PROD_ARTIFACT_REGISTRY_REPO_NAME
PROD_FRONTEND_UPTIME_CHECK_CONFIG_ID
PROD_FRONTEND_ALERT_POLICY_ID
PROD_ALERT_NOTIFICATION_CHANNEL_FULL_ID
PROD_FRONTEND_STARTUP_ALERT_DELAY
PROD_ALERT_ALIGNMENT_PERIOD
PROD_WORKER_MIN_INSTANCES
PROD_WORKER_MAX_INSTANCES
```

### Manually Configured Secrets

These secrets must still be added manually to your GitHub repository settings (Settings > Secrets and variables > Actions). They are typically sensitive, obtained from third-party services, or not part of the Terraform-managed infrastructure.

```
# Global
VERCEL_ORG_ID
VERCEL_TOKEN
TF_STATE_BUCKET_NAME

# Development Environment
DEV_JIGSAWSTACK_API_KEY
DEV_SUPABASE_ANON_KEY
DEV_SUPABASE_JWT_SECRET
DEV_SUPABASE_SERVICE_ROLE
DEV_SUPABASE_URL
DEV_VERCEL_PROJECT_ID
DEV_UPSTASH_REDIS_ENDPOINT
DEV_UPSTASH_REDIS_PASSWORD
DEV_UPSTASH_REDIS_PORT

# Production Environment
PROD_JIGSAWSTACK_API_KEY
PROD_SUPABASE_ANON_KEY
PROD_SUPABASE_JWT_SECRET
PROD_SUPABASE_SERVICE_ROLE
PROD_SUPABASE_URL
PROD_VERCEL_PROJECT_ID
PROD_UPSTASH_REDIS_ENDPOINT
PROD_UPSTASH_REDIS_PASSWORD
PROD_UPSTASH_REDIS_PORT
```

## Terraform Outputs & Secret Population

While many GitHub secrets are now set automatically using the `scripts/gh_populate_secrets.sh` script (which internally uses `terraform output`), you might still want to inspect Terraform outputs directly for verification or debugging.

After applying your Terraform configuration for each environment, you can view the outputs. For example:

1. For Development environment:

   ```bash
   # After running scripts/gcp_apply.sh on the develop branch
   # To view specific outputs (already used by the automation script):
   cd terraform
   terraform workspace select dev
   terraform output -raw workload_identity_full_provider_name
   terraform output -raw cicd_service_account_email
   # etc.
   ```

2. For Production environment:
   ```bash
   # After running scripts/gcp_apply.sh on the main branch
   cd terraform
   terraform workspace select prod
   terraform output -raw workload_identity_full_provider_name
   # etc.
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

### Vercel Development

- `DEV_VERCEL_PROJECT_ID`: The Vercel Project ID for the development frontend deployment.

### Redis Development (for Rate-Limit Flush)

- `DEV_UPSTASH_REDIS_ENDPOINT`: The Redis endpoint hostname for the development environment (without protocol, e.g., "your-redis.upstash.io")
- `DEV_UPSTASH_REDIS_PASSWORD`: The Redis password for the development environment
- `DEV_UPSTASH_REDIS_PORT`: The Redis port for the development environment (optional, defaults to 6379)

### Frontend Monitoring Development (GCP)

- `DEV_FRONTEND_UPTIME_CHECK_CONFIG_ID`: The ID of the GCP Uptime Check configuration for the dev frontend.
- `DEV_FRONTEND_ALERT_POLICY_ID`: The ID of the GCP Alert Policy for the dev frontend.
- `DEV_ALERT_NOTIFICATION_CHANNEL_FULL_ID`: The full ID of the GCP Notification Channel for dev alerts (e.g., projects/your-project/notificationChannels/your-channel-id).
- `DEV_FRONTEND_STARTUP_ALERT_DELAY`: The delay before alerts become active for new dev frontend deployments (e.g., '300s').
- `DEV_ALERT_ALIGNMENT_PERIOD`: The alignment period for dev frontend alert conditions (e.g., '300s').

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

### Vercel Production

- `PROD_VERCEL_PROJECT_ID`: The Vercel Project ID for the production frontend deployment.

### Redis Production (for Rate-Limit Flush)

- `PROD_UPSTASH_REDIS_ENDPOINT`: The Redis endpoint hostname for the production environment (without protocol, e.g., "your-redis.upstash.io")
- `PROD_UPSTASH_REDIS_PASSWORD`: The Redis password for the production environment
- `PROD_UPSTASH_REDIS_PORT`: The Redis port for the production environment (optional, defaults to 6379)

### Frontend Monitoring Production (GCP)

- `PROD_FRONTEND_UPTIME_CHECK_CONFIG_ID`: The ID of the GCP Uptime Check configuration for the prod frontend.
- `PROD_FRONTEND_ALERT_POLICY_ID`: The ID of the GCP Alert Policy for the prod frontend.
- `PROD_ALERT_NOTIFICATION_CHANNEL_FULL_ID`: The full ID of the GCP Notification Channel for prod alerts (e.g., projects/your-project/notificationChannels/your-channel-id).
- `PROD_FRONTEND_STARTUP_ALERT_DELAY`: The delay before alerts become active for new prod frontend deployments (e.g., '2100s').
- `PROD_ALERT_ALIGNMENT_PERIOD`: The alignment period for prod frontend alert conditions (e.g., '300s').

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
