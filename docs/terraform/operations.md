# Terraform Operations Guide

This guide covers common operational tasks for managing the Concept Visualizer infrastructure on Google Cloud Platform (GCP).

## Common Operations

### Checking Infrastructure Status

To check the current state of your infrastructure:

```bash
cd terraform
terraform workspace select dev  # or prod
terraform plan
```

A properly deployed infrastructure should show "No changes. Your infrastructure matches the configuration."

### Applying Infrastructure Updates

When making changes to the Terraform configuration:

```bash
# Use the helper script for a complete deployment
./scripts/gcp_apply.sh

# Or for manual control:
cd terraform
terraform workspace select dev  # or prod
terraform plan -var-file="environments/dev.tfvars" -out=tfplan
terraform apply tfplan
```

### Updating API VM Software

To update the API application:

1. Build and push a new Docker image:

```bash
cd backend
docker build -t REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/concept-api-ENV:latest .
docker push REGION-docker.pkg.dev/PROJECT_ID/REPO_NAME/concept-api-ENV:latest
```

2. Restart the VM instances to pick up the new image:

```bash
# Get the instance group name
INSTANCE_GROUP=$(terraform -chdir=terraform output -raw api_igm_name)
ZONE=$(terraform -chdir=terraform output -raw api_igm_zone)
PROJECT_ID=$(terraform -chdir=terraform output -raw project_id)

# Restart the instance group
gcloud compute instance-groups managed rolling-action restart $INSTANCE_GROUP \
  --zone=$ZONE \
  --project=$PROJECT_ID
```

### Updating Worker (Cloud Function)

To update the worker code:

1. Make your changes to the worker code
2. Run the infrastructure apply script which will:
   - Build the new Docker image for the worker
   - Update the Cloud Function to use the new image

```bash
./scripts/gcp_apply.sh
```

### Managing Secrets

To update secrets in Secret Manager:

```bash
# Update a specific secret
gcloud secrets versions add SECRET_NAME \
  --data-file=/path/to/secret/file \
  --project=PROJECT_ID
```

Or use the helper script to update all secrets:

```bash
./scripts/gcp_populate_secrets.sh
```

### Scaling Resources

To adjust scaling parameters:

1. Edit the environment-specific `.tfvars` file:

```bash
nano terraform/environments/dev.tfvars  # or prod.tfvars
```

2. Update the scaling parameters:

   - `api_min_instances`
   - `api_max_instances`
   - `worker_min_instances`
   - `worker_max_instances`

3. Apply the changes:

```bash
./scripts/gcp_apply.sh
```

## Monitoring Operations

### Checking Infrastructure Health

Monitor your infrastructure using Cloud Monitoring dashboards:

```bash
# Open Cloud Monitoring dashboard
PROJECT_ID=$(terraform -chdir=terraform output -raw project_id)
open "https://console.cloud.google.com/monitoring/dashboards?project=$PROJECT_ID"
```

### Viewing Logs

Check logs for the various components:

```bash
# API VM logs
gcloud logging read "resource.type=gce_instance AND resource.labels.instance_id=INSTANCE_ID" \
  --project=PROJECT_ID \
  --limit=10

# Cloud Function logs
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=FUNCTION_NAME" \
  --project=PROJECT_ID \
  --limit=10

# Pub/Sub logs
gcloud logging read "resource.type=pubsub_topic AND resource.labels.topic_id=TOPIC_ID" \
  --project=PROJECT_ID \
  --limit=10
```

### Alert Management

Check and manage alert notifications:

```bash
# List alert policies
gcloud alpha monitoring policies list --project=PROJECT_ID

# Get alert policy details
gcloud alpha monitoring policies describe POLICY_ID --project=PROJECT_ID
```

## Maintenance Operations

### Rotating Credentials

Regularly rotate credentials stored in Secret Manager:

1. Generate new credentials
2. Add the new version to Secret Manager
3. The API and worker will automatically pick up the new credentials on restart

```bash
# Add a new version of a secret
gcloud secrets versions add SECRET_NAME \
  --data-file=/path/to/new/credential \
  --project=PROJECT_ID
```

### Updating VM Startup Scripts

To update VM startup scripts:

1. Modify `terraform/scripts/startup-api.sh`
2. Upload the script to Cloud Storage:

```bash
./scripts/upload_startup_scripts.sh
```

3. Restart the VM instances to use the new startup script:

```bash
# Get instance group details
INSTANCE_GROUP=$(terraform -chdir=terraform output -raw api_igm_name)
ZONE=$(terraform -chdir=terraform output -raw api_igm_zone)
PROJECT_ID=$(terraform -chdir=terraform output -raw project_id)

# Restart the instances
gcloud compute instance-groups managed rolling-action restart $INSTANCE_GROUP \
  --zone=$ZONE \
  --project=$PROJECT_ID
```

### Updating External IP in Vercel Configuration

After recreating the API VM (which might change the external IP):

```bash
# Get the new external IP
API_IP=$(terraform -chdir=terraform output -raw api_vm_external_ip)

# Update the vercel.json file in the frontend directory
sed -i.bak "s|\"destination\": \"http://[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/|\"destination\": \"http://$API_IP/|g" \
  frontend/my-app/vercel.json

# Commit and push the changes
git add frontend/my-app/vercel.json
git commit -m "Update API IP in vercel.json to $API_IP"
git push
```

Note: The `gcp_apply.sh` script now includes this step automatically.

## Backup and Recovery

### State File Backup

Terraform state is automatically versioned in Cloud Storage. To view state file versions:

```bash
gsutil ls -a gs://YOUR_TF_STATE_BUCKET/terraform/state/dev.tfstate
```

To restore a previous state version:

```bash
gsutil cp gs://YOUR_TF_STATE_BUCKET/terraform/state/dev.tfstate#1234567890 \
  gs://YOUR_TF_STATE_BUCKET/terraform/state/dev.tfstate
```

### Infrastructure Backup

Critical infrastructure configuration can be exported:

```bash
# Export service account keys
gcloud iam service-accounts keys list --iam-account=SERVICE_ACCOUNT_EMAIL \
  --project=PROJECT_ID
```

### Infrastructure Recovery

In case of complete infrastructure loss, follow these steps:

1. Ensure the Terraform state bucket exists
2. Run a fresh deployment:

```bash
./scripts/gcp_apply.sh
```

## Troubleshooting

### Common Issues and Solutions

#### Terraform State Lock

If Terraform fails with a state lock error:

```bash
# Get the current terraform state locks
gsutil ls gs://YOUR_TF_STATE_BUCKET/terraform/state/*.tflock

# Remove a stale lock
gsutil rm gs://YOUR_TF_STATE_BUCKET/terraform/state/dev.tflock
```

#### VM Startup Failures

If VMs fail to start properly:

1. Check the VM's serial port output:

```bash
gcloud compute instances get-serial-port-output INSTANCE_NAME \
  --zone=ZONE \
  --project=PROJECT_ID
```

2. Check startup script logs:

```bash
gcloud logging read "resource.type=gce_instance AND logName=projects/PROJECT_ID/logs/startupscript.log" \
  --project=PROJECT_ID
```

#### Cloud Function Errors

If Cloud Functions fail:

```bash
# Check Cloud Function logs
gcloud logging read "resource.type=cloud_function AND resource.labels.function_name=FUNCTION_NAME" \
  --project=PROJECT_ID

# Check the Cloud Function's container image
gcloud functions describe FUNCTION_NAME \
  --gen2 \
  --region=REGION \
  --project=PROJECT_ID
```

## Security Operations

### Checking Service Account Permissions

Review current IAM permissions:

```bash
# List project IAM bindings
gcloud projects get-iam-policy PROJECT_ID --format=json | jq '.bindings[]'

# List service account roles
gcloud projects get-iam-policy PROJECT_ID --format=json | \
  jq '.bindings[] | select(.members[] | contains("serviceAccount:SERVICE_ACCOUNT_EMAIL"))'
```

### Audit Logging

Enable Data Access audit logs:

```bash
gcloud logging sinks create audit-logs \
  storage.googleapis.com/YOUR_AUDIT_BUCKET \
  --log-filter="logName:\"projects/PROJECT_ID/logs/cloudaudit.googleapis.com%2Fdata_access\"" \
  --project=PROJECT_ID
```

## Next Steps

- Review the [Security Overview](security.md) for security considerations
- Check the [Monitoring Guide](monitoring.md) for observability setup
- Explore the [Disaster Recovery Plan](disaster_recovery.md) for business continuity
