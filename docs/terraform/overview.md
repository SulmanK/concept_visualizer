# Terraform Infrastructure Overview

## Introduction

The Concept Visualizer application is deployed on Google Cloud Platform (GCP) using Terraform for infrastructure as code. This ensures consistent, reproducible deployments across development and production environments.

The infrastructure follows a multi-tier architecture with:

- Frontend hosted on Vercel
- Backend API running on GCP Compute Engine
- Background processing handled by Cloud Functions
- Communication via Pub/Sub messaging
- Data stored in Supabase and Google Cloud Storage
- Secrets managed in GCP Secret Manager

## Environment Structure

The project uses two separate GCP projects for isolation:

- **Development Environment**: Deployed from the `develop` branch
- **Production Environment**: Deployed from the `main` branch

Terraform state is stored in a dedicated GCP Storage bucket to enable collaboration and track infrastructure changes.

## Key Components

### Compute Resources

- **API Server**: GCP Compute Engine VM running the FastAPI application in Docker containers
- **Worker**: GCP Cloud Function (2nd Gen) executing background tasks like AI image generation
- **Frontend**: Hosted on Vercel (managed separately from the Terraform configuration)

### Storage

- **Database**: PostgreSQL database hosted on Supabase (managed separately)
- **Object Storage**: Supabase Storage for user-generated content
- **Artifact Registry**: For storing Docker images
- **Cloud Storage**: For various assets and Terraform state

### Messaging

- **Pub/Sub Topics**: For asynchronous communication between API and worker

### Security

- **Secret Manager**: For securely storing credentials and API keys
- **IAM Roles**: Fine-grained permissions for service accounts
- **Firewalls**: Network protection for compute resources

### Monitoring

- **Cloud Monitoring**: Uptime checks, alerting policies, and dashboards
- **Logs**: Centralized logging for troubleshooting

## Deployment Process

The infrastructure deployment follows a specific sequence to handle dependencies:

1. Create service accounts and IAM permissions
2. Set up Secret Manager resources (without populating secrets)
3. Populate secrets using scripts
4. Deploy full infrastructure (network, compute, storage, messaging)
5. Build and push API Docker images
6. Configure VM startup scripts

## Architecture Diagram

Below is a simplified architecture diagram showing how the Terraform-managed components connect:

```
┌─────────────────┐         ┌─────────────────┐
│                 │         │                 │
│  Vercel         │         │  GCP            │
│  (Frontend)     │         │  Infrastructure │
│                 │         │                 │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │                           │
         │ HTTPS                     │
         │                           │
┌────────▼────────┐         ┌────────▼────────┐
│                 │         │                 │
│  API Server     │◄────────┤  Secret Manager │
│  (Compute VM)   │         │                 │
│                 │         └────────┬────────┘
└────────┬────────┘                  │
         │                           │
         │                           │
         │                  ┌────────▼────────┐
         │                  │                 │
         │                  │  Artifact       │
         │                  │  Registry       │
         │                  │                 │
         │                  └────────┬────────┘
         │                           │
         │                           │
┌────────▼────────┐         ┌────────▼────────┐
│                 │         │                 │
│  Pub/Sub        ├─────────►  Cloud Function │
│  (Task Queue)   │         │  (Worker)       │
│                 │         │                 │
└────────┬────────┘         └────────┬────────┘
         │                           │
         │                           │
         │                           │
┌────────▼────────┐         ┌────────▼────────┐
│                 │         │                 │
│  Supabase       │◄────────┤  JigsawStack    │
│  (Database)     │         │  API (External) │
│                 │         │                 │
└─────────────────┘         └─────────────────┘
```

## Further Information

For detailed information about specific components, deployment procedures, and management operations, refer to the following documentation:

- [Setup Guide](setup.md) - Initial setup steps
- [Components Overview](components.md) - Detailed description of each component
- [Operations Guide](operations.md) - Day-to-day management tasks
- [Security Overview](security.md) - Security considerations
- [Monitoring Guide](monitoring.md) - Infrastructure monitoring
