"""
JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import logging
from functools import lru_cache
from typing import List

import httpx
from fastapi import Depends

from app.core.config import settings

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
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
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
        endpoint = f"{self.api_url}/v1/images/generations"
        payload = {
            "prompt": prompt,
            "width": width,
            "height": height,
            "model": model,
            "n": 1  # Generate one image
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract the image URL from the response
                return data["data"][0]["url"]
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
        endpoint = f"{self.api_url}/v1/images/edits"
        payload = {
            "prompt": prompt,
            "image": image_url,
            "strength": strength,
            "model": model,
            "n": 1  # Generate one image
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract the image URL from the response
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
        endpoint = f"{self.api_url}/v1/colors/generate"
        payload = {
            "prompt": prompt,
            "num_colors": num_colors
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                
                # Extract the color codes from the response
                return data["colors"]
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            raise


@lru_cache()
def get_jigsawstack_client() -> JigsawStackClient:
    """
    Factory function for JigsawStackClient instances.
    
    Returns:
        JigsawStackClient: A singleton instance of the JigsawStack client
    """
    return JigsawStackClient(
        api_key=settings.JIGSAWSTACK_API_KEY,
        api_url=settings.JIGSAWSTACK_API_URL
    ) 