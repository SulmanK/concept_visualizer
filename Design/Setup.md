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
      supabase link --project-ref <your-dev-project-id>
      # or
      supabase link --project-ref <your-prod-project-id>
      ```
    - **Set Secrets:** Set the required secrets for the function (replace placeholders):
      ```bash
      # Run from project root (adjust values for dev/prod)
      supabase secrets set MY_SUPABASE_URL=<your-supabase-url>
      supabase secrets set MY_SERVICE_ROLE_KEY=<your-service-role-key>
      supabase secrets set STORAGE_BUCKET_CONCEPT=<your-concept-bucket>
      supabase secrets set STORAGE_BUCKET_PALETTE=<your-palette-bucket>
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
    - Run `gcloud auth login` to authenticate your primary user account.
    - Run `gcloud auth application-default login`.
2.  **Create GCP Projects:** Manually create three separate GCP Projects via the Cloud Console: one for `dev` (e.g., `yourproject-dev`) and one for `prod` (e.g., `yourproject-prod`) and one for managed tf state. Note down their unique Project IDs.
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
      cloudfunctions.googleapis.com
      --project=YOUR_PROJECT_ID_HERE
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
      --project="project-hosting-tfstate-bucket" # Project where bucket lives
    ```

6.  Update tf.vars with your .env variables

7.  Run `scripts/gcp_apply.sh`.

## 6. GitHub Secrets Setup

Configure secrets in your GitHub repository settings ("Settings" > "Secrets and variables" > "Actions") to allow CI/CD workflows to authenticate with GCP.

Required Secrets: (Get values from Terraform outputs and your .env files)

```
# GCP Authentication (Common)
GCP_REGION

# Development Environment
DEV_GCP_PROJECT_ID
DEV_GCP_ZONE
DEV_ARTIFACT_REGISTRY_REPO_NAME # From Terraform output (e.g., concept-viz-dev-docker-repo)
DEV_NAMING_PREFIX
DEV_WORKLOAD_IDENTITY_PROVIDER  # From Terraform output
DEV_CICD_SERVICE_ACCOUNT_EMAIL  # From Terraform output
DEV_WORKER_SERVICE_ACCOUNT_EMAIL # From Terraform output
DEV_API_SERVICE_ACCOUNT_EMAIL    # From Terraform output
DEV_SUPABASE_URL                 # From your .env.develop
DEV_SUPABASE_ANON_KEY            # From your .env.develop (Supabase anon key)
DEV_SUPABASE_SERVICE_ROLE        # From your .env.develop
DEV_SUPABASE_JWT_SECRET          # From your .env.develop
DEV_JIGSAWSTACK_API_KEY          # From your .env.develop
DEV_WORKER_MIN_INSTANCES
DEV_WORKER_MAX_INSTANCES

# Production Environment
PROD_GCP_PROJECT_ID
PROD_GCP_ZONE
PROD_ARTIFACT_REGISTRY_REPO_NAME # From Terraform output (e.g., concept-viz-prod-docker-repo)
PROD_NAMING_PREFIX
PROD_WORKLOAD_IDENTITY_PROVIDER  # From Terraform output
PROD_CICD_SERVICE_ACCOUNT_EMAIL  # From Terraform output
PROD_WORKER_SERVICE_ACCOUNT_EMAIL # From Terraform output
PROD_API_SERVICE_ACCOUNT_EMAIL   # From Terraform output
PROD_SUPABASE_URL                # From your .env.main
PROD_SUPABASE_ANON_KEY           # From your .env.main (Supabase anon key)
PROD_SUPABASE_SERVICE_ROLE       # From your .env.main
PROD_SUPABASE_JWT_SECRET         # From your .env.main
PROD_JIGSAWSTACK_API_KEY         # From your .env.main
PROD_WORKER_MAX_INSTANCES

```

### 7. Vercel Frontend Setup

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

---

### 8. Running Locally

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

### 8. Running Cloud

    - After the backend and frontend is deployed on GCP and Vercel, respectively. Head on over to the project url given by vercel.

### Important: Full Recreations

- If you run `scripts/gcp_destroy.sh` and then `scripts/gcp_apply.sh`, you are **fully recreating** the GCP infrastructure.
- **After a full recreation:**
  - The **External IP Address** of your backend VM will likely change (unless you explicitly reserved it outside Terraform's management, which isn't standard here). You **MUST** update the IP in `frontend/my-app/vercel.json` and redeploy the frontend.
  - Terraform outputs (Service Account emails, WIF provider) might change. You **MUST** update the corresponding **GitHub Secrets**.
  - You likely need to re-run `scripts/gcp_populate_secrets.sh` as the Secret Manager resources were recreated.

Regular deployments via CI/CD (pushing code changes) will typically _not_ require these full update steps, only updating the application code or container image.

# Everytime we recreate our terraform resources

- Populate the secrets in Github
- Poulate the secrets in vercel
- Update the vercel.json (with the new ip)
