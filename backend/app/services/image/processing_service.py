"""Image processing service implementation.

This module provides a dedicated service for image processing operations,
following the Single Responsibility Principle.
"""

import logging
from io import BytesIO
from typing import Any, BinaryIO, Dict, List, Optional, Union, cast

from app.services.image.conversion import ConversionError, convert_image_format, generate_thumbnail, get_image_metadata, optimize_image
from app.services.image.interface import ImageProcessingServiceInterface
from app.services.image.processing import apply_palette_with_masking_optimized, extract_dominant_colors

# Set up logging
logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    """Exception raised for image processing errors."""

    pass


class ImageProcessingService(ImageProcessingServiceInterface):
    """Service for processing images.

    This service handles image transformations, format conversions,
    and other processing operations. It focuses solely on processing
    image data and does not handle storage operations.
    """

    def __init__(self) -> None:
        """Initialize the image processing service."""
        self.logger = logging.getLogger(__name__)

    async def process_image(self, image_data: Union[bytes, BytesIO, str], operations: List[Dict[str, Any]]) -> bytes:
        """Process an image with a series of operations.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            operations: List of operations to apply to the image

        Returns:
            Processed image data as bytes

        Raises:
            ImageProcessingError: If processing fails
        """
        try:
            # Note: image_data could be a URL, bytes, or BytesIO
            current_image = image_data

            for operation in operations:
                op_type = operation.get("type", "").lower()

                if op_type == "format_conversion":
                    target_format = operation.get("target_format", "png")
                    quality = operation.get("quality", 95)

                    current_image = await self.convert_format(current_image, target_format=target_format, quality=quality)

                elif op_type == "resize":
                    width = operation.get("width")
                    height = operation.get("height")
                    maintain_aspect_ratio = operation.get("maintain_aspect_ratio", True)

                    if width is None and height is None:
                        continue  # Skip this operation

                    # Cast width to int if it's not None
                    if width is not None:
                        width = cast(int, width)
                    if height is not None:
                        height = cast(int, height)

                    # Ensure we have proper int values, not None
                    if width is None:
                        raise ValueError("Width cannot be None for resize operation")

                    current_image = await self.resize_image(
                        current_image,
                        width=width,
                        height=height,
                        maintain_aspect_ratio=maintain_aspect_ratio,
                    )

                elif op_type == "thumbnail":
                    width = operation.get("width", 128)
                    height = operation.get("height", 128)
                    preserve_aspect_ratio = operation.get("preserve_aspect_ratio", True)
                    format = operation.get("format", "png")

                    # Ensure we have bytes before generating thumbnail
                    if isinstance(current_image, str):
                        # Download image from URL
                        import httpx

                        async with httpx.AsyncClient() as client:
                            response = await client.get(current_image)
                            img_bytes = response.content
                    elif isinstance(current_image, BytesIO):
                        img_bytes = current_image.getvalue()
                    else:
                        img_bytes = current_image

                    current_image = self.generate_thumbnail(
                        img_bytes,
                        width=width,
                        height=height,
                        preserve_aspect_ratio=preserve_aspect_ratio,
                        format=format,
                    )

                elif op_type == "optimize":
                    quality = operation.get("quality", 85)
                    max_width = operation.get("max_width")
                    max_height = operation.get("max_height")

                    max_size = None
                    if max_width is not None and max_height is not None:
                        max_size = (max_width, max_height)

                    # Ensure we have bytes
                    if isinstance(current_image, str):
                        import httpx

                        async with httpx.AsyncClient() as client:
                            response = await client.get(current_image)
                            img_bytes = response.content
                    elif isinstance(current_image, BytesIO):
                        img_bytes = current_image.getvalue()
                    else:
                        img_bytes = current_image

                    current_image = optimize_image(img_bytes, quality=quality, max_size=max_size)

                elif op_type == "apply_palette":
                    palette = operation.get("palette", [])
                    blend_strength = operation.get("blend_strength", 0.75)

                    if not palette:
                        continue  # Skip if no palette provided

                    current_image = await self.apply_palette(
                        current_image,
                        palette_colors=palette,
                        blend_strength=blend_strength,
                    )

                else:
                    self.logger.warning(f"Unsupported operation type: {op_type}")

            # Ensure final result is bytes
            if isinstance(current_image, str):
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(current_image)
                    current_image = response.content
            elif isinstance(current_image, BytesIO):
                current_image = current_image.getvalue()

            return current_image

        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)

    def convert_to_format(self, image_data: bytes, target_format: str = "png", quality: int = 95) -> bytes:
        """Convert an image to a specified format.

        Args:
            image_data: Binary image data
            target_format: Target format ('png', 'jpg', 'webp', etc.)
            quality: Quality for lossy formats (0-100)

        Returns:
            Converted image as bytes

        Raises:
            ImageProcessingError: If conversion fails
        """
        try:
            return convert_image_format(image_data=image_data, target_format=target_format, quality=quality)
        except ConversionError as e:
            raise ImageProcessingError(f"Failed to convert image format: {str(e)}")

    async def resize_image(
        self,
        image_data: Union[bytes, BytesIO, str],
        width: int,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True,
    ) -> bytes:
        """Resize an image to specified dimensions.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            width: Target width in pixels
            height: Target height in pixels (optional if maintaining aspect ratio)
            maintain_aspect_ratio: Whether to preserve aspect ratio

        Returns:
            Resized image as bytes

        Raises:
            ImageProcessingError: If resizing fails
        """
        try:
            # Ensure image_data is bytes
            if isinstance(image_data, str):
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(image_data)
                    image_data = response.content
            elif isinstance(image_data, BytesIO):
                image_data = image_data.getvalue()

            # Open as PIL Image
            from PIL import Image

            img = Image.open(BytesIO(image_data))

            # Determine target size
            if maintain_aspect_ratio and height is None:
                # Calculate height to maintain aspect ratio
                aspect_ratio = img.width / img.height
                height = int(width / aspect_ratio)
            elif maintain_aspect_ratio and width is None:
                # Calculate width to maintain aspect ratio
                aspect_ratio = img.width / img.height
                width = int(height * aspect_ratio)
            elif maintain_aspect_ratio:
                # Both width and height provided, but maintain aspect ratio
                # Use the dimension that results in smaller resize
                current_aspect = img.width / img.height

                # Ensure both width and height are not None
                if width is None or height is None:
                    raise ValueError("Both width and height must be provided when maintain_aspect_ratio is True")

                # Now that we've verified both values, we can safely use them
                target_aspect = width / height

                if current_aspect > target_aspect:
                    # Width constrained
                    new_width = width
                    new_height = int(new_width / current_aspect)
                else:
                    # Height constrained
                    new_height = height
                    new_width = int(new_height * current_aspect)

                width, height = new_width, new_height

            # Ensure height is initialized
            if height is None:
                raise ValueError("Height must be provided for resizing")

            # Resize image using PIL.Image.Resampling.LANCZOS
            resized_img = img.resize((width, height), resample=Image.Resampling.LANCZOS)

            # Convert back to bytes
            output = BytesIO()
            resized_img.save(output, format=img.format or "PNG")
            return output.getvalue()

        except Exception as e:
            error_msg = f"Failed to resize image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)

    def generate_thumbnail(
        self,
        image_data: bytes,
        width: int,
        height: int,
        preserve_aspect_ratio: bool = True,
        format: str = "png",
    ) -> bytes:
        """Generate a thumbnail from image data.

        Args:
            image_data: Binary image data
            width: Thumbnail width
            height: Thumbnail height
            preserve_aspect_ratio: Whether to preserve aspect ratio
            format: Output format (png, jpg, etc.)

        Returns:
            Thumbnail image as bytes

        Raises:
            ImageProcessingError: If thumbnail generation fails
        """
        try:
            # Call the generate_thumbnail function with the proper parameters
            return generate_thumbnail(
                image_data=image_data,
                size=(width, height),
                preserve_aspect_ratio=preserve_aspect_ratio,
                format=format,
            )
        except Exception as e:
            error_msg = f"Failed to generate thumbnail: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)

    async def extract_color_palette(self, image_data: bytes, num_colors: int = 5) -> List[str]:
        """Extract dominant colors from an image.

        Args:
            image_data: Binary image data
            num_colors: Number of colors to extract

        Returns:
            List of hex color codes

        Raises:
            ImageProcessingError: If color extraction fails
        """
        try:
            return await extract_dominant_colors(image_data, num_colors)
        except Exception as e:
            error_msg = f"Failed to extract color palette: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)

    def get_image_metadata(self, image_data: bytes) -> Dict[str, Any]:
        """Extract metadata from an image.

        Args:
            image_data: Binary image data

        Returns:
            Dictionary of image metadata

        Raises:
            ImageProcessingError: If metadata extraction fails
        """
        try:
            return get_image_metadata(image_data)
        except Exception as e:
            error_msg = f"Failed to extract image metadata: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)

    async def convert_format(
        self,
        image_data: Union[bytes, BinaryIO, str],
        target_format: str,
        quality: Optional[int] = None,
    ) -> bytes:
        """Convert image to specified format.

        Args:
            image_data: Image data as bytes, file-like object, or URL
            target_format: Target format (png, jpg, webp, etc.)
            quality: Quality for lossy formats (1-100)

        Returns:
            Converted image as bytes

        Raises:
            ImageProcessingError: If conversion fails
        """
        try:
            # Ensure image_data is bytes
            if isinstance(image_data, str):
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(image_data)
                    image_data = response.content
            elif hasattr(image_data, "read"):
                image_data = image_data.read()

            return convert_image_format(
                image_data=image_data,
                target_format=target_format,
                quality=quality or 95,
            )
        except Exception as e:
            error_msg = f"Failed to convert image format: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)

    async def apply_palette(
        self,
        image_data: Union[bytes, BytesIO, str],
        palette_colors: List[str],
        blend_strength: float = 0.75,
    ) -> bytes:
        """Apply a color palette to an image.

        Args:
            image_data: Image data as bytes, BytesIO, or URL
            palette_colors: List of hex color codes
            blend_strength: How strongly to apply the palette (0.0-1.0)

        Returns:
            Processed image as bytes

        Raises:
            ValueError: If palette_colors is empty
            ImageProcessingError: If palette application fails
        """
        # Validate inputs
        if not palette_colors:
            raise ValueError("palette_colors cannot be empty")

        try:
            # Ensure image_data is bytes
            if isinstance(image_data, str):
                import httpx

                async with httpx.AsyncClient() as client:
                    response = await client.get(image_data)
                    image_data = response.content
            elif isinstance(image_data, BytesIO):
                image_data = image_data.getvalue()

            # Convert the hex colors to BGR for OpenCV
            from app.services.image.processing import hex_to_bgr

            bgr_palette = [hex_to_bgr(color) for color in palette_colors]

            # Open the image with PIL and convert to OpenCV format
            import cv2
            import numpy as np
            from PIL import Image

            img = Image.open(BytesIO(image_data))
            img_rgb = np.array(img.convert("RGB"))
            img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)

            # Apply the palette
            processed_img = apply_palette_with_masking_optimized(img_bgr, bgr_palette, k=min(10, len(bgr_palette) * 2))

            # Handle the case where apply_palette_with_masking_optimized returns a string
            if isinstance(processed_img, str):
                return processed_img.encode()

            # Handle the case where processed_img is bytes
            if isinstance(processed_img, bytes):
                return processed_img

            # If blend_strength < 1.0, blend with original
            if blend_strength < 1.0:
                processed_img = cv2.addWeighted(
                    processed_img,
                    blend_strength,
                    img_bgr,
                    1.0 - blend_strength,
                    0,
                )

            # Convert back to PIL and then to bytes
            processed_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
            output_img = Image.fromarray(processed_rgb)

            output = BytesIO()
            output_img.save(output, format="PNG")
            return output.getvalue()

        except Exception as e:
            error_msg = f"Failed to apply color palette: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)
