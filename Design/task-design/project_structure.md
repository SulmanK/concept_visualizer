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
├── docs/                 # Project documentation
│   ├── backend/          # Backend documentation
│   └── frontend/         # Frontend documentation
└── scripts/              # Utility scripts for development
```

## Backend Structure

The backend follows a layered architecture pattern with clear separation of concerns. The current structure is:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py           # Application entry point
│   ├── core/             # Core application code
│   │   ├── __init__.py
│   │   ├── config.py     # Configuration management
│   │   ├── middleware/   # Application middleware
│   │   │   ├── __init__.py
│   │   │   └── prioritization.py # Request prioritization middleware
│   │   ├── supabase/     # Supabase integration
│   │   │   ├── __init__.py
│   │   │   ├── client.py # Base client implementation
│   │   │   ├── session_storage.py # Session storage operations
│   │   │   ├── concept_storage.py # Concept storage operations
│   │   │   └── image_storage.py   # Image storage operations
│   │   ├── limiter/      # Rate limiting infrastructure
│   │   │   ├── __init__.py
│   │   │   ├── config.py # Core limiter configuration
│   │   │   └── redis_store.py # Redis integration
│   │   └── exceptions.py # Custom exception definitions
│   ├── api/              # API layer
│   │   ├── __init__.py
│   │   ├── router.py     # Main router configuration
│   │   ├── dependencies.py # Common API dependencies
│   │   ├── errors.py     # Error handling and custom exceptions
│   │   └── routes/       # API routes organized by domain
│   │       ├── __init__.py
│   │       ├── api.py    # Base API routes
│   │       ├── concept/  # Concept generation routes
│   │       │   ├── __init__.py
│   │       │   ├── generation.py
│   │       │   └── refinement.py
│   │       ├── concept_storage/ # Concept storage routes
│   │       │   ├── __init__.py
│   │       │   └── storage.py
│   │       ├── health/   # Health check routes
│   │       │   ├── __init__.py
│   │       │   ├── check.py
│   │       │   ├── limits.py
│   │       │   └── utils.py
│   │       ├── session/  # Session management routes
│   │       │   ├── __init__.py
│   │       │   └── session_routes.py
│   │       ├── svg/      # SVG conversion routes
│   │       │   ├── __init__.py
│   │       │   ├── converter.py
│   │       │   └── utils.py
│   │       └── __tests__/ # Route-specific tests
│   ├── services/         # Service layer (business logic)
│   │   ├── __init__.py
│   │   ├── interfaces/   # Service interfaces
│   │   │   ├── __init__.py
│   │   │   ├── concept_service.py
│   │   │   ├── storage_service.py
│   │   │   └── image_service.py
│   │   ├── concept/      # Concept generation services
│   │   │   ├── __init__.py
│   │   │   ├── generation.py  # Concept generation logic
│   │   │   ├── refinement.py  # Concept refinement logic
│   │   │   └── palette.py     # Color palette generation
│   │   ├── storage/      # Storage services
│   │   │   ├── __init__.py
│   │   │   ├── interfaces.py    # Storage service interfaces
│   │   │   ├── factory.py       # Factory functions for storage services
│   │   │   ├── concept/         # Concept storage services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── persistence.py  # Basic concept persistence
│   │   │   │   ├── query.py        # Concept querying operations
│   │   │   │   └── factory.py      # Factory functions
│   │   │   ├── palette/         # Palette storage services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── persistence.py  # Palette persistence
│   │   │   │   └── factory.py      # Factory functions
│   │   │   └── utils.py          # Shared storage utilities
│   │   ├── image/        # Image processing services
│   │   │   ├── __init__.py      # Export factory functions and interfaces
│   │   │   ├── interfaces/      # Service interfaces
│   │   │   │   ├── __init__.py
│   │   │   │   ├── generation.py    # Image generation interfaces
│   │   │   │   ├── storage.py       # Storage interfaces
│   │   │   │   ├── processing.py    # Processing interfaces
│   │   │   │   └── conversion.py    # Conversion interfaces
│   │   │   ├── generation/      # Image generation services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── jigsawstack.py   # JigsawStack implementation
│   │   │   │   └── factory.py       # Factory functions
│   │   │   ├── storage/         # Storage services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── supabase.py      # Supabase implementation
│   │   │   │   ├── metadata.py      # Metadata management
│   │   │   │   └── factory.py       # Factory functions
│   │   │   ├── processing/      # Image processing services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── color.py         # Color operations
│   │   │   │   ├── transformation.py # Image transformations
│   │   │   │   ├── filters.py       # Visual filters
│   │   │   │   └── factory.py       # Factory functions
│   │   │   ├── conversion/      # Format conversion services
│   │   │   │   ├── __init__.py
│   │   │   │   ├── format.py        # Format conversion
│   │   │   │   ├── svg.py           # SVG-specific operations
│   │   │   │   ├── enhancement.py   # Image enhancement
│   │   │   │   └── factory.py       # Factory functions
│   │   │   ├── service.py       # Main image service (uses composition)
│   │   │   └── factory.py       # Main factory functions
│   │   ├── session/      # Session services
│   │   │   ├── __init__.py      # Export factory functions and interfaces
│   │   │   ├── interfaces.py    # Session service interfaces
│   │   │   ├── auth.py          # Session authentication service
│   │   │   ├── persistence.py   # Session persistence service
│   │   │   ├── lifecycle.py     # Session lifecycle management
│   │   │   ├── manager.py       # Main session service (uses composition)
│   │   │   └── factory.py       # Factory functions
│   │   └── jigsawstack/  # External API integration
│   │       ├── __init__.py      # Export factory functions and classes
│   │       ├── base.py          # Base client with common functionality
│   │       ├── image.py         # Image generation/refinement client
│   │       ├── palette.py       # Color palette generation client
│   │       ├── interfaces.py    # Client interfaces
│   │       ├── utils.py         # Shared utilities
│   │       ├── exceptions.py    # Client-specific exceptions
│   │       ├── factory.py       # Factory functions for clients
│   │       └── client.py        # Legacy client (uses composition)
│   ├── models/           # Data models
│   │   ├── __init__.py
│   │   ├── common/       # Shared model components
│   │   │   ├── __init__.py
│   │   │   └── base.py   # Base model classes
│   │   ├── concept/      # Concept-related models
│   │   │   ├── __init__.py
│   │   │   ├── domain.py # Domain models
│   │   │   ├── request.py # Request models
│   │   │   └── response.py # Response models
│   │   ├── session/      # Session-related models
│   │   │   ├── __init__.py
│   │   │   └── session.py # Session models
│   │   └── svg/          # SVG-related models
│   │       ├── __init__.py
│   │       └── conversion.py # Conversion models
│   └── utils/            # Utility functions
│       ├── __init__.py
│       ├── logging/      # Logging utilities
│       │   ├── __init__.py
│       │   └── setup.py  # Logging configuration
│       ├── validation/   # Validation utilities
│       │   ├── __init__.py
│       │   └── validators.py # Custom validators
│       ├── api_limits/   # API rate limiting utilities
│       │   ├── __init__.py
│       │   └── endpoints.py # Endpoint rate limiting functions
│       ├── data/         # Data transformation
│       │   ├── __init__.py
│       │   └── transformers.py # Data transformers
│       └── security/     # Security utilities
│           ├── __init__.py
│           └── mask.py   # Data masking
├── docs/                 # Backend documentation
│   ├── api/              # API documentation
│   ├── services/         # Services documentation
│   ├── models/           # Models documentation
│   ├── core/             # Core documentation
│   └── utils/            # Utils documentation
├── static/               # Static files served by backend
├── tests/                # Test directory
│   ├── __init__.py
│   ├── conftest.py       # Test fixtures
│   ├── test_api/         # API tests
│   ├── test_services/    # Service tests
│   ├── test_models/      # Model tests
│   └── test_utils/       # Utility tests
├── scripts/              # Backend utility scripts
├── run.py                # Script to run the application
├── setup.py              # Package setup script
├── requirements.txt      # Project dependencies
├── .env                  # Environment variables (not in git)
└── .env.example          # Example environment variables template
```

### Backend Layer Responsibilities

1. **API Layer** (`api/`): Handles HTTP requests/responses, input validation, and routing

   - Responsible for input validation using Pydantic models
   - Routes requests to appropriate service functions
   - Handles cookies and session management
   - Returns HTTP responses with proper status codes
   - Uses centralized dependencies and error handling

2. **Service Layer** (`services/`): Contains business logic and coordinates with external services

   - Implements domain logic in feature-specific modules
   - Exposes clean interfaces through the interfaces directory
   - Follows single responsibility principle with focused modules
   - Orchestrates calls to external APIs
   - Delegates specialized operations to appropriate sub-services

3. **Models** (`models/`): Defines data structures using Pydantic

   - Organized by domain with focused model modules
   - Request models validate incoming API requests
   - Response models define API response structures
   - Domain models represent core business entities

4. **Core** (`core/`): Application configuration and setup

   - Manages environment variables and settings
   - Configures middleware and application infrastructure
   - Provides client implementations for external services
   - Handles cross-cutting concerns like rate limiting

5. **Utils** (`utils/`): Reusable utility functions
   - Organized by function type (logging, validation, etc.)
   - Provides domain-agnostic helper functions
   - Implements cross-cutting functionalities
   - Focuses on reusability across different modules

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

## Areas for Improvement

### Backend Enhancements

1. **API Layer Refinement**:

   - Create dedicated route files for different concept operations
   - Add error handling middleware
   - Implement dependencies.py for cleaner dependency injection

2. **Security Improvements**:

   - Secure environment variable management
   - Implement proper rate limiting
   - Add CSRF protection

3. **Performance Optimization**:

   - Add caching layer for frequent operations
   - Optimize image processing operations

4. **Documentation**:
   - Enhance API documentation with more examples
   - Create detailed deployment instructions

### Frontend Enhancements

1. **Performance Optimization**:

   - Implement code splitting
   - Add caching for API responses
   - Optimize bundle size

2. **User Experience**:
   - Add more micro-interactions
   - Improve loading states
   - Enhance error feedback

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
CONCEPT_JIGSAWSTACK_API_KEY=your_api_key_here
CONCEPT_LOG_LEVEL=INFO
CONCEPT_CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
CONCEPT_SUPABASE_URL=your_supabase_url
CONCEPT_SUPABASE_KEY=your_supabase_key
CONCEPT_ENVIRONMENT=development

# Frontend
VITE_API_BASE_URL=http://localhost:8000/api
```

## Deployment Configuration

The project is prepared for deployment with the following considerations:

1. **Backend Deployment**:

   - Runs as a FastAPI application
   - Requires environment variables for configuration
   - Uses Supabase for data storage

2. **Frontend Deployment**:
   - Built with Vite for optimized bundles
   - Requires API URL configuration
   - Static assets can be served from CDN

This structure follows clean architecture principles while being pragmatic for a modern web application with Python backend and React frontend.
