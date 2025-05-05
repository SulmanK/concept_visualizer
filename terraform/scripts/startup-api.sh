#!/bin/bash
set -euo pipefail # Exit on error, unset var error, pipefail

echo "Starting API VM startup script..."

# --- Install Prerequisites ---
install_pkg() {
    if ! command -v $1 &> /dev/null; then
        echo "Installing $1..."
        apt-get update -y && apt-get install -y $2 && echo "$1 installed."
    else
        echo "$1 already installed."
    fi
}

# Install Docker prerequisites
echo "Installing Docker prerequisites..."
apt-get update
apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release software-properties-common

# Add Docker's official GPG key
echo "Adding Docker GPG key..."
mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

# Add Docker repository
echo "Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker
echo "Installing Docker..."
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

install_pkg "gcloud" "google-cloud-sdk"

# Configure Docker permissions (run docker commands as non-root if needed)
# usermod -aG docker your_user # Example

systemctl start docker
systemctl enable docker

# --- Fetch Metadata ---
echo "Fetching instance metadata..."
ENVIRONMENT=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/attributes/environment" -H "Metadata-Flavor: Google" || echo "dev")
NAMING_PREFIX=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/attributes/naming_prefix" -H "Metadata-Flavor: Google" || echo "concept-viz")
REGION=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/instance/zone" -H "Metadata-Flavor: Google" | awk -F'/' '{print $NF}' | awk -F'-' '{print $1"-"$2}')
GCP_PROJECT_ID=$(curl -sf "http://metadata.google.internal/computeMetadata/v1/project/project-id" -H "Metadata-Flavor: Google")

echo "Running startup for environment: $ENVIRONMENT in project: $GCP_PROJECT_ID, region: $REGION"

# --- Set Configuration Environment Variables ---
echo "Setting configuration environment variables..."
export ENVIRONMENT="$ENVIRONMENT"
export CONCEPT_STORAGE_BUCKET_CONCEPT="concept-images-${ENVIRONMENT}"
export CONCEPT_STORAGE_BUCKET_PALETTE="palette-images-${ENVIRONMENT}"
export CONCEPT_DB_TABLE_TASKS="tasks_${ENVIRONMENT}"
export CONCEPT_DB_TABLE_CONCEPTS="concepts_${ENVIRONMENT}"
export CONCEPT_DB_TABLE_PALETTES="color_variations_${ENVIRONMENT}"
export CONCEPT_LOG_LEVEL=$( [[ "$ENVIRONMENT" == "prod" ]] && echo "INFO" || echo "DEBUG" )
export CONCEPT_API_PREFIX="/api"
export CONCEPT_UPSTASH_REDIS_PORT="6379"
# Add other non-secret config vars needed by the backend app

# --- Fetch Secrets ---
echo "Fetching secrets..."
fetch_secret() {
    local secret_name_suffix=$1
    local env_var_name=$2
    local secret_id="${NAMING_PREFIX}-${secret_name_suffix}-${ENVIRONMENT}"

    # First try with the correct naming pattern (naming_prefix-secret-environment)
    local value=$(gcloud secrets versions access latest --secret="$secret_id" --project="$GCP_PROJECT_ID" 2>/dev/null)

    # If that fails, try the alternate pattern that includes environment in the naming prefix
    if [ $? -ne 0 ]; then
        local alt_secret_id="${NAMING_PREFIX}-${ENVIRONMENT}-${secret_name_suffix}-${ENVIRONMENT}"
        echo "First attempt failed, trying alternate secret name: $alt_secret_id"
        value=$(gcloud secrets versions access latest --secret="$alt_secret_id" --project="$GCP_PROJECT_ID" 2>/dev/null || echo "SECRET_NOT_FOUND")
    fi

    if [[ "$value" == "SECRET_NOT_FOUND" ]]; then
        echo "Warning: Secret '$secret_id' and alternate patterns not found or access denied."
    else
        echo "Secret '$secret_name_suffix' found and loaded."
    fi
    export "$env_var_name"="$value"
}

fetch_secret "supabase-url"                "CONCEPT_SUPABASE_URL"
fetch_secret "supabase-key"                "CONCEPT_SUPABASE_KEY"
fetch_secret "supabase-service-role"       "CONCEPT_SUPABASE_SERVICE_ROLE"
fetch_secret "supabase-jwt-secret"         "CONCEPT_SUPABASE_JWT_SECRET"
fetch_secret "jigsawstack-api-key"         "CONCEPT_JIGSAWSTACK_API_KEY"
fetch_secret "redis-endpoint"              "CONCEPT_UPSTASH_REDIS_ENDPOINT"
fetch_secret "redis-password"              "CONCEPT_UPSTASH_REDIS_PASSWORD"
echo "Secrets fetched (values hidden)."

# --- Configure Docker for Artifact Registry ---
echo "Configuring Docker for Artifact Registry: ${REGION}-docker.pkg.dev"
gcloud auth configure-docker "${REGION}-docker.pkg.dev" -q
if [ $? -ne 0 ]; then echo "Warning: Failed to configure docker for Artifact Registry."; fi

# --- Pull API Image ---
# Construct image URL dynamically
ARTIFACT_REGISTRY_REPO="${NAMING_PREFIX}-docker-repo" # Matches terraform resource name pattern
API_IMAGE_URL="${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPO}/concept-api-${ENVIRONMENT}:latest" # Assumes :latest tag

echo "Pulling latest API image: $API_IMAGE_URL"
docker pull "$API_IMAGE_URL" || echo "Warning: Failed to pull image '$API_IMAGE_URL'. Maybe it hasn't been pushed yet?"

# --- Run API Container ---
CONTAINER_NAME="concept-api"
echo "Stopping existing container '$CONTAINER_NAME' if running..."
docker stop "$CONTAINER_NAME" || true
echo "Removing existing container '$CONTAINER_NAME' if present..."
docker rm "$CONTAINER_NAME" || true

echo "Starting API container '$CONTAINER_NAME'..."
# Pass ALL required env vars (config + secrets) to the container
# Using --env-file might be cleaner if many vars, requires creating a file
docker run -d --name "$CONTAINER_NAME" \
  -p 80:8000 \
  --env ENVIRONMENT \
  --env CONCEPT_STORAGE_BUCKET_CONCEPT \
  --env CONCEPT_STORAGE_BUCKET_PALETTE \
  --env CONCEPT_DB_TABLE_TASKS \
  --env CONCEPT_DB_TABLE_CONCEPTS \
  --env CONCEPT_DB_TABLE_PALETTES \
  --env CONCEPT_LOG_LEVEL \
  --env CONCEPT_API_PREFIX \
  --env CONCEPT_UPSTASH_REDIS_PORT \
  --env CONCEPT_SUPABASE_URL \
  --env CONCEPT_SUPABASE_KEY \
  --env CONCEPT_SUPABASE_SERVICE_ROLE \
  --env CONCEPT_SUPABASE_JWT_SECRET \
  --env CONCEPT_JIGSAWSTACK_API_KEY \
  --env CONCEPT_UPSTASH_REDIS_ENDPOINT \
  --env CONCEPT_UPSTASH_REDIS_PASSWORD \
  --restart always \
  "$API_IMAGE_URL"

if [ $? -eq 0 ]; then
    echo "API container '$CONTAINER_NAME' started successfully."
else
    echo "Error: Failed to start API container '$CONTAINER_NAME'."
    # You might want to add more detailed error checking/logging here
fi

echo "Startup script finished."
