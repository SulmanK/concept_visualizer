"""
Concept generation and refinement service.

This module provides the service layer for generating and refining visual concepts
using the JigsawStack API.
"""

import datetime
import logging
import uuid
from functools import lru_cache
from typing import List, Optional

from fastapi import Depends

from backend.app.models.response import ColorPalette, GenerationResponse
from backend.app.services.jigsawstack.client import JigsawStackClient, get_jigsawstack_client

logger = logging.getLogger(__name__)


class ConceptService:
    """Service for generating and refining visual concepts."""

    def __init__(self, client: JigsawStackClient):
        """
        Initialize the concept service.
        
        Args:
            client: The JigsawStack API client
        """
        self.client = client

    async def generate_concept(
        self, logo_description: str, theme_description: str
    ) -> GenerationResponse:
        """
        Generate a new visual concept based on provided descriptions.
        
        Args:
            logo_description: Description of the logo to generate
            theme_description: Description of the theme/color scheme to generate
            
        Returns:
            GenerationResponse: The generated concept with image URL and color palette
            
        Raises:
            Exception: If there is an error during generation
        """
        logger.info(f"Generating concept with descriptions: {logo_description}, {theme_description}")
        
        try:
            # Generate logo image
            image_url = await self.client.generate_image(
                prompt=f"Logo design: {logo_description}. Style/theme: {theme_description}",
                width=512,
                height=512,
                model="stable-diffusion-xl",
            )
            
            # Generate color palette based on theme description
            colors = await self.client.generate_color_palette(
                prompt=theme_description,
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
                image_url=image_url,
                color_palette=palette,
                generation_id=str(uuid.uuid4()),
                created_at=datetime.datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Error generating concept: {str(e)}")
            raise

    async def refine_concept(
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
            Exception: If there is an error during refinement
        """
        logger.info(f"Refining concept with prompt: {refinement_prompt}")
        
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
                f"Refinement instructions: {refinement_prompt}.{preservation_text}"
            )
            
            # Generate refined image using image-to-image
            image_url = await self.client.refine_image(
                prompt=prompt,
                image_url=original_image_url,
                strength=0.7,  # Control how much to preserve original image
                model="stable-diffusion-xl",
            )
            
            # Generate or refine color palette
            colors = await self.client.generate_color_palette(
                prompt=f"{theme_desc} {refinement_prompt}",
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
                image_url=image_url,
                color_palette=palette,
                generation_id=str(uuid.uuid4()),
                created_at=datetime.datetime.utcnow().isoformat(),
                original_image_url=original_image_url,
                refinement_prompt=refinement_prompt
            )
        except Exception as e:
            logger.error(f"Error refining concept: {str(e)}")
            raise


@lru_cache()
def get_concept_service(
    client: JigsawStackClient = Depends(get_jigsawstack_client),
) -> ConceptService:
    """
    Factory function for ConceptService instances.
    
    Args:
        client: The JigsawStack API client
        
    Returns:
        ConceptService: A singleton instance of the concept service
    """
    return ConceptService(client) 