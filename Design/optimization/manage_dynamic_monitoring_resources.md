# Design Document: Managing Dynamically Created Frontend Monitoring Resources

## 1. Problem Statement

The `deploy_backend.yml` GitHub Actions workflow dynamically creates/updates GCP monitoring resources (specifically, a `google_monitoring_uptime_check_config` and an associated `google_monitoring_alert_policy`) for the project's Vercel frontend deployment. This is necessary because the frontend's deployment URL is only definitively known at deployment time.

These resources are managed by an ephemeral Terraform configuration within the workflow. The main Terraform setup, located in the `/terraform` directory and managed by `scripts/gcp_apply.sh` and `scripts/gcp_destroy.sh`, creates initial placeholder monitoring resources.

The issue is that `scripts/gcp_destroy.sh` is unaware of the specific frontend monitoring resources last configured by the `deploy_backend.yml` workflow. As a result, these dynamically managed resources are not reliably destroyed, leading to orphaned resources and potential cost implications in GCP.

The core requirements are:

1.  The frontend monitoring configuration must use the dynamic URL from Vercel, determined at deployment time.
2.  The workflow must ensure it's configuring/updating a single, authoritative set of monitoring resources for the frontend per environment, cleaning up any stale dynamic configurations from previous runs if necessary.
3.  All GCP resources, including the dynamically configured frontend monitoring, must be properly destroyed by the main `scripts/gcp_destroy.sh` script when an environment is torn down.
4.  The solution should integrate smoothly with the existing Terraform and GitHub Actions workflows.

## 2. Proposed Solution: Import into Main Terraform State with Workflow Coordination

This solution ensures that the main Terraform configuration ultimately manages the lifecycle of all resources, including those dynamically updated by the deployment workflow.

### 2.1. Main Terraform Configuration (`/terraform` directory)

- **Resource Definitions:** The main Terraform configuration (e.g., in `terraform/monitoring.tf`) will continue to define the `google_monitoring_uptime_check_config` and `google_monitoring_alert_policy` resources for the frontend. For example:

  ```terraform
  resource "google_monitoring_uptime_check_config" "frontend_availability" {
    project      = var.gcp_project_id
    display_name = "${var.naming_prefix}-frontend-availability-${var.environment}"
    // ... other configurations, initially pointing to a placeholder host
    http_check {
      host = var.initial_frontend_hostname // e.g., "placeholder.example.com"
      path = "/"
      port = "443"
      use_ssl = true
      validate_ssl = true
    }
    // ...
  }

  resource "google_monitoring_alert_policy" "frontend_availability_failure_alert" {
    project      = var.gcp_project_id
    display_name = "${var.naming_prefix}-frontend-down-al-${var.environment}"
    // ... conditions referencing google_monitoring_uptime_check_config.frontend_availability.uptime_check_id
  }
  ```

- **Initial Creation:** The `scripts/gcp_apply.sh` script will create these resources with placeholder values (e.g., a generic hostname). The IDs of these created resources (e.g., `frontend_uptime_check_id`, `frontend_alert_policy_id`) are outputted and stored as GitHub secrets (e.g., `DEV_FRONTEND_UPTIME_CHECK_CONFIG_ID`, `PROD_FRONTEND_UPTIME_CHECK_CONFIG_ID`).
- **Consistency:** The Terraform resource names (`frontend_availability`, `frontend_availability_failure_alert`) and the GCP `displayName` format must be consistent with those used by the `deploy_backend.yml` workflow's ephemeral Terraform.

### 2.2. `deploy_backend.yml` Workflow Enhancements

- **Step 1: Clean Up Stale Dynamic Monitoring Resources (Hygiene):**

  - Before the workflow's Terraform steps for monitoring, implement a step to find and delete any _orphaned_ uptime checks or alert policies in GCP that match the expected `displayName` pattern but whose IDs _do not_ match the ones currently stored in the environment's secrets (`env.FRONTEND_UPTIME_CHECK_ID`, `env.FRONTEND_ALERT_POLICY_ID`).
  - This step acts as a safeguard against orphaned resources from previous, potentially failed or misconfigured, workflow runs. It is primarily for cleanup of unexpected duplicates, not for deleting the primary placeholder which will be updated.
  - Use `gcloud monitoring uptime-check-configs list --filter="displayName='...'" --format="value(name)"` and `gcloud alpha monitoring policies list --filter="displayName='...'" --format="value(name)"` to find potential orphans, then `delete` them.

- **Step 2: Configure/Update Monitoring Resources (Largely Existing Logic):**

  - The workflow will continue to use its temporary Terraform setup (in `/tmp/terraform_monitor`).
  - **Import:** The existing `terraform import` commands in the workflow are crucial. They use the IDs from secrets (e.g., `env.FRONTEND_UPTIME_CHECK_ID`) to import the placeholder resources (created by `gcp_apply.sh`) into the workflow's temporary Terraform state.
    ```bash
    # Example for uptime check
    terraform import -no-color google_monitoring_uptime_check_config.frontend_availability "projects/${GCP_PROJECT_ID_FOR_MONITOR}/uptimeCheckConfigs/${UPTIME_CHECK_ID_FOR_MONITOR}" || echo "Uptime check import failed or does not exist."
    ```
  - **Apply:** The subsequent `terraform apply -var-file=terraform.tfvars` in the workflow will then _update these imported resources in place_ with the new Vercel deployment URL (`target_hostname`) and any other dynamic settings. The placeholder resource is effectively transformed into the correctly configured dynamic resource.

- **Step 3: Store Definitive Resource IDs:**

  - After the workflow's `terraform apply` completes, it must reliably obtain the _current and definitive GCP resource IDs_ of the `google_monitoring_uptime_check_config.frontend_availability` and `google_monitoring_alert_policy.frontend_availability_failure_alert` it just configured.
  - While these IDs are likely unchanged if the update was in-place, it's best practice to re-fetch them from the workflow's Terraform state outputs or via `gcloud` lookup using the known `displayName`.

    ```bash
    # Example: Get ID from terraform output in the workflow's temp dir
    # Ensure the temporary Terraform configuration in the workflow outputs these IDs
    UPTIME_CHECK_FULL_ID=$(terraform output -raw frontend_availability_config_id) # Or a similar output name
    ALERT_POLICY_FULL_ID=$(terraform output -raw frontend_availability_alert_policy_id) # Or a similar output name
    ```

    Or using `gcloud`:

    ```bash
    UPTIME_CHECK_DISPLAY_NAME="${NAMING_PREFIX}-frontend-availability-${ENVIRONMENT}"
    UPTIME_CHECK_FULL_ID=$(gcloud monitoring uptime-check-configs list --project="${GCP_PROJECT_ID_FOR_MONITOR}" --filter="displayName=${UPTIME_CHECK_DISPLAY_NAME}" --format="value(name)" | head -n 1)

    ALERT_POLICY_DISPLAY_NAME="${NAMING_PREFIX}-frontend-down-al-${ENVIRONMENT}"
    ALERT_POLICY_FULL_ID=$(gcloud alpha monitoring policies list --project="${GCP_PROJECT_ID_FOR_MONITOR}" --filter="displayName=${ALERT_POLICY_DISPLAY_NAME}" --format="value(name)" | head -n 1)
    ```

  - Store these definitive full IDs (e.g., `projects/PROJECT_ID/uptimeCheckConfigs/CONFIG_ID`) in a known, environment-specific GCS location. The Terraform state bucket is a suitable place.
    - `gs://${TF_STATE_BUCKET_NAME}/dynamic_frontend_monitoring_ids/${ENVIRONMENT}/frontend_uptime_check_id.txt`
    - `gs://${TF_STATE_BUCKET_NAME}/dynamic_frontend_monitoring_ids/${ENVIRONMENT}/frontend_alert_policy_id.txt`
      (The `TF_STATE_BUCKET_NAME` name will need to be available to the workflow, ideally passed via a GitHub secret, e.g., `secrets.TF_STATE_BUCKET_NAME`).

### 2.3. `scripts/gcp_destroy.sh` Script Enhancements

- **Step 1: Fetch Definitive Resource IDs:**

  - Before running `terraform plan -destroy`, the script will attempt to read the stored definitive resource IDs from the GCS location populated by the workflow.

    ```bash
    TF_STATE_BUCKET=$(grep 'terraform_state_bucket_name' "$TFVARS_FILE" | awk -F'=' '{print $2}' | tr -d ' "') # Get from tfvars
    UPTIME_CHECK_ID_FILE="gs://${TF_STATE_BUCKET}/dynamic_frontend_monitoring_ids/${WORKSPACE}/frontend_uptime_check_id.txt"
    ALERT_POLICY_ID_FILE="gs://${TF_STATE_BUCKET}/dynamic_frontend_monitoring_ids/${WORKSPACE}/frontend_alert_policy_id.txt"

    DEFINITIVE_UPTIME_CHECK_ID=$(gsutil cat "$UPTIME_CHECK_ID_FILE" 2>/dev/null || echo "")
    DEFINITIVE_ALERT_POLICY_ID=$(gsutil cat "$ALERT_POLICY_ID_FILE" 2>/dev/null || echo "")
    ```

- **Step 2: Import Resources into Main Terraform State:**

  - If the definitive IDs are found, the script will execute `terraform import` commands. This brings the resources (as last configured by the workflow) into the main Terraform state (`/terraform` directory's state).
    ```bash
    if [[ -n "$DEFINITIVE_UPTIME_CHECK_ID" ]]; then
      terraform import "google_monitoring_uptime_check_config.frontend_availability" "$DEFINITIVE_UPTIME_CHECK_ID" || echo "Warning: Failed to import dynamic uptime check. It might have already been deleted or was never created."
    fi
    if [[ -n "$DEFINITIVE_ALERT_POLICY_ID" ]]; then
      terraform import "google_monitoring_alert_policy.frontend_availability_failure_alert" "$DEFINITIVE_ALERT_POLICY_ID" || echo "Warning: Failed to import dynamic alert policy. It might have already been deleted or was never created."
    fi
    ```
  - The resource names used here (`google_monitoring_uptime_check_config.frontend_availability`, `google_monitoring_alert_policy.frontend_availability_failure_alert`) must exactly match those in the main `/terraform/monitoring.tf`.

- **Step 3: Proceed with Destruction (Existing Logic):**

  - The script will then run `terraform plan -destroy -out=tfplan` and `terraform apply tfplan` as usual. Since the resources have been imported, they will be part of the destruction plan and correctly removed by Terraform.

- **Step 4: Clean Up ID Files (Recommended):**
  - After successful destruction, delete the ID files from GCS.
    ```bash
    gsutil rm "$UPTIME_CHECK_ID_FILE" 2>/dev/null || true
    gsutil rm "$ALERT_POLICY_ID_FILE" 2>/dev/null || true
    ```

## 3. Rationale

- **Single Source of Truth for Destruction:** The main Terraform configuration remains the authority for destroying all infrastructure.
- **Handles Dynamic Updates:** The workflow can safely update monitoring configurations based on real-time deployment information.
- **State Consistency:** Importing ensures that Terraform's state accurately reflects the actual GCP resources before destruction.
- **Minimal Changes to Existing Structure:** Leverages existing scripts and workflow structures with targeted additions.
- **Idempotency (Improved):** The workflow's update-in-place mechanism and the destroy script's import-then-destroy are idempotent.

## 4. Future Considerations / Alternatives

- **Terraform Cloud/Enterprise:** If using Terraform Cloud/Enterprise, its state management and API could offer alternative ways to coordinate.
- **Dedicated Cleanup Job:** A separate, scheduled job could periodically scan for and remove orphaned monitoring resources based on tags or naming patterns, as an additional layer of defense. This is more of a global cleanup than environment-specific.

## 5. Impact Assessment

- **Workflow (`deploy_backend.yml`):** Requires modifications to add GCS write steps for IDs, and potentially logic to fetch definitive IDs post-apply. Cleanup logic for stale dynamic resources also needs to be added. The workflow also needs access to `TF_STATE_BUCKET_NAME`.
- **Scripts (`gcp_destroy.sh`):** Requires modifications to add GCS read steps and `terraform import` commands.
- **Terraform Configuration (`/terraform`):** Ensure resource definitions for frontend monitoring are present and consistent. Add `initial_frontend_hostname` variable.
- **IAM Permissions:** The CI/CD service account used by the workflow will need permissions to write to the GCS bucket (`roles/storage.objectAdmin` on the bucket or specific path). The service account/user running `gcp_destroy.sh` will need read/delete permissions for those GCS objects (`roles/storage.objectViewer` and `roles/storage.objectAdmin` respectively).

This approach provides a robust way to manage the lifecycle of these dynamically configured resources.
