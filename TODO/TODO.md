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
- **Status:** ✅ Completed. Added api_igm_name, api_igm_zone, worker_service_region, and project_id outputs.

**Step 5.2: Create Backend API Dockerfile (`backend/Dockerfile`)**

- **Goal:** Define how to build the FastAPI application container.
- **Status:** ✅ Completed. Created a multi-stage Dockerfile for the API.

**Step 5.3: Verify/Create Backend Worker Dockerfile (`backend/Dockerfile.worker`)**

- **Status:** ✅ Completed. The Dockerfile.worker already existed and looks good.

**Step 5.4: Configure CI Pipeline**

- **Goal:** Build, test, and push Docker images on pushes/PRs to `develop`/`main`.
- **Status:** ✅ Completed. Added build and push functionality to the existing ci-tests.yml workflow file.

**Step 5.5: Configure Backend CD Pipeline (`.github/workflows/deploy_backend.yml`)**

- **Goal:** Deploy backend API (VM) and worker (Cloud Run) when code is pushed to `develop` or `main`.
- **Status:** ✅ Completed. Created deploy_backend.yml workflow file.

**Step 5.6: Configure Frontend CD (Vercel)**

1.  **Connect Repository:** In your Vercel dashboard, connect the project to your GitHub repository.
2.  **Build Settings:** Configure the Root Directory (`frontend/my-app`), Build Command (`npm run build` or similar), Output Directory (`dist`).
3.  **Environment Variables:**
    - Go to Project Settings -> Environment Variables.
    - Add variables like `VITE_API_BASE_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_ANON_KEY`, etc.
    - For **each variable**, set **different values** for the **Production** environment (linked to `main` branch) and **Preview** environments (linked to `develop` and potentially feature branches). Production should point to your production API endpoint (VM IP or Load Balancer), dev should point to your dev API endpoint. Use the correct Supabase anon keys for each.
4.  **Deploy Hooks (Optional):** Configure Vercel deploy hooks if you need to trigger other actions upon frontend deployment.
5.  **Push Code:** Pushing to `develop` or `main` should now automatically trigger Vercel builds and deployments.

- **Status:** 🔄 In Progress. Set up Vercel dashboard for the project.

**Step 5.7: Testing and Verification**

1.  Push changes to `develop`. Verify CI passes and backend/frontend deploy successfully to the `dev` environment. Test the application functionality.
2.  Merge `develop` into `main`. Verify CI passes and backend/frontend deploy successfully to the `prod` environment. Test critical paths in production.

- **Status:** 🔄 To Do. After completing Step 5.6, test the CI/CD pipelines.

**Step 5.8: Add GitHub Secrets Documentation**

- **Goal:** Document all the required GitHub secrets for the CI/CD pipelines.
- **Status:** ✅ Completed. Created .github/SECRETS.md with all required secrets.

---

This comprehensive plan covers the necessary steps for automating your build, test, and deployment processes across GCP and Vercel, integrating with the infrastructure established in Phase 2. Remember to carefully manage secrets and permissions in your CI/CD environment.
