"""
JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import logging
import httpx
import json
from functools import lru_cache
from typing import List, Dict, Any

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
        self, logo_description: str, width: int = 512, height: int = 512, model: str = "stable-diffusion-xl"
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
            logger.info(f"Generating image with prompt: {logo_description}")
            
            # Determine aspect ratio based on dimensions
            aspect_ratio = "1:1"  # Default
            if width > height:
                aspect_ratio = "16:9"
            elif height > width:
                aspect_ratio = "9:16"
            
            prompt = f"""Create a professional logo design based on this description: {logo_description}.

Design requirements:
- Create a minimalist, scalable vector-style logo
- Use simple shapes with clean edges for easy masking
- Include distinct foreground and background elements
- Avoid complex gradients or photorealistic elements
- Design with high contrast between elements
- Create clear boundaries between different parts of the logo
- Ensure the design works in monochrome before color is applied
- Text or typography can be included if appropriate for the logo
"""

            # Use the correct endpoint according to API reference
            endpoint = f"{self.api_url}/v1/ai/image_generation"
            payload = {
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "steps": 30,
                "advance_config": {
                    "negative_prompt": "blurry, low quality, complex backgrounds, photorealistic elements,",
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
    
    async def generate_multiple_palettes(self, logo_description: str, theme_description: str, num_palettes: int = 7) -> List[Dict[str, Any]]:
        """Generate multiple color palettes in a single LLM call.
        
        Args:
            logo_description: Text description of the logo
            theme_description: Text description of the desired theme
            num_palettes: Number of palettes to generate
            
        Returns:
            List[Dict[str, Any]]: List of palette dictionaries with name, colors, and description
            
        Raises:
            Exception: If the API request fails
        """
        try:
            logger.info(f"Generating {num_palettes} color palettes based on logo and theme descriptions")
            
            
            # Create payload using the structure from the working example
            payload = {
                "inputs": [
                    {
                        "key": "theme_description",
                        "optional": False,
                        "initial_value": "theme description"
                    },
                    {
                        "key": "logo_description",
                        "optional": False,
                        "initial_value": "logo description"
                    },
                    {
                        "key": "num_palettes", 
                        "optional": True,
                        "initial_value": "8"
                    }
                ],
               # "prompt": "Generate {num_palettes} creative color palettes for a brand with logo and theme described as: {theme}. Each palette should have a descriptive name related to the brand, 5 harmonious hex color codes, and a brief explanation of how it relates to the brand identity.",
                "prompt": "Generate exactly {num_palettes} professional color palettes for a logo with the following description: {logo_description}. The theme is: {theme_description}. For each palette: - Include exactly 5 colors (primary, secondary, accent, background, and highlight) - Provide the exact hex codes (e.g., #FFFFFF) - Ensure sufficient contrast between elements for accessibility - Make each palette distinctly different from the others Ensure variety across the 7 palettes by including: - At least one monochromatic palette - At least one palette with complementary colors - At least one high-contrast palette - At least one palette with a transparent/white background option",
                
                "prompt_guard": ["hate", "sexual_content",],
                "input_values": {
                    "logo_description": logo_description,
                    "theme_description": theme_description,
                    "num_palettes": str(num_palettes)
                },
                "return_prompt": [
                    {
                        "name": "Name of the palette",
                        "colors": [
                            {
                                "0": "#colorhex1",
                                "1": "#colorhex2",
                                "2": "#colorhex3",
                                "3": "#colorhex4",
                                "4": "#colorhex5"
                            }
                        ],
                        "description": "Description of how the palette relates to the theme."
                    }
                ],
                "optimize_prompt": True
            }
            
            # Log the exact payload being sent for debugging
            logger.info("Sending request to prompt engine with combined logo and theme description")
            
            endpoint = f"{self.api_url}/v1/prompt_engine/run"
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    endpoint, 
                    headers=self.headers, 
                    json=payload, 
                    timeout=40.0
                )
                
                logger.info(f"Response status code: {response.status_code}")
                
                if response.status_code != 200:
                    error_details = f"Status: {response.status_code}, Response: {response.text}"
                    logger.error(f"Color palette generation API error: {error_details}")
                    return self._get_default_palettes(num_palettes, f"Logo: {logo_description}. Theme: {theme_description}")
                
                # Parse the response
                try:
                    response_data = response.json()
                    logger.info(f"Raw API response structure: {list(response_data.keys()) if isinstance(response_data, dict) else type(response_data)}")
                    
                    # Check if we have a successful result
                    if isinstance(response_data, dict) and response_data.get("success") is True and "result" in response_data:
                        raw_palettes = response_data["result"]
                        if isinstance(raw_palettes, list) and raw_palettes:
                            # Process each palette to extract colors properly
                            processed_palettes = [self._process_palette_colors(palette) for palette in raw_palettes]
                            return self._validate_and_clean_palettes(processed_palettes, num_palettes, f"Logo: {logo_description}. Theme: {theme_description}")
                    
                    # If we couldn't get proper palettes from the response
                    logger.warning("Invalid response format from JigsawStack API")
                    return self._get_default_palettes(num_palettes, f"Logo: {logo_description}. Theme: {theme_description}")
                    
                except Exception as e:
                    logger.error(f"Error processing response: {e}")
                    return self._get_default_palettes(num_palettes, f"Logo: {logo_description}. Theme: {theme_description}")
            
        except Exception as e:
            logger.error(f"Error generating multiple color palettes: {str(e)}")
            return self._get_default_palettes(num_palettes, f"Logo: {logo_description}. Theme: {theme_description}")
    
    def _process_palette_colors(self, palette: Dict[str, Any]) -> Dict[str, Any]:
        """Process the color structure from JigsawStack API to create a list of hex colors.
        
        Args:
            palette: A palette dictionary from the API response
            
        Returns:
            A palette dictionary with simplified colors list
        """
        processed_palette = palette.copy()
        hex_colors = []
        
        # Handle different possible color structure formats in the API response
        if isinstance(palette.get("colors"), list):
            color_list = palette["colors"]
            
            for color_item in color_list:
                # Case 1: Direct list of hex colors
                if isinstance(color_item, str) and color_item.startswith("#"):
                    hex_colors.append(color_item)
                
                # Case 2: Dictionary with numeric keys
                elif isinstance(color_item, dict):
                    for _, hex_value in color_item.items():
                        if isinstance(hex_value, str) and hex_value.startswith("#"):
                            hex_colors.append(hex_value)
        
        # If we have colors, use them; otherwise, use defaults
        if hex_colors:
            processed_palette["colors"] = hex_colors[:5]  # Limit to 5 colors
        else:
            processed_palette["colors"] = ["#333333", "#666666", "#999999", "#CCCCCC", "#FFFFFF"]
        
        return processed_palette
    
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
                    if palette["colors"]:
                        clean_palette["colors"] = palette["colors"][:5]  # Limit to 5 colors
            
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
            },
            {
                "name": "Warm Palette",
                "colors": ["#F59E0B", "#FBBF24", "#FCD34D", "#FEF3C7", "#92400E"],
                "description": f"A warm and inviting palette for: {prompt}"
            },
            {
                "name": "Cool Palette",
                "colors": ["#0EA5E9", "#38BDF8", "#7DD3FC", "#E0F2FE", "#075985"],
                "description": f"A cool and refreshing palette for: {prompt}"
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