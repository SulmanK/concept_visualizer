# Base Models

This documentation covers the base models used throughout the Concept Visualizer API.

## Overview

The `base.py` module in `app/models/common/` defines base models that provide common functionality to be reused across other model types in the application. These base models ensure consistent behavior and configuration for all derived models.

## Models

### APIBaseModel

```python
class APIBaseModel(BaseModel):
    """Base model with common API model configuration."""
    
    class Config:
        """Configuration for all API models."""
        
        json_encoders = {
            # Add any custom encoders needed across models
        }
        from_attributes = True  # For compatibility with ORM models (formerly orm_mode)
        populate_by_field_name = True  # Allow populating models by field name in addition to alias
        validate_assignment = True  # Validate when assigning values to fields
```

This is the base model class that all other API models in the application should inherit from. It provides the following common configurations:

1. **ORM Compatibility**: `from_attributes = True` allows converting ORM models to Pydantic models by reading attributes instead of dict keys.
2. **Field Name Flexibility**: `populate_by_field_name = True` allows populating models by both field names and aliases.
3. **Assignment Validation**: `validate_assignment = True` ensures that values assigned to model attributes are validated.
4. **Extensible JSON Encoders**: The `json_encoders` dict can be extended with custom encoders as needed.

### ErrorResponse

```python
class ErrorResponse(APIBaseModel):
    """Standard error response model."""
    
    detail: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    status_code: int = Field(..., description="HTTP status code")
    path: Optional[str] = Field(None, description="Request path")
    
    class Config:
        """Error response model configuration."""
        
        json_schema_extra = {  # Formerly schema_extra
            "example": {
                "detail": "Resource not found",
                "code": "NOT_FOUND",
                "status_code": 404,
                "path": "/api/concepts/123"
            }
        }
```

This model defines the standard error response format used throughout the API:

- `detail`: A human-readable error message describing what went wrong
- `code`: A machine-readable error code (e.g., "NOT_FOUND", "VALIDATION_ERROR")
- `status_code`: The HTTP status code associated with the error
- `path`: Optional field indicating the request path that caused the error

The model includes an example in its schema for documentation purposes.

## Usage in Models

All model classes in the application should inherit from `APIBaseModel` rather than directly from Pydantic's `BaseModel`. This ensures consistent behavior across all models.

### Example Implementation

```python
from ..common.base import APIBaseModel
from pydantic import Field
from typing import Optional, List

class ConceptModel(APIBaseModel):
    """Example model inheriting from APIBaseModel."""
    
    id: str = Field(..., description="Unique identifier")
    name: str = Field(..., description="Concept name")
    description: Optional[str] = Field(None, description="Optional description")
    tags: List[str] = Field(default=[], description="List of tags")
```

## Usage for Error Handling

The `ErrorResponse` model is used in the global exception handlers to provide consistent error responses:

```python
from fastapi import Request, status
from fastapi.responses import JSONResponse
from ..models.common.base import ErrorResponse

@app.exception_handler(NotFoundException)
async def not_found_exception_handler(request: Request, exc: NotFoundException):
    """Handle not found exceptions."""
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            detail=str(exc),
            code="NOT_FOUND",
            status_code=status.HTTP_404_NOT_FOUND,
            path=request.url.path
        ).dict()
    )
```

## Benefits

Using these base models provides several benefits:

1. **Consistency**: All models have the same configuration and behavior
2. **Maintainability**: Configuration changes can be made in one place
3. **API Documentation**: Standard error responses are well-documented
4. **Flexibility**: Easy to add common functionality to all models

## Related Files

- [Concept Models](../concept/domain.md): Domain models for concepts
- [API Errors](../../api/errors.md): API error handling
- [Exception Types](../../core/exceptions.md): Custom exception types 