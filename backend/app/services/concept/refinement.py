"""Concept refinement module.

This module provides functionality for refining existing concepts.
"""

import datetime
import logging
import uuid
from typing import Any, Dict, List, Optional

from app.core.exceptions import ConceptError, JigsawStackError
from app.services.jigsawstack.client import JigsawStackClient


class ConceptRefiner:
    """Component responsible for refining visual concepts."""

    def __init__(self, client: JigsawStackClient):
        """Initialize the concept refiner.

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
    ) -> Dict[str, Any]:
        """Refine an existing concept based on provided instructions.

        Args:
            original_image_url: URL of the original image to refine
            logo_description: Updated description of the logo (optional)
            theme_description: Updated description of the theme (optional)
            refinement_prompt: Specific instructions for refinement
            preserve_aspects: Aspects of the original design to preserve

        Returns:
            Dictionary containing refined concept data instead of GenerationResponse

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

            prompt = f"Refine this logo design: {logo_desc}. " f"Theme/style: {theme_desc}. " f"Changes to make: {refinement_prompt}.{preservation_text}"

            # Generate refined image using the image-to-image endpoint
            refined_image_url = await self.client.refine_image(
                prompt=prompt,
                image_url=original_image_url,
                strength=0.7,  # How much to preserve the original image (0.0-1.0)
                model="stable-diffusion-xl",
            )

            # Generate updated color palette based on the theme description
            palettes = await self.client.generate_multiple_palettes(logo_description=logo_desc, theme_description=theme_desc, num_palettes=1)

            # Extract the colors from the first palette
            colors = palettes[0]["colors"] if palettes else ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]

            # Return a dictionary that can be used to create a GenerationResponse later
            return {
                "prompt_id": str(uuid.uuid4()),
                "logo_description": logo_desc,
                "theme_description": theme_desc,
                "image_data": refined_image_url if isinstance(refined_image_url, bytes) else None,
                "image_url": None if isinstance(refined_image_url, bytes) else refined_image_url,
                "colors": colors,
                "created_at": datetime.datetime.utcnow().isoformat(),
                "refinement_prompt": refinement_prompt,
                "original_image_url": original_image_url,
                "preserve_aspects": preserve_aspects,
            }

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
                    "preserve_aspects": preserve_aspects,
                },
            )
