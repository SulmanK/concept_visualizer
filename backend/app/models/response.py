"""
Response models for the Concept Visualizer API.

This module defines Pydantic models for API responses.
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, HttpUrl


class ColorPalette(BaseModel):
    """Color palette model containing hex color codes."""
    
    primary: str = Field(..., description="Primary brand color")
    secondary: str = Field(..., description="Secondary brand color")
    accent: str = Field(..., description="Accent color")
    background: str = Field(..., description="Background color")
    text: str = Field(..., description="Text color")
    additional_colors: List[str] = Field(
        default=[],
        description="Additional complementary colors"
    )


class PaletteVariation(BaseModel):
    """Model for a color palette variation with its own image."""
    
    name: str = Field(..., description="Name of the palette variation")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_url: HttpUrl = Field(..., description="URL of the image with this palette")


class GenerationResponse(BaseModel):
    """Response model for concept generation and refinement."""
    
    prompt_id: str = Field(..., description="Unique ID for the generation")
    logo_description: str = Field(..., description="The logo description prompt")
    theme_description: str = Field(..., description="The theme description prompt")
    created_at: str = Field(..., description="Creation timestamp")
    
    # For backward compatibility - points to the first variation
    image_url: HttpUrl = Field(..., description="URL of the default generated image")
    color_palette: Optional[ColorPalette] = Field(
        None,
        description="Generated color palette (legacy format)"
    )
    
    # New field for multiple variations
    variations: List[PaletteVariation] = Field(
        default=[],
        description="List of palette variations with distinct images"
    )
    
    # Optional fields for refinement responses
    original_image_url: Optional[HttpUrl] = Field(
        None,
        description="URL of the original image (for refinements)"
    )
    refinement_prompt: Optional[str] = Field(
        None,
        description="Prompt used for refinement"
    ) 