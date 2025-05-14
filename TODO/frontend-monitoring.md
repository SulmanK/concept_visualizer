Okay, here's a comprehensive step-by-step guide for setting up your frontend health monitoring, integrating the Vercel deployment URL update into your existing GitHub Actions workflow.

**Goal:** Automatically monitor the availability of your Vercel-deployed frontend using GCP Uptime Checks, ensuring the check always targets the latest deployment URL for both `develop` (preview) and `main` (production) branches.

**Prerequisites Checklist:**

1.  ✅ **GCP Project(s):** You have your dev and prod GCP projects set up.
2.  ✅ **Terraform Setup:** Your Terraform code for other GCP resources (including backend monitoring and notification channels) is in place.
3.  ✅ **Vercel Project(s):** Your frontend (`frontend/my-app`) is linked to one or two Vercel projects (one for dev/previews, one for production, or a single project handling both via branch deployments).
4.  ✅ **Vercel GitHub Integration:** Vercel automatically deploys your frontend when you push to `develop` and `main` branches.
5.  ✅ **Required Tools:** `gcloud` CLI, `terraform` CLI, `npm`/`node`, `vercel` CLI (will be installed in CI).
6.  ✅ **GitHub Repository:** Your code is in a GitHub repository with Actions enabled.
7.  ✅ **Necessary Secrets (to be created/updated in GitHub):**
    - `VERCEL_TOKEN`: Your Vercel Personal Access Token.
    - `VERCEL_ORG_ID`: Your Vercel Organization/Team ID (if your project is under a team, otherwise can be omitted or set to your Vercel username).
    - `VERCEL_PROJECT_ID_DEV`: Vercel Project ID for your `develop` branch deployments.
    - `VERCEL_PROJECT_ID_PROD`: Vercel Project ID for your `main` branch deployments.
    - GCP credentials for CI/CD (Workload Identity Federation secrets like `DEV_WORKLOAD_IDENTITY_PROVIDER`, `DEV_CICD_SERVICE_ACCOUNT_EMAIL`, etc., are already set up from your backend deployment).

---

**Step-by-Step Guide:**

**Step 1: Add Frontend Uptime Check to Terraform**

1.  **Define Variables (`terraform/variables.tf`):**
    If not already present from the previous backend setup, add:

    ```terraform
    variable "initial_frontend_hostname_placeholder" {
      description = "A placeholder hostname for the frontend uptime check. This will be updated by CI/CD. Can be an empty string or a generic domain if Terraform requires a value."
      type        = string
      default     = "placeholder.vercel.app" # Or your main custom domain if relatively stable
    }

    # Ensure you have alert_email_address for the notification channel
    variable "alert_email_address" {
      description = "The email address to send monitoring alerts to."
      type        = string
    }

    variable "alert_alignment_period" {
      description = "The alignment period for alerts (e.g., '300s' for 5 minutes)."
      type        = string
      default     = "300s"
    }

    # A separate alert delay for frontend, or reuse api_startup_alert_delay
    variable "frontend_startup_alert_delay" {
      description = "The duration a failing frontend health check must persist before alerting."
      type        = string
      default     = "300s" # 5 minutes, Vercel deployments are usually fast
    }
    ```

2.  **Create Notification Channel (if not already present in `terraform/monitoring.tf`):**
    You likely have this from your backend setup. If not, add it:

    ```terraform
    resource "google_monitoring_notification_channel" "email_alert_channel" {
      project      = var.project_id
      display_name = "${var.naming_prefix}-alert-email-${var.environment}"
      type         = "email"
      labels = {
        email_address = var.alert_email_address
      }
      description = "Email notification channel for Concept Visualizer alerts (${var.environment})."
      enabled     = true
    }
    ```

3.  **Define Uptime Check and Alert Policy (`terraform/monitoring.tf`):**
    Add the following resources:

    ```terraform
    # --- Frontend Availability Uptime Check ---
    resource "google_monitoring_uptime_check_config" "frontend_availability" {
      project      = var.project_id
      display_name = "${var.naming_prefix}-frontend-availability-${var.environment}"
      timeout      = "10s" # How long each ping waits for a response

      http_check {
        path           = "/"                # Check the root path of your frontend
        port           = "443"              # Vercel uses HTTPS
        use_ssl        = true
        request_method = "GET"
        # Validates that the page title is present - a good sign the app loaded
        content_matchers {
          content = "<title>Concept Visualizer</title>" # Adjust to your actual <title>
          matcher = "MATCHES_STRING"                    # Checks if the string is present in the response body
        }
      }

      monitored_resource {
        type = "uptime_url"
        labels = {
          host = var.initial_frontend_hostname_placeholder # This will be updated by CI/CD
        }
      }
      period = "180s" # Check every 3 minutes
    }

    # --- Alert Policy for Frontend Availability Failures ---
    resource "google_monitoring_alert_policy" "frontend_availability_failure_alert" {
      project      = var.project_id
      display_name = "${var.naming_prefix}-frontend-down-al-${var.environment}"
      combiner     = "OR"

      conditions {
        display_name = "Frontend Application Unavailable (Sustained)"
        condition_threshold {
          filter = "metric.type=\"monitoring.googleapis.com/uptime_check/check_passed\" AND resource.type=\"uptime_url\" AND resource.label.check_id==\"${google_monitoring_uptime_check_config.frontend_availability.uptime_check_id}\""
          aggregations {
            alignment_period   = var.alert_alignment_period # e.g., "300s"
            per_series_aligner = "ALIGN_FRACTION_TRUE"
          }
          comparison      = "COMPARISON_LT"
          threshold_value = 0.9 # Alert if less than 90% success rate in an alignment_period
          duration        = var.frontend_startup_alert_delay # e.g., "300s"
          trigger {
            count = 1
          }
        }
      }

      notification_channels = [
        google_monitoring_notification_channel.email_alert_channel.id,
      ]

      documentation {
        content = <<-EOT
    ### Frontend Availability Alert (${var.environment})

    **Summary:** The frontend application is failing uptime checks.
    **Monitored Host (may be placeholder if CI/CD hasn't updated it yet):** `${var.initial_frontend_hostname_placeholder}`
    **Uptime Check ID:** `${google_monitoring_uptime_check_config.frontend_availability.uptime_check_id}`
    **Condition:** Success rate less than 90% over a ${var.alert_alignment_period} window, persisting for ${var.frontend_startup_alert_delay}.

    **Possible Causes:**
    *   Vercel platform issues.
    *   DNS resolution problems for your custom domain (if any).
    *   Misconfiguration in Vercel deployment settings.
    *   The application is not serving the expected content (e.g., your app's title tag).
    *   The Uptime Check's target hostname in GCP Monitoring is outdated (CI/CD job may have failed to update it).

    **Recommended Actions:**
    1.  **Check Vercel Status:** Visit [status.vercel.com](https://status.vercel.com/).
    2.  **Check Vercel Deployment Logs:** Review logs for your frontend deployment in the Vercel dashboard.
    3.  **Verify DNS Configuration:** If using a custom domain, ensure DNS records are correct.
    4.  **Verify Uptime Check Target:** In GCP Monitoring, check the hostname configured for Uptime Check ID `${google_monitoring_uptime_check_config.frontend_availability.uptime_check_id}`. Ensure it matches your latest Vercel deployment URL.
    5.  **Manually Access Frontend URL:** Try accessing your Vercel deployment URL from different networks/devices.
        EOT
        mime_type = "text/markdown"
      }

      user_labels = {
        environment = var.environment
        service     = "${var.naming_prefix}-frontend"
        tier        = "frontend"
      }

      depends_on = [
        google_monitoring_uptime_check_config.frontend_availability,
        google_monitoring_notification_channel.email_alert_channel,
      ]
    }
    ```

4.  **Define Outputs (`terraform/outputs.tf`):**

    ```terraform
    output "frontend_uptime_check_id" {
      description = "The ID (not full name) of the Uptime Check configuration for the frontend."
      value       = google_monitoring_uptime_check_config.frontend_availability.uptime_check_id
    }

    output "frontend_uptime_check_name_full" {
      description = "The full name/path of the frontend uptime check. Useful for `gcloud` commands."
      value       = google_monitoring_uptime_check_config.frontend_availability.name
    }
    ```

5.  **Update Environment Variables (`terraform/environments/dev.tfvars.example` & `prod.tfvars.example`):**
    Add/update:

    ```
    initial_frontend_hostname_placeholder = "your-app-name.vercel.app" # Or a generic placeholder
    frontend_startup_alert_delay        = "300s" # 5 minutes
    alert_email_address                 = "your-alert-email@example.com" # Ensure this is set
    ```

    Copy these example files to `dev.tfvars` and `prod.tfvars` and fill them with actual values.

6.  **Apply Terraform:**
    Run your `scripts/gcp_apply.sh` script for both `develop` and `main` branches (or apply manually per environment after checking out the respective branch). This will create the uptime check and alert policy.

    - `git checkout develop`
    - `./scripts/gcp_apply.sh`
    - `git checkout main`
    - `./scripts/gcp_apply.sh`

    Note the output `frontend_uptime_check_id` for each environment.

---

**Step 2: Configure GitHub Secrets**

1.  **Vercel Token:**

    - Go to Vercel Dashboard > Your Account Settings > Tokens.
    - Create a new Access Token. Copy it.
    - In your GitHub repository > Settings > Secrets and variables > Actions > New repository secret:
      - Name: `VERCEL_TOKEN`
      - Value: Paste your Vercel Access Token.

2.  **Vercel Org ID (if applicable):**

    - If your Vercel project is under a Team/Organization, go to Vercel Dashboard > Your Team > Settings > General.
    - The "Team ID" is what you need.
    - In GitHub Secrets:
      - Name: `VERCEL_ORG_ID`
      - Value: Paste your Vercel Team ID. (If it's a personal project, you might use your Vercel username or omit this secret and adjust the Vercel CLI commands in the workflow).

3.  **Vercel Project IDs:**

    - Go to your Vercel Dashboard, select your project for `develop` branch (e.g., `concept-visualizer-dev`).
    - Go to Project Settings > General > Project ID. Copy it.
    - In GitHub Secrets:
      - Name: `VERCEL_PROJECT_ID_DEV`
      - Value: Paste the Project ID.
    - Repeat for your `main` branch's Vercel project (e.g., `concept-visualizer-prod`):
      - Name: `VERCEL_PROJECT_ID_PROD`
      - Value: Paste the Project ID.
        _(If you use a single Vercel project for both, these two secrets will have the same value)._

4.  **GCP Frontend Uptime Check IDs:**

    - From the Terraform output in Step 1.6 (or by looking up the Uptime Check ID in GCP Cloud Monitoring), get the Uptime Check ID for your **dev** environment.
    - In GitHub Secrets:
      - Name: `DEV_FRONTEND_UPTIME_CHECK_CONFIG_ID`
      - Value: Paste the ID (e.g., `abcdef1234567890`).
    - Repeat for your **prod** environment:
      - Name: `PROD_FRONTEND_UPTIME_CHECK_CONFIG_ID`
      - Value: Paste the ID.

    * Make sure the gcp_apply.sh also shares these outputs

      ```# Display important output values for setting up GitHub Actions
      echo -e "\n===== IMPORTANT OUTPUT VALUES FOR CI/CD SETUP =====\n"
      echo "Copy these values to set up your GitHub repository secrets:"
      echo -e "\nAPI Service Account Email for $ENVIRONMENT environment (DEV_API_SERVICE_ACCOUNT_EMAIL or PROD_API_SERVICE_ACCOUNT_EMAIL):"
      terraform output -raw api_service_account_email

      echo -e "\nWorker Service Account Email for $ENVIRONMENT environment (DEV_WORKER_SERVICE_ACCOUNT_EMAIL or PROD_WORKER_SERVICE_ACCOUNT_EMAIL):"
      terraform output -raw worker_service_account_email

      echo -e "\nCI/CD Service Account Email for $ENVIRONMENT environment (DEV_CICD_SERVICE_ACCOUNT_EMAIL or PROD_CICD_SERVICE_ACCOUNT_EMAIL):"
      terraform output -raw cicd_service_account_email

      echo -e "\nWorkload Identity Provider for $ENVIRONMENT environment (DEV_WORKLOAD_IDENTITY_PROVIDER or PROD_WORKLOAD_IDENTITY_PROVIDER):"
      terraform output -raw workload_identity_full_provider_name

      echo -e "\nArtifact Registry Repository Name for $ENVIRONMENT environment (DEV_ARTIFACT_REGISTRY_REPO_NAME or PROD_ARTIFACT_REGISTRY_REPO_NAME):"
      echo "${NAMING_PREFIX}-docker-repo"

      echo -e "\nExternal IP for API VM for $ENVIRONMENT environment:"
      terraform output -raw api_vm_external_ip
      ```

5.  **GCP CI/CD Permissions:**
    Ensure your CI/CD service account (e.g., `PROD_CICD_SERVICE_ACCOUNT_EMAIL`) has the `roles/monitoring.editor` permission in GCP. Your `terraform/iam.tf` should already try to set this up. Verify it:
    ```terraform
    # terraform/iam.tf
    resource "google_project_iam_member" "cicd_sa_monitoring_editor" {
      project = var.project_id
      role    = "roles/monitoring.editor"
      member  = "serviceAccount:${google_service_account.cicd_service_account.email}"
    }
    ```
    If you added this now, re-run `terraform apply`.

---

**Step 3: Update GitHub Actions Workflow (`deploy_backend.yml`)**

Modify your existing `.github/workflows/deploy_backend.yml` as shown in the previous detailed response. The key additions are:

1.  **Branch Name Determination:** Correctly use `github.event.workflow_run.head_branch` in the `Set Environment Specifics` step.
2.  **Environment Variables for Frontend Monitoring:** Add `FRONTEND_UPTIME_CHECK_ID` and `VERCEL_PROJECT_ID` to the environment variables set in the `Set Environment Specifics` step.
3.  **Node.js Setup and Vercel CLI Installation:**

    ```yaml
    - name: Set up Node.js for Vercel CLI
      if: env.ENVIRONMENT == 'dev' || env.ENVIRONMENT == 'prod'
      uses: actions/setup-node@v4
      with:
        node-version: "18"

    - name: Install Vercel CLI
      if: env.ENVIRONMENT == 'dev' || env.ENVIRONMENT == 'prod'
      run: npm install -g vercel
    ```

4.  **Get Latest Vercel Deployment URL Step:**

    ```yaml
    - name: Get Latest Vercel Deployment URL
      id: get_vercel_url
      if: env.ENVIRONMENT == 'dev' || env.ENVIRONMENT == 'prod'
      env:
        VERCEL_TOKEN: ${{ secrets.VERCEL_TOKEN }}
        VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
        PROJECT_ID_VERCEL: ${{ env.VERCEL_PROJECT_ID }}
        # Pass the commit SHA from the parent workflow that triggered this one
        COMMIT_SHA_FROM_PARENT_WORKFLOW: ${{ github.event.workflow_run.head_sha }}
        BRANCH_NAME_FROM_PARENT_WORKFLOW: ${{ github.event.workflow_run.head_branch }}
      run: |
        echo "Fetching deployment URL for Vercel Project ID: $PROJECT_ID_VERCEL"
        echo "Branch: $BRANCH_NAME_FROM_PARENT_WORKFLOW, Commit: $COMMIT_SHA_FROM_PARENT_WORKFLOW"

        SCOPE_ARG=""
        if [[ -n "$VERCEL_ORG_ID" ]]; then
          SCOPE_ARG="--scope $VERCEL_ORG_ID"
        fi

        # Get the latest deployment for the commit SHA on the specific branch
        # Vercel ls output can be tricky. `inspect` is more reliable for a specific deployment.
        # First, find the deployment ID for the commit
        LATEST_DEPLOYMENT_ID=$(vercel ls $PROJECT_ID_VERCEL --token $VERCEL_TOKEN $SCOPE_ARG --meta githubCommitSha=$COMMIT_SHA_FROM_PARENT_WORKFLOW --meta githubCommitRef=$BRANCH_NAME_FROM_PARENT_WORKFLOW --state READY --yes | awk 'NR==2{print $1}') # NR==2 skips header

        if [[ -z "$LATEST_DEPLOYMENT_ID" ]]; then
          echo "Error: Could not find a READY Vercel deployment ID for commit $COMMIT_SHA_FROM_PARENT_WORKFLOW on branch $BRANCH_NAME_FROM_PARENT_WORKFLOW."
          # Fallback: try to get the latest ready deployment for the branch if commit-specific one fails
          echo "Attempting fallback: latest READY deployment for branch $BRANCH_NAME_FROM_PARENT_WORKFLOW"
          LATEST_DEPLOYMENT_ID=$(vercel ls $PROJECT_ID_VERCEL --token $VERCEL_TOKEN $SCOPE_ARG --meta githubCommitRef=$BRANCH_NAME_FROM_PARENT_WORKFLOW --state READY --yes | awk 'NR==2{print $1}')
          if [[ -z "$LATEST_DEPLOYMENT_ID" ]]; then
              echo "Fallback failed. Could not determine deployment ID."
              exit 1
          fi
        fi
        echo "Found Vercel Deployment ID: $LATEST_DEPLOYMENT_ID"

        # Inspect that deployment to get its URL
        DEPLOYMENT_JSON_OUTPUT=$(vercel inspect $LATEST_DEPLOYMENT_ID --token $VERCEL_TOKEN $SCOPE_ARG --yes)
        echo "Vercel Inspect Output: $DEPLOYMENT_JSON_OUTPUT"
        DEPLOY_URL=$(echo "$DEPLOYMENT_JSON_OUTPUT" | jq -r '.url') # The unique deployment URL

        # For production (main branch), prefer the aliased production domain if available
        if [[ "$BRANCH_NAME_FROM_PARENT_WORKFLOW" == "main" ]]; then
          PROD_TARGET_URL=$(echo "$DEPLOYMENT_JSON_OUTPUT" | jq -r '.targets.production.url // empty')
          if [[ -n "$PROD_TARGET_URL" && "$PROD_TARGET_URL" != "null" ]]; then
            DEPLOY_URL="https://$PROD_TARGET_URL" # Ensure https
            echo "Using production alias for main branch: $DEPLOY_URL"
          else
            DEPLOY_URL="https://$DEPLOY_URL" # Default to unique URL with https
            echo "Production alias not found, using unique deployment URL for main branch: $DEPLOY_URL"
          fi
        else
          DEPLOY_URL="https://$DEPLOY_URL" # For develop/preview, use the unique URL with https
        fi

        if [[ -z "$DEPLOY_URL" || "$DEPLOY_URL" == "null" || "$DEPLOY_URL" == "https://null" ]]; then
          echo "Error: Could not parse deployment URL from Vercel CLI output for deployment ID $LATEST_DEPLOYMENT_ID."
          exit 1
        fi

        echo "Final Vercel Deployment URL for Monitoring: $DEPLOY_URL"
        echo "VERCEL_DEPLOYMENT_URL_FOR_MONITORING=$DEPLOY_URL" >> $GITHUB_ENV
        echo "::set-output name=url::$DEPLOY_URL"
    ```

5.  **Update GCP Frontend Uptime Check Step:** (As provided in the previous answer, ensure environment variables are correctly mapped).

    ```yaml
    - name: Update GCP Frontend Uptime Check
      if: env.FRONTEND_UPTIME_CHECK_ID != '' && env.VERCEL_DEPLOYMENT_URL_FOR_MONITORING != ''
      env:
        GCP_PROJECT_ID_FOR_MONITOR: ${{ env.GCP_PROJECT_ID }}
        UPTIME_CHECK_ID_FOR_MONITOR: ${{ env.FRONTEND_UPTIME_CHECK_ID }}
        VERCEL_URL_TO_MONITOR: ${{ env.VERCEL_DEPLOYMENT_URL_FOR_MONITORING }}
      run: |
        # ... (script to update uptime check as shown before) ...
        echo "Updating Frontend Uptime Check for environment: ${{ env.ENVIRONMENT }}"
        echo "Monitoring URL: $VERCEL_URL_TO_MONITOR"
        HOSTNAME=$(echo "$VERCEL_URL_TO_MONITOR" | sed 's|https://||' | cut -d/ -f1)
        echo "Extracted hostname: $HOSTNAME"

        echo "Updating Uptime Check: projects/$GCP_PROJECT_ID_FOR_MONITOR/uptimeCheckConfigs/$UPTIME_CHECK_ID_FOR_MONITOR to monitor $HOSTNAME"

        gcloud beta monitoring uptime update "projects/$GCP_PROJECT_ID_FOR_MONITOR/uptimeCheckConfigs/$UPTIME_CHECK_ID_FOR_MONITOR" \
          --project="$GCP_PROJECT_ID_FOR_MONITOR" \
          --hostname="$HOSTNAME" \
          --path="/" \
          --port="443" \
          --use-ssl \
          --format="value(name)"

        echo "GCP Frontend Uptime Check updated successfully."
    ```

---

**Step 4: Test the Workflow**

1.  Commit and push the Terraform changes to your `develop` and `main` branches. Run `scripts/gcp_apply.sh` for each to create the monitoring resources.
2.  Verify the `frontend_uptime_check_id` output and update your GitHub secrets accordingly.
3.  Commit and push the `.github/workflows/deploy_backend.yml` changes.
4.  Make a small change to your backend code (e.g., in the `CI Tests & Deployment` workflow trigger path or a backend file) and push to `develop`.
    - This should trigger `CI Tests & Deployment`.
    - Upon its successful completion, the `Deploy Backend and Update Frontend Monitor` workflow should run.
    - Observe the GitHub Actions logs for the "Get Latest Vercel Deployment URL" and "Update GCP Frontend Uptime Check" steps.
    - Check GCP Cloud Monitoring to see if the "Host" for your frontend uptime check has been updated to the new Vercel preview URL.
5.  Repeat for the `main` branch by merging `develop` into `main` (or making a direct push if that's your flow). Verify the production uptime check is updated with your production Vercel URL.

---

**Important Considerations for Vercel URL Fetching:**

- **`vercel ls` Reliability:** The `vercel ls ... | awk 'NR==2{print $1}'` command assumes a certain output format. If Vercel CLI changes its `ls` output, this might break. Using `vercel inspect $(vercel ...)` is more robust as `inspect` provides JSON.
- **Timing:** There might be a slight delay between when Vercel finishes its deployment and when the `vercel ls` or `vercel inspect` commands can find the _latest ready_ deployment for that specific commit. The example above tries to filter by `githubCommitSha` and `githubCommitRef` and `READY` state, which should be quite reliable.
- **Production URL vs. Preview URL:** The logic in the `Get Latest Vercel Deployment URL` step attempts to differentiate:
  - For `main` branch, it tries to find the aliased production URL first.
  - For `develop` (or other preview branches), it uses the unique deployment URL (e.g., `my-app-git-develop-my-org.vercel.app` or `my-app-asdf123.vercel.app`). This is generally what you want to monitor for previews.
- **Error Handling in Script:** The shell script in the GitHub Action has basic error checking (e.g., `if [[ -z "$DEPLOY_URL" ... ]]`). You might want to enhance this if you encounter issues.

This detailed plan should guide you through setting up the automated frontend health monitoring. Remember to test each step thoroughly!
