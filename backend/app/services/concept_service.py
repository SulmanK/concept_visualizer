"""
Concept generation and refinement service.

This module provides the service layer for generating and refining visual concepts
using the JigsawStack API.
"""

import datetime
import logging
import uuid
from functools import lru_cache
from typing import List, Optional, Dict, Any, Tuple

from fastapi import Depends

from app.models.response import ColorPalette, GenerationResponse
from app.services.jigsawstack.client import JigsawStackClient, get_jigsawstack_client

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
        self.logger = logging.getLogger("concept_service")

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
                logo_description=logo_description,
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
                prompt_id=str(uuid.uuid4()),
                logo_description=logo_description,
                theme_description=theme_description,
                image_url=image_url,
                color_palette=palette,
                created_at=datetime.datetime.utcnow().isoformat()
            )
        except Exception as e:
            logger.error(f"Error generating concept: {str(e)}")
            raise

    async def generate_concept_with_palettes(
        self, logo_description: str, theme_description: str, num_palettes: int = 3
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Generate a concept with multiple palette variations, each with its own image.
        
        Args:
            logo_description: Description of the logo to generate
            theme_description: Description of the theme/color scheme
            num_palettes: Number of palette variations to generate
            
        Returns:
            Tuple of (palettes, variation_images): 
            - palettes: List of palette dictionaries with name, colors, description
            - variation_images: List of dictionaries with palette info and image data
            
        Raises:
            Exception: If there is an error during generation
        """
        self.logger.info(f"Generating concept with {num_palettes} palette variations")
        
        try:
            # 1. Generate multiple distinct color palettes
            palettes = await self.client.generate_multiple_palettes(
                logo_description=logo_description,
                theme_description=theme_description,
                num_palettes=num_palettes
            )
            self.logger.info(f"Generated {len(palettes)} distinct color palettes")
            
            # 2. Generate a separate image for each palette
            variation_images = []
            
            for palette in palettes:
                name = palette["name"]
                colors = palette["colors"]
                description = palette["description"]
                
                try:
                    # Generate image with this specific palette
                    image_data = await self.client.generate_image_with_palette(
                        logo_prompt=logo_description,
                        palette=colors,
                        palette_name=name
                    )
                    
                    # Store binary image data in the variation info
                    variation = {
                        "name": name,
                        "colors": colors,
                        "description": description,
                        "image_data": image_data  # This now contains binary data, not a URL
                    }
                    variation_images.append(variation)
                    
                    self.logger.info(f"Generated image for palette '{name}' successfully")
                except Exception as e:
                    self.logger.error(f"Error generating image for palette '{name}': {e}")
                    # Continue with other palettes even if one fails
            
            return palettes, variation_images
            
        except Exception as e:
            self.logger.error(f"Error in generate_concept_with_palettes: {e}")
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
                prompt_id=str(uuid.uuid4()),
                logo_description=logo_description or "Refined logo",
                theme_description=theme_description or "Refined theme",
                image_url=image_url,
                color_palette=palette,
                created_at=datetime.datetime.utcnow().isoformat(),
                original_image_url=original_image_url,
                refinement_prompt=refinement_prompt
            )
        except Exception as e:
            logger.error(f"Error refining concept: {str(e)}")
            raise
            
    async def generate_color_palettes(
            self, 
            theme_description: str, 
            logo_description: Optional[str] = None,
            num_palettes: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate color palettes based on a theme description and logo description.
        
        Args:
            theme_description: Description of the theme/color scheme
            logo_description: Description of the logo (optional)
            num_palettes: Number of different palettes to generate
            
        Returns:
            List of color palette dictionaries, each with:
                - name: Name of the palette
                - colors: List of hex color codes
                - description: Description of the palette
        """
        self.logger.info(f"Generating {num_palettes} color palettes")
        
        # Define some common palette names for better results
        palette_names = [
            "Primary Palette", "Accent Palette", "Neutral Palette", 
            "Vibrant Palette", "Complementary Palette", "Monochromatic Palette", 
            "Analogous Palette", "Triadic Palette", "Modern Palette",
            "Earthy Palette", "Pastel Palette", "Bold Palette"
        ]
        
        try:
            # Get multiple palettes in a single call to JigsawStack
            self.logger.info(f"Making a single LLM call to generate {num_palettes} color palettes")
            
            # Use the logo description if provided
            logo_desc = logo_description or "generic logo"
                
            # Generate palettes with suggested names
            
            palettes = await self.client.generate_multiple_palettes(
                logo_description=logo_desc,
                theme_description=theme_description,
                num_palettes=num_palettes
            )
            
            self.logger.info(f"Generated {len(palettes)} color palettes successfully in a single call")
            
            # Ensure we have the expected palette names if possible
            for i, palette in enumerate(palettes):
                if i < len(palette_names) and palette["name"] == "Unnamed Palette":
                    palette["name"] = palette_names[i]
                    
            return palettes
            
        except Exception as e:
            self.logger.error(f"Error generating color palettes: {e}")
            # Return a default palette in case of error
            return [{
                "name": "Default Palette",
                "colors": ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"],
                "description": f"Default palette for: {theme_description}"
            }]


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