# Terraform Components Overview

This document provides detailed information about each component in the Concept Visualizer infrastructure deployed using Terraform.

## Infrastructure Components

The infrastructure is organized across several Terraform files, each managing different aspects of the GCP resources:

### Core Infrastructure Components

#### Compute Resources (`compute.tf`)

- **API VM Instance**: Managed instance group running the FastAPI application
  - Uses a custom startup script that:
    - Installs Docker
    - Pulls the API container image from Artifact Registry
    - Configures logging
    - Sets up health checks
  - Automatically scales based on load (minimum and maximum instances configurable)
  - Secured with appropriate firewall rules
  - Configured with service account for accessing secrets and other resources

#### Background Processing (`cloud_function.tf`)

- **Cloud Function (2nd Gen)**: Processes asynchronous tasks
  - Triggered by Pub/Sub messages
  - Runs in a containerized environment
  - Uses service account with minimal permissions
  - Configured with memory and CPU allocations based on workload
  - Auto-scales based on incoming message volume

#### Networking (`network.tf`)

- **VPC Network**: Dedicated network for the application components
- **Firewall Rules**:
  - Allow HTTP/HTTPS traffic to API VM
  - Allow health check traffic from Google Cloud healthcheck ranges
  - Allow SSH access for administration (restricted to specific IP ranges)
- **External IP**: Static IP for the API server

### Storage and Registry

#### Artifact Registry (`artifact_registry.tf`)

- **Docker Repository**: For storing container images
  - Stores API container images
  - Stores worker (Cloud Function) container images
  - Access controlled via IAM

#### Storage Buckets (`storage.tf`)

- **Asset Bucket**: Stores application assets
- **Startup Scripts Bucket**: Stores VM initialization scripts

### Messaging & Integration

#### Pub/Sub (`pubsub.tf`)

- **Topics**:
  - `concept-tasks`: For sending tasks from API to worker
  - `concept-results`: For returning results from worker to API
- **Subscriptions**:
  - Cloud Function subscription for processing tasks
  - Dead letter topics for error handling

### Security & Access Control

#### IAM & Service Accounts (`iam.tf`)

- **Service Accounts**:
  - `api-service-account`: Used by the API VM
  - `worker-service-account`: Used by the Cloud Function worker
  - `cicd-service-account`: For CI/CD pipelines via GitHub Actions
- **Workload Identity Federation**:
  - Allows GitHub Actions to authenticate as a GCP service account
  - Secures CI/CD workflows without using long-lived credentials
- **IAM Roles**:
  - Custom roles with minimal permissions
  - Secret access permissions for secure credential access

#### Secret Management (`secrets.tf`)

- **Secret Manager Secrets**:
  - Database credentials (Supabase)
  - API keys (JigsawStack)
  - Redis credentials
  - JWT secrets
- **Secret Access Control**:
  - Service accounts granted access only to required secrets

### Monitoring & Observability (`monitoring.tf`)

- **Uptime Checks**:
  - Frontend application health monitoring
  - API endpoints monitoring
- **Alert Policies**:
  - Resource utilization alerts
  - Error rate thresholds
  - Uptime check failures
- **Notification Channels**:
  - Email notifications for alerts
  - Integration with monitoring systems

## File Descriptions

| File                   | Description                                      |
| ---------------------- | ------------------------------------------------ |
| `main.tf`              | Provider configuration and backend setup         |
| `variables.tf`         | Input variable definitions with descriptions     |
| `outputs.tf`           | Output values exported from the infrastructure   |
| `compute.tf`           | API VM and instance group configurations         |
| `cloud_function.tf`    | Worker Cloud Function configuration              |
| `network.tf`           | VPC, subnetworks, and firewall configurations    |
| `iam.tf`               | Service accounts and access permissions          |
| `secrets.tf`           | Secret Manager configuration                     |
| `pubsub.tf`            | Pub/Sub topics and subscriptions                 |
| `storage.tf`           | Cloud Storage bucket configurations              |
| `artifact_registry.tf` | Container registry configuration                 |
| `monitoring.tf`        | Uptime checks, alerts, and notification channels |
| `random.tf`            | Random resource generation (for unique naming)   |

## Environment-Specific Configuration

The infrastructure uses Terraform workspaces and environment-specific variable files (`dev.tfvars` and `prod.tfvars`) to manage differences between environments:

| Environment | Variable File | Workspace | Git Branch |
| ----------- | ------------- | --------- | ---------- |
| Development | `dev.tfvars`  | `dev`     | `develop`  |
| Production  | `prod.tfvars` | `prod`    | `main`     |

## Resource Dependencies

The infrastructure deployment is organized with dependencies in mind:

1. **First tier**: IAM, service accounts, and networking
2. **Second tier**: Secret Manager, Storage, Artifact Registry
3. **Third tier**: Pub/Sub, Cloud Functions
4. **Fourth tier**: Compute VM (API)
5. **Fifth tier**: Monitoring and alerting

## Customization Points

The infrastructure can be customized through variables in the `.tfvars` files:

- `project_id`: GCP Project ID
- `region` and `zone`: GCP location for resources
- `naming_prefix`: Prefix for resource names
- `api_machine_type`: VM size for API server
- `worker_min_instances` and `worker_max_instances`: Worker scaling configuration
- `alert_email_address`: Email for monitoring alerts

## Scaling Considerations

The infrastructure includes several auto-scaling components:

- API VM Instance Group: Scales based on CPU utilization
- Cloud Function: Scales based on Pub/Sub message volume
- Artifact Registry and Cloud Storage: Auto-scale with usage

## Next Steps

- Review the [Security Overview](security.md) for security best practices
- Check the [Operations Guide](operations.md) for day-to-day tasks
- See the [Monitoring Guide](monitoring.md) for observability setup
