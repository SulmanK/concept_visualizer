# Deploy Backend and Update Frontend Monitor Workflow

## Overview

The `Deploy Backend and Update Frontend Monitor` workflow handles the deployment of backend components to Google Cloud Platform (GCP) and updates the monitoring configuration for the frontend. This workflow runs after the CI Tests & Deployment workflow has successfully built the Docker images.

## Triggers

This workflow runs when:

- The `CI Tests & Deployment` workflow completes successfully on `main` or `develop` branches

## Workflow Structure

### Environment Setup

The workflow first sets environment-specific variables based on the branch that triggered the workflow:

- `develop` branch → dev environment
- `main` branch → production environment

It configures variables for:

- GCP project ID and zone
- Naming prefixes
- Workload identity provider
- Service account emails
- Artifact registry repository names
- Worker instance configurations
- Monitoring settings

### GCP Authentication

Uses Google GitHub Actions to authenticate to GCP using Workload Identity Federation, providing secure access to GCP resources without storing static credentials.

### Deploy Cloud Function Worker

Deploys the background worker as a Cloud Function (gen2):

- Sets appropriate environment variables
- Configures secrets from Secret Manager
- Sets resource limits (memory, timeout)
- Configures the Pub/Sub trigger
- Sets auto-scaling parameters
- Deploys from the `backend` directory

### Deploy API to Compute Engine MIG

Deploys the API to a Managed Instance Group (MIG) on Compute Engine:

1. Constructs a Docker image URL with the commit SHA
2. Creates a unique instance template with timestamp and commit hash
3. Gets the static IP address for the API
4. Creates a new instance template with:
   - The new Docker image
   - Service account configuration
   - Network settings
   - Startup script reference
   - Metadata including environment variables
5. Updates the MIG to use the new template
6. Gets current VM instances in the group
7. For single-instance MIGs:
   - Restarts existing instances to apply the new template
   - Temporarily scales the MIG to 0 then back to 1 to force recreation with the new template
8. Cleans up old templates, keeping only the latest 10

### Get Latest Vercel Deployment URL

For frontend monitoring:

1. Fetches the URL of the latest Vercel deployment
2. For `main` branch, looks for production deployments
3. Handles both production domains and preview deployments
4. Uses fallback strategies when needed

### Apply/Update Frontend Monitoring Resources

Updates GCP monitoring for the frontend:

1. Configures Terraform with the remote backend
2. Selects the appropriate Terraform workspace
3. Creates a temporary tfvars file with monitoring settings
4. Applies changes to uptime check and alert policy resources
5. Cleans up temporary files

## Key Features

1. **Template Management**: Creates unique templates with timestamps and cleans up old ones
2. **Instance Recreation**: Forces VM recreations to ensure new Docker images are used
3. **Environment Separation**: Maintains separate configurations for dev and prod environments
4. **Frontend Monitoring**: Automatically updates monitoring to target the latest deployment

## Configuration Requirements

The workflow requires numerous secrets to be configured in the GitHub repository:

- GCP project IDs and regions
- Workload identity providers
- Service account emails
- Naming prefixes
- Terraform state bucket names
- Artifact registry repository names
- Vercel configuration settings
- Monitoring resource IDs
