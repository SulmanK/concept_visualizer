# Concept Visualizer

A web application for generating and refining visual concepts with AI assistance. 

## Features

- **Concept Generation**: Create logos and color palettes from text descriptions
- **Concept Refinement**: Refine existing designs by specifying modifications
- **Color Palette Generation**: Get harmonious color palettes for your brand

## Tech Stack

### Backend
- Python 3.11
- FastAPI 
- Pydantic
- JigsawStack API integration

### Frontend
- React 19
- TypeScript
- Tailwind CSS
- React Router

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
│   │   ├── features/  # Feature-specific components
│   │   ├── hooks/     # Custom React hooks
│   │   ├── services/  # API integration
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

### Backend Setup

1. Navigate to the backend directory:
   ```
   cd backend
   ```

2. Install dependencies:
   ```
   pip install -e .
   ```

3. Create a `.env` file with your JigsawStack API key:
   ```
   CONCEPT_JIGSAWSTACK_API_KEY=your_api_key_here
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
   ```

3. Create a `.env` file:
   ```
   VITE_API_BASE_URL=http://localhost:8000/api
   ```

4. Start the development server:
   ```
   npm run dev
   ```

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

## License

This project is licensed under the MIT License - see the LICENSE file for details. 