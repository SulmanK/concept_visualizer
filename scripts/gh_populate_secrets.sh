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
    ["FRONTEND_ALERT_POLICY_ID"]="frontend_alert_policy_id"
    ["ALERT_NOTIFICATION_CHANNEL_FULL_ID"]="frontend_notification_channel_id"
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

# --- Return to Original Directory ---
cd "$PROJECT_ROOT"
echo "
GitHub secret population script finished."
