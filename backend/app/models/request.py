"""
Request models for the Concept Visualizer API.

This module defines Pydantic models for API request validation.
"""

from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field, HttpUrl, validator


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
        description="Description of the theme/color scheme to generate"
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


class SVGConversionRequest(BaseModel):
    """Request model for SVG conversion"""
    image_data: str = Field(..., description="Base64 encoded image data with or without data URL prefix")
    max_size: Optional[int] = Field(1024, description="Maximum dimension for the output SVG")
    color_mode: str = Field("color", description="Color mode for conversion: binary, grayscale, or color")
    hierarchical: bool = Field(True, description="Whether to use hierarchical organization in SVG")
    filter_speckle_size: int = Field(4, description="Size of speckles to filter out")
    corner_threshold: float = Field(60.0, description="Corner threshold in degrees")
    length_threshold: float = Field(4.0, description="Length threshold for curves")
    splice_threshold: float = Field(45.0, description="Splice threshold in degrees")
    path_precision: int = Field(8, description="Number of decimal places in path data")
    color_quantization_steps: int = Field(16, description="Number of colors in the output SVG") 