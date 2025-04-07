"""
Models for concept-related data structures.

This module defines the Pydantic models for concepts, color palettes,
and related data structures.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid


class ColorPalette(BaseModel):
    """Model for a color palette."""
    
    name: str
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = None
    image_url: Optional[str] = None
    image_path: Optional[str] = None


class ConceptSummary(BaseModel):
    """Model for a concept summary (used in list views)."""
    
    id: uuid.UUID
    created_at: datetime
    logo_description: str
    theme_description: str
    base_image_url: str
    image_path: str
    color_variations: List[ColorPalette]


class ConceptDetail(BaseModel):
    """Model for detailed concept information."""
    
    id: uuid.UUID
    created_at: datetime
    user_id: uuid.UUID
    logo_description: str
    theme_description: str
    base_image_url: str
    image_path: str
    color_variations: List[ColorPalette]
    is_anonymous: Optional[bool] = True


class ConceptCreate(BaseModel):
    """Model for creating a new concept."""
    
    user_id: uuid.UUID
    logo_description: str
    theme_description: str
    image_path: str
    is_anonymous: Optional[bool] = True


class ColorVariationCreate(BaseModel):
    """Model for creating a new color variation."""
    
    concept_id: uuid.UUID
    palette_name: str
    colors: List[str]
    description: Optional[str] = None
    image_path: str 