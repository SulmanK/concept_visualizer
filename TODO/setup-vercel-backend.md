Okay, let's break down the process of deploying your Concept Visualizer application, focusing on getting the `develop` branch working first, and then planning for `main`.

**Understanding Your Current Setup:**

- **Backend:** FastAPI app running in Docker containers on GCP Compute Engine VMs, managed by an Instance Group Manager (IGM). Deployed via GitHub Actions using Terraform. Secrets are managed by GCP Secret Manager. A Cloud Function handles background tasks.
- **Frontend:** React/Vite app in `frontend/my-app`. You want to deploy this to Vercel.
- **CI/CD:** GitHub Actions handle tests, linting, Docker builds, and backend deployment.
- **Environments:** Separate `dev` (from `develop` branch) and `prod` (from `main` branch) configurations managed via Terraform workspaces and GitHub Secrets.

**Goal:** Deploy the frontend from the `develop` branch to Vercel and connect it to the backend API running on GCP for the `dev` environment.

---

**Design Plan: Deploying `develop` Branch**

**Phase 1: Backend Verification & Access**

1.  **Confirm Backend Deployment:**

    - Ensure your `develop` branch CI/CD pipeline (`ci-tests.yml` and `deploy_backend.yml`) is successfully building the Docker image and updating the GCP Compute Engine Instance Group Manager (`concept-viz-dev-api-igm-dev`) and the Cloud Function (`concept-viz-dev-worker-dev`).
    - Verify the relevant GitHub Actions runs are completing without errors after pushes to `develop`.

2.  **Determine Backend API Endpoint (Develop):**
    - **Problem:** Your Terraform setup (`compute.tf`) currently only assigns a static IP for the `prod` environment. The VMs in the `dev` IGM likely have ephemeral public IPs. This makes pointing the frontend difficult as the IP can change.
    - **Solution Options:**
      - **(Recommended for Dev Stability):** Modify `terraform/compute.tf` to also create a static IP for the `dev` environment (`google_compute_address`, similar to the `prod` one but perhaps using `network_tier = "STANDARD"`) and assign it in the `google_compute_instance_template`'s `access_config`. Apply this change via `scripts/gcp_apply.sh` on the `develop` branch.
      - **(Alternative - Less Stable):** Manually find the current public IP of one of the running VMs in the `concept-viz-dev-api-igm-dev` group using the GCP console or `gcloud compute instances list --filter="name~'concept-viz-dev-api-vm-dev'"` and `gcloud compute instances describe <INSTANCE_NAME> --zone=<YOUR_DEV_ZONE> --format='get(networkInterfaces[0].accessConfigs[0].natIP)'`. _Use this IP temporarily, knowing it might change if the VM is recreated._
      - **(Better Long-Term Dev):** Set up a simple GCP HTTP(S) Load Balancer pointing to your `dev` IGM. This gives you a stable IP/hostname for the dev backend. This involves adding more resources to `terraform/`.
    - **Action:** Choose one of the solutions. For this plan, let's assume you implement the **Recommended** option and get a static IP for `dev`. Let's call this `DEV_BACKEND_STATIC_IP`. You can get this value from `terraform output api_vm_external_ip` after applying the change.

**Phase 2: Frontend Deployment (Vercel)**

3.  **Connect GitHub Repo to Vercel:**

    - Go to your Vercel dashboard.
    - Create a "New Project".
    - Import your GitHub repository (`your-github-username/concept_visualizer`).
    - Vercel should automatically detect the framework (likely Vite or Create React App).

4.  **Configure Vercel Project Settings:**

    - **Framework Preset:** Ensure it's set correctly (e.g., Vite).
    - **Root Directory:** Set this to `frontend/my-app`.
    - **Build Command:** Default is likely `npm run build` or `vite build`. Verify this matches your `package.json`.
    - **Output Directory:** Set this to `dist` (the default for Vite/CRA builds).
    - **Install Command:** Default is likely `npm install`. Verify this is correct.

5.  **Configure Vercel Environment Variables (for `develop` branch):**

    - In your Vercel project settings, go to "Environment Variables".
    - Add the following variables, selecting only the "Development" environment (Vercel often maps this to non-production branches like `develop`):
      - `VITE_API_URL`: Set this to `http://<DEV_BACKEND_STATIC_IP>/api` (Replace `<DEV_BACKEND_STATIC_IP>` with the actual static IP you obtained/configured in Step 2. Note the `/api` suffix based on your backend router setup). _Initially use HTTP. HTTPS requires a Load Balancer and certificate on the backend._
      - `VITE_SUPABASE_URL`: Get the value from your `DEV_SUPABASE_URL` GitHub Secret.
      - `VITE_SUPABASE_ANON_KEY`: Get the value from your `DEV_SUPABASE_ANON_KEY` GitHub Secret.
      - `VITE_ENVIRONMENT`: Set this to `development`.

6.  **Configure Vercel Production Branch:**
    - In Vercel project settings under "Git", ensure the "Production Branch" is set to `main`. This means pushes to `develop` will create preview deployments.

**Phase 3: Connecting Frontend and Backend**

7.  **Update Backend CORS Configuration (Develop):**

    - Vercel preview deployments have URLs like `project-name-git-develop-account.vercel.app`. You need to allow requests from this origin.
    - **Action:** Update the `CONCEPT_CORS_ORIGINS` environment variable for your _backend_ `dev` environment. You can either:
      - Update the `backend/.env.develop` file and ensure it's loaded when the backend starts.
      - **(Better for Cloud):** Store the CORS origins list in GCP Secret Manager (e.g., `${NAMING_PREFIX}-cors-origins-${ENVIRONMENT}`) and load it in your backend application startup (`backend/app/core/factory.py`). Modify `terraform/secrets.tf` and `scripts/gcp_populate_secrets.sh` accordingly.
    - The allowed origins list for `dev` should include `http://localhost:5173` (local dev) and your Vercel preview URL pattern (e.g., `https://*.vercel.app` or a more specific pattern if possible).
    - Push this backend configuration change to the `develop` branch. This will trigger a backend redeployment via GitHub Actions.

8.  **Trigger Vercel Deployment:**

    - Push a commit to your `develop` branch in GitHub.
    - Vercel should automatically detect the push and start building/deploying a preview deployment.
    - Monitor the deployment logs in the Vercel dashboard.

9.  **Test the Connection:**

    - Access the Vercel preview URL provided after deployment.
    - Open your browser's Developer Tools (Network tab and Console).
    - Navigate through your frontend application and perform actions that trigger API calls (e.g., generating a concept).
    - **Check Network Tab:** Verify requests are going to the correct `DEV_BACKEND_STATIC_IP/api/...` endpoint. Check the status codes (should be 2xx, not 4xx/5xx). Look for CORS errors (often indicated by failed OPTIONS requests or specific console errors).
    - **Check Console Tab:** Look for JavaScript errors, especially related to network requests or CORS.
    - **Check Backend Logs:** If possible, check the logs of your backend VMs/containers on GCP to see if requests are being received and processed, or if there are errors there.

10. **Iterate and Debug:**
    - If CORS errors occur, double-check the `CONCEPT_CORS_ORIGINS` on the backend and the Vercel URL. Ensure the backend deployment with the updated CORS settings completed successfully.
    - If network errors occur (e.g., connection refused, timeout), verify the `DEV_BACKEND_STATIC_IP` is correct and reachable. Check GCP firewall rules (ports 80/443 should be open to `0.0.0.0/0` or Vercel's IP ranges if known).
    - If `VITE_API_URL` issues persist, ensure it includes the `/api` suffix and the correct protocol (HTTP initially).

---

**Plan for `main` Branch (Production)**

Once the `develop` branch deployment is working correctly:

1.  **Backend Static IP:** Confirm the static IP is correctly assigned to your `prod` IGM via Terraform (`google_compute_address.api_static_ip`). Get this IP using `terraform output api_vm_external_ip` (after applying the `prod` workspace). Let's call it `PROD_BACKEND_STATIC_IP`.
2.  **Vercel Environment Variables (Production):**
    - In Vercel, add environment variables specifically for the "Production" environment (linked to your `main` branch).
    - `VITE_API_URL`: Set to `https://<PROD_BACKEND_STATIC_IP>/api` (Ideally use HTTPS). If you don't have HTTPS setup on the backend (e.g., via a Load Balancer), use `http://`.
    - `VITE_SUPABASE_URL`: Use `PROD_SUPABASE_URL` secret value.
    - `VITE_SUPABASE_ANON_KEY`: Use `PROD_SUPABASE_ANON_KEY` secret value.
    - `VITE_ENVIRONMENT`: Set to `production`.
3.  **Backend CORS Configuration (Production):**
    - Update the `CONCEPT_CORS_ORIGINS` for your _backend_ `prod` environment to include your production frontend domain (e.g., `https://yourdomain.com`).
    - Push this change to the `main` branch to trigger a production backend deployment.
4.  **Vercel Domain:** Configure your custom domain (if any) in Vercel settings for the `main` branch.
5.  **Deploy:** Merge your working changes from `develop` into `main`. Pushing to `main` will trigger the Vercel production deployment.
6.  **Test:** Thoroughly test the production deployment.

---

**Recommendations & Considerations:**

- **HTTPS:** Strongly recommend setting up an HTTPS Load Balancer in GCP for both `dev` and `prod` environments in front of your IGMs. This provides SSL termination, a stable entry point, and simplifies configuration. Update `VITE_API_URL` to use `https://`.
- **Static IP for Dev:** Using a static IP or Load Balancer for the `dev` backend makes frontend configuration much easier and stable.
- **CORS Management:** Managing CORS origins via environment variables loaded from Secret Manager is more flexible than hardcoding them in `config.py`.
- **Vercel Environment Mapping:** Double-check how Vercel maps GitHub branches (`develop`, `main`) to its environments (Development, Preview, Production) and set variables accordingly.
- **Backend Health Checks:** Ensure your backend has a reliable `/api/health` endpoint that Vercel or GCP Load Balancers can use.

This plan provides a structured approach. Remember to test thoroughly at each stage, especially the connection between the deployed frontend and backend.
