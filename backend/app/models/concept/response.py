"""
Response models for concept-related API endpoints.

This module defines Pydantic models for structuring responses from
concept generation and refinement endpoints.
"""

from typing import List, Optional
from pydantic import Field, HttpUrl

from ..common.base import APIBaseModel


class ColorPalette(APIBaseModel):
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


class PaletteVariation(APIBaseModel):
    """Model for a color palette variation with its own image."""
    
    name: str = Field(..., alias="palette_name", description="Name of the palette variation")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_url: HttpUrl = Field(..., description="URL of the image with this palette")


class GenerationResponse(APIBaseModel):
    """Response model for concept generation and refinement."""
    
    prompt_id: str = Field(..., description="Unique ID for the generation")
    logo_description: str = Field(..., description="The logo description prompt")
    theme_description: str = Field(..., description="The theme description prompt")
    created_at: str = Field(..., description="Creation timestamp")
    
    # For backward compatibility - points to the first variation
    image_url: HttpUrl = Field(..., description="URL of the default generated image")
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
    original_image_url: Optional[HttpUrl] = Field(
        None,
        description="URL of the original image (for refinements)"
    )
    refinement_prompt: Optional[str] = Field(
        None,
        description="Prompt used for refinement"
    )


class RefinementResponse(GenerationResponse):
    """Response model specifically for concept refinement."""
    
    original_image_url: HttpUrl = Field(..., description="URL of the original image that was refined")
    refinement_prompt: str = Field(..., description="Prompt used for refinement")
    original_concept_id: Optional[str] = Field(None, description="ID of the original concept")
    

class ConceptSummary(APIBaseModel):
    """Summary information about a concept for list views."""
    
    id: str = Field(..., description="Unique concept ID")
    created_at: str = Field(..., description="Creation timestamp")
    logo_description: str = Field(..., description="The logo description prompt")
    theme_description: str = Field(..., description="The theme description prompt")
    image_url: HttpUrl = Field(..., description="URL of the concept image")
    has_variations: bool = Field(default=True, description="Whether the concept has color variations")
    variations_count: int = Field(default=0, description="Number of available color variations")
    is_refinement: bool = Field(default=False, description="Whether this is a refinement of another concept")
    original_concept_id: Optional[str] = Field(None, description="ID of the original concept if this is a refinement")
    color_variations: List[PaletteVariation] = Field(
        default=[],
        description="List of all color variations with their images"
    )


class ConceptDetail(ConceptSummary):
    """Detailed information about a concept including all variations."""
    
    variations: List[PaletteVariation] = Field(
        default=[],
        description="List of all color variations with their images"
    )
    refinement_prompt: Optional[str] = Field(None, description="Prompt used for refinement, if applicable")
    original_image_url: Optional[HttpUrl] = Field(None, description="URL of the original image, if this is a refinement") 