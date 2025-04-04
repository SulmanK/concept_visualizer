"""
Color palette generation module.

This module provides functionality for generating and manipulating color palettes.
"""

import logging
from typing import List, Dict, Any, Optional

from app.core.exceptions import ConceptError, JigsawStackError
from app.services.jigsawstack.client import JigsawStackClient


class PaletteGenerator:
    """Component responsible for generating color palettes."""

    def __init__(self, client: JigsawStackClient):
        """
        Initialize the palette generator.
        
        Args:
            client: The JigsawStack API client
        """
        self.client = client
        self.logger = logging.getLogger("concept_service.palette")

    async def generate_palettes(
        self, 
        theme_description: str, 
        logo_description: Optional[str] = None,
        num_palettes: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple color palettes based on a theme description.
        
        Args:
            theme_description: Description of the theme/color scheme
            logo_description: Optional description of the logo to help contextualize
            num_palettes: Number of palettes to generate
            
        Returns:
            List of palette dictionaries, each containing name, colors, and description
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during palette generation
        """
        self.logger.info(f"Generating {num_palettes} color palettes for: {theme_description}")
        
        try:
            # Generate palettes using the multiple palettes endpoint
            palettes = await self.client.generate_multiple_palettes(
                logo_description=logo_description or "",
                theme_description=theme_description,
                num_palettes=num_palettes
            )
            
            self.logger.info(f"Successfully generated {len(palettes)} palettes")
            return palettes
        except JigsawStackError:
            # Re-raise specific JigsawStack errors
            self.logger.error("JigsawStack API error during palette generation", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error generating palettes: {str(e)}", exc_info=True)
            raise ConceptError(
                message=f"Failed to generate palettes: {str(e)}",
                details={
                    "theme_description": theme_description,
                    "logo_description": logo_description,
                    "num_palettes": num_palettes
                }
            )

    async def generate_single_palette(
        self, 
        theme_description: str, 
        num_colors: int = 8
    ) -> List[str]:
        """
        Generate a single color palette with the specified number of colors.
        
        Args:
            theme_description: Description of the theme/color scheme
            num_colors: Number of colors in the palette
            
        Returns:
            List of color hex codes
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during palette generation
        """
        self.logger.info(f"Generating a single palette with {num_colors} colors for: {theme_description}")
        
        try:
            # Generate a single palette
            colors = await self.client.generate_color_palette(
                prompt=theme_description,
                num_colors=num_colors
            )
            
            self.logger.info(f"Successfully generated palette with {len(colors)} colors")
            return colors
        except JigsawStackError:
            # Re-raise specific JigsawStack errors
            self.logger.error("JigsawStack API error during single palette generation", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"Error generating single palette: {str(e)}", exc_info=True)
            raise ConceptError(
                message=f"Failed to generate palette: {str(e)}",
                details={
                    "theme_description": theme_description,
                    "num_colors": num_colors
                }
            ) 