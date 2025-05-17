# Design Document: Update Frontend Monitoring Workflow

## 1. Objective

Simplify the management of frontend uptime checks and alert policies within the CI/CD pipeline by fully integrating these resources into the main Terraform remote state. This aims to enhance reliability, reduce complexity, and provide a single source of truth for all infrastructure components.

## 2. Problem Statement Recap

The current method for managing frontend monitoring resources involves complex, ephemeral local Terraform state management within GitHub Actions, custom scripting for ID transfers via a dedicated GCS path (`dynamic_frontend_monitoring_ids/`), and a lack of integration with the main Terraform remote state. This leads to brittleness, potential state drift, and reduced visibility.

## 3. Proposed Solution (Key Changes)

The solution involves refactoring the existing workflow to leverage the main Terraform remote state for managing frontend monitoring resources.

### 3.1. `terraform/modules/monitoring/monitoring.tf` (or equivalent monitoring configuration)

- **Modify `google_monitoring_uptime_check_config.frontend_availability` resource:**
  - Remove the `lifecycle { ignore_changes = [monitored_resource[0].labels.host] }` block.
  - This will allow Terraform to detect and manage changes to the `host` label within the `monitored_resource` block, enabling it to update the uptime check target from a placeholder to the actual Vercel deployment URL.
  - Ensure `lifecycle { create_before_destroy = true }` is retained to prevent downtime during updates.

### 3.2. `.github/workflows/deploy_backend.yml`

- **Remove the existing "Update GCP Frontend Uptime Check" step:**

  - This includes the creation of a temporary Terraform directory (e.g., `/tmp/terraform_monitor`).
  - The local `terraform init` and `terraform apply` for monitoring resources.
  - The logic for writing/reading `DEFINITIVE_UPTIME_CHECK_FULL_ID` and `DEFINITIVE_ALERT_POLICY_FULL_ID` to/from GCS (`gs://${TF_STATE_BUCKET_NAME}/dynamic_frontend_monitoring_ids/...`).
  - The cleanup logic for stale dynamic monitoring resources that was part of this step.

- **Add a new step (or integrate into an existing Terraform apply step if suitable): "Apply/Update Frontend Monitoring Resources"**
  - This step should run after the Vercel deployment URL is obtained.
  - **Terraform Initialization:**
    - `terraform -chdir=terraform init -reconfigure \`
      `-backend-config="bucket=${{ secrets.TF_STATE_BUCKET_NAME }}" \`
      `(adjust prefix if necessary, e.g., -backend-config="prefix=terraform/state/${{ env.ENVIRONMENT }}")`
    - This ensures Terraform uses the shared remote backend.
  - **Workspace Selection:**
    - `terraform -chdir=terraform workspace select ${{ env.ENVIRONMENT }}`
  - **Terraform Apply:**
    - `terraform -chdir=terraform apply -auto-approve \`
      `-var="frontend_hostname=${{ steps.get_vercel_url.outputs.url }}" \`
      `(or steps.get_vercel_url.outputs.VERCEL_DEPLOYMENT_URL_FOR_MONITORING if that's the final output name)`
      `-target=module.frontend_monitor` (if monitoring resources are in a module named `frontend_monitor`)
    - Or target specific resources: `-target=google_monitoring_uptime_check_config.frontend_availability -target=google_monitoring_alert_policy.frontend_availability_failure_alert`
  - This step will create the monitoring resources on the first run (replacing any placeholder if `frontend_hostname` was initially a placeholder in `.tfvars`) or update them on subsequent runs if the Vercel URL changes.

### 3.3. `scripts/gcp_destroy.sh`

- **Simplify resource destruction:**
  - Remove the section that attempts to read IDs from `gs://${TF_STATE_BUCKET}/dynamic_frontend_monitoring_ids/...` and import them into Terraform state (`terraform import ...`).
  - The standard `terraform destroy` command (with the appropriate workspace and var file) will now correctly identify and destroy these monitoring resources as they are part of the remote state.
  - Remove the GCS cleanup of the `dynamic_frontend_monitoring_ids/` directory from this script as the directory itself will be deprecated.

## 4. Clean-up Tasks (Post-Implementation)

1.  **GCS Cleanup:** Manually delete the entire `dynamic_frontend_monitoring_ids/` folder from the GCS bucket used for Terraform state, as it will no longer be needed.
2.  **Script Removal:** Delete any old Bash helper scripts that were specifically created to support the previous placeholder workflow and ID management (e.g., scripts for writing IDs to GCS, if any existed outside the main workflow file).
3.  **Permissions Verification:** Confirm that the CI/CD service account (e.g., `CICD_SERVICE_ACCOUNT`) has the necessary permissions (`storage.objects.get`, `storage.objects.create`, `storage.objects.delete` - or `roles/storage.objectAdmin` on the specific state prefix) to manage objects within the main Terraform state prefix in GCS. It likely already has these, but verification is good practice.
4.  **Documentation Update:** Add a note to the project's `README.md` or relevant infrastructure documentation explaining that the frontend uptime check and alert policy are managed within the main Terraform configuration and require the `frontend_hostname` variable to be set (typically via CI) for their creation/update. Example:
    > "The frontend uptime check (`google_monitoring_uptime_check_config.frontend_availability`) and its associated alert policy (`google_monitoring_alert_policy.frontend_availability_failure_alert`) are managed by Terraform. To enable or update them, ensure the `frontend_hostname` variable is passed during `terraform apply`. In the CI/CD pipeline, this variable is automatically set to the latest Vercel deployment URL."

## 5. Benefits

- **Single Canonical State:** All infrastructure, including frontend monitoring, is managed in one Terraform remote state, enabling consistent drift detection and history.
- **Reduced Complexity:** Eliminates brittle Bash scripting for ID management and local Terraform state handling in CI.
- **Improved Reliability:** Leverages Terraform's backend locking mechanism to prevent race conditions during parallel deployments.
- **Increased Transparency:** Provides a clearer and more unified view of all managed infrastructure.

## 6. Assumptions

- The Terraform configuration for monitoring (uptime check and alert policy) is already present or will be structured (e.g., in a module like `frontend_monitor` or directly in the root configuration) to accept a `frontend_hostname` variable.
- The Vercel deployment URL is reliably obtained and made available as an output (e.g., `steps.get_vercel_url.outputs.url`) in the GitHub Actions workflow.
- The Terraform state bucket and CI/CD service account permissions are already configured for managing the main infrastructure.
