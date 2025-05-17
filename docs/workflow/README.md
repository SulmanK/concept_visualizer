# GitHub Actions Workflows Documentation

## Overview

This directory contains documentation for all GitHub Actions workflows used in the Concept Visualizer project. These workflows automate the CI/CD pipeline, security scanning, environment validation, and maintenance tasks.

## Workflows

| Workflow                                     | Description                                       | Triggers                          |
| -------------------------------------------- | ------------------------------------------------- | --------------------------------- |
| [CI Tests & Deployment](ci-tests.md)         | Runs tests, linting, and builds Docker images     | Push to main/develop, PRs, manual |
| [Deploy Backend](deploy_backend.md)          | Deploys backend services to GCP                   | After CI workflow success         |
| [Environment Security Check](env_check.md)   | Scans for secrets and validates environment files | Push to main, PRs, weekly, manual |
| [Schedule Data Cleanup](schedule-cleanup.md) | Triggers DB cleanup via Supabase Edge Function    | Hourly, manual                    |
| [Security Scan](security_scan.md)            | Performs code and dependency security scanning    | Push to main, PRs, weekly, manual |

## Workflow Dependencies

The workflows have the following dependencies:

```
CI Tests & Deployment → Deploy Backend
```

The other workflows run independently based on their respective triggers.

## Environment Configuration

The workflows operate in two environments:

- **Development**: Tied to the `develop` branch
- **Production**: Tied to the `main` branch

Each environment has its own set of secrets and configurations defined in GitHub.

## Common Components

Several patterns are used across multiple workflows:

1. **Environment Selection**: Dynamically selecting environment variables based on branch
2. **GCP Authentication**: Using Workload Identity Federation for secure GCP access
3. **Docker Image Management**: Building, tagging, and deploying Docker images
4. **Terraform Integration**: Using Terraform to manage infrastructure
5. **Security Scanning**: Running various security tools to identify vulnerabilities

## Security Considerations

The workflows implement several security best practices:

- No hardcoded secrets (using GitHub Secrets)
- Regular security scanning
- Dependency vulnerability checks
- Environment validation
- Least privilege principles for service accounts

## Maintenance

To maintain these workflows:

1. Keep workflow files in the `.github/workflows/` directory
2. Update this documentation when modifying workflows
3. Test changes using the manual trigger option (`workflow_dispatch`)
4. Review workflow run logs for any issues

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Google Cloud GitHub Actions](https://github.com/google-github-actions)
- [Terraform GitHub Actions](https://github.com/hashicorp/setup-terraform)
