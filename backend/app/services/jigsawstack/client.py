"""
JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import logging
import httpx
import json
from functools import lru_cache
from typing import List, Dict, Any
import re

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
            
            # Determine aspect ratio based on dimensions
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
                return response.content
            
        except Exception as e:
            logger.error(f"Error generating image: {str(e)}")
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
                return response.content
                
        except Exception as e:
            logger.error(f"Error refining image: {str(e)}")
            raise
    
    async def generate_multiple_palettes(self, prompt: str, num_palettes: int = 5) -> List[Dict[str, Any]]:
        """
        Generate multiple color palettes in a single LLM call.
        
        Args:
            prompt: Text description of the desired theme
            num_palettes: Number of palettes to generate
            
        Returns:
            List[Dict[str, Any]]: List of palette dictionaries with name, colors, and description
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Generating {num_palettes} color palettes in a single call")
            
            # Create a structured prompt for the LLM to generate multiple palettes at once
            detailed_prompt = (
                f"Generate {num_palettes} distinctly different color palettes based on the theme: '{prompt}'. "
                f"Each palette should have 5 hex color codes. Make the palettes visually distinct from each other. "
                f"For each palette, provide a name, description, and the color codes. "
                f"Return as a JSON array of objects with 'name', 'description', and 'colors' (array of hex codes)."
            )
            
            # Use direct HTTP request to the prompt engine
            endpoint = f"{self.api_url}/v1/prompt_engine/run"
            payload = {
                "prompt": detailed_prompt,
                "inputs": [],
                "return_prompt": "Return a valid JSON array of palette objects only",
                "model": "gpt-4-turbo"  # Use the most capable model for structured output
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=40.0  # Longer timeout for complex generation
                )
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Color palette generation API error: {error_details}")
                    # Return default palettes instead of failing
                    return self._get_default_palettes(num_palettes, prompt)
            
            # Parse the response
            try:
                response_data = response.json()
                
                # The data could be in different formats depending on the LLM response
                if "result" in response_data:
                    # If the result is a JSON string, parse it
                    if isinstance(response_data["result"], str):
                        try:
                            palettes = json.loads(response_data["result"])
                            if isinstance(palettes, list):
                                return self._validate_and_clean_palettes(palettes, num_palettes, prompt)
                        except json.JSONDecodeError:
                            logger.error("Failed to parse JSON from result string")
                    
                    # If result is already a list
                    elif isinstance(response_data["result"], list):
                        return self._validate_and_clean_palettes(response_data["result"], num_palettes, prompt)
                
                # If the response is already the list we want
                elif isinstance(response_data, list):
                    return self._validate_and_clean_palettes(response_data, num_palettes, prompt)
                
                # Extract any JSON-like content from the response
                response_text = str(response_data)
                json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(0))
                        if isinstance(json_data, list):
                            return self._validate_and_clean_palettes(json_data, num_palettes, prompt)
                    except json.JSONDecodeError:
                        pass
                
                # If we can't parse anything useful, use defaults
                logger.warning("Failed to parse multiple palettes response, using defaults")
                return self._get_default_palettes(num_palettes, prompt)
                
            except Exception as e:
                logger.error(f"Error processing multiple palettes response: {e}")
                return self._get_default_palettes(num_palettes, prompt)
            
        except Exception as e:
            logger.error(f"Error generating multiple color palettes: {str(e)}")
            return self._get_default_palettes(num_palettes, prompt)
    
    def _validate_and_clean_palettes(self, palettes: List[Dict[str, Any]], num_palettes: int, prompt: str) -> List[Dict[str, Any]]:
        """
        Validate and clean palette data to ensure it meets our requirements.
        
        Args:
            palettes: The list of palette dictionaries to validate
            num_palettes: The number of palettes requested
            prompt: The original prompt for context
            
        Returns:
            List of validated palette dictionaries
        """
        valid_palettes = []
        
        for i, palette in enumerate(palettes[:num_palettes]):
            # Create a clean palette dict
            clean_palette = {
                "name": "Unnamed Palette",
                "colors": ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"],  # Default
                "description": f"A palette inspired by: {prompt}"
            }
            
            # Copy valid data
            if isinstance(palette, dict):
                if "name" in palette and isinstance(palette["name"], str):
                    clean_palette["name"] = palette["name"]
                
                if "description" in palette and isinstance(palette["description"], str):
                    clean_palette["description"] = palette["description"]
                
                if "colors" in palette and isinstance(palette["colors"], list):
                    # Validate colors (must be valid hex codes)
                    valid_colors = []
                    for color in palette["colors"]:
                        if isinstance(color, str) and color.startswith("#") and len(color) in [4, 7, 9]:
                            valid_colors.append(color)
                    
                    if valid_colors:
                        clean_palette["colors"] = valid_colors[:5]  # Limit to 5 colors
            
            valid_palettes.append(clean_palette)
        
        # If we didn't get enough valid palettes, pad with defaults
        if len(valid_palettes) < num_palettes:
            default_palettes = self._get_default_palettes(num_palettes - len(valid_palettes), prompt)
            valid_palettes.extend(default_palettes)
        
        return valid_palettes[:num_palettes]
    
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
            },
            {
                "name": "Vibrant Palette",
                "colors": ["#10B981", "#34D399", "#6EE7B7", "#ECFDF5", "#064E3B"],
                "description": f"A vibrant palette for: {prompt}"
            },
            {
                "name": "Complementary Palette",
                "colors": ["#8B5CF6", "#A78BFA", "#C4B5FD", "#EDE9FE", "#4C1D95"],
                "description": f"A complementary palette for: {prompt}"
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