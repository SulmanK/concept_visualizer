"""Interface for the concept generation and refinement service."""

import abc
from typing import Any, Dict, List, Optional, Tuple


class ConceptServiceInterface(abc.ABC):
    """Interface for concept generation and refinement services."""

    @abc.abstractmethod
    async def generate_concept(
        self,
        logo_description: str,
        theme_description: str,
        user_id: Optional[str] = None,
        skip_persistence: bool = False,
    ) -> Dict[str, Any]:
        """Generate a new visual concept based on provided descriptions.

        Args:
            logo_description: Description of the logo to generate
            theme_description: Description of the theme/color scheme to generate
            user_id: Optional user ID for storing the concept
            skip_persistence: If True, don't store the concept in the database

        Returns:
            Dict containing generated concept details with image URL and color palette

        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
        """
        pass

    @abc.abstractmethod
    async def generate_concept_with_palettes(self, logo_description: str, theme_description: str, num_palettes: int = 3) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate a concept with multiple palette variations, each with its own image.

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
        refinement_prompt: str,
        logo_description: Optional[str] = None,
        theme_description: Optional[str] = None,
        user_id: Optional[str] = None,
        skip_persistence: bool = False,
        strength: float = 0.7,
    ) -> Dict[str, Any]:
        """Refine an existing concept based on provided instructions.

        Args:
            original_image_url: URL of the original image to refine
            refinement_prompt: Specific instructions for refinement
            logo_description: Updated description of the logo (optional)
            theme_description: Updated description of the theme (optional)
            user_id: Optional user ID for storing the concept
            skip_persistence: If True, don't store the concept in the database
            strength: Control how much to preserve of the original image (0.0-1.0)

        Returns:
            Dict containing refined concept details with image URL and color palette

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
        num_palettes: int = 7,
    ) -> List[Dict[str, Any]]:
        """Generate multiple color palettes based on a theme description.

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
