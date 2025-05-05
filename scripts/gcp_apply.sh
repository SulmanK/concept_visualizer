#!/bin/bash
set -e

# Branch-aware Terraform apply script
# This script detects your current git branch and applies the appropriate Terraform workspace

# Get the absolute path to the project root directory (parent of the script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
DEV_BRANCH="develop"
PROD_BRANCH="main"
DEV_WORKSPACE="dev"
PROD_WORKSPACE="prod"
DEV_TFVARS_FILE="$TERRAFORM_DIR/environments/dev.tfvars"
PROD_TFVARS_FILE="$TERRAFORM_DIR/environments/prod.tfvars"

# Get current git branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current git branch: $CURRENT_BRANCH"

# Choose env file and environment name based on branch
if [[ "$CURRENT_BRANCH" == "$DEV_BRANCH" ]]; then
    ENVIRONMENT="dev"
    TFVARS_FILE="$DEV_TFVARS_FILE"
    echo "Using development environment based on branch '$DEV_BRANCH'"
elif [[ "$CURRENT_BRANCH" == "$PROD_BRANCH" ]]; then
    ENVIRONMENT="prod"
    TFVARS_FILE="$PROD_TFVARS_FILE"
    echo "Using production environment based on branch '$PROD_BRANCH'"

    # Extra confirmation for production
    echo ""
    echo "WARNING: You are about to deploy to PRODUCTION."
    echo ""
    read -p "Type 'update-production' to confirm: " CONFIRM_PROD

    if [[ "$CONFIRM_PROD" != "update-production" ]]; then
        echo "Production confirmation does not match. Deployment cancelled."
        exit 1
    fi
else
    echo "Error: Branch '$CURRENT_BRANCH' does not match either '$DEV_BRANCH' or '$PROD_BRANCH'."
    echo "Please checkout one of those branches to run this script."
    exit 1
fi

# Check if tfvars file exists
if [[ ! -f "$TFVARS_FILE" ]]; then
    echo "Error: Terraform variables file '$TFVARS_FILE' not found."
    echo "Please create this file with your environment-specific variables."
    exit 1
fi

# Get project ID from tfvars
PROJECT_ID=$(grep 'project_id' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -z "$PROJECT_ID" ]]; then
    echo "Error: project_id not found in $TFVARS_FILE."
    exit 1
fi

NAMING_PREFIX=$(grep 'naming_prefix' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -z "$NAMING_PREFIX" ]]; then
    echo "Error: naming_prefix not found in $TFVARS_FILE."
    exit 1
fi

# Change to Terraform directory
cd "$TERRAFORM_DIR"

# Initialize Terraform with backend configuration
TF_STATE_BUCKET=$(grep 'terraform_state_bucket_name' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -z "$TF_STATE_BUCKET" ]]; then
    echo "Error: terraform_state_bucket_name not found in $TFVARS_FILE."
    exit 1
fi
echo "Initializing Terraform with backend bucket: $TF_STATE_BUCKET"
terraform init -input=false -no-color \
    -backend-config="bucket=$TF_STATE_BUCKET"
if [ $? -ne 0 ]; then echo "Error: Terraform init failed."; exit 1; fi

# Select workspace
echo "Selecting Terraform workspace: $ENVIRONMENT"
terraform workspace select "$ENVIRONMENT" || terraform workspace new "$ENVIRONMENT"

# STEP 1: First create service accounts and IAM permissions
echo -e "\n===== STEP 1: Creating Service Accounts and IAM Permissions =====\n"
terraform plan -var-file="$TFVARS_FILE" \
  -target=google_service_account.api_service_account \
  -target=google_service_account.worker_service_account \
  -target=google_project_iam_member.worker_sa_secret_accessor \
  -target=google_project_iam_member.api_sa_secret_accessor \
  -out=tfplan.accounts

echo "Ready to create/update Service Accounts and IAM Permissions."
terraform apply -auto-approve tfplan.accounts
if [ $? -ne 0 ]; then
    echo "Error: Failed to create Service Accounts and IAM Permissions."
    exit 1
fi

# STEP 2: Apply to create just the Secret Manager resources
echo -e "\n===== STEP 2: Creating Secret Manager resources =====\n"
terraform plan -var-file="$TFVARS_FILE" \
  -target=google_secret_manager_secret.supabase_url \
  -target=google_secret_manager_secret.supabase_key \
  -target=google_secret_manager_secret.supabase_service_role \
  -target=google_secret_manager_secret.supabase_jwt_secret \
  -target=google_secret_manager_secret.jigsaw_key \
  -target=google_secret_manager_secret.redis_endpoint \
  -target=google_secret_manager_secret.redis_password \
  -target=google_secret_manager_secret_iam_member.worker_sa_can_access_secrets \
  -target=google_secret_manager_secret_iam_member.api_sa_can_access_secrets \
  -out=tfplan.secrets

echo "Ready to create/update Secret Manager resources."
terraform apply -auto-approve tfplan.secrets
if [ $? -ne 0 ]; then
    echo "Error: Failed to create Secret Manager resources."
    exit 1
fi

# Wait for resources to be fully propagated
echo -e "\nWaiting for Secret Manager resources to be fully propagated (15 seconds)..."
sleep 15

# STEP 3: Run the script to populate secrets
echo -e "\n===== STEP 3: Populating secrets =====\n"
"$SCRIPT_DIR/gcp_populate_secrets.sh"
SECRETS_RESULT=$?
if [ $SECRETS_RESULT -ne 0 ]; then
    echo "Error: Failed to populate secrets (exit code $SECRETS_RESULT)."
    echo "Please check the secrets script and try again."
    echo "You may need to run only the populate_secrets script separately."
    read -p "Continue with infrastructure deployment anyway? (y/n) " CONTINUE_ANYWAY
    if [[ "$CONTINUE_ANYWAY" != "y" && "$CONTINUE_ANYWAY" != "Y" ]]; then
        echo "Deployment canceled."
        exit 1
    fi
    echo "Continuing with deployment despite secret population failure..."
fi

# STEP 4: Apply the full Terraform configuration
echo -e "\n===== STEP 4: Applying full infrastructure =====\n"
terraform plan -var-file="$TFVARS_FILE" -out=tfplan.full
echo -e "\nReady to apply changes to $ENVIRONMENT environment."
read -p "Do you want to continue with the full infrastructure apply? (y/n) " CONTINUE

if [[ "$CONTINUE" != "y" && "$CONTINUE" != "Y" ]]; then
    echo "Terraform full apply canceled."
    exit 0
fi

terraform apply -auto-approve tfplan.full
if [ $? -ne 0 ]; then
    echo "Error: Failed to apply full infrastructure."
    exit 1
fi

echo -e "\nInfrastructure deployment completed successfully!"

# STEP 5: Upload startup scripts to the created storage bucket
echo -e "\n===== STEP 5: Uploading startup scripts to storage bucket =====\n"
"$SCRIPT_DIR/upload_startup_scripts.sh"
if [ $? -ne 0 ]; then
    echo "Warning: Failed to upload startup scripts. VMs may not initialize correctly."
    echo "Please run scripts/upload_startup_scripts.sh manually."
else
    echo "Startup scripts uploaded successfully."
fi

echo -e "\nDeployment process completed!"
