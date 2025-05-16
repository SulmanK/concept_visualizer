#!/bin/bash
set -e

# Script to populate GitHub Actions secrets from Terraform outputs and .tfvars files.

# Get the absolute path to the project root directory (parent of the script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
DEV_BRANCH="develop"
PROD_BRANCH="main"
DEV_PREFIX="DEV_"
PROD_PREFIX="PROD_"

# --- Branch Detection and Environment Setup ---
CURRENT_BRANCH=$(git branch --show-current)
echo "Current git branch: $CURRENT_BRANCH"

TARGET_PREFIX=""
ENV_NAME=""
TFVARS_FILE=""

if [[ "$CURRENT_BRANCH" == "$DEV_BRANCH" ]]; then
    TARGET_PREFIX="$DEV_PREFIX"
    ENV_NAME="dev"
    TFVARS_FILE="$TERRAFORM_DIR/environments/dev.tfvars"
    echo "Using development environment (prefix: $TARGET_PREFIX) based on branch '$DEV_BRANCH'"
elif [[ "$CURRENT_BRANCH" == "$PROD_BRANCH" ]]; then
    TARGET_PREFIX="$PROD_PREFIX"
    ENV_NAME="prod"
    TFVARS_FILE="$TERRAFORM_DIR/environments/prod.tfvars"
    echo "Using production environment (prefix: $TARGET_PREFIX) based on branch '$PROD_BRANCH'"

    echo ""
    echo "WARNING: You are about to set GitHub secrets for the PRODUCTION environment."
    echo ""
    read -p "Type 'set-production-github-secrets' to confirm: " CONFIRM_PROD
    if [[ "$CONFIRM_PROD" != "set-production-github-secrets" ]]; then
        echo "Production confirmation does not match. GitHub secret population cancelled."
        exit 1
    fi
else
    echo "Error: Branch '$CURRENT_BRANCH' does not match either '$DEV_BRANCH' or '$PROD_BRANCH'."
    echo "Please checkout one of those branches to run this script."
    exit 1
fi

if [[ ! -f "$TFVARS_FILE" ]]; then
    echo "Error: Terraform variables file '$TFVARS_FILE' not found." >&2
    exit 1
fi

# --- Prerequisite Checks ---
echo "Checking prerequisites..."
if ! command -v gh &> /dev/null; then
    echo "GitHub CLI ('gh') could not be found. Please install it and authenticate (gh auth login)."
    echo "See: https://cli.github.com/"
    exit 1
fi
echo "Found GitHub CLI."

if ! command -v terraform &> /dev/null; then
    echo "Terraform CLI ('terraform') could not be found. Please install it."
    echo "See: https://developer.hashicorp.com/terraform/downloads"
    exit 1
fi
echo "Found Terraform CLI."

# --- Change to Terraform Directory ---
echo "Changing to Terraform directory: $TERRAFORM_DIR"
cd "$TERRAFORM_DIR"

# Check if we need to unlock the state
TF_STATE_BUCKET=$(grep 'terraform_state_bucket_name' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
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

# Initialize and select workspace
terraform init -backend-config="bucket=$TF_STATE_BUCKET" -reconfigure
terraform workspace select "$ENV_NAME"

# Check for state lock
check_and_clear_state_lock "$ENV_NAME"

# --- Define Secrets to Automate ---
# Associative array: GitHub Secret Suffix -> Terraform Output Name
declare -A PREFIXED_SECRETS
PREFIXED_SECRETS=(
    ["GCP_PROJECT_ID"]="project_id"
    ["GCP_ZONE"]="gcp_zone"
    ["NAMING_PREFIX"]="naming_prefix"
    ["API_SERVICE_ACCOUNT_EMAIL"]="api_service_account_email"
    ["WORKER_SERVICE_ACCOUNT_EMAIL"]="worker_service_account_email"
    ["CICD_SERVICE_ACCOUNT_EMAIL"]="cicd_service_account_email"
    ["WORKLOAD_IDENTITY_PROVIDER"]="workload_identity_full_provider_name"
    ["ARTIFACT_REGISTRY_REPO_NAME"]="artifact_registry_repository_name"
    ["FRONTEND_UPTIME_CHECK_CONFIG_ID"]="frontend_uptime_check_id"
    ["FRONTEND_ALERT_POLICY_ID"]="frontend_alert_policy_id_short"
    ["ALERT_NOTIFICATION_CHANNEL_FULL_ID"]="notification_channel_id_full"
    ["FRONTEND_STARTUP_ALERT_DELAY"]="frontend_startup_alert_delay_output"
    ["ALERT_ALIGNMENT_PERIOD"]="alert_alignment_period_output"
    ["WORKER_MIN_INSTANCES"]="worker_min_instances_output"
    ["WORKER_MAX_INSTANCES"]="worker_max_instances_output"
)

# --- Set Global Secrets ---
echo "
Setting Global GitHub Secrets..."

# GCP_REGION
GH_SECRET_NAME_REGION="GCP_REGION"
VALUE_GCP_REGION=$(grep '^region\s*=' "$TFVARS_FILE" | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -n "$VALUE_GCP_REGION" ]]; then
    echo "Setting $GH_SECRET_NAME_REGION..."
    if gh secret set "$GH_SECRET_NAME_REGION" -b "$VALUE_GCP_REGION"; then
        echo "Successfully set $GH_SECRET_NAME_REGION."
    else
        echo "Error setting $GH_SECRET_NAME_REGION." >&2
        # Decide if to exit or continue: for now, continue but flag error
    fi
else
    echo "Warning: Could not find 'region' in $TFVARS_FILE. Skipping $GH_SECRET_NAME_REGION." >&2
fi

# --- Set Prefixed Secrets ---
echo "
Setting Prefixed GitHub Secrets ($TARGET_PREFIX)..."

for SECRET_SUFFIX in "${!PREFIXED_SECRETS[@]}"; do
    TF_OUTPUT_NAME="${PREFIXED_SECRETS[$SECRET_SUFFIX]}"
    FULL_GH_SECRET_NAME="${TARGET_PREFIX}${SECRET_SUFFIX}"

    echo "Fetching value for $FULL_GH_SECRET_NAME (Terraform output: $TF_OUTPUT_NAME)..."
    SECRET_VALUE=$(terraform output -raw "$TF_OUTPUT_NAME" 2>/dev/null)

    if [[ -n "$SECRET_VALUE" ]]; then
        echo "Setting $FULL_GH_SECRET_NAME..."
        if gh secret set "$FULL_GH_SECRET_NAME" -b "$SECRET_VALUE"; then
            echo "Successfully set $FULL_GH_SECRET_NAME."
        else
            echo "Error setting $FULL_GH_SECRET_NAME." >&2
            # Decide if to exit or continue
        fi
    else
        echo "Warning: Terraform output '$TF_OUTPUT_NAME' for secret $FULL_GH_SECRET_NAME was empty or not found. Skipping." >&2
    fi
done

# Set additional essential secrets that may not come from Terraform
echo "
Setting any additional essential secrets:"

# Set TF_STATE_BUCKET_NAME
FULL_GH_SECRET_NAME="${TARGET_PREFIX}TF_STATE_BUCKET_NAME"
echo "Setting $FULL_GH_SECRET_NAME..."
if gh secret set "$FULL_GH_SECRET_NAME" -b "$TF_STATE_BUCKET"; then
    echo "Successfully set $FULL_GH_SECRET_NAME."
else
    echo "Error setting $FULL_GH_SECRET_NAME." >&2
fi

# Set ALERT_EMAIL_ADDRESS - get from tfvars file
ALERT_EMAIL=$(grep 'alert_email_address' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -n "$ALERT_EMAIL" ]]; then
    echo "Setting ALERT_EMAIL_ADDRESS..."
    if gh secret set "ALERT_EMAIL_ADDRESS" -b "$ALERT_EMAIL"; then
        echo "Successfully set ALERT_EMAIL_ADDRESS."
    else
        echo "Error setting ALERT_EMAIL_ADDRESS." >&2
    fi
else
    echo "Warning: alert_email_address not found in $TFVARS_FILE."
    echo "Please set this secret manually to enable frontend monitoring alerts."

    # Prompt user to provide the email
    read -p "Would you like to provide an alert email address now? (y/n): " SET_EMAIL
    if [[ "$SET_EMAIL" == "y" || "$SET_EMAIL" == "Y" ]]; then
        read -p "Enter email address for monitoring alerts: " USER_EMAIL
        if [[ -n "$USER_EMAIL" ]]; then
            if gh secret set "ALERT_EMAIL_ADDRESS" -b "$USER_EMAIL"; then
                echo "Successfully set ALERT_EMAIL_ADDRESS to $USER_EMAIL."
            else
                echo "Error setting ALERT_EMAIL_ADDRESS." >&2
            fi
        else
            echo "No email provided. Skipping."
        fi
    fi
fi

# Handle VERCEL_PROJECT_ID if needed
# This is not part of Terraform state but needed for frontend monitoring
VERCEL_PROJECT_ID_SECRET="${TARGET_PREFIX}VERCEL_PROJECT_ID"
if ! gh secret list | grep -q "$VERCEL_PROJECT_ID_SECRET"; then
    echo "WARNING: $VERCEL_PROJECT_ID_SECRET is not set. This is required for frontend monitoring."
    echo "Please set this secret manually with your Vercel project ID."

    # Prompt user to provide Vercel Project ID
    read -p "Would you like to provide a Vercel Project ID now? (y/n): " SET_VERCEL_ID
    if [[ "$SET_VERCEL_ID" == "y" || "$SET_VERCEL_ID" == "Y" ]]; then
        read -p "Enter Vercel Project ID: " VERCEL_ID
        if [[ -n "$VERCEL_ID" ]]; then
            if gh secret set "$VERCEL_PROJECT_ID_SECRET" -b "$VERCEL_ID"; then
                echo "Successfully set $VERCEL_PROJECT_ID_SECRET to $VERCEL_ID."
            else
                echo "Error setting $VERCEL_PROJECT_ID_SECRET." >&2
            fi
        else
            echo "No Vercel Project ID provided. Skipping."
        fi
    fi
fi

# --- Verify Frontend Monitoring Secrets ---
echo "
Verifying frontend monitoring secrets:"

FRONTEND_UPTIME_CHECK_ID="${TARGET_PREFIX}FRONTEND_UPTIME_CHECK_CONFIG_ID"
FRONTEND_ALERT_POLICY_ID="${TARGET_PREFIX}FRONTEND_ALERT_POLICY_ID"
ALERT_NOTIFICATION_CHANNEL_ID="${TARGET_PREFIX}ALERT_NOTIFICATION_CHANNEL_FULL_ID"

# Get the current values from GitHub to check if they exist
UPTIME_CHECK_ID_VALUE=$(gh secret list | grep -w "$FRONTEND_UPTIME_CHECK_ID" | wc -l)
ALERT_POLICY_ID_VALUE=$(gh secret list | grep -w "$FRONTEND_ALERT_POLICY_ID" | wc -l)
NOTIFICATION_CHANNEL_ID_VALUE=$(gh secret list | grep -w "$ALERT_NOTIFICATION_CHANNEL_ID" | wc -l)
ALERT_EMAIL_VALUE=$(gh secret list | grep -w "ALERT_EMAIL_ADDRESS" | wc -l)

if [[ "$UPTIME_CHECK_ID_VALUE" -eq 0 || "$ALERT_POLICY_ID_VALUE" -eq 0 ||
     "$NOTIFICATION_CHANNEL_ID_VALUE" -eq 0 || "$ALERT_EMAIL_VALUE" -eq 0 ]]; then
    echo "WARNING: One or more required frontend monitoring secrets are missing."
    echo "Please ensure the following secrets are set correctly:"
    echo "- $FRONTEND_UPTIME_CHECK_ID"
    echo "- $FRONTEND_ALERT_POLICY_ID"
    echo "- $ALERT_NOTIFICATION_CHANNEL_ID"
    echo "- ALERT_EMAIL_ADDRESS"
else
    echo "All required frontend monitoring secrets appear to be set."
fi

# --- Return to Original Directory ---
cd "$PROJECT_ROOT"
echo "
GitHub secret population script finished."
