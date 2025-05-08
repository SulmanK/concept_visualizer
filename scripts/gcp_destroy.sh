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

echo "Terraform destroy completed."
