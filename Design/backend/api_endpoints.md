# API Endpoints Design Document

## Current Context

- The Concept Visualizer requires well-defined API endpoints for frontend-backend communication
- FastAPI will be used to implement these endpoints
- Two primary operations are required: generating new concepts and refining existing ones

## Requirements

### Functional Requirements

- Provide an endpoint to generate visual concepts based on text descriptions
- Provide an endpoint to refine previously generated concepts
- Support proper request validation
- Return structured responses with appropriate status codes
- Implement error handling for various failure cases

### Non-Functional Requirements

- Low latency responses (acknowledging that AI generation may take time)
- Scalable to handle multiple concurrent requests
- Secure handling of user inputs
- Well-documented API for frontend integration
- RESTful design principles

## Design Decisions

### 1. API Structure

Will implement a RESTful API structure using FastAPI:

- Clear endpoint naming reflecting actions
- Proper HTTP methods (POST for creation, PUT for refinement)
- Consistent response formats
- OpenAPI documentation generated automatically

### 2. Input Validation

Will implement comprehensive input validation using:

- Pydantic models for request validation
- Field constraints (min/max length, regex patterns)
- Custom validators where needed
- Descriptive error messages for validation failures

### 3. Error Handling

Will implement standardized error handling with:

- Global exception handlers
- Consistent error response format
- Appropriate HTTP status codes
- Detailed error messages for debugging (in development)

## Technical Design

### 1. Core API Components

```python
# backend/app/api/routes/concept.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import Optional, List
from ...models.request import PromptRequest, RefinementRequest
from ...models.response import GenerationResponse
from ...services.concept_service import ConceptService

router = APIRouter(prefix="/concept", tags=["concept"])

@router.post("/generate", response_model=GenerationResponse, status_code=201)
async def generate_concept(
    request: PromptRequest,
    concept_service: ConceptService = Depends()
):
    """Generate a new concept based on text descriptions.

    Args:
        request: The prompt request containing logo and theme descriptions
        concept_service: Injected concept service

    Returns:
        GenerationResponse containing image URL and color palettes

    Raises:
        HTTPException: On generation failure
    """
    try:
        result = await concept_service.generate_concept(
            logo_description=request.logo_description,
            theme_description=request.theme_description
        )
        return result
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate concept: {str(e)}"
        )

@router.post("/refine", response_model=GenerationResponse)
async def refine_concept(
    request: RefinementRequest,
    concept_service: ConceptService = Depends()
):
    """Refine an existing concept with additional details.

    Args:
        request: The refinement request containing the original prompt ID and additional details
        concept_service: Injected concept service

    Returns:
        GenerationResponse containing refined image URL and color palettes

    Raises:
        HTTPException: On refinement failure or if original concept not found
    """
    try:
        result = await concept_service.refine_concept(
            original_prompt_id=request.original_prompt_id,
            additional_details=request.additional_details
        )
        return result
    except ValueError as e:
        # Value errors are likely due to invalid prompt ID
        raise HTTPException(
            status_code=404,
            detail=f"Original concept not found: {str(e)}"
        )
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refine concept: {str(e)}"
        )
```

### 2. Health Check Endpoint

```python
# backend/app/api/routes/health.py
from fastapi import APIRouter
from ...models.response import HealthResponse
from ...core.config import settings

router = APIRouter(tags=["health"])

@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API health status.

    Returns:
        Health status information
    """
    return {
        "status": "ok",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT
    }
```

### 3. Router Registration

```python
# backend/app/api/routes/__init__.py
from fastapi import APIRouter
from .concept import router as concept_router
from .health import router as health_router

# Create main router
router = APIRouter()

# Include all routers
router.include_router(concept_router)
router.include_router(health_router)
```

### 4. API Setup in Main Application

```python
# backend/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .core.config import settings
from .core.exceptions import register_exception_handlers

# Create FastAPI application
app = FastAPI(
    title="Concept Visualizer API",
    description="API for generating visual concepts based on text descriptions",
    version=settings.VERSION
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
register_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix="/api")
```

## Request and Response Models

### Request Models

```python
# backend/app/models/request.py
from pydantic import BaseModel, Field

class PromptRequest(BaseModel):
    """Request model for generating a concept."""

    logo_description: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Description of the logo to generate"
    )

    theme_description: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Description of the theme/style for color palettes"
    )

    class Config:
        schema_extra = {
            "example": {
                "logo_description": "A modern tech startup logo with abstract geometric shapes",
                "theme_description": "Professional corporate theme with a touch of creativity"
            }
        }

class RefinementRequest(BaseModel):
    """Request model for refining an existing concept."""

    original_prompt_id: str = Field(
        ...,
        description="ID of the original prompt to refine"
    )

    additional_details: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Additional details to refine the concept"
    )

    class Config:
        schema_extra = {
            "example": {
                "original_prompt_id": "abc123",
                "additional_details": "Make the logo more minimalist and use blue tones"
            }
        }
```

### Response Models

```python
# backend/app/models/response.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ColorPalette(BaseModel):
    """Model for a color palette."""

    name: str = Field(..., description="Name of the color palette")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the color palette")

    class Config:
        schema_extra = {
            "example": {
                "name": "Ocean Breeze",
                "colors": ["#1A535C", "#4ECDC4", "#F7FFF7", "#FF6B6B", "#FFE66D"],
                "description": "Fresh and calming palette inspired by coastal scenes"
            }
        }

class GenerationResponse(BaseModel):
    """Response model for concept generation/refinement."""

    prompt_id: str = Field(..., description="Unique identifier for the prompt")
    image_url: str = Field(..., description="URL of the generated image")
    color_palettes: List[ColorPalette] = Field(..., description="Generated color palettes")

    class Config:
        schema_extra = {
            "example": {
                "prompt_id": "abc123",
                "image_url": "https://example.com/images/abc123.png",
                "color_palettes": [
                    {
                        "name": "Corporate Trust",
                        "colors": ["#0A1128", "#001F54", "#034078", "#1282A2", "#FEFCFB"],
                        "description": "Professional palette with reliable blue tones"
                    }
                ]
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check."""

    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")

    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "version": "0.1.0",
                "environment": "development"
            }
        }
```

## Exception Handling

```python
# backend/app/core/exceptions.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Any, Dict, Optional

class AppException(Exception):
    """Base exception for application-specific errors."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        self.status_code = status_code
        self.detail = detail
        self.headers = headers

def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the FastAPI application.

    Args:
        app: FastAPI application
    """
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail}
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "detail": "Validation error",
                "errors": exc.errors()
            }
        )

    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"detail": "An unexpected error occurred"}
        )
```

## CORS Configuration

```python
# backend/app/core/config.py
from typing import List
from pydantic import BaseSettings

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # API settings
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # Other settings...

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_api/test_routes/test_concept.py
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
from app.main import app

client = TestClient(app)

def test_generate_concept_success():
    # Mock the concept service
    with patch("app.services.concept_service.ConceptService.generate_concept") as mock_generate:
        # Setup mock return value
        mock_generate.return_value = {
            "prompt_id": "test123",
            "image_url": "https://example.com/image.png",
            "color_palettes": [
                {
                    "name": "Test Palette",
                    "colors": ["#000000", "#FFFFFF"],
                    "description": "Test description"
                }
            ]
        }

        # Make request
        response = client.post(
            "/api/concept/generate",
            json={
                "logo_description": "Test logo",
                "theme_description": "Test theme"
            }
        )

        # Assert response
        assert response.status_code == 201
        assert response.json()["prompt_id"] == "test123"
        assert len(response.json()["color_palettes"]) == 1

def test_generate_concept_validation_error():
    # Make request with invalid data
    response = client.post(
        "/api/concept/generate",
        json={
            "logo_description": "",  # Too short
            "theme_description": "Test theme"
        }
    )

    # Assert validation error
    assert response.status_code == 422
    assert "errors" in response.json()
```

## API Documentation

The API will be automatically documented using FastAPI's built-in Swagger UI and ReDoc:

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI schema: `/openapi.json`

## Future Considerations

### Potential Enhancements

- Implement pagination for retrieving multiple concepts
- Add user authentication for personal concept storage
- Support image upload for style reference
- Implement webhooks for long-running generations
- Add rate limiting to prevent abuse

### Known Limitations

- Synchronous request/response model may not be ideal for long-running generations
- Limited input validation for creative prompts
- No persistence of generated concepts beyond current session

## Dependencies

### Runtime Dependencies

- FastAPI
- Pydantic
- Starlette
- Uvicorn (for serving)
- Python-dotenv (for environment variables)

### Development Dependencies

- Pytest
- Requests (for testing)
- Black (for formatting)
- Flake8 (for linting)

## Security Considerations

- Input validation to prevent injection attacks
- CORS restrictions to allow only specified origins
- No sensitive data in responses
- Rate limiting to prevent DoS attacks

## References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [RESTful API Design Best Practices](https://restfulapi.net/)
