# Concept Visualizer

A web application for generating and refining visual concepts with AI assistance.

## Features

- **Concept Generation**: Create logos and color palettes from text descriptions
- **Concept Refinement**: Refine existing designs by specifying modifications
- **Color Palette Generation**: Get harmonious color palettes for your brand
- **Concept Storage**: Save and view your generated concepts

## Tech Stack

### Backend

- Python 3.11
- FastAPI
- Pydantic
- JigsawStack API integration
- Supabase for storage and database

### Frontend

- React 19
- TypeScript
- Tailwind CSS
- React Router
- Supabase JS client

## Project Structure

This project follows a clean, modular structure with clear separation between frontend and backend:

```
concept_visualizer/
├── .github/             # GitHub workflows and CI/CD configuration
├── backend/             # Python FastAPI backend
│   ├── .venv/           # Backend virtual environment (not tracked in git)
│   ├── app/             # Application code
│   ├── docs/            # Backend documentation
│   ├── tests/           # Test suite
│   ├── .env             # Environment variables (not tracked in git)
│   ├── .env.example     # Example environment file
│   └── pyproject.toml   # Backend dependencies and configuration
├── frontend/            # React frontend
│   ├── my-app/          # Main React application
│   │   ├── node_modules/ # Frontend dependencies (not tracked in git)
│   │   ├── src/         # Source code
│   │   ├── .env         # Environment variables (not tracked in git)
│   │   └── .env.example # Example environment file
├── Design/              # Design documentation
└── docs/                # Project-wide documentation
```

## Development Setup

### Backend

To set up the backend:

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
uv venv

# Install dependencies
uv pip install -e .

# Set up environment variables
cp .env.example .env
# Edit .env with your specific configuration

# Run the development server
cd backend && uv run uvicorn app.main:app --reload
```

### Frontend

To set up the frontend:

```bash
# Navigate to the frontend directory
cd frontend/my-app

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your specific configuration

# Run the development server
npm run dev
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality and maintain architectural standards. To set up pre-commit hooks:

```bash
# Install pre-commit
pip install pre-commit

# Install the git hooks
pre-commit install
```

These hooks will automatically run when you attempt to commit changes and will prevent commits that don't meet the project's standards. The hooks include:

- Code formatting with Black and Prettier
- Import sorting with isort
- Linting with flake8 and ESLint
- Type checking with mypy and TypeScript
- Custom architectural checks to enforce project structure

To manually run all pre-commit hooks on all files:

```bash
pre-commit run --all-files
```

## Getting Started

### Prerequisites

- Python 3.11
- Node.js 18+
- npm or yarn
- JigsawStack API key
- Supabase account and project

### Supabase Setup

1. Create a new Supabase project

2. Set up the database tables:

   - `sessions`: Stores user sessions
   - `concepts`: Stores generated concepts
   - `color_variations`: Stores color variations for concepts

3. Set up storage buckets:
   - `concept-images`: For storing base concept images
   - `palette-images`: For storing color variation images

See `design/supabase_setup_guide.md` for detailed instructions.

## Testing

The project uses Vitest for unit and integration testing.

### Running Tests

```
cd frontend/my-app
npm test          # Run all tests
npm run test:watch # Run tests in watch mode
```

### Mock API Service

For testing API integrations without making actual network calls, the project includes a mock API service:

```typescript
import { mockApiService, setupMockApi, resetMockApi } from "../services/mocks";

// Configure mock API behavior
setupMockApi({
  shouldFail: false,
  responseDelay: 10,
  customResponses: {
    generateConcept: {
      imageUrl: "https://example.com/test-image.png",
      // other properties...
    },
  },
});

// Reset mock API to default state
resetMockApi();
```

The mock service simulates the behavior of the backend API and can be configured to return custom responses or simulate errors for testing edge cases.

## Security

### Credentials Management

The application uses environment variables for managing all sensitive credentials. These include:

- **CONCEPT_JIGSAWSTACK_API_KEY**: API key for JigsawStack services
- **CONCEPT_SUPABASE_KEY**: Supabase API key for database and storage access
- **CONCEPT_UPSTASH_REDIS_PASSWORD**: Password for Upstash Redis service

Never commit actual credentials to the repository. The repository contains example files (`.env.example`) with placeholder values that should be used as templates.

### Branch-Based Environment Switching

This project implements automatic environment switching based on Git branches. When you check out different branches, the system automatically copies the appropriate environment configuration files for that branch.

#### How it works

1. The project uses a Git `post-checkout` hook that runs after switching branches
2. When you switch to `develop` or `main`, the hook copies the corresponding `.env.develop` or `.env.main` to `.env` in both backend and frontend
3. The application then uses these environment-specific configurations

#### Setup

Run the setup script to create the necessary environment files:

```bash
# Make the setup script executable (if not already)
chmod +x scripts/setup_env_files.sh

# Run the setup script
./scripts/setup_env_files.sh
```

This will create:

- `.env.develop` - Contains development environment settings
- `.env.main` - Contains production environment settings with placeholders
- `.env.example` - Template showing all required variables

After running the script, make sure the Git hook is executable:

```bash
chmod +x .git/hooks/post-checkout
```

Now, when you switch branches with `git checkout develop` or `git checkout main`, the appropriate environment files will be automatically applied.

#### Notes

- The `.env` files themselves are not tracked in Git (they're in `.gitignore`)
- Only the branch-specific templates (`.env.develop`, `.env.main`) may be committed, with placeholders for sensitive values
- After switching branches, review your `.env` files to ensure they have the correct values

### Setting Up Credentials

1. Copy the example environment files to create your own:

   ```bash
   # Backend
   cp backend/.env.example backend/.env

   # Frontend
   cp frontend/my-app/.env.example frontend/my-app/.env
   ```

2. Fill in your actual credentials in the `.env` files

3. Make sure `.env` files are listed in the `.gitignore` to prevent accidental commits

### Security Workflows

This project includes GitHub workflows for security scanning:

- **Security Scan**: Uses CodeQL to scan for security vulnerabilities in the code
- **Environment Security Check**: Checks for hardcoded credentials and verifies proper environment file structure

### Logging Security

The application implements secure logging practices:

- Sensitive information is masked in logs (only first few characters are shown)
- User session IDs are never logged in full form
- API keys and credentials are not logged

## License

This project is licensed under the MIT License - see the LICENSE file for details.
