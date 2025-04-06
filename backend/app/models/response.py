"""
Response models for the API.

This module defines the response models used across the API endpoints.
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, AnyUrl, field_validator
import re


class ColorPalette(BaseModel):
    """Color palette model containing hex color codes."""
    
    primary: str = Field(..., description="Primary brand color")
    secondary: str = Field(..., description="Secondary brand color")
    accent: str = Field(..., description="Accent color")
    background: str = Field(..., description="Background color")
    text: str = Field(..., description="Text color")
    additional_colors: List[str] = Field(
        default=[],
        description="Additional color options"
    )


class PaletteVariation(BaseModel):
    """Model for a color palette variation with its own image."""
    
    name: str = Field(..., description="Name of the palette variation")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_url: str = Field(..., description="URL of the image with this palette")
    
    @field_validator('image_url')
    @classmethod
    def ensure_absolute_url(cls, v):
        """Ensure the URL is absolute by adding Supabase URL if needed."""
        from app.core.config import settings
        if v and v.startswith('/object/sign/'):
            return f"{settings.SUPABASE_URL}{v}"
        return v


class GenerationResponse(BaseModel):
    """Response model for concept generation and refinement."""
    
    prompt_id: str = Field(..., description="Unique ID for the generation")
    logo_description: str = Field(..., description="The logo description prompt")
    theme_description: str = Field(..., description="The theme description prompt")
    created_at: str = Field(..., description="Creation timestamp")
    
    # For backward compatibility - points to the first variation
    image_url: str = Field(..., description="URL of the default generated image")
    color_palette: Optional[ColorPalette] = Field(
        None,
        description="Generated color palette (deprecated format, kept for backward compatibility)"
    )
    
    # New field for multiple variations
    variations: List[PaletteVariation] = Field(
        default=[],
        description="List of palette variations with distinct images"
    )
    
    # Optional fields for refinement responses
    original_image_url: Optional[str] = Field(
        None,
        description="URL of the original image (for refinements)"
    )
    refinement_prompt: Optional[str] = Field(
        None,
        description="Prompt used for refinement"
    )
    
    @field_validator('image_url', 'original_image_url')
    @classmethod
    def ensure_absolute_url(cls, v):
        """Ensure the URL is absolute by adding Supabase URL if needed."""
        if not v:
            return v
        from app.core.config import settings
        if v.startswith('/object/sign/'):
            return f"{settings.SUPABASE_URL}{v}"
        return v


class SVGConversionResponse(BaseModel):
    """Response model for SVG conversion"""
    svg_data: str = Field(..., description="SVG data as a string")
    success: bool = Field(..., description="Whether the conversion was successful")
    message: str = Field(..., description="Message about the conversion process") 