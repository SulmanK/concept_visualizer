# Concept Visualizer - Project TODO

## Design Documents

## Schema Update Tasks

### Backend Updates

- [x] **Data Models**

  - [x] Update Pydantic models for concepts with image_path and image_url
  - [x] Update Pydantic models for color variations with image_url field
  - [x] Modify database query functions to use new column names

- [x] **Image Storage Service**

  - [x] Modify store_image method to save both path and signed URL
  - [x] Update get_signed_url to handle URL regeneration if URL is expired
  - [x] Ensure storage service handles both fields consistently

- [x] **Concept Storage Service**

  - [x] Update create_concept to store both image_path and image_url
  - [x] Update get_concept methods to handle both old and new schema
  - [x] Modify create_variation to store both path and URL

- [x] **API Endpoints**
  - [x] Update concept creation endpoint to include image_url in response
  - [x] Modify concept retrieval endpoint to return both fields
  - [x] Update image URL refresh endpoints to handle new schema

### Frontend Updates

- [x] **API Client/Types**

  - [x] Update ConceptData interface to include image_url
  - [x] Modify ColorVariation interface to include image_url
  - [x] Update API response type definitions

- [x] **Image Display Components**

  - [x] Update ConceptResult to use image_url when available
  - [x] Modify ConceptCard to use image_url directly
  - [x] Update RecentConceptsSection to handle both fields
  - [x] Fix any components with double-signing issues

- [x] **Utility Functions**
  - [x] Update getFormattedUrl to prioritize image_url field
  - [x] Modify getImageUrl function to check for existing URL first
  - [x] Fix any URL processing logic to prevent double-signing

## Rate Limit Optimization Tasks

### Backend Changes

- [ ] **Non-Counting Rate Limit Endpoint**

  - [ ] Create new `GET /api/health/rate-limits-status` endpoint
  - [ ] Mark as non-counting against user limits
  - [ ] Use same implementation as current rate limits but exempt from counting

- [ ] **Rate Limit Headers Implementation**

  - [ ] Create `app/api/middleware/rate_limit_headers.py` with RateLimitHeadersMiddleware
  - [ ] Implement middleware to add X-RateLimit-\* headers to all responses
  - [ ] Register middleware in app factory
  - [ ] Update common dependencies to ensure limiter info is in request state

- [ ] **Endpoint Exemption Configuration**
  - [ ] Define NON_COUNTING_ENDPOINTS in app/api/routes/health/**init**.py
  - [ ] Update rate limiter config to support endpoint exemptions
  - [ ] Add non-counting pattern to rate limit middleware
  - [ ] Test exemption patterns work correctly

### Frontend Changes

- [ ] **Enhanced Rate Limit Service**

  - [ ] Add client-side caching to rateLimitService.ts
  - [ ] Implement extractRateLimitHeaders function
  - [ ] Create updateRateLimitCache utility
  - [ ] Add helper to map API endpoints to rate limit categories

- [ ] **Improved Rate Limit Hook**

  - [ ] Update useRateLimits hook to use cache
  - [ ] Add decrementRateLimit function for optimistic updates
  - [ ] Implement resetRateLimits function
  - [ ] Add endpoint-specific limit access helpers

- [ ] **API Client Enhancement**

  - [ ] Update apiClient to extract rate limit headers from all responses
  - [ ] Modify API response handlers to update rate limit cache
  - [ ] Add specific error handling for rate limit errors
  - [ ] Update error display with rate limit recovery information

- [ ] **UI Components Update**
  - [ ] Modify RateLimitDisplay component to use enhanced hook
  - [ ] Implement optimistic updates in UI
  - [ ] Add visual indicators for rate limit status
  - [ ] Improve error messaging for rate limit violations

## Supabase Anonymous Auth Migration

- [ ] **Database Schema Migration**

  - [x] Create new concepts table with user_id instead of session_id
  - [x] Create new color_variations table
  - [x] Set up RLS policies for concepts table
  - [x] Set up RLS policies for color_variations table
  - [x] Create storage bucket policies for concept-images and palette-images
  - [ ] Create indexes for performance optimization

- [ ] **Backend Changes**

  - [ ] **Authentication Integration**

    - [x] Create SupabaseAuthClient in app/core/supabase/client.py
      - [x] Add JWT token verification methods
      - [x] Add user extraction from request headers
      - [x] Add error handling for auth failures
    - [x] Create auth middleware for FastAPI in app/api/middleware/auth_middleware.py
      - [x] Implement request processing to extract and verify tokens
      - [x] Add public paths exclusion logic
      - [x] Set user information in request state
    - [x] Update app/core/factory.py to register auth middleware
    - [x] Add JWT secret to app/core/config.py
    - [x] Create app/core/exceptions.py AuthenticationError class

  - [ ] **API Dependency Updates**

    - [x] Create app/api/middleware/auth_middleware.py:
      - [x] Create get_current_user dependency to extract user from request state
      - [x] Create get_current_user_id helper to get user ID
      - [x] Update CommonDependencies to include user information
      - [x] Remove get_or_create_session dependency

  - [ ] **Storage Service Updates**

    - [x] Update app/core/supabase/concept_storage.py:
      - [x] Modify all methods to use user_id instead of session_id
      - [x] Update query filters to use user_id
    - [x] Update app/core/supabase/image_storage.py:
      - [x] Update storage paths to include user_id
      - [x] Modify permissions handling for user-specific access
    - [x] Update app/services/storage/concept_storage.py:
      - [x] Replace session_id parameters with user_id
      - [x] Update storage methods to work with user_id

  - [ ] **Route Handler Updates**

    - [x] Create app/api/routes/auth/auth_routes.py:
      - [x] Add signin-anonymous endpoint
      - [x] Add refresh token endpoint
      - [x] Add signout endpoint
    - [x] Create app/api/routes/auth/**init**.py
    - [x] Update app/api/router.py to include auth routes
    - [x] Update app/api/routes/concept_storage/storage_routes.py:
      - [x] Replace session_id cookie with user dependency
      - [x] Update route handlers to use user_id
    - [x] Update app/api/routes/concept/generation.py and refinement.py:
      - [x] Replace session handling with user authentication
      - [x] Update endpoints to use user_id
    - [x] Remove app/api/routes/session/ directory entirely
    - [x] Update app/api/router.py to remove session routes

  - [ ] **Model Updates**

    - [x] Update app/models/concept/domain.py to use user_id
    - [x] Update app/models/concept/request.py and response.py as needed
    - [x] Remove app/models/session/ directory

  - [ ] **Utility Updates**

    - [x] Update app/utils/api_limits to use user_id for rate limiting
    - [x] Enhance app/utils/jwt_utils.py for Supabase JWT verification

  - [ ] **Clean Up Legacy Session Code**
    - [x] Remove `backend/app/services/session/` directory
    - [x] Remove `backend/app/core/supabase/session_storage.py`
    - [x] Remove references from SVG converter
    - [x] Remove SessionServiceInterface
    - [x] Remove test_session_service.py
    - [x] Update rate limiter to use user_id instead of session_id

- [x] **Frontend Changes**

  - [x] **Supabase Auth Client Enhancement**

    - [x] Update src/services/supabaseClient.ts:
      - [x] Add signInAnonymously function
      - [x] Create initializeAnonymousAuth function
      - [x] Add getUserId, isAnonymousUser, and other auth utilities
      - [x] Improve error handling for auth operations

  - [x] **Auth Context Implementation**

    - [x] Create src/contexts/AuthContext.tsx:
      - [x] Implement context provider with auth state management
      - [x] Add auth state listener with Supabase
      - [x] Create useAuth hook for components
    - [x] Update src/contexts/ConceptContext.tsx:
      - [x] Remove session synchronization logic
      - [x] Use auth context for user identity

  - [x] **API Client Updates**

    - [x] Update src/services/apiClient.ts:
      - [x] Add auth token handling in requests
      - [x] Create convenience methods (get, post, put, delete)
      - [x] Implement auth-specific error handling
    - [x] Update src/hooks/useApi.ts:
      - [x] Use auth tokens instead of cookies
      - [x] Update error handling for auth failures

  - [x] **Component Updates**

    - [x] Update src/App.tsx:
      - [x] Replace session initialization with auth initialization
      - [x] Add AuthProvider to component tree
      - [x] Remove session debugging code
    - [x] Update src/features components:
      - [x] landing/LandingPage.tsx - Use auth instead of session
      - [x] concepts/detail/ConceptDetailPage.tsx - Use user_id
      - [x] concepts/recent/RecentConceptsPage.tsx - Use user_id
      - [x] refinement/RefinementPage.tsx - Use user_id
    - [x] Update src/hooks components:
      - [x] useConceptGeneration.ts - Use auth context
      - [x] useConceptRefinement.ts - Use auth context

  - [x] **Type Updates**

    - [x] Update src/types/api.types.ts to include auth types
    - [x] Update src/types/concept.types.ts to use user_id instead of session_id
    - [x] Add auth-specific types (User, Session, etc.)

  - [x] **Session Cleanup**
    - [x] Remove src/services/sessionManager.ts
    - [x] Update any imports referencing sessionManager
    - [x] Clean up session cookie usage throughout the app

## Backend Refactoring and Production Preparation

- [ ] **Security Improvements**

  - [ ] Remove API keys and sensitive information from .env files and use environment variables [LATER]
  - [ ] Create a secrets management strategy for production deployment [LATER]
  - [x] Implement proper rate limiting on API endpoints
  - [ ] Add CSRF protection for authenticated endpoints (when implemented) [LATER]
  - [x] Audit backend dependencies for security vulnerabilities
  - [x] Update JigsawStack client error handling to prevent exposing sensitive information
  - [x] **Migrate from Public URLs to Signed URLs for Supabase Storage**
    - [x] Create new `get_signed_url` method in `ImageStorageService` with 3-day expiration (259200 seconds)
    - [x] Remove `get_public_url` method and update all callers to use `get_signed_url` directly
    - [x] Update all internal service calls to use the new method without fallbacks
    - [x] Update JWT token creation with 3-day expiration to match file retention policy
    - [x] Add validation to ensure storage buckets are configured as private
    - [x] Update frontend API client to use signed URLs exclusively (remove public URL functions)
    - [x] Update image loading components to handle token expiration
    - [x] Remove all public URL access patterns from the codebase
    - [x] Add audit logging for URL access patterns
    - [x] Implement proper caching strategy for signed URLs in frontend

- [ ] **Directory Structure Refinement**

  - [x] **API Routes Refactoring** (COMPLETED)

    - [x] Split concept.py (469 lines) into separate modules:
      - [x] Implemented package structure in concept/ directory
      - [x] Created concept/generation.py module for concept generation endpoints
      - [x] Created concept/refinement.py module for concept refinement endpoints
      - [x] Added concept/**init**.py to expose the router
      - [x] Extracted common rate limiting logic to a utility module
    - [x] Split health.py (401 lines) into separate modules:
      - [x] Created health/ directory with package structure
      - [x] Created health/check.py module for health check endpoint
      - [x] Created health/limits.py module for rate limit checking functionality
      - [x] Created health/utils.py for shared utility functions
      - [x] Added health/**init**.py to combine routers
    - [x] Split svg_conversion.py (304 lines) into more focused modules:
      - [x] Created svg/ directory with package structure
      - [x] Created svg/converter.py module for SVG conversion endpoint
      - [x] Created svg/utils.py module for shared utility functions
      - [x] Added svg/**init**.py to combine routers
    - [x] Organize remaining route files into subdirectories:
      - [x] Create session/ directory with package structure
      - [x] Move session.py into session/ directory
      - [x] Create session/**init**.py to expose the router
      - [x] Create concept_storage/ directory with package structure
      - [x] Move concept_storage.py into concept_storage/ directory
      - [x] Create concept_storage/**init**.py to expose the router
    - [x] Move utility modules to appropriate locations:
      - [x] Move rate_limiting.py from api/routes/ to app/utils/ since it's shared across routes
      - [x] Update imports in all files that use rate_limiting.py
    - [x] Reorganize API structure to match the architecture guidelines:
      - [x] Create api/dependencies.py with shared dependency functions
      - [x] Create api/errors.py with custom error handling
      - [x] Move API route registration from **init**.py to a dedicated router.py file

  - [ ] **1. Utils and Main Refactoring** (CURRENT FOCUS)

    - [x] Refactor main.py (145 lines) to improve structure:
      - [x] Extract PrioritizationMiddleware to a dedicated module in core/middleware/prioritization.py
      - [x] Create core/middleware/**init**.py to expose middleware
      - [x] Move application setup code to a factory function in app/core/factory.py
      - [x] Fix linting errors (add proper spacing between functions, fix unused imports)
      - [x] Improve type hints and docstrings
    - [x] Organize utils directory following the project structure:
      - [x] Create logging/ directory:
        - [x] Move logging.py content to logging/setup.py
        - [x] Create logging/**init**.py to expose setup function
      - [x] Create api_limits/ directory:
        - [x] Move rate_limiting.py to api_limits/endpoints.py
        - [x] Create api_limits/**init**.py to expose rate limiting functions
      - [x] Create security/ directory:
        - [x] Move mask.py to security/mask.py
        - [x] Create security/**init**.py to expose masking functions
      - [x] Create placeholder directories with proper **init**.py files:
        - [x] Create validation/ directory with **init**.py
        - [x] Create data/ directory with **init**.py
      - [x] Update utils/**init**.py to provide a clean interface to utility functions
    - [x] Update import paths across the codebase:
      - [x] Fix imports in API routes that use utils.rate_limiting
      - [x] Fix imports in any files that use utils.logging
      - [x] Fix imports in any files that use utils.mask
    - [ ] Add comprehensive tests for utils modules:
      - [ ] Write tests for logging setup
      - [ ] Write tests for rate limiting functions
      - [ ] Write tests for masking utilities

  - [ ] **2. Core Module Refactoring** (COMPLETED)

    - [x] Refactor `supabase.py` into smaller modules
      - [x] Create `supabase/` directory with proper package structure
      - [x] Extract `client.py` for core client functionality
      - [x] Extract `session_storage.py` for session management
      - [x] Extract `concept_storage.py` for concept storage
      - [x] Extract `image_storage.py` for image handling
      - [x] Create `__init__.py` to provide a clean interface
      - [x] Update imports across codebase to use new modules
      - [x] Remove original supabase.py file
    - [x] Refactor `rate_limiter.py` into better organized modules
      - [x] Create `limiter/` directory with proper package structure
      - [x] Extract `config.py` for core limiter configuration
      - [x] Extract `redis_store.py` for Redis integration
      - [x] Extract `keys.py` for key generation operations
      - [x] Extract `decorators.py` for rate limiting decorators
      - [x] Create `__init__.py` to provide a clean interface
      - [x] Update imports across codebase to use new modules
    - [x] Create domain-specific exceptions for core modules
      - [x] Create `exceptions.py` for custom exception classes
      - [x] Define domain-specific exception hierarchy
      - [x] Add proper exception handling to FastAPI app
      - [x] Update services to use domain-specific exceptions
      - [x] Improve error messages and documentation
    - [x] Ensure proper error handling and logging throughout core modules
      - [x] Add appropriate try/except blocks
      - [x] Use specific exception types
      - [x] Include detailed logging
      - [x] Update `supabase/client.py` to use proper error handling
      - [x] Update `limiter/redis_store.py` for better error handling
      - [x] Improve error handling in configuration module
      - [x] Enhance middleware error handling

  - [ ] **3. Service Layer Refactoring** (AFTER CORE)

    - [x] Refactor concept_service.py (370 lines) into smaller modules:
      - [x] Create concept/ directory with package structure
      - [x] Create concept/**init**.py to expose service functionality
      - [x] Extract generation.py module for concept generation
      - [x] Extract refinement.py module for concept refinement
      - [x] Extract palette.py module for palette generation and color operations
      - [x] Update imports in all files that use concept_service
    - [x] Refactor image_service.py (261 lines) and image_processing.py (311 lines):
      - [x] Create image/ directory with package structure
      - [x] Create image/**init**.py to expose service functionality
      - [x] Extract processing.py module for image processing operations
      - [x] Extract storage.py module for image storage operations
      - [x] Extract conversion.py module for format conversion operations
      - [x] Create service.py module implementing ImageServiceInterface
      - [x] Update imports in all files that use image_service and image_processing
    - [x] Refactor session_service.py (217 lines):
      - [x] Create session/ directory with package structure
      - [x] Create session/**init**.py to expose service functionality
      - [x] Extract manager.py module for session management operations
      - [x] Update imports in all files that use session_service
    - [x] Organize jigsawstack/ module:
      - [x] Ensure proper structure with client.py and appropriate submodules
      - [x] Clean up and optimize JigsawStackClient implementation
    - [x] Create interfaces/ directory for service abstractions:
      - [x] Create interfaces/**init**.py
      - [x] Create interfaces/concept_service.py with base interface
      - [x] Create interfaces/storage_service.py with base interface
      - [x] Create interfaces/image_service.py with base interface
      - [x] Create interfaces/session_service.py with base interface
    - [x] Implement storage/ directory for storage services:
      - [x] Create storage/ directory structure
      - [x] Create storage/**init**.py to expose storage functionality
      - [x] Move concept_storage_service.py to storage/concept_storage.py
      - [x] Refactor as needed for proper separation of concerns
    - [x] Improve separation of concerns in all service modules

      - [x] Ensure services depend on interfaces rather than implementations
      - [x] Use dependency injection to connect components
      - [x] Improve error handling patterns
      - [x] Add comprehensive unit tests for refactored services

    - [ ] **Further Service Refactoring - Large Modules** (NEW FOCUS)

      - [ ] **Image Service Modules** (High Priority)

        - [ ] Create ImageGenerationService for JigsawStack image generation
        - [ ] Create ImageTransformationService for processing operations
        - [ ] Create ImageStorageService to handle storage operations
        - [ ] Update ImageService to use composition with these specialized services
        - [ ] Create StorageClient for low-level operations
        - [ ] Create MetadataService for managing image metadata
        - [ ] Create PermissionsService for access control
        - [ ] Create ColorProcessor for palette and color operations
        - [ ] Create ImageTransformer for non-color transformations
        - [ ] Create FilterService for applying visual filters
        - [ ] Create FormatConverter for basic format conversions
        - [ ] Create SVGProcessor for vector-specific operations
        - [ ] Create EnhancementService for image enhancement operations

      - [ ] **JigsawStack Client Refactoring** (High Priority)

        - [ ] Create BaseJigsawClient for authentication and common request handling
        - [ ] Create JigsawImageClient for image generation operations
        - [ ] Create JigsawPaletteClient for color palette operations
        - [ ] Create JigsawRefinementClient for image refinement operations
        - [ ] Extract common utilities into a separate jigsawstack/utils.py module
        - [ ] Create proper interfaces for each client type
        - [ ] Update service dependencies to use the appropriate specialized clients

      - [ ] **Session and Storage Services** (Medium Priority)

        - [ ] Create SessionAuthService for authentication aspects
        - [ ] Create SessionPersistenceService for storage operations
        - [ ] Create SessionLifecycleService for creation/expiration
        - [ ] Create PaletteStorageService for palette-specific operations
        - [ ] Create ConceptQueryService for retrieval operations
        - [ ] Extract common utilities to a storage/utils.py module

      - [ ] **Common Refactoring Tasks**
        - [ ] Create comprehensive interfaces for all services
        - [ ] Implement better error handling and logging
        - [ ] Update dependency injection to use new services
        - [ ] Add unit tests for all new service components
        - [ ] Create integration tests to verify service interactions
        - [ ] Update documentation to reflect new service structure

    - [x] **4. Models Refactoring** (FINAL LAYER)

      - [x] Organize models into domain-specific modules:
        - [x] Create concept/ directory for concept-related models
        - [x] Create session/ directory for session-related models
        - [x] Create svg/ directory for SVG-related models
        - [x] Create common/ directory for shared model components
        - [x] Ensure proper validation and documentation for all models

    - [ ] **Code Quality**
      - [ ] Organize imports consistently and fix import patterns:
        - [x] Updated direct router imports in **init**.py for cleaner organization
        - [ ] Sort imports using isort pattern: stdlib, third-party, local
        - [ ] Use consistent relative vs. absolute imports across files
      - [ ] Remove unused imports and code from all files
      - [ ] Reorganize tests to match current structure
        - [ ] Create test fixtures directory
        - [ ] Add tests for refactored modules

- [ ] **Error Handling Improvements**

  - [x] Implement centralized error handler middleware
  - [x] Create custom exception classes
  - [x] Add proper error responses with consistent format
  - [ ] Improve logging for better debugging of production issues

- [ ] **Performance Optimization**

  - [ ] Add caching layer for frequently accessed resources
  - [ ] Optimize image processing operations
  - [ ] Profile API endpoints and optimize bottlenecks
  - [ ] Implement async task processing for long-running operations

- [ ] **Background Task Implementation for Vercel Deployment**

  - [ ] Create Supabase table for task tracking
  - [ ] Add task_status endpoint for checking task status
  - [ ] Update concept.py to use BackgroundTasks for generation
  - [ ] Implement task service for managing background jobs
  - [ ] Create vercel.json configuration with cron jobs
  - [ ] Add vercel_app.py entry point
  - [ ] Set up cron endpoint for processing timed-out tasks
  - [ ] Test background task functionality with multiple concurrent users
  - [ ] Add task status polling in frontend

- [ ] **Documentation**

  - [x] Create central docs/ directory with subdirectories for backend/ and frontend/
  - [x] Create API route documentation:
    - [x] Document concept endpoints
    - [x] Document concept_storage endpoints
    - [x] Document session endpoints
    - [x] Document health endpoints
    - [x] Document svg endpoints
  - [ ] Create service layer documentation:
    - [ ] Document concept_service
    - [ ] Document concept_storage_service
    - [ ] Document image_service and image_processing
    - [ ] Document session_service
    - [ ] Document jigsawstack client
  - [ ] Create core module documentation:
    - [ ] Document configuration management
    - [ ] Document rate limiter implementation
    - [ ] Document Supabase integration
    - [ ] Document error handling patterns
  - [ ] Create models documentation:
    - [ ] Document request models
    - [ ] Document response models
    - [ ] Document domain models
  - [ ] Create utils documentation:
    - [ ] Document logging utilities
    - [ ] Document masking utilities
    - [ ] Document rate limiting utilities
  - [ ] Create deployment documentation:
    - [ ] Document environment setup
    - [ ] Document configuration options
    - [ ] Document deployment process
  - [ ] Create developer guide:
    - [ ] Document development environment setup
    - [ ] Document testing procedures
    - [ ] Document code style and architecture guidelines
  - [ ] Update Swagger/OpenAPI documentation with detailed descriptions

- [ ] **Testing Improvements**

  - [ ] Add integration tests for API endpoints
  - [ ] Increase test coverage
  - [ ] Add performance tests
  - [ ] Create test fixtures and helper functions

- [ ] **API Refactoring Improvements**
  - [x] Create centralized dependencies module for route handlers
  - [x] Implement a consistent error handling pattern
  - [x] Refactor route handlers to use new dependency and error modules
  - [x] Continue refactoring remaining route handlers
    - [x] Refactor concept_storage/storage_routes.py handlers
    - [x] Refactor concept/generation.py handlers
    - [x] Refactor concept/refinement.py handlers
    - [x] Refactor session/session_routes.py handlers
    - [x] Refactor health check module handlers
    - [x] Refactor svg module handlers
  - [ ] Add integration tests for new error handling patterns
  - [ ] Document new dependency and error handling patterns

## Code Quality Improvements

- [ ] Fix linter errors across the codebase:
  - [ ] Fix spacing between functions (two blank lines needed)
  - [ ] Fix line length issues in docstrings and comments
  - [ ] Fix unused imports
- [ ] Refactor large functions:
  - [x] Extract rate limiting logic from concept.py endpoints into separate helper functions
    - [x] Created rate_limiting.py utility module for common rate limiting functions
    - [ ] Consider moving rate_limiting.py to app/core/ as it's a cross-cutting concern
  - [ ] Reduce complexity in \_get_limit_info() in health.py
  - [ ] Refactor error handling patterns in service classes
- [ ] Standardize error handling throughout the codebase:
  - [ ] Create custom exception classes for different error categories
  - [ ] Implement consistent error response format
  - [ ] Add more descriptive error messages for API users
- [ ] Improve docstrings consistency:
  - [ ] Ensure all public functions have complete docstrings with Args, Returns, Raises
  - [ ] Add module-level docstrings for all new modules
- [ ] Extract duplicated code into shared utility functions:
  - [ ] Consolidate rate limiting code
  - [ ] Create shared validation helpers
- [ ] Apply SRP (Single Responsibility Principle) more rigorously:
  - [ ] Move rate limiting logic out of route handlers
  - [ ] Separate HTTP concerns from business logic in services
- [ ] Add type hints for all function parameters and return values
- [ ] Add more detailed logging throughout the codebase
- [ ] Update variable naming for clarity:
  - [ ] Rename variables with more descriptive names (e.g., 'e' to 'error')
  - [ ] Use consistent naming patterns across all modules

Future

- Consider Implementing Background Tasks:
  For long-running operations, use FastAPI's BackgroundTasks
  Or implement a task queue system like Celery with Redis

- update other structures now
- Autoclear storage buckets every day
- Tests
- Setup Github Workflows
- Clean up Code
- Make sure no .env files are leaked
- Setup for Deployment
- Setup Docs
- Security Audit

## Concept Visualizer - Current Status

### Testing Progress

- [x] UI Component Tests: Fixed and passing
  - [x] Button, Card, Input, TextArea components
  - [x] Header, Footer components
  - [x] ColorPalette component
- [x] Concept Component Tests: Fixed and passing
  - [x] ConceptForm component
  - [x] ConceptRefinementForm component
  - [x] ConceptResult component
- [x] Feature Component Tests: Fixed and passing
  - [x] ConceptGenerator component
  - [x] ConceptRefinement component
  - [x] Home component
  - [x] ~~TestHeader component~~ (Removed: TestHeader component and tests were removed to clean up the codebase)
- [x] Hook Tests: Fixed and passing
  - [x] useApi hook
  - [x] useConceptGeneration hook
  - [x] useConceptRefinement hook

### Code Refactoring Progress

- [x] CSS Refactoring
  - [x] Combined header-fix.css and header.module.css into a single file
  - [x] Converted Header component from inline styles to CSS modules
  - [x] Improved organization and documentation in CSS files
- [x] Backend API Refactoring
  - [x] Concept API Routes Refactoring
    - [x] Restructured concept.py into concept/ package with specialized modules
    - [x] Created utility module for rate limiting logic
    - [x] Updated imports to use explicit router naming convention
  - [x] Health API Routes Refactoring
    - [x] Created health/ directory with specialized modules
    - [x] Extracted functions into separate modules based on responsibility
    - [x] Improved organization with shared utility functions
  - [x] SVG Conversion API Routes Refactoring
    - [x] Created svg/ directory with specialized modules
    - [x] Created svg/converter.py module for SVG conversion endpoint
    - [x] Created svg/utils.py module for shared utility functions
    - [x] Added svg/**init**.py to combine routers

### Next Steps

- [x] Implement API mock service for better integration tests
- [x] Set up end-to-end testing with Playwright
- [x] Add responsive design tests
- [x] Add visual regression tests
- [x] Add accessibility testing

## Project Management

- [ ] Set up GitHub repository
- [ ] Configure GitHub Actions for CI/CD
  - [ ] Set up continuous integration for frontend tests
  - [ ] Create workflow for backend tests
  - [ ] Configure deployment pipeline
- [ ] Create issue templates
- [ ] Define release process

# Concept Visualizer - Development Roadmap

## Phase 1: Basic Setup and Core Functionality ✅

- [x] Set up React project with TypeScript
- [x] Create responsive UI layout
- [x] Implement ConceptInput component
- [x] Set up API service
- [x] Connect to backend
- [x] Display generated results
- [x] Implement basic session management

## Phase 2: Enhanced Features and Polish ✅

- [x] Add routing system with React Router
  - [x] Create routes for Home, Create, View Concept, etc.
  - [x] Implement navigation between routes
- [x] Implement concept storage and retrieval
  - [x] Create database schema
  - [x] Build API endpoints
  - [x] Implement client-side storage service
- [x] Create landing page with recent concepts
- [x] Build concept detail view
- [x] Add concept refinement capabilities
- [x] Implement loading states and error displays ✅
  - [x] Create LoadingIndicator component
  - [x] Create ErrorMessage component
  - [x] Implement toast notification system
  - [x] Add skeleton loaders for content
  - [x] Create useErrorHandling hook
  - [x] Add React Error Boundaries for component-level error handling ✅
  - [x] Create network status monitoring with offline support ✅
- [x] Improve UI/UX design
  - [x] Enhance typography and color scheme
  - [x] Add animations for transitions and loading states
  - [x] Optimize for mobile and desktop views

## Phase 3: Advanced Features 🚧

- [ ] Implement user authentication
  - [ ] Create login/signup forms
  - [ ] Add OAuth options
  - [ ] Build secure session management
- [ ] Add user collections/folders
  - [ ] Create collection management UI
  - [ ] Implement backend storage for collections
  - [ ] Add drag-and-drop organization
- [ ] Implement sharing features
  - [ ] Generate shareable links
  - [ ] Add social media sharing
  - [ ] Create collaborative editing options
- [ ] Build advanced search and filtering
  - [ ] Implement full-text search
  - [ ] Add tag-based filtering
  - [ ] Create sorting options
- [ ] Integrate analytics and user feedback
  - [ ] Track usage patterns
  - [ ] Implement feedback forms
  - [ ] Create A/B testing framework

## Phase 4: Production Deployment and DevOps 🚧

- [ ] **Backend Production Preparation**
  - [ ] Implement secure environment variable management
  - [ ] Configure proper CORS for production domains
  - [ ] Set up production-appropriate logging levels
  - [ ] Optimize FastAPI application for production
  - [ ] Create separate development/staging/production configurations
- [ ] **Frontend Production Optimization**
  - [ ] Optimize bundle size with code splitting
  - [ ] Configure proper caching strategies
  - [ ] Implement performance monitoring
  - [ ] Create optimized Docker build for production
- [ ] **Infrastructure Setup**
  - [ ] Create infrastructure as code (Terraform/Pulumi)
  - [ ] Set up monitoring and alerting
  - [ ] Configure automated backups
  - [ ] Implement CDN for static assets
- [ ] **CI/CD Pipeline**
  - [ ] Set up GitHub Actions for automated testing
  - [ ] Configure automated deployment workflows
  - [ ] Implement canary/blue-green deployment strategy
  - [ ] Create rollback mechanisms
- [ ] **Post-Deployment**
  - [ ] Implement web analytics
  - [ ] Set up error monitoring
  - [ ] Create performance dashboards
  - [ ] Configure uptime monitoring
