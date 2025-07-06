"""Concept service implementation.

This module implements the ConceptService class which integrates the specialized
concept generation, refinement, and palette generation modules.
"""

import os
import uuid
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
from fastapi import UploadFile

from app.core.exceptions import ConceptError
from app.services.concept.generation import ConceptGenerator
from app.services.concept.interface import ConceptServiceInterface
from app.services.concept.palette import PaletteGenerator
from app.services.concept.refinement import ConceptRefiner
from app.services.image.interface import ImageServiceInterface
from app.services.jigsawstack.client import JigsawStackClient
from app.services.persistence.interface import ConceptPersistenceServiceInterface, ImagePersistenceServiceInterface
from app.utils.logging import get_logger
from app.utils.security.mask import mask_id


class ConceptService(ConceptServiceInterface):
    """Service for generating and refining visual concepts."""

    def __init__(
        self,
        client: JigsawStackClient,
        image_service: ImageServiceInterface,
        concept_persistence_service: ConceptPersistenceServiceInterface,
        image_persistence_service: ImagePersistenceServiceInterface,
    ):
        """Initialize the concept service with specialized components.

        Args:
            client: The JigsawStack API client
            image_service: Service for image processing
            concept_persistence_service: Service for concept persistence
            image_persistence_service: Service for image persistence
        """
        self.client = client
        self.image_service = image_service
        self.concept_persistence = concept_persistence_service
        self.image_persistence = image_persistence_service
        self.logger = get_logger("concept_service")

        # Initialize specialized components
        self.generator = ConceptGenerator(client)
        self.refiner = ConceptRefiner(client)
        self.palette_generator = PaletteGenerator(client)

    async def generate_concept(
        self,
        logo_description: str,
        theme_description: str,
        user_id: Optional[str] = None,
        skip_persistence: bool = False,
    ) -> Dict[str, Any]:
        """Generate a new concept image based on text descriptions and store it if user_id provided.

        Args:
            logo_description: Text description of the logo
            theme_description: Text description of the theme
            user_id: Optional user ID to associate with the stored concept
            skip_persistence: If True, skip storing the concept in the database

        Returns:
            Dictionary containing the concept details (image URL, path, etc.)

        Raises:
            ConceptError: If image generation or storage fails
        """
        try:
            self.logger.info(f"Generating concept with logo_description='{logo_description}', theme_description='{theme_description}'")

            # Generate the image using the JigsawStack client - only use logo_description for image generation
            image_response = await self.client.generate_image(prompt=logo_description, width=256, height=256)

            # Extract the image URL from the response - handling different response formats
            image_url = None

            if image_response:
                # Direct url in the response
                if "url" in image_response:
                    image_url = image_response.get("url")
                # Check for nested output structure
                elif "output" in image_response and isinstance(image_response["output"], dict):
                    if "image_url" in image_response["output"]:
                        image_url = image_response["output"]["image_url"]
                # Check for binary_data
                elif "binary_data" in image_response:
                    # If we have binary data but no URL, we could create a local file and reference it
                    import os
                    import tempfile
                    import uuid

                    # Generate a temporary filename
                    filename = f"temp_image_{uuid.uuid4()}.png"
                    temp_path = os.path.join(tempfile.gettempdir(), filename)

                    # Save the image data
                    with open(temp_path, "wb") as f:
                        f.write(image_response["binary_data"])

                    # Set the URL to the local file path
                    image_url = f"file://{temp_path}"
                    self.logger.info(f"Created local file for binary data: {temp_path}")

            # Check if we have a valid URL
            if not image_url:
                self.logger.error(f"No image URL returned from image generation service. Response: {str(image_response)}")
                raise ConceptError("No image URL returned from image generation service")

            self.logger.info(f"Image generated successfully: {image_url}")

            # Initialize variables
            image_path = None
            concept_id = None
            stored_image_url = None
            image_content = None

            # If a user ID is provided, download the image
            if user_id:
                try:
                    # Always download the image content if user_id is provided,
                    # regardless of skip_persistence flag
                    self.logger.info(f"Downloading image from URL: {image_url}")
                    image_content = await self._download_image(image_url)

                    # Check if image_content is None before using it
                    if image_content is None:
                        raise ConceptError("Failed to download image content")

                    self.logger.info(f"Successfully downloaded image, size: {len(image_content)} bytes")

                    # Only store the image and concept if not skipping persistence
                    if not skip_persistence:
                        # Store the image using the persistence service
                        # Use synchronous version with event loop handling to match interface
                        import asyncio

                        loop = asyncio.get_event_loop()
                        storage_result = loop.run_until_complete(
                            self.image_persistence.store_image(
                                image_data=image_content,
                                user_id=user_id,
                                metadata={
                                    "logo_description": logo_description,
                                    "theme_description": theme_description,
                                },
                            )
                        )

                        # Set the variables without redeclaring types
                        image_path = storage_result[0]
                        stored_image_url = storage_result[1]

                        # Store the concept in the database
                        if self.concept_persistence:
                            concept_data = {
                                "user_id": user_id,
                                "logo_description": logo_description,
                                "theme_description": theme_description,
                                "image_path": image_path,
                                "image_url": stored_image_url,
                            }
                            concept_id = await self.concept_persistence.store_concept(concept_data)
                            self.logger.info(f"Stored concept {concept_id} for user {user_id}")

                except Exception as e:
                    error_msg = f"Failed to process image: {str(e)}"
                    self.logger.error(error_msg)
                    # In this case, we need to raise the error to signal download failure
                    raise ConceptError(error_msg)

            # Create the response
            # Determine which URL to return based on persistence
            final_image_url = stored_image_url if stored_image_url else image_url

            response: Dict[str, Any] = {
                "image_url": final_image_url,
                "image_path": image_path,
                "concept_id": concept_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
            }

            # Include the image data if it was downloaded (useful for background tasks)
            if image_content:
                response["image_data"] = image_content

            return response
        except Exception as e:
            self.logger.error(f"Failed to generate concept: {str(e)}")
            raise ConceptError(f"Failed to generate concept: {str(e)}")

    async def generate_concept_with_palettes(
        self,
        logo_description: str,
        theme_description: str,
        num_palettes: int = 3,
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate a concept with multiple palette variations, each with its own image.

        Args:
            logo_description: Description of the logo to generate
            theme_description: Description of the theme/color scheme
            num_palettes: Number of palette variations to generate

        Returns:
            Tuple of (palettes, variation_images):
            - palettes: List of palette dictionaries with name, colors, description
            - variation_images: List of palette variations with image URLs

        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
        """
        self.logger.info(f"Generating concept with {num_palettes} palette variations")

        # Generate the concept using user_id=None to avoid persistence in this step
        base_concept_data = await self.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description,
            user_id=None,  # Don't persist at this stage
        )

        # Then, generate additional palettes
        palettes = await self.palette_generator.generate_palettes(
            theme_description=theme_description,
            logo_description=logo_description,
            num_palettes=num_palettes,
        )

        # Initialize empty variation images list
        variation_images: List[Dict[str, Any]] = []

        # Get the image URL from the base concept
        base_image_url = base_concept_data.get("image_url")

        if base_image_url and self.image_service:
            try:
                # Download the base image
                base_image_data = await self._download_image(base_image_url)

                # Generate variations for each palette
                if base_image_data is not None and palettes:
                    for palette in palettes:
                        try:
                            # Apply the palette to the base image
                            palette_colors = palette.get("colors", [])
                            if not palette_colors:
                                continue

                            # Process image with this palette
                            colorized_image = await self.image_service.apply_palette_to_image(
                                image_data=base_image_data,
                                palette_colors=palette_colors,
                                blend_strength=0.75,
                            )

                            # Create variation info - in a real system you would store this
                            # and generate a proper URL
                            variation_info = {
                                "name": palette.get("name", "Unnamed Palette"),
                                "colors": palette_colors,
                                "description": palette.get("description", ""),
                                "image_data": colorized_image,
                                # In a real system, you would convert this to a URL
                            }
                            variation_images.append(variation_info)

                        except Exception as e:
                            self.logger.error(f"Error creating variation for palette '{palette.get('name', 'unnamed')}': {str(e)}")
                            # Continue with other palettes

            except Exception as e:
                self.logger.error(f"Error downloading base image: {str(e)}")
                # Continue with what we have

        return palettes, variation_images

    async def refine_concept(
        self,
        original_image_url: str,
        refinement_prompt: str,
        logo_description: Optional[str] = None,
        theme_description: Optional[str] = None,
        user_id: Optional[str] = None,
        skip_persistence: bool = False,
        strength: float = 0.7,
    ) -> Dict[str, Any]:
        """Refine an existing concept based on provided instructions.

        Args:
            original_image_url: URL of the original image to refine
            refinement_prompt: Specific instructions for refinement
            logo_description: Updated description of the logo (optional)
            theme_description: Updated description of the theme (optional)
            user_id: Optional user ID for persisting the refined concept
            skip_persistence: If True, don't store the concept in the database
            strength: Control how much to preserve the original image (0.0-1.0)

        Returns:
            Dict containing refined concept details with image URL and color palette

        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If refinement fails due to API errors
            ConceptError: If there is an error during concept refinement
        """
        self.logger.info(f"Refining concept with prompt: {refinement_prompt}")

        # Create preserve_aspects from refinement_prompt if not provided
        preserve_aspects = []
        if "preserve" in refinement_prompt.lower():
            # Extract preservation aspects from the refinement prompt
            # This is a simplified approach
            preserve_parts = refinement_prompt.lower().split("preserve")
            if len(preserve_parts) > 1:
                aspects_text = preserve_parts[1].strip()
                preserve_aspects = [aspect.strip() for aspect in aspects_text.split(",")]

        # Use the refiner component to refine the concept
        response = await self.refiner.refine(
            original_image_url=original_image_url,
            logo_description=logo_description,
            theme_description=theme_description,
            refinement_prompt=refinement_prompt,
            preserve_aspects=preserve_aspects,
        )

        # If user_id is provided and we have persistence services, store the refined concept
        if user_id and self.image_persistence and self.concept_persistence and not skip_persistence:
            try:
                # First, we need to get the image data from the URL
                image_data = None

                # Check if we have image_data directly in the response
                if "image_data" in response and response["image_data"]:
                    image_data = response["image_data"]
                # Otherwise try to download from the image_url
                elif "image_url" in response and response["image_url"]:
                    image_data = await self._download_image(response["image_url"])

                # Only proceed if we have valid image data
                if image_data is not None:
                    # Then store the image
                    import asyncio

                    loop = asyncio.get_event_loop()
                    storage_result = loop.run_until_complete(
                        self.image_persistence.store_image(
                            image_data=image_data,
                            user_id=user_id,
                            metadata={
                                "logo_description": logo_description if logo_description else "",
                                "theme_description": theme_description if theme_description else "",
                                "refinement_prompt": refinement_prompt,
                                "is_refinement": True,
                            },
                        )
                    )

                    # Properly typed variables
                    img_path: str = storage_result[0]
                    img_url: str = storage_result[1]

                    # Extract colors from the response
                    colors = response.get("colors", [])

                    # Now store the concept with the stored image info
                    concept_data = {
                        "user_id": user_id,
                        "logo_description": logo_description if logo_description else "",
                        "theme_description": theme_description if theme_description else "",
                        "image_path": img_path,
                        "image_url": img_url,
                        "color_palettes": [
                            {
                                "name": "Refined Palette",
                                "colors": colors,
                                "description": "Color palette for the refined concept",
                            }
                        ],
                        "is_refinement": True,
                        "refinement_prompt": refinement_prompt,
                        "original_image_url": original_image_url,
                    }

                    concept_id = await self.concept_persistence.store_concept(concept_data)
                    self.logger.info(f"Stored refined concept with ID: {mask_id(concept_id)} for user: {mask_id(user_id)}")

                    # Update the response with the stored image URL
                    response["image_url"] = img_url
            except Exception as e:
                self.logger.error(f"Error storing refined concept: {str(e)}")
                # Don't fail the operation if storage fails, just log it

        return response

    async def generate_color_palettes(
        self,
        theme_description: str,
        logo_description: Optional[str] = None,
        num_palettes: int = 7,
    ) -> List[Dict[str, Any]]:
        """Generate multiple color palettes based on a theme description.

        Args:
            theme_description: Description of the theme/color scheme
            logo_description: Optional description of the logo to help contextualize
            num_palettes: Number of palettes to generate

        Returns:
            List of palette dictionaries, each containing name, colors, and description

        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during palette generation
        """
        self.logger.info(f"Generating {num_palettes} color palettes for: {theme_description}")

        # Delegate to specialized palette generator component
        return await self.palette_generator.generate_palettes(
            theme_description=theme_description,
            logo_description=logo_description,
            num_palettes=num_palettes,
        )

    async def apply_palette_to_concept(
        self,
        concept_image_url: str,
        palette_colors: List[str],
        user_id: Optional[str] = None,
        blend_strength: float = 0.75,
    ) -> Tuple[str, str]:
        """Apply a color palette to a concept image.

        Args:
            concept_image_url: URL of the concept image
            palette_colors: List of color hex codes
            user_id: Optional user ID for persistence
            blend_strength: How strongly to apply the new palette (0.0-1.0)

        Returns:
            Tuple of (image_path, image_url)

        Raises:
            ConceptError: If palette application fails
        """
        try:
            # 1. Download the concept image
            image_data = await self._download_image(concept_image_url)
            if not image_data:
                self.logger.error(f"Failed to download image from {concept_image_url}")
                raise ConceptError(f"Failed to download image from {concept_image_url}")

            # 2. Apply the palette using the image service
            colorized_image = await self.image_service.apply_palette_to_image(
                image_data=image_data,
                palette_colors=palette_colors,
                blend_strength=blend_strength,
            )

            # 3. Store the image if user_id is provided
            if user_id:
                path, url = await self.image_persistence.store_image(
                    image_data=colorized_image,
                    user_id=user_id,
                    metadata={"palette_colors": ",".join(palette_colors)},
                )
                # Add type annotations to fix mypy errors
                image_path: str = path
                image_url: str = url
                return image_path, image_url
            else:
                # If no user_id, create a temporary file for testing
                temp_file = f"temp_palette_{uuid.uuid4()}.png"
                with open(temp_file, "wb") as f:
                    f.write(colorized_image)
                self.logger.warning(f"No user_id provided, saving to temp file: {temp_file}")
                return temp_file, f"file://{os.path.abspath(temp_file)}"
        except Exception as e:
            self.logger.error(f"Error applying palette to concept: {str(e)}")
            raise ConceptError(f"Failed to apply palette to concept: {str(e)}")

    async def _download_image(self, image_url: Optional[str]) -> Optional[bytes]:
        """Download an image from a URL or read from a local file path.

        Args:
            image_url: URL of the image to download, or file:// URL for local files

        Returns:
            Image data as bytes or None if the URL is None

        Raises:
            IOError: If the download fails or the file doesn't exist
            ValueError: If the downloaded content is empty
        """
        if image_url is None:
            self.logger.warning("Cannot download image from None URL")
            return None

        try:
            # Handle local file:// URLs by reading the file directly
            if image_url.startswith("file://"):
                # Extract the file path from the URL
                file_path = image_url[7:]  # Remove the "file://" prefix

                # Check if the file exists
                if not os.path.exists(file_path):
                    self.logger.error(f"Local file not found: {file_path}")
                    raise FileNotFoundError(f"Local image file not found: {file_path}")

                # Read the file
                with open(file_path, "rb") as f:
                    image_data = f.read()

                self.logger.info("Read image data from local file")

                # Clean up the temporary file after reading if needed
                try:
                    os.remove(file_path)
                    self.logger.info(f"Removed temporary file: {file_path}")
                except Exception as rm_err:
                    self.logger.warning(f"Could not remove temporary file {file_path}: {rm_err}")

                return image_data

            # For remote URLs, use httpx to download
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()  # Raises an exception for 4xx/5xx responses

                # Check if content is empty
                if not response.content:
                    raise ValueError("Downloaded image content is empty")

                return response.content
        except httpx.HTTPStatusError as e:
            self.logger.error(f"HTTP error downloading image from {image_url}: {e.response.status_code} - {e.response.text}")
            raise IOError(f"HTTP error {e.response.status_code} downloading image") from e
        except Exception as e:
            self.logger.error(f"Error downloading image from {image_url}: {str(e)}")
            raise IOError(f"Failed to download image: {str(e)}") from e

    async def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "image/png",
        is_palette: bool = False,
    ) -> Tuple[str, str]:
        """Store an image using the image persistence service.

        Args:
            image_data: Image data
            user_id: User ID
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name
            metadata: Optional metadata
            content_type: Content type
            is_palette: Whether this is a palette image

        Returns:
            Tuple of (path, url)

        Raises:
            ConceptError: If storage fails
        """
        try:
            path, url = await self.image_persistence.store_image(
                image_data=image_data,
                user_id=user_id,
                concept_id=concept_id,
                file_name=file_name,
                metadata=metadata,
                is_palette=is_palette,
            )

            # Add type annotations to fix mypy errors
            stored_path: str = path
            stored_url: str = url

            return stored_path, stored_url
        except Exception as e:
            self.logger.error(f"Failed to store image: {str(e)}")
            raise ConceptError(f"Failed to store image: {str(e)}")
