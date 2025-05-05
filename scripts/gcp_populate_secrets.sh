#!/bin/bash
set -e

# Script to populate GCP Secret Manager with values from a local .env file
# This runs separately from Terraform to avoid storing secrets in state files

# Get the absolute path to the project root directory (parent of the script directory)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Configuration
DEV_BRANCH="develop"
PROD_BRANCH="main"
ENV_FILE_DEV="$PROJECT_ROOT/backend/.env.develop"
ENV_FILE_PROD="$PROJECT_ROOT/backend/.env.main"

# Get current git branch
CURRENT_BRANCH=$(git branch --show-current)
echo "Current git branch: $CURRENT_BRANCH"

# Choose env file and environment name based on branch
if [[ "$CURRENT_BRANCH" == "$DEV_BRANCH" ]]; then
    ENV_FILE="$ENV_FILE_DEV"
    ENVIRONMENT="dev"
    echo "Using development environment based on branch '$DEV_BRANCH'"
elif [[ "$CURRENT_BRANCH" == "$PROD_BRANCH" ]]; then
    ENV_FILE="$ENV_FILE_PROD"
    ENVIRONMENT="prod"
    echo "Using production environment based on branch '$PROD_BRANCH'"

    # Extra confirmation for production
    echo ""
    echo "WARNING: You are about to update PRODUCTION secrets."
    echo ""
    read -p "Type 'update-production-secrets' to confirm: " CONFIRM_PROD

    if [[ "$CONFIRM_PROD" != "update-production-secrets" ]]; then
        echo "Production confirmation does not match. Secret update cancelled."
        exit 1
    fi
else
    echo "Error: Branch '$CURRENT_BRANCH' does not match either '$DEV_BRANCH' or '$PROD_BRANCH'."
    echo "Please checkout one of those branches to run this script."
    exit 1
fi

# Check if env file exists
if [[ ! -f "$ENV_FILE" ]]; then
    echo "Error: Environment file '$ENV_FILE' not found."
    echo "Please create this file with your environment-specific secrets."
    exit 1
fi

# Load environment variables from the file - using safer parsing
# Instead of directly sourcing the file, parse it with grep
function load_env_var() {
    local var_name=$1
    local env_value

    # Use grep to extract the variable value, avoiding shell interpretation issues
    env_value=$(grep "^$var_name=" "$ENV_FILE" | cut -d '=' -f 2- | sed 's/^"//' | sed 's/"$//')

    if [[ -n "$env_value" ]]; then
        # Remove surrounding quotes if present
        env_value="${env_value%\"}"
        env_value="${env_value#\"}"
        export "$var_name"="$env_value"
        echo "Loaded $var_name from env file"
    fi
}

# Load the specific environment variables we need
load_env_var "CONCEPT_SUPABASE_URL"
load_env_var "CONCEPT_SUPABASE_KEY"
load_env_var "CONCEPT_SUPABASE_SERVICE_ROLE"
load_env_var "CONCEPT_SUPABASE_JWT_SECRET"
load_env_var "CONCEPT_JIGSAWSTACK_API_KEY"
load_env_var "CONCEPT_UPSTASH_REDIS_ENDPOINT"
load_env_var "CONCEPT_UPSTASH_REDIS_PASSWORD"

# Get the project ID from the relevant tfvars file
TERRAFORM_DIR="$PROJECT_ROOT/terraform"
if [[ "$ENVIRONMENT" == "dev" ]]; then
    TFVARS_FILE="$TERRAFORM_DIR/environments/dev.tfvars"
else
    TFVARS_FILE="$TERRAFORM_DIR/environments/prod.tfvars"
fi

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

echo "Using project ID: $PROJECT_ID"
echo "Using naming prefix: $NAMING_PREFIX"

# Define function to set a secret
set_secret() {
    local secret_name="$1"
    local env_var_name="$2"
    local secret_value="${!env_var_name}"

    if [[ -z "$secret_value" ]]; then
        echo "Warning: Environment variable $env_var_name is empty or not set."
        return
    fi

    local full_secret_id="${NAMING_PREFIX}-${secret_name}-${ENVIRONMENT}"

    echo "Setting secret $full_secret_id..."

    # Wait a bit for the resource to be available (dealing with eventual consistency)
    echo "Waiting a moment for secret resources to be fully available..."
    sleep 5

    # Add version to the secret - might fail if the secret exists but isn't ready yet
    if ! printf "%s" "$secret_value" | gcloud secrets versions add "$full_secret_id" --project="$PROJECT_ID" --data-file=- 2>/dev/null; then
        echo "Failed to add version directly. Trying alternative approach..."

        # Check if the secret exists at all
        if gcloud secrets describe "$full_secret_id" --project="$PROJECT_ID" &>/dev/null; then
            echo "Secret exists but is not ready. Retrying with delay..."
            # Secret exists but might not be ready, try with more delay
            sleep 10
            printf "%s" "$secret_value" | gcloud secrets versions add "$full_secret_id" --project="$PROJECT_ID" --data-file=-
        else
            # Secret doesn't exist, create it
            echo "Secret doesn't exist at all. Creating it..."
            gcloud secrets create "$full_secret_id" --project="$PROJECT_ID" --replication-policy="automatic"
            sleep 5
            printf "%s" "$secret_value" | gcloud secrets versions add "$full_secret_id" --project="$PROJECT_ID" --data-file=-
        fi
    else
        echo "Successfully added version to the secret."
    fi
}

# Populate secrets
echo "Populating secrets for $ENVIRONMENT environment in project $PROJECT_ID..."

set_secret "supabase-url" "CONCEPT_SUPABASE_URL"
set_secret "supabase-key" "CONCEPT_SUPABASE_KEY"
set_secret "supabase-service-role" "CONCEPT_SUPABASE_SERVICE_ROLE"
set_secret "supabase-jwt-secret" "CONCEPT_SUPABASE_JWT_SECRET"
set_secret "jigsawstack-api-key" "CONCEPT_JIGSAWSTACK_API_KEY"
set_secret "redis-endpoint" "CONCEPT_UPSTASH_REDIS_ENDPOINT"
set_secret "redis-password" "CONCEPT_UPSTASH_REDIS_PASSWORD"

echo "All secrets populated successfully!"

# Print reminder about GitHub Actions secrets
echo -e "\n===== GITHUB ACTIONS SECRETS REMINDER =====\n"
echo "Remember to set these GitHub Actions secrets for CI/CD:"
echo "1. ${ENVIRONMENT^^}_GCP_PROJECT_ID: $PROJECT_ID"
echo "2. ${ENVIRONMENT^^}_GCP_ZONE: (from your tfvars file)"
echo "3. ${ENVIRONMENT^^}_NAMING_PREFIX: $NAMING_PREFIX"
echo "4. ${ENVIRONMENT^^}_API_SERVICE_ACCOUNT_EMAIL: (from Terraform outputs)"
echo "5. ${ENVIRONMENT^^}_WORKER_SERVICE_ACCOUNT_EMAIL: (from Terraform outputs)"
echo "6. ${ENVIRONMENT^^}_CICD_SERVICE_ACCOUNT_EMAIL: (from Terraform outputs)"
echo "7. ${ENVIRONMENT^^}_WORKLOAD_IDENTITY_PROVIDER: (from Terraform outputs)"
echo "8. ${ENVIRONMENT^^}_ARTIFACT_REGISTRY_REPO_NAME: (from Terraform outputs)"
echo "9. GCP_REGION: (from your tfvars file)"
echo -e "\nYou can get most of these values by running: ./scripts/gcp_apply.sh"
