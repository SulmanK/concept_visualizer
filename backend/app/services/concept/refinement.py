"""
Concept refinement module.

This module provides functionality for refining existing concepts.
"""

import datetime
import logging
import uuid
from typing import List, Optional

from app.core.exceptions import (
    ConceptError, 
    JigsawStackError
)
from app.models.concept.response import ColorPalette, GenerationResponse
from app.services.jigsawstack.client import JigsawStackClient


class ConceptRefiner:
    """Component responsible for refining visual concepts."""

    def __init__(self, client: JigsawStackClient):
        """
        Initialize the concept refiner.
        
        Args:
            client: The JigsawStack API client
        """
        self.client = client
        self.logger = logging.getLogger("concept_service.refiner")

    async def refine(
        self,
        original_image_url: str,
        logo_description: Optional[str],
        theme_description: Optional[str],
        refinement_prompt: str,
        preserve_aspects: List[str],
    ) -> GenerationResponse:
        """
        Refine an existing concept based on provided instructions.
        
        Args:
            original_image_url: URL of the original image to refine
            logo_description: Updated description of the logo (optional)
            theme_description: Updated description of the theme (optional)
            refinement_prompt: Specific instructions for refinement
            preserve_aspects: Aspects of the original design to preserve
            
        Returns:
            GenerationResponse: The refined concept with image URL and color palette
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If refinement fails due to API errors
            ConceptError: If there is an error during concept refinement
        """
        self.logger.info(f"Refining concept with prompt: {refinement_prompt}")
        
        try:
            # Prepare the prompt with original descriptions and refinement instructions
            logo_desc = logo_description or "the existing logo"
            theme_desc = theme_description or "the existing theme"
            
            preservation_text = ""
            if preserve_aspects:
                preservation_text = f" Preserve the following aspects: {', '.join(preserve_aspects)}."
                
            prompt = (
                f"Refine this logo design: {logo_desc}. "
                f"Theme/style: {theme_desc}. "
                f"Changes to make: {refinement_prompt}.{preservation_text}"
            )
            
            # Generate refined image using the image-to-image endpoint
            refined_image_url = await self.client.refine_image(
                prompt=prompt,
                init_image_url=original_image_url,
                strength=0.7,  # How much to preserve the original image (0.0-1.0)
                guidance_scale=7.5,  # How closely to follow the prompt
                width=512,
                height=512,
            )
            
            # Generate updated color palette based on the theme description
            colors = await self.client.generate_color_palette(
                prompt=theme_desc,
                num_colors=8
            )
            
            # Map colors to specific roles in our palette
            palette = ColorPalette(
                primary=colors[0],
                secondary=colors[1],
                accent=colors[2],
                background=colors[3],
                text=colors[4],
                additional_colors=colors[5:] if len(colors) > 5 else []
            )
            
            # Create the response
            return GenerationResponse(
                prompt_id=str(uuid.uuid4()),
                logo_description=logo_desc,
                theme_description=theme_desc,
                image_url=refined_image_url,
                color_palette=palette,
                created_at=datetime.datetime.utcnow().isoformat(),
                refinement_prompt=refinement_prompt,
                original_image_url=original_image_url,
                preserve_aspects=preserve_aspects
            )
            
        except JigsawStackError:
            # Re-raise specific JigsawStack errors
            self.logger.error("JigsawStack API error during concept refinement", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error refining concept: {str(e)}", exc_info=True)
            raise ConceptError(
                message=f"Failed to refine concept: {str(e)}",
                details={
                    "original_image_url": original_image_url,
                    "logo_description": logo_description,
                    "theme_description": theme_description,
                    "refinement_prompt": refinement_prompt,
                    "preserve_aspects": preserve_aspects
                }
            ) 