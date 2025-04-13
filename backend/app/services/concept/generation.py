"""
Concept generation module.

This module provides functionality for generating visual concepts using the JigsawStack API.
"""

import datetime
import logging
import uuid
from typing import List, Dict, Any, Tuple

from app.core.exceptions import (
    ConceptError, 
    JigsawStackError, 
)
from app.models.concept.response import ColorPalette, GenerationResponse
from app.services.jigsawstack.client import JigsawStackClient


class ConceptGenerator:
    """Component responsible for generating visual concepts."""

    def __init__(self, client: JigsawStackClient):
        """
        Initialize the concept generator.
        
        Args:
            client: The JigsawStack API client
        """
        self.client = client
        self.logger = logging.getLogger("concept_service.generator")

    async def generate(
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
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
        """
        self.logger.info(f"Generating concept with descriptions: {logo_description}, {theme_description}")
        
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
        except JigsawStackError:
            # Re-raise specific JigsawStack errors
            self.logger.error(f"JigsawStack API error during concept generation", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error generating concept: {str(e)}", exc_info=True)
            raise ConceptError(
                message=f"Failed to generate concept: {str(e)}",
                details={
                    "logo_description": logo_description,
                    "theme_description": theme_description
                }
            )

    async def generate_with_palettes(
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
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
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
            failed_palettes = []
            
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
                except JigsawStackError as e:
                    self.logger.error(f"JigsawStack error generating image for palette '{name}': {e}")
                    failed_palettes.append(name)
                except Exception as e:
                    self.logger.error(f"Error generating image for palette '{name}': {e}")
                    failed_palettes.append(name)
                    # Continue with other palettes even if one fails
            
            # If we failed to generate any images, raise an error
            if len(variation_images) == 0 and len(palettes) > 0:
                raise ConceptError(
                    message="Failed to generate any images for the provided palettes",
                    details={
                        "failed_palettes": failed_palettes,
                        "logo_description": logo_description,
                        "theme_description": theme_description
                    }
                )
                
            return palettes, variation_images
            
        except JigsawStackError:
            # Re-raise specific JigsawStack errors
            self.logger.error("JigsawStack API error during palette generation", exc_info=True)
            raise
        except ConceptError:
            # Re-raise ConceptError
            raise
        except Exception as e:
            self.logger.error(f"Error in generate_concept_with_palettes: {e}", exc_info=True)
            raise ConceptError(
                message=f"Failed to generate concept with palettes: {str(e)}",
                details={
                    "logo_description": logo_description,
                    "theme_description": theme_description,
                    "num_palettes": num_palettes
                }
            ) 