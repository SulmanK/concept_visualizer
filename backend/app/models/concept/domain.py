"""
Domain models for concept-related data structures.

This module defines the Pydantic models for concepts, color palettes,
and related data structures used within the application domain.
"""

from pydantic import Field
from typing import List, Optional
from datetime import datetime
import uuid

from ..common.base import APIBaseModel


class ColorPalette(APIBaseModel):
    """Model for a color palette."""
    
    name: str = Field(..., description="Name of the palette")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_url: Optional[str] = Field(None, description="URL to the palette image")
    image_path: Optional[str] = Field(None, description="Storage path for the palette image")


class ConceptSummary(APIBaseModel):
    """Model for a concept summary (used in list views)."""
    
    id: uuid.UUID = Field(..., description="Unique identifier for the concept")
    created_at: datetime = Field(..., description="Creation timestamp")
    logo_description: str = Field(..., description="Description of the logo")
    theme_description: str = Field(..., description="Description of the theme/color scheme")
    image_url: str = Field(..., description="URL to the concept image")
    image_path: str = Field(..., description="Storage path for the concept image")
    color_variations: List[ColorPalette] = Field(..., description="Color variations for this concept")


class ConceptDetail(APIBaseModel):
    """Model for detailed concept information."""
    
    id: uuid.UUID = Field(..., description="Unique identifier for the concept")
    created_at: datetime = Field(..., description="Creation timestamp")
    session_id: uuid.UUID = Field(..., description="ID of the session that created this concept")
    logo_description: str = Field(..., description="Description of the logo")
    theme_description: str = Field(..., description="Description of the theme/color scheme")
    image_url: str = Field(..., description="URL to the concept image")
    image_path: str = Field(..., description="Storage path for the concept image")
    color_variations: List[ColorPalette] = Field(..., description="Color variations for this concept")


class ConceptCreate(APIBaseModel):
    """Model for creating a new concept."""
    
    session_id: uuid.UUID = Field(..., description="ID of the session creating this concept")
    logo_description: str = Field(..., description="Description of the logo")
    theme_description: str = Field(..., description="Description of the theme/color scheme")
    image_path: str = Field(..., description="Storage path for the concept image")
    image_url: Optional[str] = Field(None, description="URL to the concept image")
    

class ColorVariationCreate(APIBaseModel):
    """Model for creating a new color variation."""
    
    concept_id: uuid.UUID = Field(..., description="ID of the concept this variation belongs to")
    palette_name: str = Field(..., description="Name of the palette")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_path: str = Field(..., description="Storage path for the variation image") 
    image_url: Optional[str] = Field(None, description="URL to the variation image") 