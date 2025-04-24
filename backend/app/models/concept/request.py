"""Request models for concept-related API endpoints.

This module defines Pydantic models for validating requests to
concept generation and refinement endpoints.
"""

from typing import List, Optional

from pydantic import Field, HttpUrl, field_validator

from ..common.base import APIBaseModel


class PromptRequest(APIBaseModel):
    """Request model for concept generation."""

    logo_description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Description of the logo to generate",
    )
    theme_description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Description of the theme/color scheme to generate",
    )


class RefinementRequest(APIBaseModel):
    """Request model for concept refinement."""

    original_image_url: HttpUrl = Field(..., description="URL of the original image to refine")
    logo_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Updated description of the logo",
    )
    theme_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Updated description of the theme/color scheme",
    )
    refinement_prompt: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Specific instructions for refinement",
    )
    preserve_aspects: List[str] = Field(default=[], description="Aspects of the original design to preserve")

    @classmethod
    @field_validator("preserve_aspects")
    def validate_preserve_aspects(cls, v: List[str]) -> List[str]:
        """Validate that preserve_aspects contains valid values."""
        valid_aspects = {"colors", "layout", "style", "shapes"}
        for aspect in v:
            if aspect not in valid_aspects:
                raise ValueError(f"Invalid aspect: {aspect}. Valid values are: {', '.join(valid_aspects)}")
        return v
