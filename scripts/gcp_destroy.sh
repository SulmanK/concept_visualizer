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

# Choose env file and environment name based on branch
if [[ "$CURRENT_BRANCH" == "$DEV_BRANCH" ]]; then
    ENVIRONMENT="dev"
    WORKSPACE="$DEV_WORKSPACE"
    TFVARS_FILE="$DEV_TFVARS_FILE"
    echo "Using development environment based on branch '$DEV_BRANCH'"
elif [[ "$CURRENT_BRANCH" == "$PROD_BRANCH" ]]; then
    ENVIRONMENT="prod"
    WORKSPACE="$PROD_WORKSPACE"
    TFVARS_FILE="$PROD_TFVARS_FILE"
    echo "Using production environment based on branch '$PROD_BRANCH'"

    # Extra confirmation for production
    echo ""
    echo "WARNING: You are about to DESTROY ALL RESOURCES in PRODUCTION."
    echo "This action is NOT REVERSIBLE and will DELETE ALL RESOURCES."
    echo ""
    read -p "Type 'destroy-production' to confirm: " CONFIRM_PROD

    if [[ "$CONFIRM_PROD" != "destroy-production" ]]; then
        echo "Production confirmation does not match. Destruction cancelled."
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
TF_STATE_BUCKET=$(grep 'terraform_state_bucket_name' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -z "$TF_STATE_BUCKET" ]]; then
    echo "Error: terraform_state_bucket_name not found in $TFVARS_FILE."
    exit 1
fi

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

# Change to Terraform directory
cd "$TERRAFORM_DIR"

# Initialize Terraform with backend configuration
echo "Initializing Terraform with backend bucket: $TF_STATE_BUCKET"
terraform init -input=false -no-color \
    -backend-config="bucket=$TF_STATE_BUCKET"
if [ $? -ne 0 ]; then echo "Error: Terraform init failed."; exit 1; fi

# Select workspace
echo "Selecting Terraform workspace: $WORKSPACE"
terraform workspace select "$WORKSPACE"

# Check for state lock before proceeding
check_and_clear_state_lock "$WORKSPACE"

# Plan destroy
echo "Planning destruction of Terraform resources..."
terraform plan -destroy -var-file="$TFVARS_FILE" -out=tfplan

# Confirm destruction
echo "
WARNING: You are about to DESTROY ALL RESOURCES for the $ENVIRONMENT environment.
This action is NOT REVERSIBLE.
"
read -p "Do you want to proceed with the destruction? (yes/no) " CONFIRM_DESTROY

if [[ "$CONFIRM_DESTROY" != "yes" ]]; then
    echo "Destruction cancelled."
    exit 0
fi

# Apply the destroy
echo "Applying Terraform destroy..."
terraform apply -auto-approve tfplan

echo "Resource destruction completed."
