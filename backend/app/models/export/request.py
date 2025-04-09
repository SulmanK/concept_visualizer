"""
Export request models for the API.

This module defines the request models for image export functionality.
"""

from typing import Dict, Literal, Optional
from pydantic import Field, validator
import re

from ..common.base import APIBaseModel


class ExportRequest(APIBaseModel):
    """Request model for image export."""
    
    image_identifier: str = Field(
        ..., 
        description="Storage path identifier for the image (e.g., user_id/.../image.png)"
    )
    target_format: Literal["png", "jpg", "svg"] = Field(
        ..., 
        description="Target format for export"
    )
    target_size: Literal["small", "medium", "large", "original"] = Field(
        "original", 
        description="Target size for export"
    )
    svg_params: Optional[Dict] = Field(
        None, 
        description="Optional parameters for SVG conversion (when target_format is 'svg')"
    )
    storage_bucket: str = Field(
        "concept-images",
        description="Storage bucket where the image is stored (concept-images or palette-images)"
    )
    
    @validator("image_identifier")
    def validate_image_identifier(cls, v):
        """Validate the image identifier format."""
        # Ensure it's a valid storage path without any URL components
        if "://" in v or "?" in v or v.startswith("/"):
            raise ValueError("image_identifier must be a storage path, not a URL")
        return v
        
    @validator("storage_bucket")
    def validate_storage_bucket(cls, v):
        """Validate the storage bucket name."""
        valid_buckets = ["concept-images", "palette-images"]
        if v not in valid_buckets:
            raise ValueError(f"storage_bucket must be one of: {', '.join(valid_buckets)}")
        return v 