# API Routes

This documentation provides an overview of the API routes in the Concept Visualizer application.

## Overview

The `routes` directory contains all the route definitions for the API endpoints. Routes are organized by domain or feature area, with each subdirectory containing related endpoints.

## Route Categories

| Category                                             | Directory          | Description                                  |
| ---------------------------------------------------- | ------------------ | -------------------------------------------- |
| [Authentication](auth/auth_routes.md)                | `auth/`            | User authentication and session management   |
| [Concept Generation](concept/generation.md)          | `concept/`         | Generate and refine concepts                 |
| [Concept Storage](concept_storage/storage_routes.md) | `concept_storage/` | Store and retrieve concepts                  |
| [Export](export/export_routes.md)                    | `export/`          | Export concepts to different formats         |
| [Health](health/endpoints.md)                        | `health/`          | API health checks and rate limit information |
| [Task](task/routes.md)                               | `task/`            | Background task management                   |

## Route Structure

Each route module follows a consistent structure:

1. **Router Definition**: Each module defines a FastAPI router
2. **Route Handlers**: Functions decorated with `@router.get()`, `@router.post()`, etc.
3. **Dependency Injection**: Routes use dependencies for service injection
4. **Request Validation**: Input is validated using Pydantic models
5. **Error Handling**: Consistent error handling patterns

## Example Route Definition

```python
from fastapi import APIRouter, Depends, HTTPException
from app.api.dependencies import CommonDependencies
from app.models.concept.request import ConceptRequest
from app.models.concept.response import ConceptResponse

router = APIRouter()

@router.post("/generate", response_model=ConceptResponse)
async def generate_concept(
    request: ConceptRequest,
    deps: CommonDependencies = Depends()
):
    """
    Generate a new concept based on the provided description.
    """
    try:
        return await deps.concept_service.generate_concept(request.description)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## Route Naming Conventions

Routes follow these naming conventions:

- **Resource-based Paths**: Routes are named after the resources they manipulate
- **HTTP Verbs**: Appropriate HTTP methods are used (GET, POST, PUT, DELETE)
- **Plural Nouns**: Resource collections use plural nouns (e.g., `/concepts`)
- **Nested Resources**: Related resources use nested paths (e.g., `/concepts/{id}/refinements`)

## Common Route Patterns

### Collection and Item Operations

```
GET /resources          # List resources
POST /resources         # Create a resource
GET /resources/{id}     # Get a specific resource
PUT /resources/{id}     # Update a resource
DELETE /resources/{id}  # Delete a resource
```

### Search and Filtering

```
GET /resources?query=term&filter=value
```

### Related Resources

```
GET /resources/{id}/related-items
```

## Authentication Requirements

Most routes require authentication via the AuthMiddleware. Exceptions include:

- Health check endpoints
- Authentication endpoints
- Documentation endpoints

## Rate Limiting

Routes are subject to rate limiting as defined in the rate limit middleware. See the [Rate Limit Apply Middleware](../middleware/rate_limit_apply.md) documentation for details.
