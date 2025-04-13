"""
Export service for converting and exporting images.

This module provides services for exporting images in different formats.
"""

import logging
import os
import tempfile
import base64
from io import BytesIO
from typing import Dict, Literal, Optional, Tuple, Any, BinaryIO, Union
from fastapi import Depends, HTTPException
from PIL import Image

import vtracer
from app.services.image.interface import ImageServiceInterface, ImageProcessingServiceInterface
from app.services.image import get_image_service, get_image_processing_service
from app.utils.security.mask import mask_id, mask_path

# Configure logging
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Exception raised for image export errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ExportService:
    """Service for exporting images in different formats."""
    
    def __init__(
        self, 
        image_service: ImageServiceInterface = Depends(get_image_service),
        processing_service: ImageProcessingServiceInterface = Depends(get_image_processing_service),
    ):
        """Initialize export service with required dependencies.
        
        Args:
            image_service: Service for image operations
            processing_service: Service for image processing operations
        """
        self.image_service = image_service
        self.processing_service = processing_service
        self.logger = logging.getLogger("export_service")
    
    async def process_export(
        self,
        image_data: bytes,
        original_filename: str,
        target_format: Literal["png", "jpg", "svg"],
        target_size: Literal["small", "medium", "large", "original"],
        svg_params: Optional[Dict] = None,
    ) -> Tuple[bytes, str, str]:
        """
        Process the image export request.
        
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
            masked_filename = mask_path(original_filename)
            self.logger.info(
                f"Processing export for image: {masked_filename}, "
                f"format: {target_format}, size: {target_size}"
            )
            
            # Process the image based on requested format and size
            if target_format == "svg":
                # Process for SVG conversion
                processed_bytes, filename, content_type = await self._convert_to_svg(
                    image_data, original_filename, svg_params
                )
            else:
                # Process for PNG/JPG
                processed_bytes, filename, content_type = await self._process_raster_image(
                    image_data, original_filename, target_format, target_size
                )
            
            self.logger.info(
                f"Export processed successfully: {mask_path(filename)}, "
                f"size: {len(processed_bytes)}, type: {content_type}"
            )
            
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
        """
        Process a raster image (resize and convert format).
        
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
                "original": None
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
                        "width": target_dimensions[0],
                        "height": target_dimensions[1],
                        "preserve_aspect_ratio": True
                    }
                ]
                
                # Resize the image
                resized_data = await self.processing_service.process_image(image_data, operations)
                
                # Convert format
                quality = 90 if output_format == "jpeg" else None
                processed_bytes = self.processing_service.convert_to_format(
                    resized_data, 
                    target_format=output_format,
                    quality=quality or 95
                )
            else:
                # Just convert format without resizing
                processed_bytes = self.processing_service.convert_to_format(
                    image_data, 
                    target_format=output_format,
                    quality=90 if output_format == "jpeg" else 95
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
        """
        Convert an image to SVG format.
        
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
                                if "path_precision" in svg_params:
                                    config.path_precision = int(svg_params["path_precision"])
                                if "corner_threshold" in svg_params:
                                    config.corner_threshold = float(svg_params["corner_threshold"])
                                if "length_threshold" in svg_params:
                                    config.length_threshold = float(svg_params["length_threshold"])
                                if "max_colors" in svg_params:
                                    config.color_palette_size = int(svg_params["max_colors"])
                                if "gradient_step" in svg_params:
                                    config.gradient_step = int(svg_params["gradient_step"])
                            
                            # Convert to SVG
                            vtracer.convert_image_to_svg_path(config, input_path, output_path)
                        else:
                            # For non-color modes, use our simpler conversion
                            self._create_simple_svg_from_image(image, output_path)
                        
                        # Read the SVG output
                        with open(output_path, 'rb') as f:
                            svg_bytes = f.read()
                    
                        # Generate output filename
                        base_name = os.path.basename(original_filename)
                    name_without_ext = os.path.splitext(base_name)[0]
                    new_filename = f"{name_without_ext}.svg"
                    
                        # Return the SVG bytes, filename, and content type
                    return svg_bytes, new_filename, "image/svg+xml"
                finally:
                    # Clean up temporary files
                        if os.path.exists(input_path):
                            os.unlink(input_path)
                        if os.path.exists(output_path):
                            os.unlink(output_path)
        except Exception as e:
            self.logger.error(f"Error converting to SVG: {str(e)}")
            raise ExportError(f"Error converting to SVG: {str(e)}")
    
    def _create_simple_svg_from_image(self, image: Image.Image, output_path: str) -> None:
        """
        Create a simple SVG from an image.
        
        Args:
            image: PIL Image to convert
            output_path: Path to save the SVG
            
        This is a simplified SVG conversion for non-color modes.
        """
        # Convert to grayscale for simplicity
        image = image.convert("L")
        
        # Get image dimensions
        width, height = image.size
        
        # Open SVG file for writing
        with open(output_path, "w") as f:
            # Write SVG header
            f.write(f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">\n')
            
            # Create a simple path representation of the image (very basic)
            f.write('<path d="')
            
            # Simple threshold-based approach for paths
            threshold = 128
            for y in range(0, height, 2):  # Sample every 2 pixels for brevity
                for x in range(0, width, 2):
                    pixel = image.getpixel((x, y))
                    if pixel < threshold:  # Dark pixel
                        f.write(f"M{x},{y} ")
            
            f.write('" fill="black" stroke="none"/>\n')
            f.write('</svg>')


async def get_export_service(
    image_service: ImageServiceInterface = Depends(get_image_service),
    processing_service: ImageProcessingServiceInterface = Depends(get_image_processing_service),
) -> ExportService:
    """
    Get an instance of the ExportService.
    
    Args:
        image_service: Service for image operations
        processing_service: Service for image processing operations
        
    Returns:
        ExportService instance
    """
    return ExportService(
        image_service=image_service,
        processing_service=processing_service
    ) 