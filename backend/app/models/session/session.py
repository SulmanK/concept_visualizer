"""
Session-related data models.

This module defines the Pydantic models for sessions and related structures.
"""

from typing import Optional, Dict, Any
from datetime import datetime
import uuid
from pydantic import Field

from ..common.base import APIBaseModel


class SessionBase(APIBaseModel):
    """Base session model with common attributes."""
    
    session_id: uuid.UUID = Field(..., description="Unique identifier for the session")
    created_at: datetime = Field(..., description="Session creation timestamp")
    last_active_at: datetime = Field(..., description="Last activity timestamp")
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="Client IP address")


class SessionCreate(APIBaseModel):
    """Model for creating a new session."""
    
    user_agent: Optional[str] = Field(None, description="User agent string")
    ip_address: Optional[str] = Field(None, description="Client IP address")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional session metadata")


class SessionResponse(SessionBase):
    """Response model for session information."""
    
    metadata: Dict[str, Any] = Field(default={}, description="Session metadata")
    concept_count: int = Field(default=0, description="Number of concepts created in this session")
    
    class Config:
        """Configuration for SessionResponse model."""
        
        schema_extra = {
            "example": {
                "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "created_at": "2023-01-01T00:00:00Z",
                "last_active_at": "2023-01-01T01:00:00Z",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "ip_address": "192.168.1.1",
                "metadata": {
                    "referrer": "https://example.com"
                },
                "concept_count": 5
            }
        } 