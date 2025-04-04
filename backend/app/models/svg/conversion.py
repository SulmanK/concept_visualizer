"""
SVG conversion models for the API.

This module defines the request and response models for SVG conversion.
"""

from typing import Optional
from pydantic import Field, validator
import re

from ..common.base import APIBaseModel


class SVGConversionRequest(APIBaseModel):
    """Request model for SVG conversion."""
    
    image_data: str = Field(
        ..., 
        description="Base64 encoded image data with or without data URL prefix"
    )
    max_size: Optional[int] = Field(
        1024, 
        description="Maximum dimension for the output SVG"
    )
    color_mode: str = Field(
        "color", 
        description="Color mode for conversion: binary, grayscale, or color"
    )
    hierarchical: bool = Field(
        True, 
        description="Whether to use hierarchical organization in SVG"
    )
    filter_speckle_size: int = Field(
        4, 
        description="Size of speckles to filter out"
    )
    corner_threshold: float = Field(
        60.0, 
        description="Corner threshold in degrees"
    )
    length_threshold: float = Field(
        4.0, 
        description="Length threshold for curves"
    )
    splice_threshold: float = Field(
        45.0, 
        description="Splice threshold in degrees"
    )
    path_precision: int = Field(
        8, 
        description="Number of decimal places in path data"
    )
    color_quantization_steps: int = Field(
        16, 
        description="Number of colors in the output SVG"
    )
    
    @validator('color_mode')
    def validate_color_mode(cls, v):
        """Validate that color_mode is one of the allowed values."""
        allowed_modes = {"binary", "grayscale", "color"}
        if v not in allowed_modes:
            raise ValueError(f"color_mode must be one of: {', '.join(allowed_modes)}")
        return v
    
    @validator('image_data')
    def validate_image_data(cls, v):
        """Validate and normalize image_data."""
        # Check if it's a data URL and strip the prefix if needed
        if v.startswith('data:image'):
            # Extract just the base64 part
            match = re.match(r'data:image\/[^;]+;base64,(.+)', v)
            if match:
                return match.group(1)
        return v


class SVGConversionResponse(APIBaseModel):
    """Response model for SVG conversion."""
    
    svg_data: str = Field(
        ..., 
        description="SVG data as a string"
    )
    success: bool = Field(
        ..., 
        description="Whether the conversion was successful"
    )
    message: str = Field(
        ..., 
        description="Message about the conversion process"
    ) 