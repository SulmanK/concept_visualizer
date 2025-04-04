"""
Base models for the Concept Visualizer API.

This module defines base models that provide common functionality
to be reused across other model types.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class APIBaseModel(BaseModel):
    """Base model with common API model configuration."""
    
    class Config:
        """Configuration for all API models."""
        
        json_encoders = {
            # Add any custom encoders needed across models
        }
        orm_mode = True  # For compatibility with ORM models


class ErrorResponse(APIBaseModel):
    """Standard error response model."""
    
    detail: str = Field(..., description="Error message")
    code: str = Field(..., description="Error code")
    status_code: int = Field(..., description="HTTP status code")
    path: Optional[str] = Field(None, description="Request path")
    
    class Config:
        """Error response model configuration."""
        
        schema_extra = {
            "example": {
                "detail": "Resource not found",
                "code": "NOT_FOUND",
                "status_code": 404,
                "path": "/api/concepts/123"
            }
        } 