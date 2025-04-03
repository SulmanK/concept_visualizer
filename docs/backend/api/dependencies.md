# Dependency Injection

This document describes the dependency injection system used in the Concept Visualizer API.

## Overview

The application uses FastAPI's dependency injection system to:
- Provide services to API endpoints
- Centralize common dependencies
- Facilitate testing through dependency overrides
- Simplify session management

## Common Dependencies

The `app.api.dependencies` module provides a `CommonDependencies` class that bundles all commonly used services:

```python
class CommonDependencies:
    """Bundle of common dependencies used across API endpoints."""
    
    def __init__(
        self,
        concept_service: ConceptService = Depends(get_concept_service),
        image_service: ImageService = Depends(get_image_service),
        session_service: SessionService = Depends(get_session_service),
        storage_service: ConceptStorageService = Depends(get_concept_storage_service)
    ):
        self.concept_service = concept_service
        self.image_service = image_service
        self.session_service = session_service
        self.storage_service = storage_service
```

## Using Dependencies in Endpoints

Dependencies can be injected into endpoints using FastAPI's `Depends` function:

```python
@router.post("/generate")
async def generate_concept(
    request: GenerationRequest,
    commons: CommonDependencies = Depends(),
):
    result = await commons.concept_service.generate_concept(request.prompt)
    return result
```

## Session Management Dependencies

The module provides specialized dependencies for session management:

### get_session_id

Extracts and validates the session ID from cookies:

```python
async def get_session_id(
    request: Request,
    session_id: Optional[str] = Cookie(None, alias="concept_session")
) -> str:
    """Get the session ID from cookies and validate it."""
    if not session_id:
        raise AuthenticationError(detail="No session ID provided")
    return session_id
```

### get_or_create_session

Creates a new session or returns the existing one:

```python
async def get_or_create_session(
    response: Response,
    session_service: SessionService,
    session_id: Optional[str] = None,
    client_session_id: Optional[str] = None
) -> Tuple[str, bool]:
    """Get or create a session and set the cookie."""
    session_id, is_new_session = await session_service.get_or_create_session(
        response, session_id, client_session_id
    )
    return session_id, is_new_session
```

## Dependency Scopes

Dependencies can have different scopes:

1. **Request-scoped**: Created for each request (default)
2. **Application-scoped**: Created once at startup (e.g., database connections)

## Testing with Dependencies

For testing, dependencies can be overridden using FastAPI's dependency override system:

```python
# In your test file
from unittest.mock import MagicMock
from app.services.concept_service import get_concept_service

async def test_generate_concept(client):
    # Create a mock service
    mock_service = MagicMock()
    mock_service.generate_concept.return_value = {"id": "test"}
    
    # Override the dependency
    app.dependency_overrides[get_concept_service] = lambda: mock_service
    
    # Test the endpoint
    response = await client.post("/api/concept/generate", json={"prompt": "test"})
    assert response.status_code == 200
    
    # Clean up
    app.dependency_overrides = {}
```

## Best Practices

1. **Use CommonDependencies** for endpoints that need multiple services
2. **Use Specific Dependencies** for endpoints that only need one service
3. **Create Factory Functions** for services to facilitate testing
4. **Document Dependencies** in endpoint docstrings
5. **Keep Dependencies Lightweight** to avoid performance issues 