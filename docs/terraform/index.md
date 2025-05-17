# Concept Visualizer Infrastructure Documentation

Welcome to the Concept Visualizer infrastructure documentation. This documentation covers the Terraform-managed Google Cloud Platform (GCP) infrastructure that powers the Concept Visualizer application.

## Documentation Sections

### Core Documentation

- [Infrastructure Overview](overview.md) - High-level overview of the infrastructure architecture
- [Setup Guide](setup.md) - Step-by-step guide for setting up the infrastructure
- [Components Overview](components.md) - Detailed information about each infrastructure component

### Operations Documentation

- [Operations Guide](operations.md) - Day-to-day operational tasks and procedures
- [Monitoring Guide](monitoring.md) - Infrastructure and application monitoring
- [Security Overview](security.md) - Security measures and best practices

## Infrastructure Diagram

Below is a simplified overview of the infrastructure components:

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

## Quick Reference

### Key Files

- **Main Configuration**: `main.tf`
- **Compute Resources**: `compute.tf`, `cloud_function.tf`
- **Networking**: `network.tf`
- **Storage**: `storage.tf`, `artifact_registry.tf`
- **Security**: `iam.tf`, `secrets.tf`
- **Monitoring**: `monitoring.tf`

### Environment Variables

The infrastructure uses environment-specific variable files:

- **Development**: `environments/dev.tfvars`
- **Production**: `environments/prod.tfvars`

### Script Reference

Key helper scripts:

- **Infrastructure Deployment**: `scripts/gcp_apply.sh`
- **Infrastructure Teardown**: `scripts/gcp_destroy.sh`
- **Secret Population**: `scripts/gcp_populate_secrets.sh`
- **Script Upload**: `scripts/upload_startup_scripts.sh`
- **GitHub Secret Management**: `scripts/gh_populate_secrets.sh`

## Getting Started

If you're new to this infrastructure, we recommend starting with the [Infrastructure Overview](overview.md) and then following the [Setup Guide](setup.md) to deploy your own environment.

For day-to-day operations, the [Operations Guide](operations.md) provides guidance on common tasks and troubleshooting.

## Contributing

When making changes to the infrastructure:

1. Follow the project's coding standards
2. Test changes in the development environment first
3. Document any new components or processes
4. Update monitoring for new resources

For significant architecture changes, create a design document and discuss with the team before implementation.
