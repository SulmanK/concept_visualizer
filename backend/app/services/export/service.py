"""Export service for converting and exporting images.

This module provides services for exporting images in different formats.
"""

import logging
import os
import tempfile
from io import BytesIO
from typing import Any, BinaryIO, Dict, List, Literal, Optional, Tuple, Union

import vtracer
from fastapi import Depends
from PIL import Image

from app.services.export.interface import ExportServiceInterface
from app.services.image import get_image_processing_service, get_image_service
from app.services.image.interface import ImageProcessingServiceInterface, ImageServiceInterface

# Configure logging
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Exception raised for image export errors."""

    def __init__(self, message: str):
        """Initialize the exception with a message.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(self.message)


class ExportService(ExportServiceInterface):
    """Service for exporting images in different formats."""

    def __init__(
        self,
        image_service: ImageServiceInterface = Depends(get_image_service),
        processing_service: ImageProcessingServiceInterface = Depends(get_image_processing_service),
    ) -> None:
        """Initialize export service with required dependencies.

        Args:
            image_service: Service for image operations
            processing_service: Service for image processing operations
        """
        self.image_service = image_service
        self.processing_service = processing_service
        self.logger = logging.getLogger("export_service")

    async def export_image(
        self,
        image_path: str,
        format: str,
        size: Optional[Dict[str, int]] = None,
        quality: Optional[int] = None,
        user_id: Optional[str] = None,
        include_original: bool = False,
        color_mode: str = "color",
    ) -> Dict[str, Any]:
        """Export an image with specified format and parameters.

        Args:
            image_path: Path or URL of the image to export
            format: Target format (PNG, JPEG, SVG, etc.)
            size: Optional dictionary with width and/or height
            quality: Quality for lossy formats (0-100)
            user_id: Optional user ID for tracking exports
            include_original: Whether to include the original image
            color_mode: Color mode of the export (color, grayscale, etc.)

        Returns:
            Dictionary containing the exported image data and metadata

        Raises:
            ExportError: If export fails
            ResourceNotFoundError: If the image is not found
        """
        try:
            self.logger.info(f"Exporting image: {os.path.basename(image_path)} to format: {format}")

            # Determine if this is from the concept or palette bucket based on path
            is_palette = False
            if "palette" in image_path.lower():
                is_palette = True
                self.logger.debug(f"Using palette bucket for image: {os.path.basename(image_path)}")
            else:
                self.logger.debug(f"Using concept bucket for image: {os.path.basename(image_path)}")

            # First try with the detected bucket
            try:
                # Get image data from image service with the detected bucket
                image_data = await self.image_service.get_image_async(image_path)

                if not image_data:
                    self.logger.error(f"Failed to get image data for {os.path.basename(image_path)}")
                    raise ExportError(f"Image not found: {image_path}")
            except Exception as e:
                # If that fails, try with the get_image_data method which supports is_palette parameter
                self.logger.warning(f"Failed to get image with default method, trying alternative approach: {str(e)}")
                try:
                    # Check if the image_service has a get_image_data method
                    if hasattr(self.image_service, "get_image_data"):
                        image_data = await self.image_service.get_image_data(image_path, is_palette=is_palette)
                    else:
                        # If not, re-raise the original exception
                        raise e

                    if not image_data:
                        self.logger.error(f"Failed to get image data with either method for {os.path.basename(image_path)}")
                        raise ExportError(f"Image not found: {image_path}")

                    # If we get here, we found the image in the opposite bucket, so update is_palette
                    is_palette = not is_palette
                    self.logger.info(f"Successfully found image in the {'palette' if is_palette else 'concept'} bucket")
                except Exception as inner_e:
                    self.logger.error(f"Failed to get image with either method: {str(e)}, {str(inner_e)}")
                    raise ExportError(f"Image not found: {image_path}")

            # Prepare size parameters for processing
            target_size = "original"
            if size:
                # Map size to a named size if it matches standard dimensions
                width = size.get("width")
                height = size.get("height")

                if width == 500 and height == 500:
                    target_size = "small"
                elif width == 1000 and height == 1000:
                    target_size = "medium"
                elif width == 2000 and height == 2000:
                    target_size = "large"

            # Process the export based on format
            target_format = format.lower()
            svg_params = {"mode": color_mode} if target_format == "svg" else None

            # Make sure target_format and target_size are valid literals
            if target_format not in ("png", "jpg", "svg"):
                target_format = "png"  # Default to PNG if invalid format

            if target_size not in ("small", "medium", "large", "original"):
                target_size = "original"  # Default to original if invalid size

            # Use the existing process_export function
            processed_bytes, filename, content_type = await self.process_export(
                image_data=image_data,
                original_filename=image_path,
                target_format=target_format,  # type: ignore
                target_size=target_size,  # type: ignore
                svg_params=svg_params,
            )

            # Return the result
            return {
                "data": processed_bytes,
                "filename": filename,
                "content_type": content_type,
                "size": len(processed_bytes),
                "format": target_format,
            }
        except Exception as e:
            self.logger.error(f"Error exporting image: {str(e)}")
            raise ExportError(f"Failed to export image: {str(e)}")

    async def export_palette(
        self,
        palette_data: List[str],
        format: str = "png",
        size: Optional[Dict[str, int]] = None,
    ) -> bytes:
        """Export a color palette as an image.

        Args:
            palette_data: List of color values (hex codes)
            format: Target format for the palette image
            size: Optional dictionary with width and/or height

        Returns:
            Binary data of the exported palette image

        Raises:
            ExportError: If export fails
        """
        try:
            self.logger.info(f"Exporting palette with {len(palette_data)} colors to {format}")

            # Set default size if not specified
            if not size:
                size = {"width": 800, "height": 200}

            # Create a palette image
            width = size.get("width", 800)
            height = size.get("height", 200)

            # Calculate the width of each color block
            block_width = width // len(palette_data)

            # Create a new image with the given size
            img = Image.new("RGB", (width, height), color="white")

            # Draw each color in the palette
            for i, color in enumerate(palette_data):
                # Ensure color has a valid hex format (add # if missing)
                if not color.startswith("#"):
                    color = f"#{color}"

                # Create a block for this color
                color_block = Image.new("RGB", (block_width, height), color=color)

                # Paste the block into the palette image
                img.paste(color_block, (i * block_width, 0))

            # Convert the image to the requested format
            output = BytesIO()
            img.save(output, format=format.upper(), quality=90 if format.lower() == "jpg" or format.lower() == "jpeg" else None)

            return output.getvalue()
        except Exception as e:
            self.logger.error(f"Error exporting palette: {str(e)}")
            raise ExportError(f"Failed to export palette: {str(e)}")

    async def export_concept_package(
        self,
        concept_id: str,
        user_id: str,
        formats: List[str],
        include_palettes: bool = True,
    ) -> Dict[str, Any]:
        """Export a complete concept package with multiple formats.

        Args:
            concept_id: ID of the concept to export
            user_id: User ID owning the concept
            formats: List of formats to include
            include_palettes: Whether to include palette images

        Returns:
            Dictionary with paths to exported files

        Raises:
            ExportError: If export fails
            ResourceNotFoundError: If the concept is not found
        """
        # NOTE: This is a placeholder implementation
        # A full implementation would require concept service integration
        self.logger.warning("export_concept_package is not fully implemented")
        return {"status": "not_implemented", "message": "This feature is not fully implemented yet", "concept_id": concept_id, "formats": formats}

    async def generate_thumbnail(
        self,
        image_data: Union[bytes, str, BinaryIO],
        width: int,
        height: int,
        format: str = "png",
    ) -> bytes:
        """Generate a thumbnail of an image.

        Args:
            image_data: Image data or path or file-like object
            width: Thumbnail width
            height: Thumbnail height
            format: Output format

        Returns:
            Thumbnail image data

        Raises:
            ExportError: If thumbnail generation fails
        """
        try:
            self.logger.info(f"Generating thumbnail with dimensions {width}x{height}")

            # Get image data if a string path is provided
            if isinstance(image_data, str):
                # Assume this is a path and get the image data
                image_bytes = await self.image_service.get_image_async(image_data)
            elif isinstance(image_data, bytes):
                # Already binary data
                image_bytes = image_data
            else:
                # Read from file-like object
                image_bytes = image_data.read()

            # Create operations for the image processing service
            operations = [
                {
                    "type": "resize",
                    "width": width,
                    "height": height,
                    "preserve_aspect_ratio": True,
                }
            ]

            # Process the image to create the thumbnail
            processed_data = await self.processing_service.process_image(image_bytes, operations)

            # Convert to the requested format
            output_format = format.lower()
            if output_format == "jpg":
                output_format = "jpeg"  # PIL uses JPEG internally

            thumbnail_bytes = self.processing_service.convert_to_format(processed_data, target_format=output_format, quality=85)  # Use a default quality value of 85 instead of conditional None

            return thumbnail_bytes
        except Exception as e:
            self.logger.error(f"Error generating thumbnail: {str(e)}")
            raise ExportError(f"Failed to generate thumbnail: {str(e)}")

    async def process_export(
        self,
        image_data: bytes,
        original_filename: str,
        target_format: Literal["png", "jpg", "svg"],
        target_size: Literal["small", "medium", "large", "original"],
        svg_params: Optional[Dict] = None,
    ) -> Tuple[bytes, str, str]:
        """Process the image export request.

        Args:
            image_data: Binary image data to export
            original_filename: Original filename for generating export filename
            target_format: Target format for export (png, jpg, svg)
            target_size: Target size for export (small, medium, large, original)
            svg_params: Optional parameters for SVG conversion

        Returns:
            Tuple containing:
                - Processed image bytes
                - Filename for the exported file
                - Content type for the exported file

        Raises:
            ExportError: If the export processing fails
        """
        try:
            masked_filename = os.path.basename(original_filename)
            self.logger.info(f"Processing export for image: {masked_filename}, " f"format: {target_format}, size: {target_size}")

            # Process the image based on requested format and size
            if target_format == "svg":
                # Process for SVG conversion
                processed_bytes, filename, content_type = await self._convert_to_svg(image_data, original_filename, svg_params)
            else:
                # Process for PNG/JPG
                (
                    processed_bytes,
                    filename,
                    content_type,
                ) = await self._process_raster_image(image_data, original_filename, target_format, target_size)

            self.logger.info(f"Export processed successfully: {os.path.basename(filename)}, " f"size: {len(processed_bytes)}, type: {content_type}")

            return processed_bytes, filename, content_type
        except Exception as e:
            self.logger.error(f"Error processing export: {str(e)}")
            raise ExportError(f"Error processing export: {str(e)}")

    async def _process_raster_image(
        self,
        image_data: bytes,
        original_filename: str,
        target_format: Literal["png", "jpg"],
        target_size: Literal["small", "medium", "large", "original"],
    ) -> Tuple[bytes, str, str]:
        """Process a raster image (resize and convert format).

        Args:
            image_data: Original image bytes
            original_filename: Original filename
            target_format: Target format (png, jpg)
            target_size: Target size (small, medium, large, original)

        Returns:
            Tuple containing:
                - Processed image bytes
                - Filename for the exported file
                - Content type for the exported file
        """
        try:
            # Define size mapping (max dimensions for each size)
            size_mapping = {
                "small": (500, 500),
                "medium": (1000, 1000),
                "large": (2000, 2000),
                "original": None,
            }

            target_dimensions = size_mapping.get(target_size)

            # Convert format if needed
            output_format = target_format.lower()
            if output_format == "jpg":
                output_format = "jpeg"  # PIL uses JPEG internally

            # Use the processing service for resizing and format conversion
            if target_size != "original":
                # Apply resize operation
                operations = [
                    {
                        "type": "resize",
                        "width": target_dimensions[0] if target_dimensions else None,
                        "height": target_dimensions[1] if target_dimensions else None,
                        "preserve_aspect_ratio": True,
                    }
                ]

                # Resize the image
                resized_data = await self.processing_service.process_image(image_data, operations)

                # Convert format
                quality = 90 if output_format == "jpeg" else None
                processed_bytes = self.processing_service.convert_to_format(resized_data, target_format=output_format, quality=quality or 95)
            else:
                # Just convert format without resizing
                processed_bytes = self.processing_service.convert_to_format(
                    image_data,
                    target_format=output_format,
                    quality=90 if output_format == "jpeg" else 95,
                )

            # Generate appropriate filename
            base_name = os.path.basename(original_filename)
            name_without_ext = os.path.splitext(base_name)[0]
            new_filename = f"{name_without_ext}.{target_format.lower()}"

            # Set content type
            content_type = f"image/{target_format.lower()}"
            if target_format.lower() == "jpg":
                content_type = "image/jpeg"

            return processed_bytes, new_filename, content_type
        except Exception as e:
            self.logger.error(f"Error processing raster image: {str(e)}")
            raise ExportError(f"Error processing image: {str(e)}")

    async def _convert_to_svg(
        self,
        image_data: bytes,
        original_filename: str,
        svg_params: Optional[Dict] = None,
    ) -> Tuple[bytes, str, str]:
        """Convert an image to SVG format.

        Args:
            image_data: Original image bytes
            original_filename: Original filename
            svg_params: Optional parameters for SVG conversion

        Returns:
            Tuple containing:
                - SVG bytes
                - Filename for the exported file
                - Content type for the exported file
        """
        try:
            # Default SVG conversion parameters
            mode = svg_params.get("mode", "color") if svg_params else "color"

            # Process the image
            image = Image.open(BytesIO(image_data))

            # Use temporary files for input/output with vtracer
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_input:
                with tempfile.NamedTemporaryFile(suffix=".svg", delete=False) as temp_output:
                    try:
                        # Save input image to temporary file
                        input_path = temp_input.name
                        output_path = temp_output.name

                        if mode == "color":
                            # Save as PNG for best color fidelity
                            image.save(input_path, format="PNG")

                            # Use vtracer for color vectorization
                            config = vtracer.Configuration()
                            config.color_mode = vtracer.ColorMode.COLOR
                            config.hierarchical = True
                            config.filter_speckle = 4
                            config.path_precision = 3

                            # Setup from SVG params if provided
                            if svg_params:
                                if "filter_speckle" in svg_params:
                                    config.filter_speckle = int(svg_params["filter_speckle"])
                                # Add more parameter handling as needed

                            # Run the tracer
                            vtracer.convert_image_to_svg(input_path, output_path, config)
                        else:
                            # Use a simpler approach for monochrome/simplified
                            self._create_simple_svg_from_image(image, output_path)

                        # Read the generated SVG file
                        with open(output_path, "rb") as svg_file:
                            svg_data = svg_file.read()

                        # Generate appropriate filename
                        base_name = os.path.basename(original_filename)
                        name_without_ext = os.path.splitext(base_name)[0]
                        new_filename = f"{name_without_ext}.svg"

                        return svg_data, new_filename, "image/svg+xml"
                    finally:
                        # Clean up temporary files
                        try:
                            os.unlink(input_path)
                            os.unlink(output_path)
                        except (OSError, PermissionError) as e:
                            # Just log errors during cleanup, don't fail the operation
                            self.logger.warning(f"Error cleaning up temp files: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error converting to SVG: {str(e)}")
            raise ExportError(f"Error converting to SVG: {str(e)}")

    def _create_simple_svg_from_image(self, image: Image.Image, output_path: str) -> None:
        """Create a simplified SVG from an image.

        Args:
            image: PIL Image to convert
            output_path: Path where the SVG should be saved
        """
        # Convert to grayscale for simpler processing
        gray_image = image.convert("L")
        # Use vtracer with simplified settings
        # First save the grayscale image to a temporary PNG
        temp_gray_path = output_path + ".temp.png"
        try:
            gray_image.save(temp_gray_path, format="PNG")
            # Configure for line art/monochrome
            config = vtracer.Configuration()
            config.color_mode = vtracer.ColorMode.BINARY
            config.hierarchical = False
            config.filter_speckle = 4
            config.path_precision = 8
            config.corner_threshold = 60
            config.length_threshold = 4.0
            # Run the tracer
            vtracer.convert_image_to_svg(temp_gray_path, output_path, config)
        finally:
            # Clean up
            try:
                if os.path.exists(temp_gray_path):
                    os.unlink(temp_gray_path)
            except OSError:
                pass


async def get_export_service(
    image_service: ImageServiceInterface = Depends(get_image_service),
    processing_service: ImageProcessingServiceInterface = Depends(get_image_processing_service),
) -> ExportService:
    """Create and configure an export service instance.

    Args:
        image_service: Image service dependency
        processing_service: Image processing service dependency

    Returns:
        Configured ExportService instance
    """
    return ExportService(image_service=image_service, processing_service=processing_service)
