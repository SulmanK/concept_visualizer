"""JigsawStack API client implementation.

This module provides a client for interacting with the JigsawStack API.
"""

import json
import logging
import traceback
import uuid
from functools import lru_cache
from typing import Any, Dict, List, Tuple, TypedDict

import httpx

from app.core.config import settings
from app.core.exceptions import JigsawStackAuthenticationError, JigsawStackConnectionError, JigsawStackError, JigsawStackGenerationError
from app.utils.security.mask import mask_id

# Configure logging
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
    id: str  # Image ID


class JigsawStackClient:
    """Client for interacting with JigsawStack API for concept generation and refinement."""

    def __init__(self, api_key: str, api_url: str):
        """Initialize the JigsawStack API client.

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
            "x-api-key": api_key,  # Some endpoints use x-api-key instead of Authorization
        }
        logger.info(f"Initialized JigsawStack client with API URL: {api_url}")

    async def generate_image(
        self,
        prompt: str,
        width: int = 256,
        height: int = 256,
        model: str = "stable-diffusion-xl",
    ) -> Dict[str, Any]:
        """Generate an image using the JigsawStack API.

        Args:
            prompt: The text prompt for image generation
            width: The width of the generated image
            height: The height of the generated image
            model: The model to use for generation

        Returns:
            Dictionary containing image URL, ID, and optionally binary_data

        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If the image generation fails
        """
        try:
            logger.info(f"Generating image with prompt: {prompt}")

            # Prepare request data
            endpoint, payload = self._prepare_image_generation_request(prompt, width, height)

            # Make the API request with retries
            response = await self._make_api_request_with_retry(endpoint, payload)

            # Process the response
            return await self._process_image_generation_response(response, prompt, endpoint)

        except JigsawStackError:
            # Re-raise JigsawStack-specific errors
            raise
        except Exception as e:
            # Handle unexpected errors
            error_detail = f"Unexpected error during image generation: {str(e)}"
            logger.error(error_detail)
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
            raise JigsawStackGenerationError(
                message=error_detail,
                content_type="image",
                prompt=prompt,
            )

    def _prepare_image_generation_request(self, prompt: str, width: int, height: int) -> Tuple[str, Dict[str, Any]]:
        """Prepare the request data for image generation.

        Args:
            prompt: The text prompt for image generation
            width: The width of the generated image
            height: The height of the generated image

        Returns:
            Tuple containing endpoint URL and request payload
        """
        # Determine aspect ratio based on dimensions
        aspect_ratio = "1:1"  # Default
        if width > height:
            aspect_ratio = "16:9"
        elif height > width:
            aspect_ratio = "9:16"

        # Enhance the prompt for logo generation - use ONLY the logo description, not the theme
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
                "guidance": 7.5,
            },
        }

        logger.debug(f"Sending request to {endpoint} with payload: {json.dumps(payload)[:200]}...")
        return endpoint, payload

    async def _make_api_request_with_retry(self, endpoint: str, payload: Dict[str, Any]) -> httpx.Response:
        """Make an API request with retry logic.

        Args:
            endpoint: The API endpoint to call
            payload: The request payload

        Returns:
            The API response

        Raises:
            JigsawStackConnectionError: If connection fails after all retries
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If the API returns an error
        """
        # Set up retry parameters
        max_retries = 3
        retry_count = 0
        retry_statuses = [429, 500, 502, 503, 504]  # Status codes that should trigger a retry

        # Use a longer timeout for image generation (90 seconds instead of 30)
        while retry_count < max_retries:
            try:
                async with httpx.AsyncClient(timeout=90.0) as client:
                    try:
                        logger.debug(f"Attempt {retry_count + 1}/{max_retries} to generate image")
                        response = await client.post(endpoint, headers=self.headers, json=payload)

                        # If status code indicates we should retry, raise an exception to trigger retry logic
                        if response.status_code in retry_statuses:
                            retry_count += 1
                            wait_time = min(2**retry_count, 60)  # Exponential backoff with a max of 60 seconds
                            logger.warning(f"Received status {response.status_code}, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                            import asyncio

                            await asyncio.sleep(wait_time)
                            continue

                    except httpx.ConnectError as e:
                        error_detail = f"Failed to connect to JigsawStack API: {str(e)}"
                        logger.error(error_detail)

                        # Retry on connection errors
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = min(2**retry_count, 60)
                            logger.warning(f"Connection error, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                            import asyncio

                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise JigsawStackConnectionError(
                                message=error_detail,
                                details={"endpoint": endpoint},
                            )

                    except httpx.TimeoutException as e:
                        error_detail = f"JigsawStack API timed out: {str(e)}"
                        logger.error(error_detail)

                        # Retry on timeouts
                        retry_count += 1
                        if retry_count < max_retries:
                            wait_time = min(2**retry_count, 60)
                            logger.warning(f"Timeout error, retrying in {wait_time} seconds (attempt {retry_count}/{max_retries})")
                            import asyncio

                            await asyncio.sleep(wait_time)
                            continue
                        else:
                            raise JigsawStackConnectionError(
                                message=error_detail,
                                details={"endpoint": endpoint, "timeout": "90.0"},
                            )

                    # Handle authentication errors - don't retry these
                    if response.status_code in (401, 403):
                        error_detail = f"Authentication failed with JigsawStack API: {response.status_code}"
                        logger.error(error_detail)
                        raise JigsawStackAuthenticationError(
                            message=error_detail,
                            details={"status_code": response.status_code},
                        )

                    # Handle other error responses that we shouldn't retry
                    if response.status_code != 200 and response.status_code not in retry_statuses:
                        self._handle_error_response(response, endpoint, payload["prompt"])

                    # If we got here, status is 200, break out of retry loop
                    break

            except (httpx.ConnectError, httpx.TimeoutException):
                # These exceptions are already handled in the inner try/except
                pass

        # If we exhausted all retries without breaking out of the loop
        if retry_count >= max_retries and response.status_code in retry_statuses:
            error_detail = f"Maximum retries ({max_retries}) exceeded with status code {response.status_code}"
            logger.error(error_detail)
            raise JigsawStackConnectionError(
                message=error_detail,
                details={"endpoint": endpoint, "status_code": response.status_code},
            )

        return response

    def _handle_error_response(self, response: httpx.Response, endpoint: str, prompt: str) -> None:
        """Handle error responses from the API.

        Args:
            response: The API response
            endpoint: The API endpoint
            prompt: The original prompt

        Raises:
            JigsawStackGenerationError: With appropriate error details
        """
        # Try to decode the response as JSON to get more error details
        try:
            error_json = response.json()
            error_message = error_json.get("message", "Unknown error")
            error_detail = f"Image generation failed - {json.dumps(error_json)[:300]}"
        except Exception:
            error_message = "Image generation failed"
            error_detail = f"Status {response.status_code}, Response: {str(response.content[:200])}..."

        logger.error(f"Image generation API error: {error_detail}")
        raise JigsawStackGenerationError(
            message=f"Image generation failed - {error_message}",
            content_type="image",
            prompt=prompt,
            details={
                "status_code": response.status_code,
                "endpoint": endpoint,
                "response_content": str(response.content[:300]),
            },
        )

    async def _process_image_generation_response(self, response: httpx.Response, prompt: str, endpoint: str) -> Dict[str, Any]:
        """Process the response from image generation API.

        Args:
            response: The API response
            prompt: The original prompt
            endpoint: The API endpoint

        Returns:
            Dictionary containing image URL and ID

        Raises:
            JigsawStackGenerationError: If processing the response fails
        """
        # Check if the response is binary data (image) or JSON
        content_type = response.headers.get("content-type", "")
        logger.debug(f"Response content type: {content_type}")

        if "application/json" in content_type:
            return self._process_json_response(response, prompt, endpoint)
        elif any(
            img_type in content_type
            for img_type in [
                "image/png",
                "image/jpeg",
                "image/jpg",
                "image/webp",
            ]
        ):
            return self._process_binary_response(response)
        else:
            # Unknown content type, try to handle it
            return self._process_unknown_content_type(response, prompt, endpoint, content_type)

    def _process_json_response(self, response: httpx.Response, prompt: str, endpoint: str) -> Dict[str, Any]:
        """Process a JSON response from the API.

        Args:
            response: The API response
            prompt: The original prompt
            endpoint: The API endpoint

        Returns:
            Dictionary containing image URL and ID

        Raises:
            JigsawStackGenerationError: If processing the response fails
        """
        try:
            result = response.json()
            logger.debug(f"JSON response: {json.dumps(result)[:500]}...")

            # Deep inspection of the response structure
            if not result:
                logger.error("Empty JSON response from API")
                raise JigsawStackGenerationError(
                    message="Empty JSON response from image generation API",
                    content_type="image",
                    prompt=prompt,
                    details={"endpoint": endpoint},
                )

            # Extract the image URL from the response
            # Handle different response formats from the API
            image_url = self._extract_image_url(result, prompt, endpoint)

            # Get the image ID, with fallbacks
            image_id = result.get("id", result.get("output", {}).get("id", str(uuid.uuid4())))

            # Return the image URL and ID
            return {"url": image_url, "id": image_id}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Failed to parse JSON response: {str(e)}",
                content_type="image",
                prompt=prompt,
                details={"endpoint": endpoint},
            )

    def _extract_image_url(self, result: Dict[str, Any], prompt: str, endpoint: str) -> str:
        """Extract the image URL from the response.

        Args:
            result: The parsed JSON response
            prompt: The original prompt
            endpoint: The API endpoint

        Returns:
            The image URL

        Raises:
            JigsawStackGenerationError: If the image URL cannot be found
        """
        image_url = None
        if "output" in result and isinstance(result["output"], dict) and "image_url" in result["output"]:
            # Format: {"output": {"image_url": "https://..."}}
            image_url = result["output"]["image_url"]
            logger.debug(f"Found image URL in output.image_url: {image_url[:100]}...")
        elif "url" in result:
            # Format: {"url": "https://..."}
            image_url = result["url"]
            logger.debug(f"Found image URL in url field: {image_url[:100]}...")
        elif "data" in result and isinstance(result["data"], dict) and "url" in result["data"]:
            # Format: {"data": {"url": "https://..."}}
            image_url = result["data"]["url"]
            logger.debug(f"Found image URL in data.url field: {image_url[:100]}...")
        else:
            # No familiar structure found
            logger.error(f"Could not find image URL in response: {json.dumps(result)[:300]}...")
            raise JigsawStackGenerationError(
                message="Could not find image URL in response",
                content_type="image",
                prompt=prompt,
                details={"endpoint": endpoint, "response": json.dumps(result)[:500]},
            )

        # Ensure we return a string value to satisfy type checking
        if image_url is None:
            # This should never happen due to the exception above, but mypy doesn't know that
            raise JigsawStackGenerationError(
                message="Failed to extract image URL from response",
                content_type="image",
                prompt=prompt,
                details={"endpoint": endpoint},
            )

        return str(image_url)

    def _process_binary_response(self, response: httpx.Response) -> Dict[str, Any]:
        """Process a binary image response.

        Args:
            response: The API response

        Returns:
            Dictionary containing image URL, ID and binary_data

        Raises:
            JigsawStackGenerationError: If processing the response fails
        """
        try:
            # Create a temporary file or directly pass bytes to caller
            logger.info("Image generation successful (binary response)")
            import os
            import tempfile
            import uuid

            # Generate a temporary filename
            filename = f"temp_image_{uuid.uuid4()}.png"
            temp_path = os.path.join(tempfile.gettempdir(), filename)

            # Save the image data
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # Return the local path as URL for now
            return {
                "url": f"file://{temp_path}",
                "id": str(uuid.uuid4()),
                "binary_data": response.content,
            }
        except Exception as binary_error:
            logger.error(f"Failed to process binary image data: {str(binary_error)}")
            raise JigsawStackGenerationError(
                message=f"Failed to process binary image data: {str(binary_error)}",
                content_type="image",
                prompt="",  # We don't have access to the prompt here
            )

    def _process_unknown_content_type(self, response: httpx.Response, prompt: str, endpoint: str, content_type: str) -> Dict[str, Any]:
        """Process a response with unknown content type.

        Args:
            response: The API response
            prompt: The original prompt
            endpoint: The API endpoint
            content_type: The content type of the response

        Returns:
            Dictionary containing image information

        Raises:
            JigsawStackGenerationError: If the response cannot be processed
        """
        # Unrecognized content type
        logger.error(f"Unrecognized content type: {content_type}")

        # Try to determine if it's binary data based on content
        if response.content and len(response.content) > 4 and response.content[0:4] == b"\x89PNG":
            logger.info("Detected PNG image data in response")
            # Handle as PNG binary data
            import os
            import tempfile
            import uuid

            # Generate a temporary filename
            filename = f"temp_image_{uuid.uuid4()}.png"
            temp_path = os.path.join(tempfile.gettempdir(), filename)

            # Save the image data
            with open(temp_path, "wb") as f:
                f.write(response.content)

            # Return the local path as URL for now
            return {
                "url": f"file://{temp_path}",
                "id": str(uuid.uuid4()),
                "binary_data": response.content,
            }

        # Try to parse as JSON anyways in case the content-type is wrong
        try:
            result = json.loads(response.content)
            logger.warning("Found JSON data despite incorrect content type")
            # Handle the parsed JSON the same way as above
            if "output" in result and isinstance(result["output"], dict) and "image_url" in result["output"]:
                return {
                    "url": result["output"]["image_url"],
                    "id": result.get("id", "unknown"),
                }
            elif "url" in result:
                return {
                    "url": result["url"],
                    "id": result.get("id", "unknown"),
                }
        except json.JSONDecodeError:
            # Not valid JSON, probably binary data
            pass

        # If we got here, we don't know how to handle the response
        logger.error(f"Unable to process response with content type: {content_type}")
        raise JigsawStackGenerationError(
            message=f"Unable to process response with content type: {content_type}",
            content_type="image",
            prompt=prompt,
            details={"content_type": content_type},
        )

    async def refine_image(
        self,
        prompt: str,
        image_url: str,
        strength: float = 0.7,
        model: str = "stable-diffusion-xl",
    ) -> bytes:
        """Refine an existing image using the JigsawStack API.

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
                    "guidance": 7.5,
                },
            }

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(endpoint, headers=self.headers, json=payload, timeout=30.0)
            except httpx.ConnectError as e:
                raise JigsawStackConnectionError(
                    message=f"Failed to connect to JigsawStack API: {str(e)}",
                    details={"endpoint": endpoint},
                )
            except httpx.TimeoutException as e:
                raise JigsawStackConnectionError(
                    message=f"JigsawStack API timed out: {str(e)}",
                    details={"endpoint": endpoint, "timeout": "30.0"},
                )

            if response.status_code == 401 or response.status_code == 403:
                raise JigsawStackAuthenticationError(
                    message="Authentication failed with JigsawStack API",
                    details={"status_code": response.status_code},
                )

            if response.status_code != 200:
                error_details = f"Status: {response.status_code}, Response: {response.text}"
                logger.error(f"Image refinement API error: {error_details}")
                raise JigsawStackGenerationError(
                    message="Image refinement failed",
                    content_type="image_refinement",
                    prompt=prompt,
                    details={
                        "status_code": response.status_code,
                        "endpoint": endpoint,
                        "response_text": response.text[:200],
                    },  # Only include part of the response
                )

            logger.info("Image refinement successful, returning binary data")
            return response.content

        except (
            JigsawStackConnectionError,
            JigsawStackAuthenticationError,
            JigsawStackGenerationError,
        ):
            # Re-raise domain-specific exceptions we've already created
            raise
        except Exception as e:
            # Catch any other exceptions and convert to domain-specific exception
            logger.error(f"Unexpected error refining image: {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Unexpected error during image refinement: {str(e)}",
                content_type="image_refinement",
                prompt=prompt,
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
                        "initial_value": "theme description",
                    },
                    {
                        "key": "logo_description",
                        "optional": False,
                        "initial_value": "logo description",
                    },
                    {"key": "num_palettes", "optional": True, "initial_value": "8"},
                ],
                "prompt": "Generate exactly {num_palettes} professional color palettes for a logo with the following description: {logo_description}. The theme is: {theme_description}. For each palette: - Include exactly 5 colors (primary, secondary, accent, background, and highlight) - Provide the exact hex codes (e.g., #FFFFFF) - Ensure sufficient contrast between elements for accessibility - Make each palette distinctly different from the others Ensure variety across the 7 palettes by including: - At least one monochromatic palette - At least one palette with complementary colors - At least one high-contrast palette - At least one palette with a transparent/white background option",
                "prompt_guard": [
                    "hate",
                    "sexual_content",
                ],
                "input_values": {
                    "logo_description": logo_description,
                    "theme_description": theme_description,
                    "num_palettes": str(num_palettes),
                },
                "return_prompt": [
                    {
                        "name": "Name of the palette",
                        "colors": [
                            {
                                "first_color": "#colorhex1",
                                "second_color": "#colorhex2",
                                "third_color": "#colorhex3",
                                "fourth_color": "#colorhex4",
                                "fifth_color": "#colorhex5",
                            }
                        ],
                        "description": "Description of how the palette relates to the theme.",
                    }
                ],
                "optimize_prompt": True,
            }

            # Log the exact payload being sent for debugging
            logger.info("Sending request to prompt engine with combined logo and theme description")

            endpoint = f"{self.api_url}/v1/prompt_engine/run"

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(endpoint, headers=self.headers, json=payload, timeout=40.0)
            except httpx.ConnectError as e:
                raise JigsawStackConnectionError(
                    message=f"Failed to connect to JigsawStack API: {str(e)}",
                    details={"endpoint": endpoint},
                )
            except httpx.TimeoutException as e:
                raise JigsawStackConnectionError(
                    message=f"JigsawStack API timed out: {str(e)}",
                    details={"endpoint": endpoint, "timeout": "40.0"},
                )

            logger.info(f"Response status code: {response.status_code}")

            if response.status_code == 401 or response.status_code == 403:
                raise JigsawStackAuthenticationError(
                    message="Authentication failed with JigsawStack API",
                    details={"status_code": response.status_code},
                )

            if response.status_code != 200:
                error_details = f"Status: {response.status_code}, Response: {response.text}"
                logger.error(f"Color palette generation API error: {error_details}")
                # Use fallback palettes instead of failing
                logger.info("Using default color palettes as fallback")
                return self._get_default_palettes(
                    num_palettes,
                    f"Logo: {logo_description}. Theme: {theme_description}",
                )

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
                        return self._validate_and_clean_palettes(
                            processed_palettes,
                            num_palettes,
                            f"Logo: {logo_description}. Theme: {theme_description}",
                        )

                # If we couldn't get proper palettes from the response
                logger.warning("Invalid response format from JigsawStack API")
                return self._get_default_palettes(
                    num_palettes,
                    f"Logo: {logo_description}. Theme: {theme_description}",
                )

            except Exception as e:
                logger.error(f"Error processing palette response: {e}")
                return self._get_default_palettes(
                    num_palettes,
                    f"Logo: {logo_description}. Theme: {theme_description}",
                )

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
            processed_palette["colors"] = [
                "#333333",
                "#666666",
                "#999999",
                "#CCCCCC",
                "#FFFFFF",
            ]

        return processed_palette

    def _validate_and_clean_palettes(self, palettes: List[Dict[str, Any]], num_palettes: int, prompt: str) -> List[Dict[str, Any]]:
        """Validate and clean palette data to ensure it meets our requirements.

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
                "colors": ["#4F46E5", "#818CF8", "#C4B5FD", "#F5F3FF", "#1E1B4B"],
                "description": f"A palette inspired by: {prompt}",
            }  # Default

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
        """Generate default color palettes as a fallback.

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
                "description": f"A primary palette for: {prompt}",
            },
            {
                "name": "Accent Palette",
                "colors": ["#EF4444", "#F87171", "#FCA5A5", "#FEE2E2", "#7F1D1D"],
                "description": f"An accent palette for: {prompt}",
            },
            {
                "name": "Neutral Palette",
                "colors": ["#1F2937", "#4B5563", "#9CA3AF", "#E5E7EB", "#F9FAFB"],
                "description": f"A neutral palette for: {prompt}",
            },
            {
                "name": "Vibrant Palette",
                "colors": ["#10B981", "#34D399", "#6EE7B7", "#ECFDF5", "#064E3B"],
                "description": f"A vibrant palette for: {prompt}",
            },
            {
                "name": "Complementary Palette",
                "colors": ["#8B5CF6", "#A78BFA", "#C4B5FD", "#EDE9FE", "#4C1D95"],
                "description": f"A complementary palette for: {prompt}",
            },
            {
                "name": "Warm Palette",
                "colors": ["#F59E0B", "#FBBF24", "#FCD34D", "#FEF3C7", "#92400E"],
                "description": f"A warm and inviting palette for: {prompt}",
            },
            {
                "name": "Cool Palette",
                "colors": ["#0EA5E9", "#38BDF8", "#7DD3FC", "#E0F2FE", "#075985"],
                "description": f"A cool and refreshing palette for: {prompt}",
            },
        ][:num_palettes]

    async def get_variation(self, image_url: str, model: str = "stable-diffusion-xl") -> bytes:
        """Generate a variation of the provided image using the JigsawStack API.

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

            payload = {"image_url": image_url, "model": model}

            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(endpoint, headers=self.headers, json=payload, timeout=60.0)  # Variations can take longer
            except httpx.ConnectError as e:
                raise JigsawStackConnectionError(
                    message=f"Failed to connect to JigsawStack API for variation: {str(e)}",
                    details={"endpoint": endpoint},
                )
            except httpx.TimeoutException as e:
                raise JigsawStackConnectionError(
                    message=f"JigsawStack API timed out during variation request: {str(e)}",
                    details={"endpoint": endpoint, "timeout": "60.0"},
                )

            if response.status_code == 401 or response.status_code == 403:
                raise JigsawStackAuthenticationError(
                    message="Authentication failed with JigsawStack API during variation request",
                    details={"status_code": response.status_code},
                )

            if response.status_code != 200:
                error_details = {
                    "status_code": response.status_code,
                    "response_text": response.text,
                }
                error_message = f"Failed to generate image variation. Status: {response.status_code}"
                logger.error(f"{error_message}. Response: {response.text}")
                raise JigsawStackGenerationError(message=error_message, details=error_details)

            # Get the image data from the response
            try:
                response_json = response.json()
                if not response_json.get("success"):
                    error_message = "Variation generation reported failure"
                    logger.error(f"{error_message}. Response: {response_json}")
                    raise JigsawStackGenerationError(message=error_message, details={"api_response": response_json})

                if "image_url" not in response_json:
                    error_message = "No image URL in successful variation response"
                    logger.error(f"{error_message}. Response: {response_json}")
                    raise JigsawStackGenerationError(message=error_message, details={"api_response": response_json})

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
                            details={
                                "status_code": image_response.status_code,
                                "image_url": image_url,
                            },
                        )

                    return image_response.content
                except httpx.ConnectError as e:
                    raise JigsawStackConnectionError(
                        message=f"Failed to connect to image URL: {str(e)}",
                        details={"image_url": image_url},
                    )
                except httpx.TimeoutException as e:
                    raise JigsawStackConnectionError(
                        message=f"Timed out downloading image: {str(e)}",
                        details={"image_url": image_url, "timeout": "30.0"},
                    )
                except Exception as e:
                    raise JigsawStackGenerationError(
                        message=f"Error downloading variation image: {str(e)}",
                        details={"image_url": image_url},
                    )
            except Exception as e:
                raise JigsawStackGenerationError(
                    message=f"Error processing variation response: {str(e)}",
                    details={"response_text": response.text},
                )

        except (
            JigsawStackConnectionError,
            JigsawStackAuthenticationError,
            JigsawStackGenerationError,
        ):
            # Re-raise these exceptions
            raise
        except Exception as e:
            # Catch any other exceptions and convert to a JigsawStackGenerationError
            raise JigsawStackGenerationError(
                message=f"Unexpected error generating image variation: {str(e)}",
                details={"image_url": image_url, "model": model},
            )

    async def generate_image_with_palette(
        self,
        logo_prompt: str,
        palette: List[str],
        palette_name: str = "",
        width: int = 256,
        height: int = 256,
    ) -> bytes:
        """Generate an image with a specific color palette.

        Args:
            logo_prompt: The logo description for image generation
            palette: List of hex color codes to use in the image
            palette_name: Optional name of the palette for logging
            width: The width of the generated image
            height: The height of the generated image

        Returns:
            Binary image data

        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If the image generation fails
        """
        try:
            logger.info(f"Generating image for palette '{palette_name}' with colors: {palette}")

            # Convert color array to comma-separated string
            color_string = ", ".join(palette)

            # Create an enhanced prompt that mentions the colors
            enhanced_prompt = f"""Create a professional logo design based on this description: {logo_prompt}.
Use ONLY these specific colors in the design: {color_string}.

Design requirements:
- Create a minimalist, scalable vector-style logo
- ONLY use the specified color palette: {color_string}
- Use simple shapes with clean edges for easy masking
- Include distinct foreground and background elements
- Design with high contrast between elements
- Create clear boundaries between different parts of the logo
- Text or typography can be included if appropriate for the logo
"""

            # Generate the image with our standard method
            result = await self.generate_image(prompt=enhanced_prompt, width=width, height=height)

            # If we got a binary_data key, return it directly
            if "binary_data" in result:
                binary_data: bytes = result["binary_data"]
                return binary_data

            # Otherwise, if it's a URL, download the image
            if "url" in result:
                image_url = result["url"]

                # Handle file:// URLs (temporary files)
                if image_url.startswith("file://"):
                    local_path = image_url[7:]  # Remove 'file://' prefix
                    with open(local_path, "rb") as f:
                        image_data = f.read()
                    return image_data

                # Download from remote URL
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    return response.content

            # If we get here, something went wrong
            raise JigsawStackGenerationError(
                message="Failed to generate image with palette: Invalid response format",
                content_type="image",
                prompt=logo_prompt,
                details={"palette": palette, "result": str(result)},
            )

        except (JigsawStackError, httpx.HTTPError) as e:
            # Pass through JigsawStackError exceptions
            if isinstance(e, JigsawStackError):
                raise

            # Convert other exceptions to JigsawStackError
            logger.error(f"Error generating image with palette '{palette_name}': {str(e)}")
            raise JigsawStackGenerationError(
                message=f"Failed to generate image with palette: {str(e)}",
                content_type="image",
                prompt=logo_prompt,
                details={"palette": palette},
            )


@lru_cache()
def get_jigsawstack_client() -> JigsawStackClient:
    """Factory function for JigsawStackClient instances.

    Returns:
        JigsawStackClient: A singleton instance of the JigsawStack client
    """
    # Mask the API key in logs
    masked_api_key = mask_id(settings.JIGSAWSTACK_API_KEY) if settings.JIGSAWSTACK_API_KEY else "none"
    logger.info(f"Creating JigsawStack client with API key: {masked_api_key}...")
    return JigsawStackClient(api_key=settings.JIGSAWSTACK_API_KEY, api_url=settings.JIGSAWSTACK_API_URL)
