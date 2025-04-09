"""
Request model definitions.

This module contains all the request models for the Concept Visualizer API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl


class PromptRequest(BaseModel):
    """Request model for concept generation."""
    
    logo_description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Description of the logo to generate"
    )
    theme_description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Description of the theme/color scheme to use"
    )


class RefinementRequest(BaseModel):
    """Request model for concept refinement."""
    
    original_image_url: HttpUrl = Field(
        ...,
        description="URL of the original image to refine"
    )
    logo_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Updated description of the logo"
    )
    theme_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Updated description of the theme/color scheme"
    )
    refinement_prompt: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Specific instructions for refinement"
    )
    preserve_aspects: List[str] = Field(
        default=[],
        description="Aspects of the original design to preserve"
    ) 