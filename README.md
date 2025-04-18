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
import { mockApiService, setupMockApi, resetMockApi } from '../services/mocks';

// Configure mock API behavior
setupMockApi({
  shouldFail: false,
  responseDelay: 10,
  customResponses: {
    generateConcept: {
      imageUrl: 'https://example.com/test-image.png',
      // other properties...
    }
  }
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