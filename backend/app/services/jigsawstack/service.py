"""
JigsawStack service implementation.

This module provides a service for interacting with JigsawStack APIs
through the JigsawStackClient, with additional business logic and error handling.
"""

import logging
from functools import lru_cache
from typing import Dict, List, Any, Optional, Union

from app.services.jigsawstack.client import JigsawStackClient
from app.services.interfaces.jigsawstack_service import JigsawStackServiceInterface
from app.core.config import settings
from app.core.exceptions import (
    JigsawStackError,
    JigsawStackGenerationError,
    JigsawStackConnectionError
)

logger = logging.getLogger(__name__)


class JigsawStackService(JigsawStackServiceInterface):
    """
    Service for JigsawStack API operations.
    
    This service wraps the JigsawStackClient and provides higher-level
    functionality for generating and refining images.
    """
    
    def __init__(self, client: JigsawStackClient):
        """
        Initialize the JigsawStack service.
        
        Args:
            client: The JigsawStackClient for API interactions
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    async def generate_image(
        self, 
        prompt: str, 
        width: int = 512, 
        height: int = 512,
        model: str = "stable-diffusion-xl"
    ) -> Dict[str, Any]:
        """
        Generate an image based on a prompt.
        
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
        try:
            # Log the request with any sensitive information masked
            self.logger.info(f"Generating image with prompt length: {len(prompt)}")
            
            # Use the client to generate the image
            result = await self.client.generate_image(
                prompt=prompt,
                width=width,
                height=height,
                model=model
            )
            
            # Log success
            self.logger.info("Image generation successful")
            return result
            
        except JigsawStackError as e:
            # Already a specific JigsawStack error, just re-raise
            self.logger.error(f"JigsawStack error during image generation: {str(e)}")
            raise
        except Exception as e:
            # Unexpected error, wrap in a generic JigsawStackGenerationError
            self.logger.error(f"Unexpected error during image generation: {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Unexpected error during image generation: {str(e)}",
                content_type="image",
                prompt=prompt
            )
    
    async def refine_image(
        self, 
        prompt: str, 
        image_url: str,
        strength: float = 0.7,
        model: str = "stable-diffusion-xl"
    ) -> Dict[str, Any]:
        """
        Refine an existing image based on a prompt.
        
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
        try:
            # Log the request with any sensitive information masked
            self.logger.info(f"Refining image with prompt length: {len(prompt)}")
            
            # Use the client to refine the image
            result = await self.client.refine_image(
                prompt=prompt,
                image_url=image_url,
                strength=strength,
                model=model
            )
            
            # Log success
            self.logger.info("Image refinement successful")
            return result
            
        except JigsawStackError as e:
            # Already a specific JigsawStack error, just re-raise
            self.logger.error(f"JigsawStack error during image refinement: {str(e)}")
            raise
        except Exception as e:
            # Unexpected error, wrap in a generic JigsawStackGenerationError
            self.logger.error(f"Unexpected error during image refinement: {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Unexpected error during image refinement: {str(e)}",
                content_type="image",
                prompt=prompt
            )
    
    async def generate_color_palettes(
        self, 
        prompt: str,
        num_palettes: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Generate color palettes based on a prompt.
        
        Args:
            prompt: The color palette generation prompt
            num_palettes: Number of palettes to generate
            
        Returns:
            List of palette dictionaries
            
        Raises:
            JigsawStackGenerationError: If palette generation fails
        """
        try:
            # Log the request with any sensitive information masked
            self.logger.info(f"Generating color palettes with prompt length: {len(prompt)}")
            
            # Use the client to generate palettes
            result = await self.client.generate_color_palettes(
                prompt=prompt,
                num_palettes=num_palettes
            )
            
            # Log success
            self.logger.info(f"Generated {len(result)} color palettes successfully")
            return result
            
        except JigsawStackError as e:
            # Already a specific JigsawStack error, just re-raise
            self.logger.error(f"JigsawStack error during palette generation: {str(e)}")
            raise
        except Exception as e:
            # Unexpected error, wrap in a generic JigsawStackGenerationError
            self.logger.error(f"Unexpected error during palette generation: {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Unexpected error during palette generation: {str(e)}",
                content_type="palette",
                prompt=prompt
            )


@lru_cache()
def get_jigsawstack_service() -> JigsawStackService:
    """
    Get a singleton instance of the JigsawStackService.
    
    Returns:
        JigsawStackService: Service for JigsawStack operations
    """
    api_key = settings.JIGSAWSTACK_API_KEY
    api_url = settings.JIGSAWSTACK_API_URL
    
    if not api_key or not api_url:
        raise ValueError("JigsawStack API key and URL must be provided in settings")
    
    client = JigsawStackClient(api_key=api_key, api_url=api_url)
    return JigsawStackService(client=client) 