# Concept Visualizer

[![Build Status](https://img.shields.io/github/actions/workflow/status/SulmanK/concept-visualizer/.github%2Fworkflows%2Fci-tests.yml?branch=main)](https://github.com/SulmanK/concept-visualizer/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A web application for generating and refining visual concepts like logos and color palettes using AI assistance. Describe your ideas, and let the AI bring them to life!

![Concept Visualizer Demo](./docs/assets/demo.gif)

<a href="https://jigsawstack.com/?ref=powered-by" rel="follow">
  <img
    src="https://jigsawstack.com/badge.svg"
    alt="Powered by JigsawStack. The One API for your next big thing."
  />
</a>

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
  - [Configuration](#configuration)
    - [Environment Files (.env)](#environment-files-env)
    - [Supabase Setup](#supabase-setup)
    - [GCP Setup](#gcp-setup)
    - [JigsawStack API Key](#jigsawstack-api-key)
    - [Redis Setup](#redis-setup)
  - [Running Locally](#running-locally)
  - [Running Cloud](#running-Cloud)
- [Testing](#testing)
  - [Unit Tests](#unit-tests)
- [Deployment](#deployment)
  - [Backend (GCP)](#backend-gcp)
  - [Frontend (Vercel)](#frontend-vercel)
- [Infrastructure](#infrastructure)
- [Security](#security)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Concept Generation**: Create logos and color palettes from text descriptions.
- **Concept Refinement**: Iteratively improve existing designs by specifying modifications. [IN PROGRESS]
- **Color Palette Management**: Generate, view, and apply harmonious color palettes.
- **Concept Storage**: Save, organize, and revisit your generated concepts.
- **Asynchronous Processing**: Handles potentially long-running AI tasks in the background.
- **API Rate Limiting**: Protects backend resources from overuse.

## Tech Stack

- **Backend:**
  - Python 3.11+
  - FastAPI
  - Uvicorn
  - Pydantic
  - Supabase (Database, Auth, Storage)
  - Redis (via Upstash for Rate Limiting)
  - JigsawStack API (AI Generation)
  - Google Cloud Functions (Gen 2) (Background Tasks)
  - Google Cloud Pub/Sub (Task Queue)
  - Docker
- **Frontend:**
  - React 19
  - TypeScript
  - Vite
  - Tailwind CSS
  - React Router
  - TanStack Query (React Query)
  - Supabase JS Client
  - Axios
- **Infrastructure & DevOps:**
  - Google Cloud Platform (GCP)
    - Compute Engine (API VM)
    - Cloud Functions (Worker)
    - Pub/Sub (Task Queue)
    - Artifact Registry (Docker Images)
    - Secret Manager
    - Cloud Storage (Terraform State, Assets)
  - Terraform (IaC)
  - Vercel (Frontend Deployment)
  - GitHub Actions (CI/CD, Scheduled Tasks)
  - Pre-commit Hooks (Code Quality)

## System Architecture

The following diagram illustrates the system architecture and data flow of the Concept Visualizer application:

![System Architecture Diagram](./system_arch_diagram.png)

## Project Structure

```
concept-visualizer/
├── .github/             # GitHub Actions workflows
├── backend/             # Python FastAPI backend service
│   ├── app/             # Core application code
│   ├── cloud_run/       # Code specific to the worker (Cloud Function)
│   ├── scripts/         # Helper scripts (DB migrations, admin tasks)
│   ├── supabase/         # Supabase edge function
│   ├── tests/           # Backend tests
│   ├── .env.develop     # Development environment variables (template, managed by hook)
│   ├── .env.main        # Production environment variables (template, managed by hook)
│   ├── Dockerfile       # Dockerfile for API service
│   ├── Dockerfile.worker# Dockerfile for API service
│   └── pyproject.toml   # Backend dependencies and project metadata
├── frontend/            # React frontend application
│   ├── my-app/          # Main application source
│   │   ├── public/      # Static assets
│   │   ├── src/         # Frontend source code
│   │   ├── tests/       # Frontend tests (unit & e2e)
│   │   ├── .env.develop # Development environment variables (template, managed by hook)
│   │   ├── .env.main    # Production environment variables (template, managed by hook)
│   │   ├── package.json # Frontend dependencies
│   │   └── vercel.json  # Vercel deployment configuration
├── scripts/             # Root-level helper scripts (GCP setup, env files)
├── terraform/           # Infrastructure as Code (IaC) for GCP
│   ├── environments/    # Environment-specific Terraform variables (*.tfvars)
│   └── scripts/         # Startup scripts for VMs
├── docs/                # Project documentation
└── README.md            # This file
```

## Getting Started

Follow these steps to set up the project for local development.

### Prerequisites

- [Git](https://git-scm.com/)
- [Node.js](https://nodejs.org/) (v18 or later) & npm
- [Python](https://www.python.org/) (v3.11 recommended)
- [`uv`](https://github.com/astral-sh/uv) (Python package manager): `pip install uv`
- [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) (`gcloud auth login`, `gcloud auth application-default login`)
- [Terraform CLI](https://developer.hashicorp.com/terraform/downloads) (v1.3 or later)
- [Supabase CLI](https://supabase.com/docs/guides/cli) (`supabase login`)
- Accounts for: Supabase, GCP, Vercel, GitHub, JigsawStack

### Installation

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/SulmanK/concept-visualizer.git
    cd concept-visualizer
    ```

2.  **Setup Backend:**

    ```bash
    cd backend
    uv venv  # Create virtual environment
    uv pip install -e .[dev] # Install dependencies
    cd ..
    ```

3.  **Setup Frontend:**

    ```bash
    cd frontend/my-app
    npm install
    cd ../..
    ```

4.  **Setup Pre-commit Hooks:**
    ```bash
    pre-commit install
    ```

### Configuration

For detailed configuration instructions, please refer to our [Setup Guide](Design/Setup.md).

#### Running Locally

1.  **Backend:**
    ```bash
    cd backend
    # Ensure .env is linked to .env.develop via post-checkout hook
    # (or manually copy: cp .env.develop .env)
    uv run uvicorn app.main:app --reload --port 8000
    ```
    The image generation and refinement is tied up with the cloud function - you will have to deploy the worker to GCP for it to work.
2.  **Frontend:**
    ```bash
    cd frontend/my-app
    # Ensure .env is linked to .env.develop via post-checkout hook
    # (or manually copy: cp .env.develop .env)
    npm run dev
    ```
    Access the app at `http://localhost:5173` (or the port Vite uses).

#### Running Cloud

After successful deployment of both the backend to GCP and the frontend to Vercel, you can access the application at the URL provided by Vercel in your project dashboard. This URL will route API requests to your GCP backend automatically through the configured rewrites in `vercel.json`.

## Testing

### Backend

```bash
cd backend
uv run pytest tests/
```

### Frontend

```bash
cd frontend/my-app
npm test
```

The frontend uses a mock API service (`src/services/mocks`) for isolated testing.

## Deployment

- **Backend:** Deployed to GCP Compute Engine (API) and Cloud Functions (Worker) via Terraform and GitHub Actions (`.github/workflows/deploy_backend.yml`). Requires secrets configured in GitHub Actions.
- **Frontend:** Deployed to Vercel. Requires Vercel project configured to point to the `frontend/my-app` directory and environment variables set for backend API URL and Supabase keys.
- **Important:** After deploying/recreating GCP infrastructure, the backend VM's external IP address **will change**. You **must update** the `destination` IP in `frontend/my-app/vercel.json` and redeploy the frontend on Vercel.

## Infrastructure

- **GCP:** Compute Engine (API VM), Cloud Functions (Gen 2) (Worker), Pub/Sub (Task Queue), Artifact Registry (Docker Images), Secret Manager, Cloud Storage (State, Assets).
- **Supabase:** PostgreSQL Database, Authentication, Storage.
- **Vercel:** Frontend hosting and serverless functions (for rewrites).
- **Upstash:** Managed Redis for rate limiting.

## Security

- Credentials managed via environment variables and GCP Secret Manager. **Never commit secrets.**
- Row Level Security (RLS) enforced in Supabase for data access.
- API rate limiting implemented on the backend.
- Secure JWT handling for authentication.
- GitHub Actions workflows include security scanning (CodeQL, Gitleaks).
- Sensitive data is masked in logs.

## Contributing

Please read `CONTRIBUTING.md` (if available) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License.
