# API Routes Documentation

This directory contains documentation for the API routes in the Concept Visualizer application. The routes are organized by domain to maintain separation of concerns and improve maintainability.

## Route Structure

The API routes are organized into the following domains:

### Concept Generation and Refinement

**Directory**: `backend/app/api/routes/concept/`

These endpoints handle the generation and refinement of visual concepts:

- `POST /api/concept/generate`: Generate a new visual concept based on user input
- `POST /api/concept/generate-with-palettes`: Generate a concept with pre-generated color palettes
- `POST /api/concept/refine`: Refine an existing concept based on user feedback

### Concept Storage and Retrieval

**Directory**: `backend/app/api/routes/concept_storage/`

These endpoints handle storing and retrieving concepts:

- `POST /api/concept/store`: Store a generated concept
- `GET /api/concept/list`: List all concepts for a session
- `GET /api/concept/{concept_id}`: Get details of a specific concept

### Session Management

**Directory**: `backend/app/api/routes/session/`

These endpoints handle user sessions:

- `POST /api/session/`: Create a new session or return existing one
- `POST /api/session/sync`: Synchronize client and server session IDs

### Health Checks

**Directory**: `backend/app/api/routes/health/`

These endpoints provide health check functionality:

- `GET /api/health/`: Basic health check endpoint
- `GET /api/health/rate-limits`: Get rate limit status for current user

### SVG Conversion

**Directory**: `backend/app/api/routes/svg/`

These endpoints handle SVG conversion:

- `POST /api/svg/convert-to-svg`: Convert a raster image to SVG format
- `POST /api/svg/convert`: Alias for backward compatibility

## Common Patterns

All route modules follow these common patterns:

1. **Input Validation**: Using Pydantic models to validate request data
2. **Dependency Injection**: Using FastAPI's dependency system for service injection
3. **Error Handling**: Using custom error types for standardized error responses
4. **Rate Limiting**: Applying rate limits to prevent API abuse
5. **Logging**: Detailed logging for debugging and monitoring

## Error Handling

All routes use the custom error types defined in `app.api.errors`:

- `ValidationError`: For input validation errors
- `ResourceNotFoundError`: For missing resources
- `ServiceUnavailableError`: For service failures
- `AuthenticationError`: For authentication/session issues

## Dependencies

Routes use the common dependencies defined in `app.api.dependencies`, particularly the `CommonDependencies` class that provides access to all required services. 