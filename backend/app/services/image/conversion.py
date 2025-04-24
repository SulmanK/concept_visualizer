"""Image conversion utilities.

This module provides functions for converting images between formats,
generating thumbnails, and other image transformation operations.
"""

import imghdr
import logging
from io import BytesIO
from typing import Any, Dict, Optional, Tuple

from PIL import Image as PILImage

logger = logging.getLogger(__name__)


class ConversionError(Exception):
    """Exception raised for errors during image conversion."""

    pass


def detect_image_format(image_data: bytes) -> str:
    """Detect the format of an image from its binary data.

    Args:
        image_data: Binary image data

    Returns:
        String representation of the image format (e.g., 'jpeg', 'png')

    Raises:
        ConversionError: If format detection fails
    """
    try:
        # Try using imghdr first
        image_format = imghdr.what(None, h=image_data)

        if not image_format:
            # Fall back to PIL if imghdr doesn't work
            img = PILImage.open(BytesIO(image_data))
            image_format = img.format.lower() if img.format else None

        # If all detection methods fail, assume PNG
        if not image_format:
            logger.warning("Could not detect image format, assuming PNG")
            image_format = "png"

        # Normalize format names
        if image_format == "jpeg":
            return "jpg"

        return image_format

    except Exception as e:
        error_msg = f"Failed to detect image format: {str(e)}"
        logger.error(error_msg)
        raise ConversionError(error_msg)


def convert_image_format(image_data: bytes, target_format: str = "png", quality: int = 95) -> bytes:
    """Convert an image to a different format.

    Args:
        image_data: Binary image data
        target_format: Target format ('png', 'jpg', 'webp', etc.)
        quality: Quality for lossy formats (0-100)

    Returns:
        Converted image as bytes

    Raises:
        ConversionError: If conversion fails
    """
    try:
        # Open the image
        img: PILImage.Image = PILImage.open(BytesIO(image_data))

        # Convert RGBA to RGB if target is JPEG (JPEG doesn't support alpha)
        if target_format.lower() in ["jpg", "jpeg"] and img.mode == "RGBA":
            # Create a white background
            background = PILImage.new("RGB", img.size, (255, 255, 255))
            # Paste the image on the background using alpha as mask
            background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
            img = background

        # Convert to target format
        output = BytesIO()

        if target_format.lower() in ["jpg", "jpeg"]:
            img.save(output, format="JPEG", quality=quality, optimize=True)
        elif target_format.lower() == "png":
            img.save(output, format="PNG", optimize=True)
        elif target_format.lower() == "webp":
            img.save(output, format="WEBP", quality=quality, method=6)
        elif target_format.lower() == "gif":
            img.save(output, format="GIF", optimize=True)
        else:
            # Default fallback
            img.save(output, format=target_format.upper())

        return output.getvalue()

    except Exception as e:
        error_msg = f"Failed to convert image to {target_format}: {str(e)}"
        logger.error(error_msg)
        raise ConversionError(error_msg)


def generate_thumbnail(
    image_data: bytes,
    size: Tuple[int, int] = (128, 128),
    format: str = "png",
    preserve_aspect_ratio: bool = True,
    quality: int = 85,
) -> bytes:
    """Generate a thumbnail from an image.

    Args:
        image_data: Binary image data
        size: Thumbnail size as (width, height)
        format: Output format
        preserve_aspect_ratio: Whether to preserve the aspect ratio
        quality: Quality for lossy formats (0-100)

    Returns:
        Thumbnail image as bytes

    Raises:
        ConversionError: If thumbnail generation fails
    """
    try:
        # Open the image
        img: PILImage.Image = PILImage.open(BytesIO(image_data))

        # Convert to RGB if necessary
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")

        if preserve_aspect_ratio:
            # Create a thumbnail that fits within the size, preserving aspect ratio
            img.thumbnail(size, PILImage.Resampling.LANCZOS)
        else:
            # Resize to exact dimensions
            img = img.resize(size, PILImage.Resampling.LANCZOS)

        # Save to BytesIO
        output = BytesIO()

        if format.lower() in ["jpg", "jpeg"]:
            # Convert RGBA to RGB if needed
            if img.mode == "RGBA":
                background = PILImage.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])
                img = background
            img.save(output, format="JPEG", quality=quality, optimize=True)
        elif format.lower() == "png":
            img.save(output, format="PNG", optimize=True)
        elif format.lower() == "webp":
            img.save(output, format="WEBP", quality=quality)
        else:
            img.save(output, format=format.upper())

        return output.getvalue()

    except Exception as e:
        error_msg = f"Failed to generate thumbnail: {str(e)}"
        logger.error(error_msg)
        raise ConversionError(error_msg)


def get_image_metadata(image_data: bytes) -> Dict[str, Any]:
    """Extract metadata from an image.

    Args:
        image_data: Binary image data

    Returns:
        Dictionary containing image metadata (format, size, mode, etc.)

    Raises:
        ConversionError: If metadata extraction fails
    """
    try:
        img: PILImage.Image = PILImage.open(BytesIO(image_data))

        metadata: Dict[str, Any] = {
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "aspect_ratio": round(img.width / img.height, 2) if img.height > 0 else 0,
            "size_bytes": len(image_data),
            "exif": {},
        }

        # Extract EXIF data if available
        if hasattr(img, "_getexif") and img._getexif():
            exif = img._getexif()
            if exif:
                # Common EXIF tags
                exif_tags = {
                    271: "make",
                    272: "model",
                    306: "datetime",
                    36867: "date_taken",
                }

                for tag_id, tag_name in exif_tags.items():
                    if tag_id in exif:
                        metadata["exif"][tag_name] = str(exif[tag_id])

        return metadata

    except Exception as e:
        error_msg = f"Failed to extract image metadata: {str(e)}"
        logger.error(error_msg)
        raise ConversionError(error_msg)


def optimize_image(image_data: bytes, quality: int = 85, max_size: Optional[Tuple[int, int]] = None) -> bytes:
    """Optimize an image for web delivery.

    Args:
        image_data: Binary image data
        quality: Quality setting for compression (0-100)
        max_size: Optional maximum dimensions (width, height)

    Returns:
        Optimized image as bytes

    Raises:
        ConversionError: If optimization fails
    """
    try:
        img: PILImage.Image = PILImage.open(BytesIO(image_data))

        # Resize if necessary
        original_format = img.format
        if max_size and (img.width > max_size[0] or img.height > max_size[1]):
            img.thumbnail(max_size, PILImage.Resampling.LANCZOS)

        # Determine best format
        if img.mode == "RGBA" or original_format == "PNG" and "transparency" in img.info:
            output_format = "PNG"
        else:
            # JPEG is typically more efficient for photos
            output_format = "JPEG"
            if img.mode != "RGB":
                img = img.convert("RGB")

        # Save optimized image
        output = BytesIO()

        if output_format == "JPEG":
            img.save(output, format="JPEG", quality=quality, optimize=True, progressive=True)
        else:  # PNG
            img.save(output, format="PNG", optimize=True)

        # If new size is larger than original (happens sometimes with PNG), return original
        optimized_data = output.getvalue()
        if len(optimized_data) > len(image_data):
            logger.info("Optimized image is larger than original, returning original")
            return image_data

        return optimized_data

    except Exception as e:
        error_msg = f"Failed to optimize image: {str(e)}"
        logger.error(error_msg)
        raise ConversionError(error_msg)
