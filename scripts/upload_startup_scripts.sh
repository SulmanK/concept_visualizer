#!/bin/bash
set -e

# Script to upload VM startup scripts to the GCS bucket
# Run after terraform apply to ensure scripts are available

# Get the absolute path to the project root directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration - match with gcp_apply.sh
DEV_BRANCH="develop"
PROD_BRANCH="main"
DEV_TFVARS_FILE="$PROJECT_ROOT/terraform/environments/dev.tfvars"
PROD_TFVARS_FILE="$PROJECT_ROOT/terraform/environments/prod.tfvars"

# Get current git branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current git branch: $CURRENT_BRANCH"

# Determine environment based on branch
if [[ "$CURRENT_BRANCH" == "$DEV_BRANCH" ]]; then
    ENVIRONMENT="dev"
    TFVARS_FILE="$DEV_TFVARS_FILE"
    echo "Using development environment based on branch '$DEV_BRANCH'"
elif [[ "$CURRENT_BRANCH" == "$PROD_BRANCH" ]]; then
    ENVIRONMENT="prod"
    TFVARS_FILE="$PROD_TFVARS_FILE"
    echo "Using production environment based on branch '$PROD_BRANCH'"
else
    echo "Error: Branch '$CURRENT_BRANCH' does not match either '$DEV_BRANCH' or '$PROD_BRANCH'."
    echo "Please checkout one of those branches to run this script."
    exit 1
fi

# Get project ID and naming prefix from tfvars
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

# Define the GCS bucket name based on naming convention (matching Terraform)
BUCKET_NAME="${NAMING_PREFIX}-assets-${ENVIRONMENT}"
SCRIPTS_DIR="$PROJECT_ROOT/terraform/scripts"

# Check if the required scripts exist
API_STARTUP_SCRIPT="$SCRIPTS_DIR/startup-api.sh"
if [[ ! -f "$API_STARTUP_SCRIPT" ]]; then
    echo "Error: API startup script not found at '$API_STARTUP_SCRIPT'."
    exit 1
fi

# Create the startup-scripts directory in the bucket if it doesn't exist
echo "Creating startup-scripts directory in bucket $BUCKET_NAME (if it doesn't exist)..."
gsutil ls gs://$BUCKET_NAME/ > /dev/null 2>&1 || { echo "Error: Bucket $BUCKET_NAME does not exist. Run terraform apply first."; exit 1; }

# Upload the scripts
echo "Uploading API startup script to gs://$BUCKET_NAME/startup-scripts/api-startup.sh..."
gsutil cp "$API_STARTUP_SCRIPT" "gs://$BUCKET_NAME/startup-scripts/api-startup.sh"

echo "Scripts uploaded successfully!"
echo "API startup script: gs://$BUCKET_NAME/startup-scripts/api-startup.sh"
