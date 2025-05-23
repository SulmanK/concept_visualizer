# Design Document: GitHub Secret Automation

## 1. Problem Statement

We need to create a new bash script, `scripts/gh_populate_secrets.sh`, designed to automate the population of specific GitHub Actions secrets. This script should:

- Be branch-aware, distinguishing between `develop` and `main` branches to set secrets with `DEV_` or `PROD_` prefixes respectively.
- Source secret values primarily from Terraform outputs (generated by `gcp_apply.sh` and defined in `terraform/outputs.tf`) and relevant `.tfvars` configuration files (`terraform/environments/dev.tfvars` and `terraform/environments/prod.tfvars`).
- Utilize the GitHub CLI (`gh`) to set these secrets in the repository.
- Explicitly exclude secrets designated as "manually added" in `Design/Setup.md` (i.e., `VERCEL_ORG_ID`, `VERCEL_TOKEN`, `DEV_VERCEL_PROJECT_ID`, `PROD_VERCEL_PROJECT_ID`, and Supabase/JigsawStack API keys which are sourced from `.env` files and set in GCP Secret Manager, not directly output by Terraform for this purpose).
- The `GCP_REGION` secret will be automated. It will be a single global secret in GitHub, sourced from the `region` variable in the _currently active_ `.tfvars` file.
- Be invoked automatically at the successful completion of the `scripts/gcp_apply.sh` script to ensure all necessary Terraform outputs are available.
- Requires a review of `terraform/outputs.tf` and potentially adding new outputs if any required secret values are not already being exposed by Terraform.

This will streamline the CI/CD setup process by reducing manual secret entry after infrastructure provisioning.

## 2. Design Details

### 2.1. New Script: `scripts/gh_populate_secrets.sh`

- **Purpose:** To set GitHub Actions secrets using values from Terraform outputs and configuration files.
- **Location:** `scripts/gh_populate_secrets.sh`
- **Branch Logic:** Detects current Git branch (`develop` or `main`) and sets secrets with appropriate `DEV_` or `PROD_` prefix.
- **Dependencies:**
  - GitHub CLI (`gh`) installed and authenticated (`gh auth login`). Script should check for `gh` and provide instructions if not found.
  - `jq` (optional, if direct Terraform outputs are not sufficient).
  - Access to `terraform` CLI.
  - Access to `.tfvars` files.
- **Core Functionality:**
  1.  **Preamble:** `set -e`, define script/project directories, branch names, prefixes.
  2.  **Branch Detection:** Determine `CURRENT_BRANCH`, set `TARGET_PREFIX` and `TFVARS_FILE`. Confirmation for `prod` branch.
  3.  **Prerequisite Check:** Verify `gh` installation.
  4.  **Change Directory:** `cd "$TERRAFORM_DIR"`.
  5.  **Secrets to Automate & Value Sources:**
      - **`GCP_REGION` (Global Secret):**
        - Value Source: `grep 'region'` from the active `$TFVARS_FILE`.
        - GitHub Secret Name: `GCP_REGION`
      - **Prefixed Secrets (DEV*/PROD*):**
        - `{PREFIX}_GCP_PROJECT_ID`: Terraform output `project_id`
        - `{PREFIX}_GCP_ZONE`: Terraform output `gcp_zone`
        - `{PREFIX}_NAMING_PREFIX`: Terraform output `naming_prefix`
        - `{PREFIX}_API_SERVICE_ACCOUNT_EMAIL`: Terraform output `api_service_account_email`
        - `{PREFIX}_WORKER_SERVICE_ACCOUNT_EMAIL`: Terraform output `worker_service_account_email`
        - `{PREFIX}_CICD_SERVICE_ACCOUNT_EMAIL`: Terraform output `cicd_service_account_email`
        - `{PREFIX}_WORKLOAD_IDENTITY_PROVIDER`: Terraform output `workload_identity_full_provider_name`
        - `{PREFIX}_ARTIFACT_REGISTRY_REPO_NAME`: Terraform output `artifact_registry_repository_name`
        - `{PREFIX}_FRONTEND_UPTIME_CHECK_CONFIG_ID`: Terraform output `frontend_uptime_check_id`
        - `{PREFIX}_FRONTEND_ALERT_POLICY_ID`: Terraform output `frontend_alert_policy_id`
        - `{PREFIX}_ALERT_NOTIFICATION_CHANNEL_FULL_ID`: Terraform output `frontend_notification_channel_id`
        - `{PREFIX}_FRONTEND_STARTUP_ALERT_DELAY`: Terraform output `frontend_startup_alert_delay_output`
        - `{PREFIX}_ALERT_ALIGNMENT_PERIOD`: Terraform output `alert_alignment_period_output`
        - `{PREFIX}_WORKER_MIN_INSTANCES`: Terraform output `worker_min_instances_output`
        - `{PREFIX}_WORKER_MAX_INSTANCES`: Terraform output `worker_max_instances_output`
      - **Secrets to EXCLUDE (Manually Added as per `Design/Setup.md`):**
        - `VERCEL_ORG_ID`
        - `VERCEL_TOKEN`
        - `DEV_VERCEL_PROJECT_ID`
        - `PROD_VERCEL_PROJECT_ID`
        - All Supabase secrets (`{PREFIX}_SUPABASE_URL`, `_ANON_KEY`, `_SERVICE_ROLE`, `_JWT_SECRET`)
        - All JigsawStack secrets (`{PREFIX}_JIGSAWSTACK_API_KEY`)
  6.  **Loop and Set Secrets:** Iterate through defined secrets, fetch values, and use `gh secret set "$FULL_SECRET_NAME" -b "$VALUE"`.
  7.  **Return to Original Directory.**

### 2.2. Modifications to `terraform/outputs.tf`

- Ensure existing outputs are suitable.
- Add any missing outputs required by `scripts/gh_populate_secrets.sh`:

  ```terraform
  // Example additions/verifications
  output "project_id" {
    description = "The GCP project ID."
    value       = var.project_id
  }

  output "gcp_zone" {
    description = "The GCP zone."
    value       = var.gcp_zone
  }

  output "naming_prefix" {
    description = "The naming prefix for resources."
    value       = var.naming_prefix
  }

  output "frontend_startup_alert_delay_output" {
    description = "Frontend startup alert delay."
    value       = var.frontend_startup_alert_delay
  }

  output "alert_alignment_period_output" {
    description = "Alert alignment period."
    value       = var.alert_alignment_period
  }

  output "worker_min_instances_output" {
      description = "Minimum number of worker instances."
      value       = var.worker_min_instances
  }

  output "worker_max_instances_output" {
      description = "Maximum number of worker instances."
      value       = var.worker_max_instances
  }

  output "artifact_registry_repository_name" {
    description = "The simple name of the Artifact Registry repository (e.g., my-project-dev-docker-repo)."
    // This should match the repository name part, not the full URL.
    // Example: if local.artifact_registry_repo_name = "${var.naming_prefix}-docker-repo"
    value       = local.artifact_registry_repo_name
  }
  // Ensure outputs like api_service_account_email, worker_service_account_email, cicd_service_account_email are present and correct.
  // Ensure workload_identity_full_provider_name, frontend_uptime_check_id, frontend_alert_policy_id, frontend_notification_channel_id are present.
  ```

  _Note: The `artifact_registry_repository_name` output should provide the simple repository name (e.g., `concept-viz-dev-docker-repo`) as this is what's typically used in GitHub Actions for configuring Docker, not the full path._

### 2.3. Integration with `scripts/gcp_apply.sh`

- At the end of `gcp_apply.sh`, after successful completion and output display:

  ```bash
  # Ensure SCRIPT_DIR is correctly defined or use absolute path if calling from a different context
  # For example, if gcp_apply.sh is in scripts/ and gh_populate_secrets.sh is also in scripts/
  # then SCRIPT_DIR as defined in gcp_apply.sh should work.

  echo -e "\n===== STEP X: Populating GitHub Secrets =====\n"
  "$SCRIPT_DIR/gh_populate_secrets.sh"
  if [ $? -ne 0 ]; then
      echo "Warning: Failed to populate GitHub secrets. Please run scripts/gh_populate_secrets.sh manually."
  else
      echo "GitHub secrets populated successfully."
  fi
  ```

### 2.4. Documentation

- Update `README.md` and/or `Design/Setup.md`.
- Note `gh` CLI prerequisite (installation and authentication).
- Clarify automated vs. manual secrets.

## 3. Implementation Phases

1.  **Update `terraform/outputs.tf`:** Add and verify all necessary outputs.
2.  **Develop `scripts/gh_populate_secrets.sh`:** Create the script based on the design.
3.  **Integrate:** Call the new script from `scripts/gcp_apply.sh`.
4.  **Test:** Thoroughly test on `develop` and `main` branches.
5.  **Document:** Update all relevant documentation.
