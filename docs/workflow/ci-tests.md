# CI Tests & Deployment Workflow

## Overview

The `CI Tests & Deployment` workflow handles testing, linting, and Docker image building for both the backend and frontend components of the Concept Visualizer project. This workflow is a critical part of the CI/CD pipeline, ensuring that code quality standards are maintained and preparing artifacts for deployment.

## Triggers

This workflow runs when:

- Code is pushed to the `main` or `develop` branches
- Pull requests are opened against `main` or `develop` branches
- Manually triggered via GitHub Actions interface (workflow_dispatch)

## Workflow Structure

### Backend Tests

**Job name**: `backend-tests`

This job runs all Python tests for the backend application:

- Uses Ubuntu as the execution environment
- Sets up Python 3.11
- Installs the `uv` package manager
- Creates a virtual environment
- Installs the backend package in development mode
- Runs pytest against the tests directory
- Uses mock environment variables for testing

### Backend Linting

**Job name**: `backend-lint`

This job performs static analysis of the backend code:

- Runs mypy for type checking on the `app` and `cloud_run/worker` directories
- Runs flake8 for code style and error checking
- Depends on successful completion of `backend-tests`

### Frontend Tests

**Job name**: `frontend-tests`

This job runs tests for the React frontend application:

- Uses Node.js 18
- Leverages npm caching to speed up dependency installation
- Performs a clean install of dependencies using `npm ci`
- Runs the frontend test suite with `npm test`
- Uses mock environment variables for testing

### Frontend Linting

**Job name**: `frontend-lint`

This job performs static analysis of the frontend code:

- Runs TypeScript type checking with `tsc --noEmit`
- Runs ESLint for code style and error checking
- Depends on successful completion of `frontend-tests`

### Build & Push Docker Images

**Job name**: `build-push-images`

This job builds and pushes Docker images to Google Artifact Registry:

- Only runs on pushes to `main` or `develop` branches, or manual triggers
- Requires both backend and frontend linting jobs to succeed
- Determines environment (dev/prod) based on branch
- Authenticates to Google Cloud using Workload Identity
- Configures Docker for Artifact Registry
- Builds and pushes the API image with two tags:
  - `latest`
  - The specific commit SHA

## Environment Configuration

The workflow uses different sets of secrets depending on the target environment:

- `develop` branch → dev environment
- `main` branch → production environment

## Dependencies

This workflow is a prerequisite for the `Deploy Backend and Update Frontend Monitor` workflow, which handles the actual deployment of the built images.

## Artifact Outputs

The workflow produces Docker images in Google Artifact Registry:

- API image:
  - `{region}-docker.pkg.dev/{project_id}/{repo_name}/concept-api-{env}:{sha}`
  - `{region}-docker.pkg.dev/{project_id}/{repo_name}/concept-api-{env}:latest`
