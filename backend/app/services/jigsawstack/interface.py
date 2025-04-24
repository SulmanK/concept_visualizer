"""Interface for JigsawStack services."""

import abc
from typing import Any, Dict, List


class JigsawStackServiceInterface(abc.ABC):
    """Interface for JigsawStack API operations."""

    @abc.abstractmethod
    async def generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "stable-diffusion-xl",
    ) -> Dict[str, Any]:
        """Generate an image based on a prompt.

        Args:
            prompt: The image generation prompt
            width: Width of the generated image
            height: Height of the generated image
            model: Model to use for generation

        Returns:
            Dictionary containing image URL and/or binary data

        Raises:
            JigsawStackGenerationError: If generation fails
        """
        pass

    @abc.abstractmethod
    async def refine_image(
        self,
        prompt: str,
        image_url: str,
        strength: float = 0.7,
        model: str = "stable-diffusion-xl",
    ) -> Dict[str, Any]:
        """Refine an existing image based on a prompt.

        Args:
            prompt: The refinement prompt
            image_url: URL of the original image
            strength: How much to change the original (0.0-1.0)
            model: Model to use for refinement

        Returns:
            Dictionary containing refined image URL and/or binary data

        Raises:
            JigsawStackGenerationError: If refinement fails
        """
        pass

    @abc.abstractmethod
    async def generate_color_palettes(self, prompt: str, num_palettes: int = 5) -> List[Dict[str, Any]]:
        """Generate color palettes based on a prompt.

        Args:
            prompt: The color palette generation prompt
            num_palettes: Number of palettes to generate

        Returns:
            List of palette dictionaries

        Raises:
            JigsawStackGenerationError: If palette generation fails
        """
        pass
