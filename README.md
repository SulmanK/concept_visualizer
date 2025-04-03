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

```
concept_visualizer/
├── backend/           # Python FastAPI backend
│   ├── app/
│   │   ├── api/       # API routes and endpoints
│   │   ├── core/      # Core functionality and settings
│   │   ├── models/    # Data models and schemas
│   │   ├── services/  # Business logic and external services
│   │   └── utils/     # Utility functions
├── frontend/          # React TypeScript frontend
│   ├── public/        # Static assets
│   ├── src/
│   │   ├── components/# Reusable UI components
│   │   ├── contexts/  # Context providers for state management
│   │   ├── features/  # Feature-specific components
│   │   ├── hooks/     # Custom React hooks
│   │   ├── services/  # API integration and external services
│   │   │   └── mocks/ # Mock services for testing
│   │   ├── styles/    # Global styles
│   │   └── types/     # TypeScript type definitions
├── design/            # Design documents and assets
└── scripts/           # Utility scripts
```

## Getting Started

### Prerequisites

- Python 3.11
- Node.js 18+
- npm or yarn
- JigsawStack API key
- Supabase account and project

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. Create a `.env` file with your API keys:
   ```
   CONCEPT_JIGSAWSTACK_API_KEY=your_jigsaw_api_key_here
   CONCEPT_SUPABASE_URL=your_supabase_url_here
   CONCEPT_SUPABASE_KEY=your_supabase_api_key_here
   ```

4. Run the development server:
   ```
   uvicorn app.main:app --reload
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```
   cd frontend/my-app
   ```

2. Install dependencies:
   ```
   npm install
   npm install @supabase/supabase-js js-cookie
   npm install --save-dev @types/js-cookie
   ```

3. Create a `.env` file:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```

4. Start the development server:
   ```
   npm run dev
   ```

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