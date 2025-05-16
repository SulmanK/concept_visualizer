# Post-Implementation Tasks for Monitoring Workflow Update

After merging the PR that updates the frontend monitoring workflow, the following tasks need to be completed to clean up the previous approach and ensure everything is working correctly:

## 1. GCS Bucket Cleanup

Delete the deprecated storage path used for the previous workflow:

```bash
# For dev environment
gsutil -m rm -r gs://${TF_STATE_BUCKET_NAME}/dynamic_frontend_monitoring_ids/dev/

# For prod environment
gsutil -m rm -r gs://${TF_STATE_BUCKET_NAME}/dynamic_frontend_monitoring_ids/prod/

# If the directory is now empty, you can remove it entirely
gsutil -m rm -r gs://${TF_STATE_BUCKET_NAME}/dynamic_frontend_monitoring_ids/
```

## 2. Verify Permissions

Ensure the CI/CD service account has the necessary permissions to manage the Terraform state in GCS. This should typically be covered by the existing IAM configuration in `iam.tf`, but it's good to verify that the account has at least:

- `storage.objects.get`
- `storage.objects.create`
- `storage.objects.update`
- `storage.objects.delete`

On the state bucket/prefix.

## 3. Test the New Workflow

After the PR is merged:

1. Make a small change to the frontend code and push to trigger a deployment
2. Verify that:
   - The frontend is deployed successfully to Vercel
   - The "Apply/Update Frontend Monitoring Resources" workflow step completes successfully
   - The uptime check in GCP Monitoring is updated to point to the newly deployed URL
   - The alert policy remains correctly associated with the uptime check

## 4. Update Documentation

Add a note to project documentation (e.g., `README.md` or a dedicated infrastructure doc) explaining:

````markdown
### Frontend Monitoring

The frontend application is monitored using a GCP Uptime Check that verifies the application is available and serving the expected content. This check is configured by Terraform and automatically updated during the CI/CD deployment process to point to the latest Vercel deployment URL.

Key points:

- The uptime check and alert policy live in the same Terraform workspace as the rest of the infrastructure
- The `frontend_hostname` variable is used during CI/CD to update the monitoring target
- If you need to manually update the monitored URL, you can run:
  ```bash
  terraform apply -var="frontend_hostname=your-app.vercel.app"
  ```
````

````

## 5. Clean Up Any Helper Scripts

If there were any helper scripts specifically created for the previous workflow (e.g., scripts for writing/reading monitoring IDs to/from GCS), they can now be removed.

## 6. Verify Terraform State

Run `terraform state list` to confirm that the frontend monitoring resources are correctly tracked in the Terraform state:

```bash
# Dev environment
terraform -chdir=terraform workspace select dev
terraform -chdir=terraform state list | grep -E "frontend_availability|frontend_.*alert"

# Prod environment
terraform -chdir=terraform workspace select prod
terraform -chdir=terraform state list | grep -E "frontend_availability|frontend_.*alert"
````

You should see at least:

- `google_monitoring_uptime_check_config.frontend_availability`
- `google_monitoring_alert_policy.frontend_availability_failure_alert`
