"""
JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import logging
import httpx
from functools import lru_cache
from typing import List

from jigsawstack import JigsawStack

from backend.app.core.config import settings

logger = logging.getLogger(__name__)


class JigsawStackClient:
    """Client for interacting with JigsawStack API for concept generation and refinement."""
    
    def __init__(self, api_key: str, api_url: str):
        """
        Initialize the JigsawStack API client.
        
        Args:
            api_key: The API key for authentication
            api_url: The base URL for the JigsawStack API
        """
        self.api_key = api_key
        self.api_url = api_url
        self.client = JigsawStack(api_key=api_key)
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        logger.info(f"Initialized JigsawStack client with API key prefix: {api_key[:10]}...")
    
    async def generate_image(
        self, prompt: str, width: int = 512, height: int = 512, model: str = "stable-diffusion-xl"
    ) -> str:
        """
        Generate an image using the JigsawStack API.
        
        Args:
            prompt: The text prompt for image generation
            width: The width of the generated image
            height: The height of the generated image
            model: The model to use for generation
            
        Returns:
            str: URL of the generated image
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Use the SDK's image_generation method
            aspect_ratio = "1:1"  # Default
            if width > height:
                aspect_ratio = "16:9"
            elif height > width:
                aspect_ratio = "9:16"
                
            result = self.client.image_generation({
                "prompt": prompt,
                "aspect_ratio": aspect_ratio
            })
            
            # Process the response according to JigsawStack documentation
            data = result.json()
            
            logger.info("Image generation successful")
            # Return the image URL from the response
            return data["url"]
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    async def refine_image(
        self, 
        prompt: str, 
        image_url: str, 
        strength: float = 0.7,
        model: str = "stable-diffusion-xl"
    ) -> str:
        """
        Refine an existing image using the JigsawStack API.
        
        Args:
            prompt: The text prompt for refinement
            image_url: URL of the image to refine
            strength: How much to change the original (0.0-1.0)
            model: The model to use for refinement
            
        Returns:
            str: URL of the refined image
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Refining image with prompt: {prompt}")
            
            # Since JigsawStack SDK doesn't have image editing, use direct HTTP
            endpoint = f"{self.api_url}/v1/images/generations"
            payload = {
                "prompt": prompt,
                "image": image_url,
                "strength": strength,
                "model": model
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info("Image refinement successful")
                # Return the image URL from the response
                return data["data"][0]["url"]
                
        except Exception as e:
            logger.error(f"Error refining image: {str(e)}")
            raise
    
    async def generate_color_palette(self, prompt: str, num_colors: int = 5) -> List[str]:
        """
        Generate a color palette based on a text description.
        
        Args:
            prompt: Text description of the desired color palette
            num_colors: Number of colors to generate
            
        Returns:
            List[str]: List of hex color codes
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Generating color palette with prompt: {prompt}")
            
            # Use the SDK's prompt_engine to generate color codes
            result = self.client.prompt_engine.run_prompt_direct({
                "prompt": f"Generate {num_colors} hex color codes for a color palette described as: {prompt}. Return only as a JSON array of hex color codes.",
                "inputs": [],
                "return_prompt": "Return a valid JSON array of hex color codes only"
            })
            
            # Process the response using json() instead of blob()
            data = result.json()
            
            # Try to parse the color codes from the response
            try:
                # If response is already a JSON array of colors
                if isinstance(data, list):
                    return data[:num_colors]
                
                # If response has colors in a nested structure
                if "colors" in data:
                    return data["colors"][:num_colors]
                    
                # Return the response as text and extract anything that looks like a hex code
                response_text = str(data)
                import re
                hex_codes = re.findall(r'#[0-9A-Fa-f]{6}', response_text)
                if hex_codes:
                    return hex_codes[:num_colors]
            except Exception:
                # Fallback: Generate some default colors
                logger.warning("Failed to parse color palette, using defaults")
                return ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]
                
            logger.info("Color palette generation successful")
            
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            # Fallback: Return some default colors
            return ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]


@lru_cache()
def get_jigsawstack_client() -> JigsawStackClient:
    """
    Factory function for JigsawStackClient instances.
    
    Returns:
        JigsawStackClient: A singleton instance of the JigsawStack client
    """
    logger.info(f"Creating JigsawStack client with API key: {settings.JIGSAWSTACK_API_KEY[:10]}...")
    return JigsawStackClient(
        api_key=settings.JIGSAWSTACK_API_KEY,
        api_url=settings.JIGSAWSTACK_API_URL
    ) 