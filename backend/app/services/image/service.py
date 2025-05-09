"""Image service implementation.

This module provides the implementation of the ImageServiceInterface
which coordinates image processing and conversion.
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union, cast

import httpx
from fastapi import UploadFile
from PIL import Image as PILImage

from app.core.exceptions import ImageStorageError

# Fix circular import - import interfaces directly from their modules
from app.services.image.interface import ImageProcessingServiceInterface, ImageServiceInterface
from app.services.persistence.interface import ImagePersistenceServiceInterface
from app.utils.security.mask import mask_id

# Set up logging
logger = logging.getLogger(__name__)


class ImageError(Exception):
    """Base exception for image service errors."""

    pass


class ImageService(ImageServiceInterface):
    """Service for processing and manipulating images.

    This service provides operations for processing, converting,
    and transforming image data.
    """

    def __init__(
        self,
        persistence_service: ImagePersistenceServiceInterface,
        processing_service: ImageProcessingServiceInterface,
    ):
        """Initialize the image service.

        Args:
            persistence_service: Service for image persistence operations
            processing_service: Service for image processing operations
        """
        self.persistence = persistence_service
        self.processing = processing_service
        self.logger = logging.getLogger(__name__)

    async def process_image(self, image_data: Union[bytes, BytesIO, str], operations: List[Dict[str, Any]]) -> bytes:
        """Process an image with a series of operations.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            operations: List of operations to apply to the image

        Returns:
            Processed image data as bytes

        Raises:
            ImageError: If processing fails
        """
        try:
            return await self.processing.process_image(image_data, operations)
        except Exception as e:
            error_msg = "Error processing image: {}".format(str(e))
            self.logger.error(error_msg)
            raise ImageError(error_msg)

    def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False,
    ) -> Tuple[str, str]:
        """Store an image and return its path and signed URL.

        Args:
            image_data: Image data as bytes, BytesIO, or UploadFile
            user_id: User ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image

        Returns:
            Tuple[str, str]: (image_path, image_url)

        Raises:
            ImageError: If storage fails
        """
        try:
            # Use the persistence service to store the image but handle the awaiting
            # inside this method to maintain a synchronous interface

            # Get running event loop or create one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                # If no event loop is available, create a new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            # Run the coroutine in the event loop
            result = loop.run_until_complete(
                self.persistence.store_image(
                    image_data=image_data,
                    user_id=user_id,
                    concept_id=concept_id,
                    file_name=file_name,
                    metadata=metadata,
                    is_palette=is_palette,
                )
            )

            return result  # This will be the tuple (image_path, image_url)
        except ImageStorageError as e:
            # Re-raise as ImageError
            raise ImageError("Failed to store image: {}".format(str(e)))

    def convert_to_format(self, image_data: bytes, target_format: str = "png", quality: int = 95) -> bytes:
        """Convert an image to a specified format.

        Args:
            image_data: Binary image data
            target_format: Target format ('png', 'jpg', 'webp', etc.)
            quality: Quality for lossy formats (0-100)

        Returns:
            Converted image as bytes

        Raises:
            ImageError: If conversion fails
        """
        try:
            return self.processing.convert_to_format(image_data=image_data, target_format=target_format, quality=quality)
        except Exception as e:
            raise ImageError("Failed to convert image format: {}".format(str(e)))

    def generate_thumbnail(
        self,
        image_data: bytes,
        width: int,
        height: int,
        preserve_aspect_ratio: bool = True,
        format: str = "png",
    ) -> bytes:
        """Generate a thumbnail from an image.

        Args:
            image_data: Binary image data
            width: Target width
            height: Target height
            preserve_aspect_ratio: Whether to preserve the aspect ratio
            format: Output format

        Returns:
            Thumbnail image as bytes

        Raises:
            ImageError: If thumbnail generation fails
        """
        try:
            return self.processing.generate_thumbnail(
                image_data=image_data,
                width=width,
                height=height,
                format=format,
                preserve_aspect_ratio=preserve_aspect_ratio,
            )
        except Exception as e:
            raise ImageError("Failed to generate thumbnail: {}".format(str(e)))

    async def extract_color_palette(self, image_data: bytes, num_colors: int = 5) -> List[str]:
        """Extract a color palette from an image.

        Args:
            image_data: Binary image data
            num_colors: Number of colors to extract

        Returns:
            List of color hex codes

        Raises:
            ImageError: If color extraction fails
        """
        try:
            return await self.processing.extract_color_palette(image_data, num_colors)
        except Exception as e:
            error_msg = "Failed to extract color palette: {}".format(str(e))
            self.logger.error(error_msg)
            raise ImageError(error_msg)

    async def create_palette_variations(
        self,
        base_image_data: bytes,
        palettes: List[Dict[str, Any]],
        user_id: str,
        blend_strength: float = 0.75,
    ) -> List[Dict[str, Any]]:
        """Create variations of an image with different color palettes.

        Args:
            base_image_data: Binary image data of the base image
            palettes: List of color palette dictionaries
            user_id: Current user ID
            blend_strength: How strongly to apply the new colors (0.0-1.0)

        Returns:
            List of palettes with added image_path and image_url fields

        Raises:
            ImageError: If applying palettes fails
        """
        result_palettes = []
        masked_user_id = mask_id(user_id)

        try:
            self.logger.info("Creating {} palette variations for user: {}".format(len(palettes), masked_user_id))
            start_time = datetime.now()

            # Preprocess the base image to ensure it's valid
            try:
                img: PILImage.Image = PILImage.open(BytesIO(base_image_data))
                if img.mode != "RGB":
                    img = img.convert("RGB")

                # Re-encode to ensure we have valid image data
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                validated_image_data = buffer.getvalue()
                self.logger.info("Successfully validated base image for processing, size: {} bytes".format(len(validated_image_data)))

            except Exception as e:
                self.logger.error("Error validating base image: {}".format(str(e)))
                validated_image_data = base_image_data  # Fall back to original data

            # Prepare the metadata prefix with timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")

            # Create async tasks for parallel processing
            tasks = []
            for idx, palette in enumerate(palettes):
                tasks.append(self._process_single_palette_variation(validated_image_data, palette, user_id, timestamp, idx, blend_strength))

            # Execute all tasks concurrently
            self.logger.info("Starting parallel processing of {} palette variations".format(len(tasks)))
            results = await asyncio.gather(*tasks, return_exceptions=True)

            # Process results
            for result in results:
                if isinstance(result, Exception):
                    self.logger.error("Error processing a palette variation: {}".format(str(result)))
                    # Skip failed variations
                    continue
                if result is not None:
                    # Type checking: only append results that are dictionaries, not exceptions or None
                    result_dict = cast(Dict[str, Any], result)
                    result_palettes.append(result_dict)

            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            self.logger.info(
                "Successfully created {} palette variations in {:.2f} seconds (avg {:.2f} seconds per variation)".format(len(result_palettes), processing_time, processing_time / max(len(palettes), 1))
            )
            return result_palettes

        except Exception as e:
            self.logger.error("Error in create_palette_variations: {}".format(str(e)))
            raise ImageError("Error creating palette variations: {}".format(str(e)))

    async def _process_single_palette_variation(
        self, base_image_data: bytes, palette: Dict[str, Any], user_id: str, timestamp: str, idx: int, blend_strength: float = 0.75
    ) -> Optional[Dict[str, Any]]:
        """Process a single palette variation.

        Args:
            base_image_data: Binary image data of the base image
            palette: Dictionary containing palette information
            user_id: User ID for storage
            timestamp: Timestamp string for unique filenames
            idx: Index of the palette in the original list
            blend_strength: Strength of the palette application

        Returns:
            Dictionary with palette information and image URLs, or None if processing fails

        Raises:
            Exception: If any step of the processing fails
        """
        try:
            # Extract palette data
            palette_name = palette.get("name", "Palette {}".format(idx + 1))
            palette_colors = palette.get("colors", [])
            palette_description = palette.get("description", "")

            if not palette_colors:
                self.logger.warning("Empty color palette: {}, skipping".format(palette_name))
                return None

            # Apply the palette to the base image using the processing service
            colorized_image = await self.processing.process_image(
                base_image_data,
                operations=[
                    {
                        "type": "apply_palette",
                        "palette": palette_colors,
                        "blend_strength": blend_strength,
                    }
                ],
            )

            if not colorized_image:
                self.logger.error("Failed to apply palette: {}".format(palette_name))
                return None

            # Generate a unique filename
            unique_id = str(uuid.uuid4())
            filename = "palette_{}_{}.png".format(timestamp, unique_id)

            # Store with metadata
            metadata = {
                "palette_name": palette_name,
                "description": palette_description,
                "colors": json.dumps(palette_colors),
            }

            palette_path, palette_url = await self.persistence.store_image(
                image_data=colorized_image,
                user_id=user_id,
                file_name=filename,
                metadata=metadata,
                is_palette=True,
            )

            # Annotate the variables to fix type errors
            palette_path_str: str = palette_path
            palette_url_str: str = palette_url

            if not palette_path_str or not palette_url_str:
                self.logger.error("Failed to store palette variation: {}".format(palette_name))
                return None

            # Return result
            return {
                "name": palette_name,
                "colors": palette_colors,
                "description": palette_description,
                "image_path": palette_path_str,
                "image_url": palette_url_str,
            }
        except Exception as e:
            self.logger.error("Error processing palette {}: {}".format(palette.get("name", f"Palette {idx + 1}"), str(e)))
            raise e  # Re-raise to be caught by asyncio.gather

    async def apply_palette_to_image(self, image_data: bytes, palette_colors: list, blend_strength: float = 0.75) -> bytes:
        """Apply a color palette to an image.

        Args:
            image_data: Binary image data
            palette_colors: List of hex color codes
            blend_strength: Strength of the palette application (0-1)

        Returns:
            Processed image data as bytes

        Raises:
            ImageError: If processing fails
        """
        try:
            # Apply the palette using the processing service
            return await self.processing.process_image(
                image_data,
                operations=[
                    {
                        "type": "apply_palette",
                        "palette": palette_colors,
                        "blend_strength": blend_strength,
                    }
                ],
            )
        except Exception as e:
            self.logger.error("Error applying palette to image: {}".format(str(e)))
            raise ImageError("Failed to apply palette to image: {}".format(str(e)))

    # Cache for storing recently downloaded images to avoid repeated downloads
    _image_cache: Dict[str, bytes] = {}
    _cache_size_limit = 20  # Maximum number of images to keep in cache

    async def get_image_async(self, image_url_or_path: str) -> bytes:
        """Asynchronously get image data from a URL or path.

        Args:
            image_url_or_path: URL or storage path of the image

        Returns:
            Image data as bytes

        Raises:
            ImageError: If retrieval fails
        """
        try:
            # If it's a URL, download it
            if image_url_or_path.startswith("http://") or image_url_or_path.startswith("https://"):
                try:
                    # Check if the image is in the cache
                    if image_url_or_path in self._image_cache:
                        self.logger.debug("Using cached image data for URL")
                        return self._image_cache[image_url_or_path]

                    # Download the image
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_url_or_path)
                        response.raise_for_status()
                        image_data = response.content

                    # Cache the image if it's not too large
                    if len(image_data) < 10 * 1024 * 1024:  # Cache images smaller than 10MB
                        # If cache is full, remove the oldest entry
                        if len(self._image_cache) >= self._cache_size_limit:
                            oldest_key = next(iter(self._image_cache))
                            del self._image_cache[oldest_key]
                        self._image_cache[image_url_or_path] = image_data
                        self.logger.debug("Cached image data from URL, size: {} bytes".format(len(image_data)))

                    return image_data
                except Exception as e:
                    self.logger.error("Error downloading image from URL: {}".format(str(e)))
                    raise ImageError("Failed to download image from URL: {}".format(str(e)))
            else:
                # It's a storage path, fetch from storage
                # Determine if this is a palette image based on the path
                is_palette = False
                if "palette" in image_url_or_path:
                    is_palette = True

                try:
                    # Cache key for storage images combines path and palette flag
                    cache_key = "storage:{}:{}".format(image_url_or_path, is_palette)
                    if cache_key in self._image_cache:
                        self.logger.debug("Using cached image data for storage path")
                        return self._image_cache[cache_key]

                    # Get from persistence service
                    image_data = await self.persistence.get_image(image_url_or_path)

                    # Cache the image if it's not too large
                    if len(image_data) < 10 * 1024 * 1024:  # Cache images smaller than 10MB
                        # If cache is full, remove the oldest entry
                        if len(self._image_cache) >= self._cache_size_limit:
                            oldest_key = next(iter(self._image_cache))
                            del self._image_cache[oldest_key]
                        self._image_cache[cache_key] = image_data

                    return image_data
                except Exception as e:
                    self.logger.error("Error getting image from storage: {}".format(str(e)))
                    raise ImageError("Failed to get image from storage: {}".format(str(e)))
        except Exception as e:
            self.logger.error("Error getting image data: {}".format(str(e)))
            raise ImageError("Failed to get image data: {}".format(str(e)))

    async def get_image_data(self, image_path: str, is_palette: bool = False) -> bytes:
        """Get image data with proper bucket selection.

        Args:
            image_path: Path to the image in storage
            is_palette: Whether this is a palette image (determines which bucket to use)

        Returns:
            Image data as bytes

        Raises:
            ImageError: If image retrieval fails
        """
        try:
            self.logger.info("Getting image data for path: {}, is_palette: {}".format(image_path, is_palette))

            # Check if it's a URL
            if image_path.startswith("http://") or image_path.startswith("https://"):
                return await self.get_image_async(image_path)

            # Determine the appropriate bucket based on the is_palette flag and path
            # If is_palette is explicitly set, use that; otherwise, infer from path
            infer_is_palette = "palette" in image_path.lower() or is_palette

            # First try using the inferred bucket
            try:
                # Get the image using the persistence service
                self.logger.debug("Fetching image from storage using {} bucket".format("palette" if infer_is_palette else "concept"))
                image_data = await self.persistence.get_image(image_path)
                self.logger.debug("Successfully retrieved image from {} bucket".format("palette" if infer_is_palette else "concept"))
                return image_data
            except Exception as e:
                # If we fail to get the image, try the opposite bucket
                if not infer_is_palette:
                    # We tried the concept bucket but failed, let's try the palette bucket
                    self.logger.warning("Failed to get image from concept bucket, trying palette bucket: {}".format(str(e)))
                    try:
                        # Try different path variations for palette images
                        try_paths = [
                            image_path,  # Original path, but with palette bucket
                            "palette_{}".format(image_path),  # Add palette prefix
                            # Extract the filename and try with just that in the palette bucket
                            image_path.split("/")[-1] if "/" in image_path else image_path,
                        ]

                        for try_path in try_paths:
                            try:
                                self.logger.debug("Trying palette bucket with path: {}".format(try_path))
                                image_data = await self.persistence.get_image(try_path)
                                self.logger.info("Successfully found image in palette bucket with path: {}".format(try_path))
                                return image_data
                            except Exception as path_err:
                                self.logger.debug("Failed with path {}: {}".format(try_path, str(path_err)))
                                continue

                        # If we've tried all paths and still failed, raise the error
                        raise ImageError("Failed to get image from palette bucket with any path variation")
                    except Exception as inner_e:
                        self.logger.error("Failed to get image from palette bucket: {}".format(str(inner_e)))
                        raise ImageError("Failed to get image from either bucket: {}, {}".format(str(e), str(inner_e)))
                else:
                    # We tried the palette bucket but failed, let's try the concept bucket
                    self.logger.warning("Failed to get image from palette bucket, trying concept bucket: {}".format(str(e)))
                    try:
                        # For palette images, they might have a 'palette_' prefix that's not in the path
                        # Try to remove it if present
                        try_path = image_path
                        if try_path.startswith("palette_"):
                            try_path = try_path[8:]  # Remove 'palette_' prefix

                        self.logger.debug("Trying concept bucket with path: {}".format(try_path))
                        image_data = await self.persistence.get_image(try_path)
                        self.logger.info("Successfully found image in concept bucket")
                        return image_data
                    except Exception as inner_e:
                        self.logger.error("Failed to get image from concept bucket: {}".format(str(inner_e)))
                        raise ImageError("Failed to get image from either bucket: {}, {}".format(str(e), str(inner_e)))
        except Exception as e:
            self.logger.error("Error getting image data: {}".format(str(e)))
            raise ImageError("Failed to get image data: {}".format(str(e)))
