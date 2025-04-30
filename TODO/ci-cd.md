Okay, let's create that step-by-step plan for Phase 5 (CI/CD Setup & Deployment), building upon the infrastructure established in Phase 2.

This plan assumes you are using GitHub Actions for CI/CD. The principles are transferable to other platforms (GitLab CI, Jenkins, etc.), but commands might differ.

**Phase 5: Full CI/CD Setup & Deployment**

- **Goal:** Automate building, testing, and deploying the backend API (VM), backend worker (Cloud Run), and frontend (Vercel) onto the Terraform-managed infrastructure for `dev` (on `develop` branch activity) and `prod` (on `main` branch activity).
- **Prerequisites:**

  - Phase 2 completed (GCP infrastructure provisioned via Terraform for `dev` and `prod`).
  - Secrets populated in GCP Secret Manager for both environments (via `gcp_populate_secrets.sh`).
  - Backend API `Dockerfile` exists (for the VM).
  - Backend Worker `Dockerfile.worker` exists.
  - Frontend `Dockerfile` exists (if building frontend via Docker for Vercel, though often Vercel builds directly).
  - Vercel project linked to your Git repository.
  - CI/CD Service Account created (e.g., via Terraform in Phase 2 or manually) with necessary IAM permissions (Artifact Registry Writer, Cloud Run Admin, Compute Instance Admin - _scope these carefully!_).
  - Workload Identity Federation configured between GitHub Actions and your GCP Service Account OR a Service Account Key generated and stored securely in GitHub Secrets (Workload Identity is preferred).

- **Branch:** This involves creating/modifying workflow files, typically done on `develop` first, tested, and then merged to `main`.

---

**Step 5.1: Verify/Update Terraform Outputs**

- **Action:** Ensure `terraform/outputs.tf` includes all necessary values for the CI/CD pipeline.
- **Needed Outputs (Examples):**
  - `api_igm_name` (Name of the Managed Instance Group for the API)
  - `api_igm_zone` (Zone of the API IGM)
  - `worker_service_name` (Name of the Cloud Run worker service)
  - `worker_service_region` (Region of the Cloud Run worker service)
  - `artifact_registry_repository_url` (Full URL of the Docker repo)
  - `dev_project_id` (Output specifically the Dev Project ID)
  - `prod_project_id` (Output specifically the Prod Project ID)
- **How CI/CD Gets Outputs:** The CD pipeline will typically need a way to _read_ these outputs after a Terraform apply. Options:
  - Have a CI step that runs `terraform output -json` after apply and stores the result as an artifact.
  - Use predictable naming conventions in Terraform so the CD script can construct the names (e.g., `${var.naming_prefix}-api-igm-${var.environment}`). This is often simpler.

**Step 5.2: Create Backend API Dockerfile (`backend/Dockerfile`)**

- **Goal:** Define how to build the FastAPI application container.
- **File:** `backend/Dockerfile`

  ```dockerfile
  # Use an official Python runtime as a parent image
  FROM python:3.11-slim as builder

  WORKDIR /app

  # Install uv
  RUN pip install uv

  # Install build dependencies (if any) separately first
  # COPY pyproject.toml pyproject.toml
  # RUN uv pip install --system --no-cache --requirement pyproject.toml # Example

  # Install application dependencies
  COPY pyproject.toml pyproject.toml
  COPY README.md README.md # Often needed if included in package
  COPY app /app/app # Copy application code
  # Install dependencies, including the app itself in editable mode if needed for discovery
  RUN uv pip install --system --no-cache -e .[dev] # Or just '.[dev]' if not separating build/runtime

  # Runtime stage
  FROM python:3.11-slim

  WORKDIR /app

  # Copy installed dependencies from the builder stage
  COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
  COPY --from=builder /usr/local/bin /usr/local/bin

  # Copy application code
  COPY app /app/app
  COPY run.py /app/run.py # Assuming run.py is at backend root

  # Expose the port the app runs on
  EXPOSE 8000

  # Command to run the application using Uvicorn (as used locally)
  # Use 0.0.0.0 to listen on all interfaces within the container
  CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```

  _(Adjust paths and dependencies as needed. Consider multi-stage builds for smaller final images)._

**Step 5.3: Verify/Create Backend Worker Dockerfile (`backend/Dockerfile.worker`)**

- _(Verify the file created in Phase 3, Step 5)_

  ```dockerfile
  # backend/Dockerfile.worker
  FROM python:3.11-slim

  WORKDIR /app

  # Copy only worker requirements and code
  COPY cloud_run/worker/requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt

  COPY cloud_run/worker /app/cloud_run/worker

  # Define how to run the worker (depends on your main.py logic)
  # If it's a script that runs and exits:
  # CMD ["python", "cloud_run/worker/main.py"]
  # If it's a long-running process that listens (less common for simple Cloud Run triggers):
  # CMD ["python", "-u", "cloud_run/worker/main.py"] # -u for unbuffered output
  ```

**Step 5.4: Configure CI Pipeline (`.github/workflows/ci.yml`)**

- **Goal:** Build, test, and push Docker images on pushes/PRs to `develop`/`main`.
- **File:** `.github/workflows/ci.yml`

  ```yaml
  name: CI Pipeline

  on:
    push:
      branches: [develop, main]
    pull_request:
      branches: [develop, main]

  jobs:
    lint-test:
      name: Lint & Test
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v4
        # Add steps for Python setup, uv install, pre-commit checks
        - name: Set up Python 3.11
          uses: actions/setup-python@v5
          with: { python-version: "3.11" }
        - name: Install uv
          run: pip install uv
        - name: Install pre-commit
          run: pip install pre-commit
        - name: Run pre-commit hooks (linting, formatting)
          run: pre-commit run --all-files
        # Add Backend Tests (using uv run pytest)
        - name: Run Backend Tests
          run: cd backend && uv run pytest tests/
          env: # Set test env vars
            CONCEPT_SUPABASE_URL: ${{ secrets.DEV_SUPABASE_URL }} # Example: Use DEV secrets for CI tests
            # ... other test env vars ...
        # Add Frontend Tests (npm test)
        - name: Run Frontend Tests
          run: cd frontend/my-app && npm ci && npm test

    build-push-images:
      name: Build & Push Docker Images
      needs: lint-test # Run only if tests pass
      runs-on: ubuntu-latest
      if: github.event_name == 'push' # Only push on direct pushes to develop/main
      permissions:
        contents: read
        id-token: write # Needed for Workload Identity Federation

      steps:
        - uses: actions/checkout@v4

        - name: Authenticate to Google Cloud
          uses: google-github-actions/auth@v2
          with:
            workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }} # e.g., projects/123/locations/global/workloadIdentityPools/my-pool/providers/my-provider
            service_account: ${{ secrets.GCP_CICD_SERVICE_ACCOUNT_EMAIL }} # e.g., cicd-runner@my-project.iam.gserviceaccount.com

        - name: Set up Docker Buildx
          uses: docker/setup-buildx-action@v3

        - name: Configure Docker for Artifact Registry
          run: gcloud auth configure-docker ${{ secrets.GCP_REGION }}-docker.pkg.dev --quiet

        # Determine Environment (dev/prod) based on branch
        - name: Set Environment Name
          id: set_env
          run: |
            if [[ "${{ github.ref_name }}" == "develop" ]]; then
              echo "ENVIRONMENT=dev" >> $GITHUB_ENV
              echo "GCP_PROJECT_ID=${{ secrets.DEV_GCP_PROJECT_ID }}" >> $GITHUB_ENV
            elif [[ "${{ github.ref_name }}" == "main" ]]; then
              echo "ENVIRONMENT=prod" >> $GITHUB_ENV
              echo "GCP_PROJECT_ID=${{ secrets.PROD_GCP_PROJECT_ID }}" >> $GITHUB_ENV
            else
              echo "Unknown branch for image tagging: ${{ github.ref_name }}"
              exit 1
            fi

        # Build and Push API Image
        - name: Build and Push API Image
          uses: docker/build-push-action@v5
          with:
            context: ./backend # Build from backend directory
            file: ./backend/Dockerfile
            push: true
            tags: |
              ${{ secrets.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ secrets.ARTIFACT_REGISTRY_REPO_NAME }}/concept-api-${{ env.ENVIRONMENT }}:${{ github.sha }}
              ${{ secrets.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ secrets.ARTIFACT_REGISTRY_REPO_NAME }}/concept-api-${{ env.ENVIRONMENT }}:latest
            cache-from: type=gha
            cache-to: type=gha,mode=max

        # Build and Push Worker Image
        - name: Build and Push Worker Image
          uses: docker/build-push-action@v5
          with:
            context: ./backend # Build from backend directory
            file: ./backend/Dockerfile.worker
            push: true
            tags: |
              ${{ secrets.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ secrets.ARTIFACT_REGISTRY_REPO_NAME }}/concept-worker-${{ env.ENVIRONMENT }}:${{ github.sha }}
              ${{ secrets.GCP_REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ secrets.ARTIFACT_REGISTRY_REPO_NAME }}/concept-worker-${{ env.ENVIRONMENT }}:latest
            cache-from: type=gha
            cache-to: type=gha,mode=max
  # --- Add GitHub Secrets ---
  # In your GitHub repo settings -> Secrets and variables -> Actions, add:
  # GCP_WORKLOAD_IDENTITY_PROVIDER: Full path from GCP WIF Pool
  # GCP_CICD_SERVICE_ACCOUNT_EMAIL: Email of the SA for CI/CD
  # GCP_REGION: e.g., us-central1
  # DEV_GCP_PROJECT_ID: Your dev project ID
  # PROD_GCP_PROJECT_ID: Your prod project ID
  # ARTIFACT_REGISTRY_REPO_NAME: The name (not full URL) of your repo (e.g., concept-viz-dev-docker-repo)
  # DEV_SUPABASE_URL, DEV_SUPABASE_KEY etc. (for running tests if needed)
  ```

**Step 5.5: Configure Backend CD Pipeline (`.github/workflows/deploy_backend.yml`)**

- **Goal:** Deploy backend API (VM) and worker (Cloud Run) when code is pushed to `develop` or `main`.
- **File:** `.github/workflows/deploy_backend.yml`

  ```yaml
  name: Deploy Backend

  on:
    push:
      branches: [develop, main]
      paths: # Only trigger if backend code changes
        - "backend/**"
        - ".github/workflows/deploy_backend.yml"

  jobs:
    deploy:
      name: Deploy to GCP
      runs-on: ubuntu-latest
      permissions:
        contents: read
        id-token: write # For Workload Identity Federation

      steps:
        - uses: actions/checkout@v4

        - name: Authenticate to Google Cloud
          uses: google-github-actions/auth@v2
          with:
            workload_identity_provider: ${{ secrets.GCP_WORKLOAD_IDENTITY_PROVIDER }}
            service_account: ${{ secrets.GCP_CICD_SERVICE_ACCOUNT_EMAIL }}

        - name: Set Environment Specifics
          id: set_env
          run: |
            if [[ "${{ github.ref_name }}" == "develop" ]]; then
              echo "ENVIRONMENT=dev" >> $GITHUB_ENV
              echo "GCP_PROJECT_ID=${{ secrets.DEV_GCP_PROJECT_ID }}" >> $GITHUB_ENV
              echo "GCP_ZONE=${{ secrets.DEV_GCP_ZONE }}" >> $GITHUB_ENV # e.g., us-central1-a
              echo "NAMING_PREFIX=${{ secrets.DEV_NAMING_PREFIX }}" >> $GITHUB_ENV # e.g., concept-viz-dev
            elif [[ "${{ github.ref_name }}" == "main" ]]; then
              echo "ENVIRONMENT=prod" >> $GITHUB_ENV
              echo "GCP_PROJECT_ID=${{ secrets.PROD_GCP_PROJECT_ID }}" >> $GITHUB_ENV
              echo "GCP_ZONE=${{ secrets.PROD_GCP_ZONE }}" >> $GITHUB_ENV # e.g., us-east1-b
              echo "NAMING_PREFIX=${{ secrets.PROD_NAMING_PREFIX }}" >> $GITHUB_ENV # e.g., concept-viz-prod
            else
              echo "Branch is not develop or main, skipping deployment."
              exit 0 # Exit successfully, don't fail
            fi
            echo "REGION=${{ secrets.GCP_REGION }}" >> $GITHUB_ENV # Assuming region is same or passed as secret

        - name: Deploy Cloud Run Worker
          run: |
            IMAGE_URL="${{ env.REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ secrets.ARTIFACT_REGISTRY_REPO_NAME }}/concept-worker-${{ env.ENVIRONMENT }}:${{ github.sha }}"
            SERVICE_NAME="${{ env.NAMING_PREFIX }}-worker-${{ env.ENVIRONMENT }}"
            gcloud run deploy "$SERVICE_NAME" \
              --image="$IMAGE_URL" \
              --region="${{ env.REGION }}" \
              --project="${{ env.GCP_PROJECT_ID }}" \
              --quiet # Add --platform=managed if needed

        - name: Deploy API to Compute Engine MIG (Rolling Update)
          run: |
            IMAGE_URL="${{ env.REGION }}-docker.pkg.dev/${{ env.GCP_PROJECT_ID }}/${{ secrets.ARTIFACT_REGISTRY_REPO_NAME }}/concept-api-${{ env.ENVIRONMENT }}:${{ github.sha }}"
            TEMPLATE_NAME="${{ env.NAMING_PREFIX }}-api-tpl-${{ env.ENVIRONMENT }}-${{ github.sha }}" # Unique name for new template version
            SOURCE_TEMPLATE_NAME=$(gcloud compute instance-templates list --project="${{ env.GCP_PROJECT_ID }}" --filter="name~'^${{ env.NAMING_PREFIX }}-api-tpl-${{ env.ENVIRONMENT }}'" --sort-by=~creationTimestamp --limit=1 --format='value(name)')
            MIG_NAME="${{ env.NAMING_PREFIX }}-api-igm-${{ env.ENVIRONMENT }}"

            echo "Source Template: $SOURCE_TEMPLATE_NAME"
            echo "New Template Name: $TEMPLATE_NAME"
            echo "MIG Name: $MIG_NAME"
            echo "New Image: $IMAGE_URL"

            # 1. Create a new instance template based on the latest one, but with the new image
            gcloud compute instance-templates create "$TEMPLATE_NAME" \
              --project="${{ env.GCP_PROJECT_ID }}" \
              --source-instance-template="$SOURCE_TEMPLATE_NAME" \
              --source-instance-template-zone="${{ env.GCP_ZONE }}" \
              --metadata=docker-image="$IMAGE_URL" # Example: Assuming startup script reads this metadata key
              # Alternatively, use --container-image if template uses direct container spec

            # 2. Start a rolling update on the Managed Instance Group
            gcloud compute instance-groups managed rolling-action start-update "$MIG_NAME" \
              --version=template="$TEMPLATE_NAME" \
              --zone="${{ env.GCP_ZONE }}" \
              --project="${{ env.GCP_PROJECT_ID }}" \
              --max-surge=1 \
              --max-unavailable=0 # Example rolling update config

  # --- Add GitHub Secrets ---
  # DEV_GCP_ZONE: e.g., us-central1-a
  # PROD_GCP_ZONE: e.g., us-east1-b
  # DEV_NAMING_PREFIX: e.g., concept-viz-dev
  # PROD_NAMING_PREFIX: e.g., concept-viz-prod
  # Plus others needed by CI job (WIF Provider, SA Email, Region, Project IDs, Repo Name)
  ```

  - **Note on VM Deploy:** The `gcloud compute instance-templates create` command assumes you pass the new image URL via metadata (`--metadata=docker-image=...`). Your `startup-api.sh` script needs to be updated to read this metadata key (`docker-image`) instead of constructing the URL itself, to ensure it pulls the _specific_ image deployed by the pipeline. Alternatively, if your instance template directly specifies a container (`--container-image`), you update that flag instead of using metadata.

**Step 5.6: Configure Frontend CD (Vercel)**

1.  **Connect Repository:** In your Vercel dashboard, connect the project to your GitHub repository.
2.  **Build Settings:** Configure the Root Directory (`frontend/my-app`), Build Command (`npm run build` or similar), Output Directory (`dist`).
3.  **Environment Variables:**
    - Go to Project Settings -> Environment Variables.
    - Add variables like `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, etc.
    - For **each variable**, set **different values** for the **Production** environment (linked to `main` branch) and **Preview** environments (linked to `develop` and potentially feature branches). Production should point to your production API endpoint (VM IP or Load Balancer), dev should point to your dev API endpoint. Use the correct Supabase anon keys for each.
4.  **Deploy Hooks (Optional):** Configure Vercel deploy hooks if you need to trigger other actions upon frontend deployment.
5.  **Push Code:** Pushing to `develop` or `main` should now automatically trigger Vercel builds and deployments.

**Step 5.7: Testing and Verification**

1.  Push changes to `develop`. Verify CI passes and backend/frontend deploy successfully to the `dev` environment. Test the application functionality.
2.  Merge `develop` into `main`. Verify CI passes and backend/frontend deploy successfully to the `prod` environment. Test critical paths in production.

---

This comprehensive plan covers the necessary steps for automating your build, test, and deployment processes across GCP and Vercel, integrating with the infrastructure established in Phase 2. Remember to carefully manage secrets and permissions in your CI/CD environment.
