"""Base models for the Concept Visualizer API.

This module defines base models that provide common functionality
to be reused across other model types.
"""

from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class APIBaseModel(BaseModel):
    """Base model with common API model configuration."""

    class Config:
        """Configuration for all API models."""

        json_encoders: Dict[Any, Any] = {
            # Add any custom encoders needed across models
        }
        from_attributes = True  # For compatibility with ORM models (formerly orm_mode)
        populate_by_field_name = True  # Allow populating models by field name in addition to alias
        validate_assignment = True  # Validate when assigning values to fields


class ErrorResponse(APIBaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    status_code: int = Field(..., description="HTTP status code")
    path: Optional[str] = Field(None, description="Request path")

    class Config:
        """Error response model configuration."""

        json_schema_extra = {
            "example": {
                "detail": "Resource not found",
                "code": "NOT_FOUND",
                "status_code": 404,
                "path": "/api/concepts/123",
            }
        }  # Formerly schema_extra
