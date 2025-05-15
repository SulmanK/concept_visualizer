#!/bin/bash
set -e

# Branch-aware Terraform destroy script
# This script detects your current git branch and destroys the appropriate Terraform workspace

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

# Choose workspace and vars file based on branch
if [[ "$CURRENT_BRANCH" == "$DEV_BRANCH" ]]; then
    WORKSPACE="$DEV_WORKSPACE"
    TFVARS_FILE="$DEV_TFVARS_FILE"
    echo "Using development environment based on branch '$DEV_BRANCH'"
elif [[ "$CURRENT_BRANCH" == "$PROD_BRANCH" ]]; then
    WORKSPACE="$PROD_WORKSPACE"
    TFVARS_FILE="$PROD_TFVARS_FILE"
    echo "Using production environment based on branch '$PROD_BRANCH'"
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
echo "Selecting Terraform workspace: $WORKSPACE"
terraform workspace select "$WORKSPACE"

# --- BEGIN: Fetch and Import Dynamically Managed Monitoring Resources ---
echo "Attempting to fetch and import dynamically managed frontend monitoring resources..."
UPTIME_CHECK_ID_GCS_PATH="gs://${TF_STATE_BUCKET}/dynamic_frontend_monitoring_ids/${WORKSPACE}/frontend_uptime_check_id.txt"
ALERT_POLICY_ID_GCS_PATH="gs://${TF_STATE_BUCKET}/dynamic_frontend_monitoring_ids/${WORKSPACE}/frontend_alert_policy_id.txt"

DEFINITIVE_UPTIME_CHECK_ID=$(gsutil cat "$UPTIME_CHECK_ID_GCS_PATH" 2>/dev/null || echo "")
DEFINITIVE_ALERT_POLICY_ID=$(gsutil cat "$ALERT_POLICY_ID_GCS_PATH" 2>/dev/null || echo "")

if [[ -n "$DEFINITIVE_UPTIME_CHECK_ID" ]]; then
  echo "Found definitive Uptime Check ID: $DEFINITIVE_UPTIME_CHECK_ID. Attempting to import..."
  terraform import -no-color "google_monitoring_uptime_check_config.frontend_availability" "$DEFINITIVE_UPTIME_CHECK_ID" || echo "Warning: Failed to import dynamic uptime check '$DEFINITIVE_UPTIME_CHECK_ID'. It might have already been deleted or was never created by the workflow."
else
  echo "No definitive Uptime Check ID found in GCS. Skipping import."
fi

if [[ -n "$DEFINITIVE_ALERT_POLICY_ID" ]]; then
  echo "Found definitive Alert Policy ID: $DEFINITIVE_ALERT_POLICY_ID. Attempting to import..."
  terraform import -no-color "google_monitoring_alert_policy.frontend_availability_failure_alert" "$DEFINITIVE_ALERT_POLICY_ID" || echo "Warning: Failed to import dynamic alert policy '$DEFINITIVE_ALERT_POLICY_ID'. It might have already been deleted or was never created by the workflow."
else
  echo "No definitive Alert Policy ID found in GCS. Skipping import."
fi
echo "Dynamic resource import attempt complete."
# --- END: Fetch and Import Dynamically Managed Monitoring Resources ---

# Plan destroy
echo "Planning destruction of Terraform resources..."
terraform plan -destroy -var-file="$TFVARS_FILE" -out=tfplan

# Multiple confirmation for destroy, especially for prod
echo ""
echo "WARNING: This will DESTROY all resources managed by Terraform in the $WORKSPACE environment."
echo "         This action cannot be undone."
echo ""
read -p "Type the environment name ($WORKSPACE) to confirm: " CONFIRM_ENV

if [[ "$CONFIRM_ENV" != "$WORKSPACE" ]]; then
    echo "Environment name does not match. Terraform destroy cancelled."
    exit 1
fi

if [[ "$WORKSPACE" == "$PROD_WORKSPACE" ]]; then
    echo ""
    echo "EXTRA WARNING: You are about to destroy the PRODUCTION environment."
    echo "               This is a very destructive action."
    echo ""
    read -p "Type 'yes-destroy-production' to confirm: " CONFIRM_PROD

    if [[ "$CONFIRM_PROD" != "yes-destroy-production" ]]; then
        echo "Production confirmation does not match. Terraform destroy cancelled."
        exit 1
    fi
fi

echo ""
read -p "Final confirmation - Do you want to continue with the destroy? (y/n) " CONTINUE

if [[ $CONTINUE != "y" && $CONTINUE != "Y" ]]; then
    echo "Terraform destroy canceled."
    exit 0
fi

# Apply the destroy
echo "Applying Terraform destroy..."
terraform apply -auto-approve tfplan
APPLY_RESULT=$?

if [ $APPLY_RESULT -eq 0 ]; then
  echo "Terraform destroy completed successfully."
  # --- BEGIN: Clean Up Dynamic ID Files from GCS ---
  echo "Cleaning up dynamic ID files from GCS..."
  if [[ -n "$DEFINITIVE_UPTIME_CHECK_ID" ]]; then # Only attempt delete if ID was read
    gsutil rm "$UPTIME_CHECK_ID_GCS_PATH" 2>/dev/null || echo "Warning: Could not remove uptime check ID file: $UPTIME_CHECK_ID_GCS_PATH. It might have already been deleted."
  fi
  if [[ -n "$DEFINITIVE_ALERT_POLICY_ID" ]]; then # Only attempt delete if ID was read
    gsutil rm "$ALERT_POLICY_ID_GCS_PATH" 2>/dev/null || echo "Warning: Could not remove alert policy ID file: $ALERT_POLICY_ID_GCS_PATH. It might have already been deleted."
  fi
  echo "Dynamic ID file cleanup attempt complete."
  # --- END: Clean Up Dynamic ID Files from GCS ---
else
  echo "Error: Terraform destroy failed with exit code $APPLY_RESULT."
  exit $APPLY_RESULT
fi

echo "Terraform destroy process finished."
