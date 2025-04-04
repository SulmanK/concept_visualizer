"""
Interface for the concept generation and refinement service.
"""

import abc
from typing import List, Optional, Dict, Any, Tuple

from app.models.response import GenerationResponse


class ConceptServiceInterface(abc.ABC):
    """Interface for concept generation and refinement services."""

    @abc.abstractmethod
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
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
        """
        pass

    @abc.abstractmethod
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
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
        """
        pass

    @abc.abstractmethod
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
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If refinement fails due to API errors
            ConceptError: If there is an error during concept refinement
        """
        pass

    @abc.abstractmethod
    async def generate_color_palettes(
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
        pass 