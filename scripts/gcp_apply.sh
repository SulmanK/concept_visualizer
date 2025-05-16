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

# NEW STEP: Build and push API Docker image (now after infrastructure exists)
echo -e "\n===== STEP 5: Building and pushing API Docker image =====\n"
# Extract variables needed for Docker build
PROJECT_ID=$(grep 'project_id' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
REGION=$(grep 'region' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
NAMING_PREFIX=$(grep 'naming_prefix' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')

# Check for and offer to clear state lock if it exists
check_and_clear_state_lock() {
  local workspace="$1"
  local bucket="$TF_STATE_BUCKET"

  echo "Checking for state locks in workspace: $workspace..."

  # Check if there's a lock file
  if gsutil -q stat "gs://${bucket}/terraform/state/${workspace}.tflock" 2>/dev/null; then
    echo "WARNING: State lock detected for workspace: $workspace"

    # Try to get lock info
    local lock_content
    lock_content=$(gsutil cat "gs://${bucket}/terraform/state/${workspace}.tflock" 2>/dev/null || echo "Could not read lock file")

    echo "Lock Info:"
    echo "$lock_content"

    read -p "Do you want to force-remove this lock? Only do this if you're sure no other operations are running! (y/n) " force_unlock

    if [[ "$force_unlock" == "y" || "$force_unlock" == "Y" ]]; then
      echo "Removing state lock..."
      if gsutil rm "gs://${bucket}/terraform/state/${workspace}.tflock"; then
        echo "Lock successfully removed."
      else
        echo "Failed to remove lock. You may need to do this manually."
        exit 1
      fi
    else
      echo "Proceeding with lock in place. This may cause failures if the lock is still active."
    fi
  else
    echo "No state lock detected for workspace: $workspace"
  fi
}

# Check for state lock before proceeding with deployment
check_and_clear_state_lock "$ENVIRONMENT"

# Construct the image name
ARTIFACT_REGISTRY_REPO="${NAMING_PREFIX}-docker-repo"
API_IMAGE_NAME="${REGION}-docker.pkg.dev/${PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/concept-api-${ENVIRONMENT}:latest"

echo "Building Docker image: $API_IMAGE_NAME"

# Configure Docker to use Artifact Registry
gcloud auth configure-docker ${REGION}-docker.pkg.dev --quiet

# Navigate to the backend directory
cd "$PROJECT_ROOT/backend"

# Build and push the Docker image
docker build -t "$API_IMAGE_NAME" -f Dockerfile .
if [ $? -ne 0 ]; then
    echo "Error: Failed to build Docker image."
    echo "VM may not start correctly without a valid image."
else
    echo "Pushing Docker image to Artifact Registry: $API_IMAGE_NAME"
    docker push "$API_IMAGE_NAME"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to push Docker image to Artifact Registry."
        echo "VM may not start correctly without a valid image in the repository."
    else
        echo "Docker image successfully built and pushed!"
    fi
fi

# Return to Terraform directory
cd "$TERRAFORM_DIR"

echo -e "\n===== ADDRESSING STARTUP TIMING COORDINATION =====\n"
echo "The VM startup script will attempt to pull the Docker image we just pushed."
echo "The startup script has been configured with retry logic to handle this timing issue."
echo "We'll still verify the VM status to ensure proper coordination."

# Check VM status before attempting a restart
echo -e "\nChecking VM status..."

# Get the instance group name from Terraform outputs
VM_IGM_NAME=$(terraform output -raw api_igm_name)
VM_IGM_ZONE=$(terraform output -raw api_igm_zone)

echo "Instance Group: $VM_IGM_NAME in zone $VM_IGM_ZONE"

# Wait long enough for VMs to be fully booted and packages to be installed
echo "Waiting to allow the VM to complete its initial startup and package installation..."
echo "This prevents interrupting critical system setup processes."
sleep 120

# Check if instances exist and their status
VM_INSTANCE_PREFIX="${NAMING_PREFIX}-api-vm-${ENVIRONMENT}"
INSTANCES=$(gcloud compute instances list \
  --filter="name~'^${VM_INSTANCE_PREFIX}'" \
  --project="$PROJECT_ID" \
  --format="value(name,zone,status)")

if [ -z "$INSTANCES" ]; then
  echo "No instances found matching the pattern '${VM_INSTANCE_PREFIX}'."
  echo "The VM may still be initializing. The VM startup script will attempt to pull the image with retries."
  echo "No manual restart required at this point - the VM will start the container when ready."
else
  echo "Found instances:"
  echo "$INSTANCES"

  # Check if all instances are in RUNNING state
  if echo "$INSTANCES" | grep -q "RUNNING"; then
    echo "VM instances are running. The startup script should be able to pull the new image."

    # Ask if user wants to restart instances
    read -p "Do you want to restart the instances to ensure they pick up the new image? (y/n) " RESTART_VMS

    if [[ "$RESTART_VMS" == "y" || "$RESTART_VMS" == "Y" ]]; then
      echo "Initiating restart of VM instances..."

      # Try rolling action restart first
      if gcloud compute instance-groups managed rolling-action restart "$VM_IGM_NAME" \
         --zone="$VM_IGM_ZONE" \
         --project="$PROJECT_ID"; then
        echo "Successfully initiated rolling restart of the VM instance group."
      else
        echo "Warning: Failed to restart VM instance group with the rolling-action command."
        echo "Trying to restart instances individually..."

        echo "$INSTANCES" | while read -r INSTANCE_NAME INSTANCE_ZONE STATUS; do
          if [ "$STATUS" = "RUNNING" ]; then
            echo "Restarting instance: $INSTANCE_NAME in zone: $INSTANCE_ZONE"
            gcloud compute instances reset "$INSTANCE_NAME" --zone="$INSTANCE_ZONE" --project="$PROJECT_ID" || \
              echo "Warning: Failed to restart instance $INSTANCE_NAME"
          else
            echo "Instance $INSTANCE_NAME is not in RUNNING state (current: $STATUS). Skipping restart."
          fi
        done
      fi
    else
      echo "Skipping VM restart. The startup script should still be able to pull the new image with its retry logic."
    fi
  else
    echo "VM instances exist but are not in RUNNING state yet."
    echo "The VM startup script has retry logic and will pull the image when available."
    echo "No restart needed at this point."
  fi
fi

# Original STEP 5: Upload startup scripts (now STEP 6)
echo -e "\n===== STEP 6: Uploading startup scripts to storage bucket =====\n"
"$SCRIPT_DIR/upload_startup_scripts.sh"
if [ $? -ne 0 ]; then
    echo "Warning: Failed to upload startup scripts. VMs may not initialize correctly."
    echo "Please run scripts/upload_startup_scripts.sh manually."
else
    echo "Startup scripts uploaded successfully."
fi

echo -e "\n===== STEP 7: Populating GitHub Secrets =====\n"
"$SCRIPT_DIR/gh_populate_secrets.sh"
if [ $? -ne 0 ]; then
    echo "Warning: Failed to populate GitHub secrets. Please run scripts/gh_populate_secrets.sh manually."
else
    echo "GitHub secrets populated successfully."
fi

echo -e "\nDeployment process completed!"

# Display important output values for setting up GitHub Actions
echo -e "\n===== IMPORTANT OUTPUT VALUES FOR CI/CD SETUP =====\n"
echo "Copy these values to set up your GitHub repository secrets:"
echo -e "\nAPI Service Account Email for $ENVIRONMENT environment (DEV_API_SERVICE_ACCOUNT_EMAIL or PROD_API_SERVICE_ACCOUNT_EMAIL):"
terraform output -raw api_service_account_email

echo -e "\nWorker Service Account Email for $ENVIRONMENT environment (DEV_WORKER_SERVICE_ACCOUNT_EMAIL or PROD_WORKER_SERVICE_ACCOUNT_EMAIL):"
terraform output -raw worker_service_account_email

echo -e "\nCI/CD Service Account Email for $ENVIRONMENT environment (DEV_CICD_SERVICE_ACCOUNT_EMAIL or PROD_CICD_SERVICE_ACCOUNT_EMAIL):"
terraform output -raw cicd_service_account_email

echo -e "\nWorkload Identity Provider for $ENVIRONMENT environment (DEV_WORKLOAD_IDENTITY_PROVIDER or PROD_WORKLOAD_IDENTITY_PROVIDER):"
terraform output -raw workload_identity_full_provider_name

echo -e "\nArtifact Registry Repository Name for $ENVIRONMENT environment (DEV_ARTIFACT_REGISTRY_REPO_NAME or PROD_ARTIFACT_REGISTRY_REPO_NAME):"
echo "${NAMING_PREFIX}-docker-repo"

echo -e "\nExternal IP for API VM for $ENVIRONMENT environment:"
terraform output -raw api_vm_external_ip

echo -e "\nFrontend Uptime Check ID for $ENVIRONMENT environment (DEV_FRONTEND_UPTIME_CHECK_CONFIG_ID or PROD_FRONTEND_UPTIME_CHECK_CONFIG_ID):"
terraform output -raw frontend_uptime_check_id

echo -e "\nFrontend Alert Policy ID for $ENVIRONMENT environment (e.g., PROD_FRONTEND_ALERT_POLICY_ID):"
terraform output -raw frontend_alert_policy_id

echo -e "\nFrontend Alert Policy Name for $ENVIRONMENT environment:"
terraform output -raw frontend_alert_policy_name

echo -e "\nAlert Notification Channel ID for $ENVIRONMENT environment (e.g., PROD_ALERT_NOTIFICATION_CHANNEL_FULL_ID):"
terraform output -raw notification_channel_id_full

# Alert Email Address
ALERT_EMAIL=$(grep 'alert_email_address' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
echo -e "\nAlert Email Address for monitoring (ALERT_EMAIL_ADDRESS):"
if [[ -n "$ALERT_EMAIL" ]]; then
    echo "$ALERT_EMAIL"
else
    echo "⚠️ ALERT_EMAIL_ADDRESS not found in $TFVARS_FILE. This is required for frontend monitoring."
    echo "Please add 'alert_email_address = \"your-email@example.com\"' to your tfvars file."
fi

echo -e "\n===== GITHUB SECRETS ALREADY POPULATED =====\n"
echo "GitHub Actions secrets for your CI/CD workflow have been automatically populated by step 7."
echo "If you need to update them again, you can manually run:"
echo "  ./scripts/gh_populate_secrets.sh"

# --- Global Secrets (Not environment-specific but fetched once) ---
GCP_REGION_SECRET_NAME="GCP_REGION"
TF_OUTPUT_GCP_REGION="gcp_region"

# --- Prefixed Secrets (e.g., PROD_GCP_PROJECT_ID) ---
# Maps Secret Suffix to Terraform Output Name
declare -A DEV_SECRET_TF_OUTPUT_MAP=(
  ["GCP_PROJECT_ID"]="project_id"
  ["GCP_ZONE"]="gcp_zone"
  ["NAMING_PREFIX"]="naming_prefix"
  ["WORKLOAD_IDENTITY_PROVIDER"]="workload_identity_full_provider_name" # Use the full name
  ["CICD_SERVICE_ACCOUNT_EMAIL"]="cicd_service_account_email"
  ["ARTIFACT_REGISTRY_REPO_NAME"]="artifact_registry_repository_name"
  ["WORKER_SERVICE_ACCOUNT_EMAIL"]="worker_service_account_email"
  ["API_SERVICE_ACCOUNT_EMAIL"]="api_service_account_email"
  ["WORKER_MIN_INSTANCES"]="worker_min_instances_output"
  ["WORKER_MAX_INSTANCES"]="worker_max_instances_output"
  ["FRONTEND_UPTIME_CHECK_CONFIG_ID"]="frontend_uptime_check_id" # Short ID
  ["FRONTEND_ALERT_POLICY_ID"]="frontend_alert_policy_id_short" # Short ID
  ["ALERT_NOTIFICATION_CHANNEL_FULL_ID"]="notification_channel_id_full" # Use the new full ID output
  ["FRONTEND_STARTUP_ALERT_DELAY"]="frontend_startup_alert_delay_output"
  ["ALERT_ALIGNMENT_PERIOD"]="alert_alignment_period_output"
  # ["TF_STATE_BUCKET_NAME"]="terraform_state_bucket_name_output" # Removed: This secret is manually set
  # Add other dev-specific mappings here if needed
)

declare -A PROD_SECRET_TF_OUTPUT_MAP=(
  ["GCP_PROJECT_ID"]="project_id"
  ["GCP_ZONE"]="gcp_zone"
  ["NAMING_PREFIX"]="naming_prefix"
  ["WORKLOAD_IDENTITY_PROVIDER"]="workload_identity_full_provider_name" # Use the full name
  ["CICD_SERVICE_ACCOUNT_EMAIL"]="cicd_service_account_email"
  ["ARTIFACT_REGISTRY_REPO_NAME"]="artifact_registry_repository_name"
  ["WORKER_SERVICE_ACCOUNT_EMAIL"]="worker_service_account_email"
  ["API_SERVICE_ACCOUNT_EMAIL"]="api_service_account_email"
  ["WORKER_MIN_INSTANCES"]="worker_min_instances_output"
  ["WORKER_MAX_INSTANCES"]="worker_max_instances_output"
  ["FRONTEND_UPTIME_CHECK_CONFIG_ID"]="frontend_uptime_check_id" # Short ID
  ["FRONTEND_ALERT_POLICY_ID"]="frontend_alert_policy_id_short" # Short ID
  ["ALERT_NOTIFICATION_CHANNEL_FULL_ID"]="notification_channel_id_full" # Use the new full ID output
  ["FRONTEND_STARTUP_ALERT_DELAY"]="frontend_startup_alert_delay_output"
  ["ALERT_ALIGNMENT_PERIOD"]="alert_alignment_period_output"
  # ["TF_STATE_BUCKET_NAME"]="terraform_state_bucket_name_output" # Removed: This secret is manually set
  # Add other prod-specific mappings here if needed
)
