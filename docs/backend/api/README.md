# API Layer Documentation

The API layer handles HTTP requests/responses, routing, and input validation for the Concept Visualizer application. It is the entry point for all client interactions.

## Components

- [Dependencies](dependencies.md): Dependency injection system for routes
- [Errors](errors.md): Error handling and exception management
- [Router](router.md): Main API router and route configuration

## Subdirectories

- [Middleware](middleware/README.md): Request/response processing middleware
- [Routes](routes/README.md): API endpoints organized by domain

## Architecture

The API layer follows these principles:

1. **Separation of Concerns**: API routes should only handle HTTP concerns (request parsing, validation, response formatting) and delegate business logic to the service layer.

2. **Input Validation**: All incoming requests are validated using Pydantic models.

3. **Consistent Error Handling**: Errors are caught and formatted consistently across all endpoints.

4. **Dependency Injection**: FastAPI's dependency injection system is used to provide services and utilities to route handlers.

5. **Route Organization**: Routes are organized by domain and feature to maintain a clean structure.

## Example Usage

```python
from fastapi import APIRouter, Depends, HTTPException
from app.models.concept.request import ConceptRequest
from app.models.concept.response import ConceptResponse
from app.services.concept.service import ConceptService

router = APIRouter()

@router.post("/generate", response_model=ConceptResponse)
async def generate_concept(
    request: ConceptRequest,
    service: ConceptService = Depends()
):
    try:
        return await service.generate_concept(request.prompt)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```
