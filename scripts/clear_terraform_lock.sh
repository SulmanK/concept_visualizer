#!/bin/bash
set -e

# Utility script to check for and clear Terraform state locks
# This is useful when a Terraform operation is interrupted and leaves a lock

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

# Function to print usage instructions
print_usage() {
  echo "Usage: $0 [ENVIRONMENT]"
  echo "  ENVIRONMENT: Optional. 'dev' or 'prod'. If not provided, will be determined from current git branch."
}

# Check if help flag is provided
if [[ "$1" == "-h" || "$1" == "--help" ]]; then
  print_usage
  exit 0
fi

# Determine environment - either from argument or from git branch
if [[ -n "$1" ]]; then
  # Environment specified as argument
  ENVIRONMENT="${1,,}" # Convert to lowercase
  if [[ "$ENVIRONMENT" != "dev" && "$ENVIRONMENT" != "prod" ]]; then
    echo "Error: Invalid environment '$ENVIRONMENT'. Must be 'dev' or 'prod'."
    print_usage
    exit 1
  fi

  if [[ "$ENVIRONMENT" == "dev" ]]; then
    WORKSPACE="$DEV_WORKSPACE"
    TFVARS_FILE="$DEV_TFVARS_FILE"
  else
    WORKSPACE="$PROD_WORKSPACE"
    TFVARS_FILE="$PROD_TFVARS_FILE"
  fi

  echo "Using $ENVIRONMENT environment as specified."
else
  # Determine environment from git branch
  CURRENT_BRANCH=$(git branch --show-current)
  echo "Current git branch: $CURRENT_BRANCH"

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
    echo "WARNING: You are about to check and potentially modify PRODUCTION state locks."
    echo ""
    read -p "Type 'check-production-locks' to confirm: " CONFIRM_PROD

    if [[ "$CONFIRM_PROD" != "check-production-locks" ]]; then
      echo "Production confirmation does not match. Operation cancelled."
      exit 1
    fi
  else
    echo "Error: Branch '$CURRENT_BRANCH' does not match either '$DEV_BRANCH' or '$PROD_BRANCH'."
    echo "Please either checkout one of those branches or specify the environment directly:"
    print_usage
    exit 1
  fi
fi

# Check if tfvars file exists
if [[ ! -f "$TFVARS_FILE" ]]; then
  echo "Error: Terraform variables file '$TFVARS_FILE' not found."
  echo "Please create this file with your environment-specific variables."
  exit 1
fi

# Get the bucket name from tfvars
TF_STATE_BUCKET=$(grep 'terraform_state_bucket_name' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
if [[ -z "$TF_STATE_BUCKET" ]]; then
  echo "Error: terraform_state_bucket_name not found in $TFVARS_FILE."
  exit 1
fi

echo "Using state bucket: $TF_STATE_BUCKET"

# Check if the lock file exists
LOCK_PATH="gs://${TF_STATE_BUCKET}/terraform/state/${WORKSPACE}.tflock"
if gsutil -q stat "$LOCK_PATH" 2>/dev/null; then
  echo "State lock detected for workspace: $WORKSPACE"

  # Try to get lock info
  echo "Lock Info:"
  gsutil cat "$LOCK_PATH" 2>/dev/null || echo "Could not read lock file"

  # Ask to remove the lock
  read -p "Do you want to remove this lock? Only do this if you're sure no Terraform operations are running! (yes/no) " REMOVE_LOCK

  if [[ "$REMOVE_LOCK" == "yes" ]]; then
    echo "Removing state lock..."
    if gsutil rm "$LOCK_PATH"; then
      echo "Lock successfully removed. You can now run Terraform operations."

      # Check for alert email configuration
      ALERT_EMAIL=$(grep 'alert_email_address' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
      if [[ -z "$ALERT_EMAIL" ]]; then
        echo ""
        echo "⚠️  REMINDER: No alert_email_address found in $TFVARS_FILE."
        echo "This is required for frontend monitoring to work correctly."
        echo "Please add 'alert_email_address = \"your-email@example.com\"' to your tfvars file,"
        echo "or ensure the ALERT_EMAIL_ADDRESS GitHub secret is set manually."
      fi
    else
      echo "Failed to remove lock. You may need higher permissions or the lock might be gone already."
      exit 1
    fi
  else
    echo "Lock will remain in place. No changes made."
  fi
else
  echo "No state lock detected for workspace: $WORKSPACE. You're good to go!"

  # Still check for alert email configuration
  ALERT_EMAIL=$(grep 'alert_email_address' "$TFVARS_FILE" | head -n 1 | awk -F'=' '{print $2}' | tr -d ' "')
  if [[ -z "$ALERT_EMAIL" ]]; then
    echo ""
    echo "⚠️  REMINDER: No alert_email_address found in $TFVARS_FILE."
    echo "This is required for frontend monitoring to work correctly."
    echo "Please add 'alert_email_address = \"your-email@example.com\"' to your tfvars file,"
    echo "or ensure the ALERT_EMAIL_ADDRESS GitHub secret is set manually."
  fi
fi
