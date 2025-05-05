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
# Add retry logic with progressive backoff to handle the case where the image isn't pushed yet
MAX_ATTEMPTS=15 # ~15 minutes of total retry time
ATTEMPT=1
PULL_SUCCESS=false

while [ $ATTEMPT -le $MAX_ATTEMPTS ] && [ "$PULL_SUCCESS" = "false" ]; do
    echo "Attempt $ATTEMPT of $MAX_ATTEMPTS to pull image..."

    if docker pull "$API_IMAGE_URL"; then
        echo "API image pulled successfully on attempt $ATTEMPT!"
        PULL_SUCCESS=true
    else
        echo "Failed to pull image on attempt $ATTEMPT."

        if [ $ATTEMPT -eq 1 ]; then
            # First attempt diagnostics
            echo "Checking if Artifact Registry is accessible..."
            gcloud artifacts repositories describe $ARTIFACT_REGISTRY_REPO --location=$REGION --project=$GCP_PROJECT_ID || echo "Could not access Artifact Registry repository"

            echo "Trying to list available images in repository..."
            gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${GCP_PROJECT_ID}/${ARTIFACT_REGISTRY_REPO} --project=$GCP_PROJECT_ID --limit=5 || echo "Failed to list images"

            echo "Checking Docker auth configuration..."
            cat ~/.docker/config.json 2>/dev/null || echo "Docker config file not found"
        fi

        # Calculate exponential backoff delay (starts at 30 seconds, increases exponentially)
        DELAY=$((30 * 2 ** (ATTEMPT - 1)))
        # Cap maximum delay at 5 minutes
        if [ $DELAY -gt 300 ]; then
            DELAY=300
        fi

        echo "Waiting for $DELAY seconds before next attempt..."
        sleep $DELAY
        ATTEMPT=$((ATTEMPT + 1))
    fi
done

# Final check for successful pull
if [ "$PULL_SUCCESS" = "false" ]; then
    echo "ERROR: Failed to pull the API image after $MAX_ATTEMPTS attempts."
    echo "This could be because the image hasn't been pushed yet or there's an issue with the Artifact Registry."
    echo "Startup will continue but the container might fail to start."

    # Try fallback to a stable/default image if available
    echo "Attempting to pull fallback image..."
    if docker pull "gcr.io/google-samples/hello-app:1.0"; then
        echo "Fallback image pulled successfully."
        # Use fallback for demo/testing purposes only
        API_IMAGE_URL="gcr.io/google-samples/hello-app:1.0"
        echo "WARNING: Using fallback demo image instead of actual API image."
    else
        echo "Even fallback image pull failed, Docker may not be configured correctly."
    fi
fi

# --- Run API Container ---
CONTAINER_NAME="concept-api"
echo "Stopping existing container '$CONTAINER_NAME' if running..."
docker stop "$CONTAINER_NAME" || true
echo "Removing existing container '$CONTAINER_NAME' if present..."
docker rm "$CONTAINER_NAME" || true

echo "Starting API container '$CONTAINER_NAME'..."
# First check if the image exists locally
if ! docker image inspect "$API_IMAGE_URL" &>/dev/null; then
  echo "Error: Image '$API_IMAGE_URL' not found locally. Container cannot be started."
  echo "Listing available images:"
  docker images
  exit 1
fi

# Pass ALL required env vars (config + secrets) to the container
# Using --env-file might be cleaner if many vars, requires creating a file
if ! docker run -d --name "$CONTAINER_NAME" \
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
  "$API_IMAGE_URL"; then

  echo "Error: Failed to start API container '$CONTAINER_NAME'."
  echo "Docker run command failed. Checking container logs for more details:"
  docker logs "$CONTAINER_NAME" 2>/dev/null || echo "No logs available - container may not have started"

  echo "Checking system resources:"
  df -h
  free -m

  echo "Checking Docker system info:"
  docker system df
  docker info

  echo "Container startup failed - VM may not function correctly!"
else
  echo "API container '$CONTAINER_NAME' started successfully."
  echo "Container is running with the following details:"
  docker ps --filter "name=$CONTAINER_NAME" --format "ID: {{.ID}}, Image: {{.Image}}, Status: {{.Status}}, Ports: {{.Ports}}"
fi

echo "Startup script finished."
