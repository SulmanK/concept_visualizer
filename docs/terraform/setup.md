# Terraform Setup Guide

This guide walks through the steps needed to set up and deploy the Concept Visualizer infrastructure on Google Cloud Platform (GCP) using Terraform.

## Prerequisites

Before beginning, ensure you have:

1. **Google Cloud Platform Account** with billing enabled
2. **Required Software**:
   - [Terraform](https://www.terraform.io/downloads.html) (>= v1.3)
   - [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)
   - [Git](https://git-scm.com/downloads)
3. **IAM Permissions** to create and manage resources in GCP
4. **Google Cloud Projects** created for:
   - Development environment
   - Production environment
   - (Optional) Terraform state management (recommended for team environments)

## Step 1: Initial GCP Setup

### Create Projects

If not already created, set up your GCP projects:

```bash
# Development project
gcloud projects create YOUR_DEV_PROJECT_ID --name="Concept Visualizer Dev"

# Production project
gcloud projects create YOUR_PROD_PROJECT_ID --name="Concept Visualizer Prod"

# Optional: Terraform state project
gcloud projects create YOUR_TF_STATE_PROJECT_ID --name="Concept Visualizer TF State"
```

### Enable Required APIs

For each project, enable the necessary Google Cloud APIs:

```bash
# Set project
gcloud config set project YOUR_PROJECT_ID

# Enable services
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

Repeat this for each project.

### Create Terraform State Bucket

Set up a Cloud Storage bucket to store the Terraform state:

```bash
# Set project to the Terraform state project (or any project you choose)
gcloud config set project YOUR_TF_STATE_PROJECT_ID

# Create a globally unique bucket name
export TF_STATE_BUCKET="YOUR_PROJECT_ID-tfstate"

# Create bucket with versioning enabled
gcloud storage buckets create gs://$TF_STATE_BUCKET \
  --location=us-central1 \
  --uniform-bucket-level-access

# Enable versioning
gcloud storage buckets update gs://$TF_STATE_BUCKET --versioning
```

### Grant IAM Permissions

Ensure your user account has the necessary permissions to access the Terraform state bucket:

```bash
gcloud storage buckets add-iam-policy-binding gs://$TF_STATE_BUCKET \
  --member="user:YOUR_EMAIL@example.com" \
  --role="roles/storage.admin"
```

## Step 2: Repository Setup

### Clone the Repository

```bash
git clone https://github.com/SulmanK/concept-visualizer.git
cd concept-visualizer
```

### Configure Environment Variables

Create the environment variable files for each environment:

1. Copy the example files:

```bash
cp terraform/environments/dev.tfvars.example terraform/environments/dev.tfvars
cp terraform/environments/prod.tfvars.example terraform/environments/prod.tfvars
```

2. Edit the files to set your specific values:

```bash
# Edit development environment variables
nano terraform/environments/dev.tfvars

# Edit production environment variables
nano terraform/environments/prod.tfvars
```

The variables to set include:

- Project IDs
- Region and zone
- Naming prefixes
- Machine types
- Terraform state bucket name
- Alert email address

## Step 3: Initialize Terraform

Set up Terraform workspaces for managing different environments:

```bash
cd terraform

# Initialize with the backend configuration
terraform init -backend-config="bucket=YOUR_TF_STATE_BUCKET"

# Create workspaces for each environment
terraform workspace new dev
terraform workspace new prod

# Verify workspaces
terraform workspace list
```

## Step 4: Deploy Infrastructure

The project includes helper scripts to deploy to the correct environment based on your current git branch:

### Development Deployment

```bash
# Checkout the develop branch
git checkout develop

# Run the apply script
../scripts/gcp_apply.sh
```

The script will:

1. Detect you're on the develop branch and use dev.tfvars
2. Create service accounts and IAM permissions
3. Set up Secret Manager resources
4. Populate secrets
5. Deploy the full infrastructure
6. Build and push the API Docker image
7. Upload startup scripts
8. Configure GitHub secrets

### Production Deployment

```bash
# Checkout the main branch
git checkout main

# Run the apply script
../scripts/gcp_apply.sh
```

For production, you'll be prompted to type `update-production` to confirm the deployment.

## Step 5: Post-Deployment Tasks

After successful deployment:

1. **Update Vercel Configuration**: Update the `frontend/my-app/vercel.json` file with the correct API VM IP address (this should be done automatically by `gcp_apply.sh`)

2. **Deploy Frontend**: Deploy the frontend to Vercel

3. **Verify Resources**: Check that all GCP resources are properly created and running

4. **Test Application**: Verify that the application works end-to-end

## Troubleshooting

### Common Issues

1. **Missing APIs**: If you encounter errors about APIs not being enabled, check that you've enabled all required services.

2. **Permission Denied**: Ensure your account has the necessary IAM roles to create resources.

3. **Terraform State Lock**: If a deployment fails and leaves a state lock, the script will offer to remove it on the next run.

4. **Docker Image Build Failure**: If the Docker image fails to build, you can manually build and push it:

```bash
cd backend
docker build -t REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/concept-api-ENV:latest .
docker push REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/concept-api-ENV:latest
```

### Getting Help

If you encounter issues not covered here:

1. Check the Terraform logs for specific error messages
2. Review the GCP Cloud Console for resource status
3. Check the project GitHub repository for known issues

## Next Steps

- Review the [Components Overview](components.md) for detailed information about each part of the infrastructure
- Learn about day-to-day operations in the [Operations Guide](operations.md)
- Understand the security configuration in the [Security Overview](security.md)
