"""
Response models for the Concept Visualizer API.

This module defines Pydantic models for API responses.
"""

from typing import List, Optional

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


class GenerationResponse(BaseModel):
    """Response model for concept generation and refinement."""
    
    image_url: HttpUrl = Field(..., description="URL of the generated image")
    color_palette: ColorPalette = Field(
        ...,
        description="Generated color palette"
    )
    generation_id: str = Field(..., description="Unique ID for the generation")
    created_at: str = Field(..., description="Creation timestamp")
    
    # Optional fields for refinement responses
    original_image_url: Optional[HttpUrl] = Field(
        None,
        description="URL of the original image (for refinements)"
    )
    refinement_prompt: Optional[str] = Field(
        None,
        description="Prompt used for refinement"
    ) 