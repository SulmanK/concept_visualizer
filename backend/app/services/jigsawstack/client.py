"""
JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import logging
import httpx
import json
from functools import lru_cache
from typing import List, Dict, Any, Optional
import uuid

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
            "Accept": "application/json",
            "x-api-key": api_key  # Some endpoints use x-api-key instead of Authorization
        }
        logger.info(f"Initialized JigsawStack client with API key prefix: {api_key[:10]}...")
    
    async def generate_image(
        self, prompt: str, width: int = 512, height: int = 512, model: str = "stable-diffusion-xl"
    ) -> bytes:
        """
        Generate an image using the JigsawStack API.
        
        Args:
            prompt: The text prompt for image generation
            width: The width of the generated image
            height: The height of the generated image
            model: The model to use for generation
            
        Returns:
            bytes: Binary image data that can be uploaded to storage
            
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
            
            # Use the correct endpoint according to API reference
            endpoint = f"{self.api_url}/v1/ai/image_generation"
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "steps": 30,
                "advance_config": {
                    "negative_prompt": "blurry, low quality",
                    "guidance": 7.5
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Image generation API error: {error_details}")
                    raise Exception(f"Image generation failed: {error_details}")
                
                logger.info("Image generation successful, returning binary data")
                # Return the binary image data 
                return response.content
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
            raise
    
    async def generate_image_with_palette(
        self, logo_prompt: str, palette: List[str], palette_name: str = "Custom Palette"
    ) -> bytes:
        """
        Generate an image using a specific color palette.
        
        Args:
            logo_prompt: The text prompt for the logo design
            palette: List of hex color codes to use in the image
            palette_name: Optional name of the palette for logging
            
        Returns:
            bytes: Binary image data that can be uploaded to storage
            
        Raises:
            Exception: If the API request fails
        """
        try:
            # Format the color palette as a readable string for the prompt
            color_str = ", ".join(palette[:5])  # Limit to first 5 colors for clarity
            prompt = f"{logo_prompt}. Use this exact color palette: {color_str}."
            
            logger.info(f"Generating image with palette '{palette_name}' and prompt: {prompt}")
            
            # Use direct HTTP call for more control
            endpoint = f"{self.api_url}/v1/ai/image_generation"
            
            payload = {
                "prompt": prompt,
                "aspect_ratio": "1:1",
                "steps": 30,
                "advance_config": {
                    "negative_prompt": "blurry, low quality, multiple color palettes, wrong colors",
                    "guidance": 8.0  # Higher guidance to emphasize following color instructions
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=45.0  # Longer timeout for image generation
                )
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Image generation API error: {error_details}")
                    raise Exception(f"Image generation failed: {error_details}")
                
                logger.info(f"Image generation with palette '{palette_name}' successful")
                # Return the binary image data
                return response.content
                
        except Exception as e:
            logger.error(f"Error generating image with palette: {str(e)}")
            raise
    
    async def refine_image(
        self, 
        prompt: str, 
        image_url: str, 
        strength: float = 0.7,
        model: str = "stable-diffusion-xl"
    ) -> bytes:
        """
        Refine an existing image using the JigsawStack API.
        
        Args:
            prompt: The text prompt for refinement
            image_url: URL of the image to refine
            strength: How much to change the original (0.0-1.0)
            model: The model to use for refinement
            
        Returns:
            bytes: Binary image data that can be uploaded to storage
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Refining image with prompt: {prompt}")
            
            # Use the correct endpoint for image refinement/variation
            endpoint = f"{self.api_url}/v1/ai/image_variation"
            payload = {
                "prompt": prompt,
                "image_url": image_url,
                "strength": strength,
                "steps": 30,
                "advance_config": {
                    "negative_prompt": "blurry, low quality",
                    "guidance": 7.5
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Image refinement API error: {error_details}")
                    raise Exception(f"Image refinement failed: {error_details}")
                
                logger.info("Image refinement successful, returning binary data")
                # Return the binary image data 
                return response.content
                
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
            
            # Use direct HTTP request instead of SDK
            endpoint = f"{self.api_url}/v1/prompt_engine/run"
            payload = {
                "prompt": f"Generate {num_colors} hex color codes for a color palette described as: {prompt}. Return only as a JSON array of hex color codes.",
                "inputs": [],
                "return_prompt": "Return a valid JSON array of hex color codes only"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Color palette generation API error: {error_details}")
                    # Return default colors instead of failing
                    return ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]
            
            # Try to parse the response
            try:
                data = response.json()
                
                # Try different ways to extract the color codes
                if isinstance(data, list) and len(data) > 0:
                    # Direct array of colors
                    if isinstance(data[0], str) and data[0].startswith('#'):
                        return data[:num_colors]
                
                if isinstance(data, dict):
                    # Check for colors in a nested structure
                    if "colors" in data:
                        return data["colors"][:num_colors]
                    elif "result" in data:
                        # Try to parse the result field as JSON
                        try:
                            result = data["result"]
                            if isinstance(result, list):
                                return result[:num_colors]
                            if isinstance(result, str):
                                # Try to parse string as JSON
                                try:
                                    colors = json.loads(result)
                                    if isinstance(colors, list):
                                        return colors[:num_colors]
                                except json.JSONDecodeError:
                                    pass
                        except Exception:
                            pass
                
                # Last resort: extract anything that looks like a hex code
                response_text = str(data)
                import re
                hex_codes = re.findall(r'#[0-9A-Fa-f]{6}', response_text)
                if hex_codes:
                    return hex_codes[:num_colors]
            
            except Exception as e:
                logger.error(f"Error parsing color palette response: {str(e)}")
            
            # Fallback: Generate some default colors
            logger.warning("Failed to parse color palette, using defaults")
            return ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]
                
        except Exception as e:
            logger.error(f"Error generating color palette: {str(e)}")
            # Return default colors as fallback
            return ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]
            
    async def generate_multiple_palettes(self, prompt: str, num_palettes: int = 3) -> List[Dict[str, Any]]:
        """
        Generate multiple distinct color palettes based on a text description.
        
        Args:
            prompt: Text description of the theme
            num_palettes: Number of distinct palettes to generate
            
        Returns:
            List[Dict[str, Any]]: List of palette dictionaries with name, colors, and description
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Generating {num_palettes} distinct color palettes for: {prompt}")
            
            # Create a prompt that asks for distinct palettes
            detailed_prompt = (
                f"Generate {num_palettes} distinctly different color palettes based on the theme: '{prompt}'. "
                f"Each palette should have 5 hex color codes. Make the palettes visually distinct from each other. "
                f"For each palette, provide a name, description, and the color codes. "
                f"Return as a JSON array of objects with 'name', 'description', and 'colors' (array of hex codes)."
            )
            
            # Use direct HTTP request instead of SDK
            endpoint = f"{self.api_url}/v1/prompt_engine/run"
            payload = {
                "prompt": detailed_prompt,
                "inputs": [],
                "return_prompt": "Return a valid JSON array of objects only"
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Color palette generation API error: {error_details}")
                    # Return default palettes instead of failing
                    return self._get_default_palettes(num_palettes, prompt)
            
            # Try to parse the response
            try:
                response_data = response.json()
                
                # If it's already a list of palette objects
                if isinstance(response_data, list) and len(response_data) > 0:
                    palettes = response_data[:num_palettes]
                    
                    # Ensure each palette has the required keys
                    for palette in palettes:
                        if not isinstance(palette.get("colors", []), list):
                            palette["colors"] = ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"]
                        if not palette.get("name"):
                            palette["name"] = "Unnamed Palette"
                        if not palette.get("description"):
                            palette["description"] = f"A palette inspired by: {prompt}"
                    
                    return palettes
                
                # If response is in some other format, extract what we can
                response_text = str(response_data)
                
                # Attempt to find JSON in the response text
                import re
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(0))
                        if isinstance(json_data, list):
                            return json_data[:num_palettes]
                    except json.JSONDecodeError:
                        pass
                
                # Fallback: Generate default palettes
                logger.warning("Failed to parse multiple palettes, using defaults")
                return self._get_default_palettes(num_palettes, prompt)
                
            except Exception as e:
                logger.error(f"Error parsing multiple palettes response: {e}")
                # Fallback: Generate default palettes
                return self._get_default_palettes(num_palettes, prompt)
                
            logger.info(f"Generated {num_palettes} color palettes successfully")
            
        except Exception as e:
            logger.error(f"Error generating multiple color palettes: {str(e)}")
            # Fallback: Generate default palettes
            return self._get_default_palettes(num_palettes, prompt)
    
    def _get_default_palettes(self, num_palettes: int, prompt: str) -> List[Dict[str, Any]]:
        """
        Generate default color palettes as a fallback.
        
        Args:
            num_palettes: Number of palettes to generate
            prompt: The original prompt for context in descriptions
            
        Returns:
            List of default palette dictionaries
        """
        return [
            {
                "name": "Primary Palette",
                "colors": ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"],
                "description": f"A primary palette for: {prompt}"
            },
            {
                "name": "Accent Palette",
                "colors": ["#EF4444", "#F87171", "#FCA5A5", "#FEE2E2", "#7F1D1D"],
                "description": f"An accent palette for: {prompt}"
            },
            {
                "name": "Neutral Palette",
                "colors": ["#1F2937", "#4B5563", "#9CA3AF", "#E5E7EB", "#F9FAFB"],
                "description": f"A neutral palette for: {prompt}"
            }
        ][:num_palettes]


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