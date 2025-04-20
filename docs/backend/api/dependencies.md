# API Dependencies

This documentation covers the dependency injection system used in the Concept Visualizer API.

## Overview

The `dependencies.py` module provides FastAPI dependency functions and classes that can be used for:

- Service injection into route handlers
- User authentication and extraction
- Common functionality shared across multiple endpoints

## Key Dependencies

### User Authentication

```python
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Extract the current user from the request session."""
```

This dependency extracts user information from the request session. It returns the user data if authenticated, or `None` otherwise.

### JWT Token Processing

```python
def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Simple decode of JWT token without verification."""
```

This utility function decodes a JWT token without verifying it (primarily used for development). It extracts the payload portion and returns the decoded data.

## Common Dependencies Class

The module provides a `CommonDependencies` class that acts as a container for all frequently used dependencies:

```python
class CommonDependencies:
    """Common dependencies for API routes."""
```

### Injected Services

The `CommonDependencies` class automatically injects the following services:

- `supabase_client`: Supabase client for database operations
- `jigsawstack_client`: JigsawStack API client for AI image generation
- `concept_service`: Service for concept generation and refinement
- `concept_persistence_service`: Service for concept persistence
- `image_service`: Service for image processing
- `image_persistence_service`: Service for image persistence
- `task_service`: Service for background task management
- `export_service`: Service for exporting concepts

### User Authentication

The class also handles user authentication by:

1. Extracting the authorization header
2. Parsing JWT tokens if present
3. Extracting user information from the session
4. Providing user_id for authorized operations

## Usage Examples

### Basic Usage in Route Handlers

```python
from fastapi import APIRouter, Depends
from app.api.dependencies import CommonDependencies

router = APIRouter()

@router.get("/resource/{resource_id}")
async def get_resource(
    resource_id: str,
    deps: CommonDependencies = Depends()
):
    # Access injected services
    result = await deps.concept_service.get_concept(resource_id)
    
    # Check if user is authenticated
    if deps.user_id:
        # Perform authorized operation
        pass
        
    return result
```

### Processing Requests

The `process_request` method can be used to extract user information from the request:

```python
@router.get("/user-info")
async def get_user_info(
    request: Request,
    deps: CommonDependencies = Depends()
):
    # Process the request to extract user information
    deps.process_request(request)
    
    # Return user information
    return {"user": deps.user}
```

## Best Practices

1. **Use CommonDependencies**: Instead of injecting individual services, use the `CommonDependencies` class to access all required services.
2. **Process Requests**: Call `process_request` when you need to extract user information from the request.
3. **Check Authentication**: Always check `deps.user_id` before performing authorized operations.
4. **Security**: Remember that JWT token decoding is done without verification for development purposes. Use proper auth middleware for production. 