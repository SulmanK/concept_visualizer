"""
JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import logging
import httpx
import json
from functools import lru_cache
from typing import List, Dict, Any, Optional, TypedDict, Union

from fastapi import Depends
from app.core.config import settings, get_masked_value
from app.utils.security.mask import mask_id
from app.core.exceptions import (
    JigsawStackError, 
    JigsawStackConnectionError, 
    JigsawStackAuthenticationError,
    JigsawStackGenerationError
)

logger = logging.getLogger(__name__)


# Define TypedDict for better type hints
class PaletteColor(TypedDict):
    """Color definition with hex value and name."""
    hex: str
    name: str


class Palette(TypedDict):
    """Color palette definition."""
    name: str
    description: str
    colors: List[PaletteColor]


class GenerationResponse(TypedDict):
    """Response from image generation API."""
    url: str  # URL to the generated image
    id: str   # Image ID


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
        logger.info(f"Initialized JigsawStack client with API URL: {api_url}")
    
    async def generate_image(
        self, 
        prompt: str, 
        width: int = 512, 
        height: int = 512, 
        model: str = "stable-diffusion-xl"
    ) -> Dict[str, str]:
        """
        Generate an image using the JigsawStack API.
        
        Args:
            prompt: The text prompt for image generation
            width: The width of the generated image
            height: The height of the generated image
            model: The model to use for generation
            
        Returns:
            Dictionary containing image URL and ID
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If the image generation fails
        """
        try:
            logger.info(f"Generating image with prompt: {prompt}")
            
            # Determine aspect ratio based on dimensions
            aspect_ratio = "1:1"  # Default
            if width > height:
                aspect_ratio = "16:9"
            elif height > width:
                aspect_ratio = "9:16"
            
            # Enhance the prompt for logo generation
            enhanced_prompt = f"""Create a professional logo design based on this description: {prompt}.

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
                "prompt": enhanced_prompt,
                "aspect_ratio": aspect_ratio,
                "steps": 30,
                "advance_config": {
                    "negative_prompt": "blurry, low quality, complex backgrounds, photorealistic elements, text that is not part of the logo design",
                    "guidance": 7.5
                }
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                try:
                    response = await client.post(
                        endpoint, 
                        headers=self.headers, 
                        json=payload
                    )
                except httpx.ConnectError as e:
                    raise JigsawStackConnectionError(
                        message=f"Failed to connect to JigsawStack API: {str(e)}",
                        details={"endpoint": endpoint}
                    )
                except httpx.TimeoutException as e:
                    raise JigsawStackConnectionError(
                        message=f"JigsawStack API timed out: {str(e)}",
                        details={"endpoint": endpoint, "timeout": "30.0"}
                    )
                
                # Handle authentication errors
                if response.status_code in (401, 403):
                    raise JigsawStackAuthenticationError(
                        message="Authentication failed with JigsawStack API",
                        details={"status_code": response.status_code}
                    )
                
                # Handle other error responses
                if response.status_code != 200:
                    logger.error(
                        f"Image generation API error: Status {response.status_code}, "
                        f"Response: {response.text[:200]}..."
                    )
                    raise JigsawStackGenerationError(
                        message="Image generation failed",
                        content_type="image",
                        prompt=prompt,
                        details={
                            "status_code": response.status_code,
                            "endpoint": endpoint,
                            "response_text": response.text[:200]  # Limit response text size
                        }
                    )
                
                # Parse response JSON
                try:
                    result = response.json()
                    logger.info("Image generation successful")
                    return {
                        "url": result["output"]["image_url"],
                        "id": result.get("id", "unknown")
                    }
                except (json.JSONDecodeError, KeyError) as e:
                    logger.error(f"Failed to parse image generation response: {str(e)}")
                    raise JigsawStackGenerationError(
                        message=f"Failed to parse image generation response: {str(e)}",
                        content_type="image",
                        prompt=prompt,
                        details={"response_text": response.text[:200]}
                    )
                
        except (JigsawStackConnectionError, JigsawStackAuthenticationError, JigsawStackGenerationError):
            # Re-raise domain-specific exceptions we've already created
            raise
        except Exception as e:
            # Catch any other exceptions and convert to domain-specific exception
            logger.error(f"Unexpected error generating image: {str(e)}")
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
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If the image refinement fails
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
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        endpoint, 
                        headers=self.headers, 
                        json=payload, 
                        timeout=30.0
                    )
            except httpx.ConnectError as e:
                raise JigsawStackConnectionError(
                    message=f"Failed to connect to JigsawStack API: {str(e)}",
                    details={"endpoint": endpoint}
                )
            except httpx.TimeoutException as e:
                raise JigsawStackConnectionError(
                    message=f"JigsawStack API timed out: {str(e)}",
                    details={"endpoint": endpoint, "timeout": "30.0"}
                )
                
            if response.status_code == 401 or response.status_code == 403:
                raise JigsawStackAuthenticationError(
                    message="Authentication failed with JigsawStack API",
                    details={"status_code": response.status_code}
                )
            
            if response.status_code != 200:
                error_details = f"Status: {response.status_code}, Response: {response.text}"
                logger.error(f"Image refinement API error: {error_details}")
                raise JigsawStackGenerationError(
                    message=f"Image refinement failed",
                    content_type="image_refinement",
                    prompt=prompt,
                    details={
                        "status_code": response.status_code,
                        "endpoint": endpoint,
                        "response_text": response.text[:200]  # Only include part of the response
                    }
                )
                
            logger.info("Image refinement successful, returning binary data")
            return response.content
                
        except (JigsawStackConnectionError, JigsawStackAuthenticationError, JigsawStackGenerationError):
            # Re-raise domain-specific exceptions we've already created
            raise
        except Exception as e:
            # Catch any other exceptions and convert to domain-specific exception
            logger.error(f"Unexpected error refining image: {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Unexpected error during image refinement: {str(e)}",
                content_type="image_refinement",
                prompt=prompt
            )
    
    async def generate_multiple_palettes(self, logo_description: str, theme_description: str, num_palettes: int = 7) -> List[Dict[str, Any]]:
        """Generate multiple color palettes in a single LLM call.
        
        Args:
            logo_description: Text description of the logo
            theme_description: Text description of the desired theme
            num_palettes: Number of palettes to generate
            
        Returns:
            List[Dict[str, Any]]: List of palette dictionaries with name, colors, and description
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails 
            JigsawStackGenerationError: If palette generation fails
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
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        endpoint, 
                        headers=self.headers, 
                        json=payload, 
                        timeout=40.0
                    )
            except httpx.ConnectError as e:
                raise JigsawStackConnectionError(
                    message=f"Failed to connect to JigsawStack API: {str(e)}",
                    details={"endpoint": endpoint}
                )
            except httpx.TimeoutException as e:
                raise JigsawStackConnectionError(
                    message=f"JigsawStack API timed out: {str(e)}",
                    details={"endpoint": endpoint, "timeout": "40.0"}
                )
                
            logger.info(f"Response status code: {response.status_code}")
            
            if response.status_code == 401 or response.status_code == 403:
                raise JigsawStackAuthenticationError(
                    message="Authentication failed with JigsawStack API",
                    details={"status_code": response.status_code}
                )
                
            if response.status_code != 200:
                error_details = f"Status: {response.status_code}, Response: {response.text}"
                logger.error(f"Color palette generation API error: {error_details}")
                # Use fallback palettes instead of failing
                logger.info("Using default color palettes as fallback")
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
                logger.error(f"Error processing palette response: {e}")
                return self._get_default_palettes(num_palettes, f"Logo: {logo_description}. Theme: {theme_description}")
        
        except (JigsawStackConnectionError, JigsawStackAuthenticationError):
            # Re-raise the connection and authentication errors
            raise
        except Exception as e:
            # For other errors, use the fallback palettes instead of failing
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

    async def get_variation(self, image_url: str, model: str = "stable-diffusion-xl") -> bytes:
        """
        Generate a variation of the provided image using the JigsawStack API.
        
        Args:
            image_url: URL of the image to generate a variation from
            model: The model to use for generation
            
        Returns:
            bytes: Binary data of the generated image
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If variation generation fails
        """
        try:
            logger.info(f"Generating variation of image {image_url}")
            endpoint = f"{self.api_url}/v1/stability/variation"
            
            payload = {
                "image_url": image_url,
                "model": model
            }
            
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(
                        endpoint, 
                        headers=self.headers, 
                        json=payload, 
                        timeout=60.0  # Variations can take longer
                    )
            except httpx.ConnectError as e:
                raise JigsawStackConnectionError(
                    message=f"Failed to connect to JigsawStack API for variation: {str(e)}",
                    details={"endpoint": endpoint}
                )
            except httpx.TimeoutException as e:
                raise JigsawStackConnectionError(
                    message=f"JigsawStack API timed out during variation request: {str(e)}",
                    details={"endpoint": endpoint, "timeout": "60.0"}
                )
                
            if response.status_code == 401 or response.status_code == 403:
                raise JigsawStackAuthenticationError(
                    message="Authentication failed with JigsawStack API during variation request",
                    details={"status_code": response.status_code}
                )
                
            if response.status_code != 200:
                error_details = {"status_code": response.status_code, "response_text": response.text}
                error_message = f"Failed to generate image variation. Status: {response.status_code}"
                logger.error(f"{error_message}. Response: {response.text}")
                raise JigsawStackGenerationError(
                    message=error_message,
                    details=error_details
                )
                
            # Get the image data from the response
            try:
                response_json = response.json()
                if not response_json.get("success"):
                    error_message = "Variation generation reported failure"
                    logger.error(f"{error_message}. Response: {response_json}")
                    raise JigsawStackGenerationError(
                        message=error_message,
                        details={"api_response": response_json}
                    )
                    
                if "image_url" not in response_json:
                    error_message = "No image URL in successful variation response"
                    logger.error(f"{error_message}. Response: {response_json}")
                    raise JigsawStackGenerationError(
                        message=error_message,
                        details={"api_response": response_json}
                    )
                    
                # Get the binary image data from the URL
                image_url = response_json["image_url"]
                logger.info(f"Variation generated successfully. Downloading from: {image_url}")
                
                # Download the image
                try:
                    async with httpx.AsyncClient() as client:
                        image_response = await client.get(image_url, timeout=30.0)
                        
                    if image_response.status_code != 200:
                        error_message = f"Failed to download variation image. Status: {image_response.status_code}"
                        logger.error(error_message)
                        raise JigsawStackGenerationError(
                            message=error_message,
                            details={"status_code": image_response.status_code, "image_url": image_url}
                        )
                        
                    return image_response.content
                except httpx.ConnectError as e:
                    raise JigsawStackConnectionError(
                        message=f"Failed to connect to image URL: {str(e)}",
                        details={"image_url": image_url}
                    )
                except httpx.TimeoutException as e:
                    raise JigsawStackConnectionError(
                        message=f"Timed out downloading image: {str(e)}",
                        details={"image_url": image_url, "timeout": "30.0"}
                    )
                except Exception as e:
                    raise JigsawStackGenerationError(
                        message=f"Error downloading variation image: {str(e)}",
                        details={"image_url": image_url}
                    )
            except Exception as e:
                raise JigsawStackGenerationError(
                    message=f"Error processing variation response: {str(e)}",
                    details={"response_text": response.text}
                )
        
        except (JigsawStackConnectionError, JigsawStackAuthenticationError, JigsawStackGenerationError):
            # Re-raise these exceptions
            raise
        except Exception as e:
            # Catch any other exceptions and convert to a JigsawStackGenerationError
            raise JigsawStackGenerationError(
                message=f"Unexpected error generating image variation: {str(e)}",
                details={"image_url": image_url, "model": model}
            )


@lru_cache()
def get_jigsawstack_client() -> JigsawStackClient:
    """
    Factory function for JigsawStackClient instances.
    
    Returns:
        JigsawStackClient: A singleton instance of the JigsawStack client
    """
    # Mask the API key in logs
    masked_api_key = mask_id(settings.JIGSAWSTACK_API_KEY) if settings.JIGSAWSTACK_API_KEY else "none"
    logger.info(f"Creating JigsawStack client with API key: {masked_api_key}...")
    return JigsawStackClient(
        api_key=settings.JIGSAWSTACK_API_KEY,
        api_url=settings.JIGSAWSTACK_API_URL
    ) 