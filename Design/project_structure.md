# Concept Visualizer Project Structure

This document outlines the directory structure for the Concept Visualizer project, following clean architecture principles to ensure maintainability, scalability, and separation of concerns.

## Overview

The project follows a monorepo approach with clear separation between frontend and backend components, while maintaining shared configuration at the root level.

```
concept_visualizer/
├── README.md
├── .gitignore
├── .env.example
├── pyproject.toml        # Python project configuration (for UV)
├── package.json          # Workspace root package for managing scripts
├── backend/              # Python FastAPI backend
├── frontend/             # React frontend
├── design/               # Design documents
└── scripts/              # Utility scripts for development
```

## Backend Structure

The backend follows a layered architecture pattern with clear separation of concerns:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── core/             # Core application code
│   │   ├── __init__.py
│   │   ├── config.py     # Configuration management
│   │   ├── logging.py    # Logging setup
│   │   └── exceptions.py # Custom exception definitions
│   ├── api/              # API layer
│   │   ├── __init__.py
│   │   ├── dependencies.py
│   │   ├── errors.py     # Error handlers
│   │   └── routes/       # API routes organized by domain
│   │       ├── __init__.py
│   │       ├── concept.py
│   │       └── health.py
│   ├── services/         # Service layer (business logic)
│   │   ├── __init__.py
│   │   ├── concept_service.py
│   │   └── jigsawstack/  # External API integration
│   │       ├── __init__.py
│   │       ├── client.py
│   │       ├── image.py
│   │       └── text.py
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   ├── request.py    # Request models (Pydantic)
│   │   └── response.py   # Response models (Pydantic)
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── color_utils.py
├── tests/                # Test directory mirroring app structure
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   ├── test_api/
│   │   └── test_routes/
│   │       ├── test_concept.py
│   │       └── test_health.py
│   └── test_services/
│       └── test_concept_service.py
├── .env                  # Environment variables (not in git)
└── requirements-dev.txt  # Development dependencies
```

### Backend Layer Responsibilities

1. **API Layer** (`api/`): Handles HTTP requests/responses, input validation, and routing
2. **Service Layer** (`services/`): Contains business logic and coordinates with external services
3. **Models** (`models/`): Defines data structures using Pydantic
4. **Core** (`core/`): Application configuration and setup
5. **Utils** (`utils/`): Reusable utility functions

## Frontend Structure

The frontend follows a feature-based organization with shared components, aligned with the routing structure:

```
frontend/
├── public/               # Static assets
│   ├── index.html
│   ├── favicon.ico
│   └── assets/
├── src/
│   ├── index.tsx         # Entry point
│   ├── App.tsx           # Root component with routing
│   ├── features/         # Feature-based organization
│   │   ├── landing/      # Main landing page (formerly concept-generator)
│   │   │   ├── components/
│   │   │   │   ├── ConceptForm.tsx
│   │   │   │   ├── ResultsSection.tsx
│   │   │   │   └── RecentConceptsSection.tsx
│   │   │   ├── hooks/
│   │   │   │   └── useConceptGeneration.ts
│   │   │   ├── types/
│   │   │   │   └── index.ts
│   │   │   ├── LandingPage.tsx   # Main landing page component
│   │   │   └── index.ts
│   │   │
│   │   ├── concepts/    # All concept-related features
│   │   │   ├── detail/  # For viewing a single concept
│   │   │   │   ├── components/
│   │   │   │   │   └── ConceptDetails.tsx
│   │   │   │   ├── ConceptDetailPage.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   ├── recent/  # For browsing recent concepts
│   │   │   │   ├── components/
│   │   │   │   │   ├── ConceptCard.tsx
│   │   │   │   │   └── ConceptList.tsx
│   │   │   │   ├── RecentConceptsPage.tsx
│   │   │   │   └── index.ts
│   │   │   │
│   │   │   └── create/  # Could redirect to landing if they're identical
│   │   │       └── index.ts  # Exports from landing if they're the same
│   │   │
│   │   └── refinement/  # For refining existing concepts
│   │       ├── components/
│   │       │   ├── RefinementForm.tsx
│   │       │   └── ComparisonView.tsx
│   │       ├── RefinementPage.tsx
│   │       └── index.ts
│   │
│   ├── components/       # Shared components
│   │   ├── ui/           # Basic UI components
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── Button.module.css
│   │   │   ├── ColorPicker/
│   │   │   ├── LoadingSpinner/
│   │   │   └── Card/
│   │   │
│   │   ├── layout/       # Layout components
│   │   │   ├── Header.tsx
│   │   │   ├── Footer.tsx
│   │   │   └── MainLayout.tsx
│   │   │
│   │   └── concept/      # Complex concept-related components
│   │       ├── ConceptForm.tsx
│   │       └── ConceptResult.tsx
│   │
│   ├── hooks/            # Shared hooks
│   │   ├── useApi.ts
│   │   └── useLocalStorage.ts
│   │
│   ├── contexts/         # React contexts
│   │   └── ConceptContext.tsx
│   │
│   ├── services/         # API service layer
│   │   ├── api.ts        # Base API configuration
│   │   ├── conceptApi.ts # Concept-specific API calls
│   │   ├── supabaseClient.ts  # Supabase client
│   │   └── sessionManager.ts  # Session management
│   │
│   ├── utils/            # Utility functions
│   │   ├── colorUtils.ts
│   │   └── formatters.ts
│   │
│   ├── types/            # Shared TypeScript types
│   │   └── index.ts
│   │
│   └── styles/           # Global styles
│       ├── global.css
│       └── variables.css
├── .eslintrc.js
├── .prettierrc
├── tsconfig.json
├── package.json
└── vite.config.ts       # Using Vite for faster development
```

### Frontend Organization Principles

1. **Feature-Based Structure**: Components, hooks, and logic are grouped by feature
2. **Route-Aligned Features**: Feature directories reflect the application's routing structure
3. **Shared Resources**: Common components, hooks, and utilities are in dedicated directories
4. **Clean API Layer**: API calls are abstracted into service modules
5. **Type Safety**: TypeScript types are defined for all data structures
6. **Consistent Naming**: Page components use the "Page" suffix for clarity

### Key Routing Structure

```tsx
<Routes>
  <Route path="/" element={<MainLayout />}>
    {/* Main landing page with concept generator */}
    <Route index element={<LandingPage />} />
    
    {/* Create page - could redirect to landing */}
    <Route path="create" element={<LandingPage />} />
    
    {/* Concept detail page */}
    <Route path="concepts/:conceptId" element={<ConceptDetailPage />} />
    
    {/* Recent concepts page */}
    <Route path="recent" element={<RecentConceptsPage />} />
    
    {/* Refinement page */}
    <Route path="refine/:conceptId" element={<RefinementPage />} />
  </Route>
</Routes>
```

## Testing Strategy

### Backend Tests

1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test API endpoints with mocked external dependencies
3. **End-to-End Tests**: Test full request/response cycle

### Frontend Tests

1. **Component Tests**: Test individual components with React Testing Library
2. **Hook Tests**: Test custom hooks
3. **Integration Tests**: Test feature workflows

## CI/CD Configuration

```
.github/
└── workflows/
    ├── backend-ci.yml    # Backend CI pipeline
    ├── frontend-ci.yml   # Frontend CI pipeline
    └── deploy.yml        # Vercel deployment
```

## Development Environment Setup

### Local Development Scripts

The project provides utility scripts for common development tasks:

```
scripts/
├── setup.sh              # Initial project setup
├── dev.sh                # Start development servers
├── test.sh               # Run all tests
├── lint.sh               # Run linters
└── build.sh              # Build for production
```

### Environment Variables

```
# .env.example (template for developers)
# Backend
JIGSAWSTACK_API_KEY=your_api_key_here
LOG_LEVEL=INFO
CORS_ORIGINS=http://localhost:3000

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api
```

## Dependency Management

1. **Backend**: UV for Python package management
   - `pyproject.toml` for project configuration
   - Virtual environment isolation

2. **Frontend**: npm/yarn for JavaScript dependencies
   - Proper version constraints in package.json

## Deployment Configuration

### Vercel Configuration

```
vercel.json
```

This file configures both frontend and backend deployment on Vercel, including:
- Build commands
- Environment variable handling
- Routing rules

## Best Practices Enforced Through Structure

1. **Separation of Concerns**: Clear boundaries between layers
2. **Single Responsibility**: Each directory has a focused purpose
3. **Dependency Injection**: Services are injected rather than imported directly
4. **Consistent Naming**: Naming conventions are consistent across project
5. **Import Organization**: Avoids circular dependencies

## Implementation Guidelines

When implementing the concept visualizer, developers should:

1. Place new API endpoints in the appropriate route file in `backend/app/api/routes/`
2. Implement business logic in service modules in `backend/app/services/`
3. Define data models in `backend/app/models/`
4. Create React components in their feature directory or in shared components
5. Follow the testing patterns established in the test directories

This structure follows clean architecture principles while being pragmatic for a modern web application with Python backend and React frontend. 