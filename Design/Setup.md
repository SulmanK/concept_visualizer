## Project Setup Guide: Concept Visualizer

This guide outlines the steps required to set up the Supabase backend, GCP infrastructure, Vercel frontend deployment, and necessary configurations for the Concept Visualizer project.

---

### 1. Prerequisites: Install Tools

Ensure you have the following command-line tools installed and configured:

- **Git:** For version control.
- **Node.js & npm:** (v18 or later recommended) For frontend development. ([https://nodejs.org/](https://nodejs.org/))
- **Python & uv:** (Python 3.11 recommended) For backend development and dependency management. ([https://www.python.org/](https://www.python.org/), [https://github.com/astral-sh/uv](https://github.com/astral-sh/uv))
- **Google Cloud SDK (`gcloud`):** For interacting with GCP. ([https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install))
  - Authenticate after installation: `gcloud auth login` and `gcloud auth application-default login`.
- **Terraform CLI:** (v1.3 or later recommended) For managing GCP infrastructure. ([https://developer.hashicorp.com/terraform/downloads](https://developer.hashicorp.com/terraform/downloads))
- **Supabase CLI:** For managing Supabase functions and secrets. ([https://supabase.com/docs/guides/cli](https://supabase.com/docs/guides/cli))
  - Log in after installation: `supabase login`.
- **GitHub CLI (`gh`):** (Optional, but required for GitHub secret automation via `gcp_apply.sh`) For interacting with GitHub. ([https://cli.github.com/](https://cli.github.com/))
  - Authenticate after installation: `gh auth login`.

### 2. JigsawStack API Key

- Obtain an API key from [JigsawStack](https://jigsawstack.com/).
- Add this key to your `backend/.env.develop` and `backend/.env.main` files as `CONCEPT_JIGSAWSTACK_API_KEY`.
- Ensure it's populated in GCP Secret Manager via `gcp_populate_secrets.sh`.

### 3. Redis Setup

- This setup assumes you are using [Upstash](https://upstash.com/) or a similar Redis provider.
- Get your Redis endpoint URL (e.g., `relevant-stud-56361.upstash.io`) and password.
- Add these to your `backend/.env.develop` and `backend/.env.main` files as `CONCEPT_UPSTASH_REDIS_ENDPOINT` and `CONCEPT_UPSTASH_REDIS_PASSWORD`.
- Ensure they are populated in GCP Secret Manager via `gcp_populate_secrets.sh`

### 4. Supabase Project Setup (Repeat for Dev & Prod)

You need two Supabase projects: one for development (`dev`) and one for production (`prod`).

1.  **Create Supabase Project:**

    - Go to [supabase.com](https://supabase.com/) and sign in.
    - Click "New Project".
    - Choose an organization.
    - **Name:** e.g., `concept-visualizer-dev` or `concept-visualizer-prod`.
    - **Database Password:** Generate and securely save this password.
    - **Region:** Choose a region (ideally matching your GCP region).
    - **Pricing Plan:** Select the "Free" tier for development.
    - Click "Create new project".

2.  **Get API Keys & URLs:**

    - Navigate to "Project Settings" > "API".
    - **Note down** the following for **both** your `dev` and `prod` projects:
      - Project URL (e.g., `https://[project-id].supabase.co`)
      - `anon` key (public)
      - `service_role` key (**Keep this secure!** Never expose in frontend code).
      - JWT Secret (**Keep this secure!**)

3.  **Configure Authentication:**

    - Go to "Authentication" in the sidebar.
    - Under "Configuration" > "Auth Providers", ensure **Email** is enabled.
    - Under "Configuration" > "Settings", enable **"Allow anonymous sign-ins"**.
    - Under "Configuration" > "URL Configuration":
      - **Site URL:** Set to your frontend's deployed URL (e.g., `http://localhost:5173` for dev, your Vercel URL for prod).
      - **Additional Redirect URLs:** Add any other URLs your app might redirect to after auth (e.g., `http://localhost:5173/**`).

4.  **Create Storage Buckets:**

    - Go to "Storage" in the sidebar.
    - Click "Create a new bucket".
    - Create **two private buckets** (important: start as private):
      - **Name:** `concept-images` (or `concept-images-dev`/`concept-images-prod` if defined differently in your `.tfvars` and backend config).
      - **Name:** `palette-images` (or `palette-images-dev`/`palette-images-prod`).
    - _Note: Access policies (RLS) will be set up later by the SQL script._

5.  **Set Up Database Schema & RLS:**

    - Go to "SQL Editor" in the sidebar.
    - Click "New query".
    - **Execute the SQL script:** Copy the content from the appropriate SQL file (`backend/scripts/dev/pg-bucket-schema-policies.sql` for dev, `backend/scripts/prod/pg-bucket-schema-policies.sql` for prod) and run it. This creates tables (`concepts`, `color_variations`, `tasks`) and sets up Row Level Security policies for both database tables and storage buckets.

6.  **Enable Realtime:**

    - Go to "Database" > "Replication".
    - Under "Source", click on "0 tables".
    - Use the toggle switch to enable replication for the `tasks` table (or `tasks_dev`/`tasks_prod`).

7.  **Deploy Edge Function (Data Cleanup):**
    - **Link Project:** Link your local directory to the correct Supabase project:
      ```bash
      # Run from project root
      cd backend
      supabase link --project-ref <your-dev-project-id>
      # or
      supabase link --project-ref <your-prod-project-id>
      ```
    - **Set Secrets:** Set the required secrets for the function (replace placeholders):
      ```bash
      # Run from project root (adjust values for dev/prod)
      cd backend
      supabase secrets set SUPABASE_URL=<your-supabase-url>
      supabase secrets set SERVICE_ROLE_KEY=<your-service-role-key>
      supabase secrets set STORAGE_BUCKET_CONCEPT=<your-concept-bucket>
      supabase secrets set STORAGE_BUCKET_PALETTE=<your-palette-bucket>
      supabase secrets set APP_ENVIRONMENT=<your-palette-bucket>
      ```
    - **Deploy:** Deploy the function:
      ```bash
      # Run from project root
      supabase functions deploy cleanup-old-data --project-ref <proj_id> --no-verify-jwt
      ```
    - _Note:_ The scheduling of this function is handled via a GitHub Actions workflow (`.github/workflows/schedule-cleanup.yml`).

---

## 5. GCP Setup

1.  **Authenticate `gcloud`:**
    - Swap accounts (if needed) `gcloud config set account ACCOUNT_NAME`
    - Run `gcloud auth login` to authenticate your primary user account.
    - Run `gcloud auth application-default login`.
2.  **Create GCP Projects:** Manually create three separate GCP Projects via the Cloud Console: one for `dev` (e.g., `yourproject-dev`) and one for `prod` (e.g., `yourproject-prod`) and one for managed tf state (`yourproject-managed`). Note down their unique Project IDs.
3.  **Enable APIs:** For **both** the `dev` and `prod` projects, run the following `gcloud` command (replace `YOUR_PROJECT_ID_HERE` accordingly for each project):
    ```bash
    gcloud services enable \
      compute.googleapis.com \
      run.googleapis.com \
      secretmanager.googleapis.com \
      artifactregistry.googleapis.com \
      pubsub.googleapis.com \
      cloudresourcemanager.googleapis.com \
      iam.googleapis.com \
      logging.googleapis.com \
      monitoring.googleapis.com \
      cloudbuild.googleapis.com \
      cloudresourcemanager.googleapis.com \
      eventarc.googleapis.com \
      cloudfunctions.googleapis.com --project=YOUR_PROJECT_ID_HERE
    ```
4.  **Create GCS Bucket for Terraform State (Manual/Bootstrap):**
    - **Action:** Choose **one** GCP project to host the state bucket (e.g., the `managed` project). Manually create a GCS bucket in that project using the Cloud Console or `gcloud`.
    - **Crucially:** **Enable Object Versioning** on this bucket.
    - **Example Name:** `yourproject-tfstate` (Replace with your globally unique name).
    - **Purpose:** Securely store Terraform state files for both `dev` and `prod` workspaces.
5.  **Grant Initial IAM Setter Permission:** Manually grant the identity running the _first_ `terraform apply` (likely your user account) the permission to _set IAM policies on the state bucket_. The `roles/storage.admin` role on the bucket is sufficient initially.

    ```bash
    gcloud storage buckets add-iam-policy-binding gs://yourproject-tfstate \
      --member="user:your-gcp-email@example.com" \
      --role="roles/storage.admin" \
      --project="yourproject-managed" # Project where bucket lives
    ```

6.  Populate environment variable files:
    - `backend/env.main`
    - `backend/env.develop`
    - `terraform/environments/dev.tfvars`
    - `terraform/environments/prod.tfvars`
7.  Initialize Terraform:

    ```bash
    cd terraform
    terraform init -backend-config="bucket=BUCKET_NAME"
    terraform workspace new dev
    terraform workspace new prod

    ```

8.  Remove Terraform Config (if needed)

    ```bash
    cd terraform
    rm -f tfplan tfplan.*
    rm -rf .terraform

    ```

9.  Update tf.vars

### 6. Vercel Frontend Setup

Deploy the frontend application using Vercel.

1.  **Connect GitHub Repo:** Import your GitHub repository into Vercel.
2.  **Configure Project:**
    - **Framework Preset:** Select "Vite".
    - **Root Directory:** Set to `frontend/my-app`.
    - **Build Command:** Should default correctly (`npm run build`).
    - **Output Directory:** Should default correctly (`dist`).
    - **Install Command:** Should default correctly (`npm install`).
3.  **Configure Environment Variables:** In Vercel project settings > "Environment Variables":
    - **Production (for `main` branch):**
      - `VITE_API_BASE_URL`: `/api` (Vercel rewrite handles proxying)
      - `VITE_SUPABASE_URL`: Value from `PROD_SUPABASE_URL` GitHub Secret.
      - `VITE_SUPABASE_ANON_KEY`: Value from `PROD_SUPABASE_ANON_KEY` GitHub Secret.
      - `VITE_ENVIRONMENT`: `production`
    - **Development/Preview (for `develop` branch and PRs):**
      - `VITE_API_BASE_URL`: `/api`
      - `VITE_SUPABASE_URL`: Value from `DEV_SUPABASE_URL` GitHub Secret.
      - `VITE_SUPABASE_ANON_KEY`: Value from `DEV_SUPABASE_ANON_KEY` GitHub Secret.
      - `VITE_ENVIRONMENT`: `development`
4.  **Configure Git:** In Vercel project settings > "Git", ensure "Production Branch" is set to `main`.
5.  **Update `vercel.json`:**
    - Ensure your `frontend/my-app/vercel.json` contains the correct `rewrites` section, **including the SPA fallback rule at the end**.
    - **Crucially, update the `destination` IP address in the API rewrite rules** to match the **External IP** provided by the Terraform output for the respective environment (`dev` or `prod`).
    ```json
    {
      "rewrites": [
        // API rewrites (ensure destination IP is correct)
        {
          "source": "/api/healthz",
          "destination": "http://<YOUR_BACKEND_VM_IP>/api/health/ping" // Replace IP
        },
        {
          "source": "/api/:path*",
          "destination": "http://<YOUR_BACKEND_VM_IP>/api/:path*" // Replace IP
        },
        // SPA Fallback (Must be LAST)
        {
          "source": "/((?!_next/static|static|favicon.ico|vite.svg|assets/).*)",
          "destination": "/index.html"
        }
      ]
    }
    ```
6.  **Deploy:** Trigger a deployment on Vercel (e.g., by pushing to `main` or `develop`).
7.  **Get the Vercel secrets for GitHub:**
    - `VERCEL_ORG_ID`
    - `VERCEL_TOKEN`
    - `PROD_VERCEL_PROJECT_ID`
    - `DEV_VERCEL_PROJECT_ID`

---

## 7. GitHub Secrets Setup

Configure secrets in your GitHub repository settings ("Settings" > "Secrets and variables" > "Actions") to allow CI/CD workflows to authenticate with GCP and other services.

**Automation Note:** The `scripts/gcp_apply.sh` script, upon successful completion, will now automatically attempt to populate many of the necessary GitHub Actions secrets using the `scripts/gh_populate_secrets.sh` helper script. This automation is branch-aware (setting `DEV_*` or `PROD_*` secrets based on the current branch).

**Prerequisite for Automation:** You must have the GitHub CLI (`gh`) installed and authenticated (`gh auth login`) for the automation to work.

### Automatically Populated Secrets (via `scripts/gcp_apply.sh`):

The following secrets will be set by the automation script. Values are sourced from Terraform outputs or active `.tfvars` files.

- **Global:**
  - `GCP_REGION`
- \*\*Environment-Specific (prefixed with `DEV_` or `PROD_`):
  - `GCP_PROJECT_ID`
  - `GCP_ZONE`
  - `NAMING_PREFIX`
  - `API_SERVICE_ACCOUNT_EMAIL`
  - `WORKER_SERVICE_ACCOUNT_EMAIL`
  - `CICD_SERVICE_ACCOUNT_EMAIL`
  - `WORKLOAD_IDENTITY_PROVIDER`
  - `ARTIFACT_REGISTRY_REPO_NAME`
  - `FRONTEND_UPTIME_CHECK_CONFIG_ID`
  - `FRONTEND_ALERT_POLICY_ID`
  - `ALERT_NOTIFICATION_CHANNEL_FULL_ID`
  - `FRONTEND_STARTUP_ALERT_DELAY`
  - `ALERT_ALIGNMENT_PERIOD`
  - `WORKER_MIN_INSTANCES`
  - `WORKER_MAX_INSTANCES`

### Manually Added GitHub Secrets:

These secrets still need to be added manually to your GitHub repository settings. They are typically sensitive, obtained from third-party services, or not directly output by the Terraform configuration in a way suitable for this automation.

- **Global:**
  - `VERCEL_ORG_ID`
  - `VERCEL_TOKEN`
  - `TF_STATE_BUCKET_NAME`
- \*\*Production (prefixed with `PROD_`):
  - `PROD_JIGSAWSTACK_API_KEY`
  - `PROD_SUPABASE_ANON_KEY`
  - `PROD_SUPABASE_JWT_SECRET`
  - `PROD_SUPABASE_SERVICE_ROLE`
  - `PROD_SUPABASE_URL`
  - `PROD_VERCEL_PROJECT_ID`
  - `PROD_UPSTASH_REDIS_ENDPOINT`
  - `PROD_UPSTASH_REDIS_PASSWORD`
  - `PROD_UPSTASH_REDIS_PORT` (optional, defaults to `6379`)
- \*\*Development (prefixed with `DEV_`):
  - `DEV_JIGSAWSTACK_API_KEY`
  - `DEV_SUPABASE_ANON_KEY`
  - `DEV_SUPABASE_JWT_SECRET`
  - `DEV_SUPABASE_SERVICE_ROLE`
  - `DEV_SUPABASE_URL`
  - `DEV_VERCEL_PROJECT_ID`
  - `DEV_UPSTASH_REDIS_ENDPOINT`
  - `DEV_UPSTASH_REDIS_PASSWORD`
  - `DEV_UPSTASH_REDIS_PORT` (optional)

_(The comprehensive list of all secrets and their descriptions can be found in `.github/SECRETS.md` which should align with the above distinction of automated vs. manual.)_

### 8. Run `scripts/gcp_apply.sh`.

### 9. Running Locally

1.  **Backend:**
    ```bash
    cd backend
    # Ensure .env is linked to .env.develop via post-checkout hook
    # (or manually copy: cp .env.develop .env)
    uvicorn app.main:app --reload --port 8000
    ```
2.  **Frontend:**
    ```bash
    cd frontend/my-app
    # Ensure .env is linked to .env.develop via post-checkout hook
    # (or manually copy: cp .env.develop .env)
    npm run dev
    ```
    Access the app at `http://localhost:5173` (or the port Vite uses).

---

### 10. Running Cloud

After the backend and frontend is deployed on GCP and Vercel, respectively. Head on over to the project url given by vercel.

### Important: Full Recreations

- If you run `scripts/gcp_destroy.sh` and then `scripts/gcp_apply.sh`, you are **fully recreating** the GCP infrastructure.
- **After a full recreation:**
  - The **External IP Address** of your backend VM will likely change (unless you explicitly reserved it outside Terraform's management, which isn't standard here). You **MUST** update the IP in `frontend/my-app/vercel.json` and redeploy the frontend.
  - Terraform outputs (Service Account emails, WIF provider) might change. You **MUST** update the corresponding **GitHub Secrets**.
  - You likely need to re-run `scripts/gcp_populate_secrets.sh` as the Secret Manager resources were recreated.

Regular deployments via CI/CD (pushing code changes) will typically _not_ require these full update steps, only updating the application code or container image.
