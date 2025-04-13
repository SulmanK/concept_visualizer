"""
Image processing service implementation.

This module provides a dedicated service for image processing operations,
following the Single Responsibility Principle.
"""

import logging
from typing import List, Dict, Any, Union, Optional, BinaryIO
from io import BytesIO
import httpx

from app.services.image.interface import ImageProcessingServiceInterface
from app.services.image.processing import apply_palette_with_masking_optimized, extract_dominant_colors
from app.services.image.conversion import (
    convert_image_format,
    generate_thumbnail,
    optimize_image,
    get_image_metadata,
    ConversionError
)

# Set up logging
logger = logging.getLogger(__name__)


class ImageProcessingError(Exception):
    """Exception raised for image processing errors."""
    pass


class ImageProcessingService(ImageProcessingServiceInterface):
    """
    Service for processing images.
    
    This service handles image transformations, format conversions,
    and other processing operations.
    """
    
    def __init__(self):
        """Initialize the image processing service."""
        self.logger = logging.getLogger(__name__)
        
    async def process_image(
        self, 
        image_data: Union[bytes, BytesIO, str], 
        operations: List[Dict[str, Any]]
    ) -> bytes:
        """
        Process an image with a series of operations.
        
        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            operations: List of operations to apply to the image
            
        Returns:
            Processed image data as bytes
            
        Raises:
            ImageProcessingError: If processing fails
        """
        try:
            current_image = image_data
            
            for operation in operations:
                op_type = operation.get("type", "").lower()
                
                if op_type == "resize":
                    width = operation.get("width")
                    height = operation.get("height")
                    preserve_aspect = operation.get("preserve_aspect_ratio", True)
                    
                    # Convert to bytes if it's not already
                    if isinstance(current_image, str):
                        async with httpx.AsyncClient() as client:
                            response = await client.get(current_image)
                            current_image = response.content
                    elif isinstance(current_image, BytesIO):
                        current_image = current_image.getvalue()
                    
                    # Generate thumbnail with target dimensions
                    current_image = generate_thumbnail(
                        current_image, 
                        size=(width, height),
                        preserve_aspect_ratio=preserve_aspect
                    )
                    
                elif op_type == "convert":
                    target_format = operation.get("format", "png")
                    quality = operation.get("quality", 95)
                    
                    # Convert to bytes if it's not already
                    if isinstance(current_image, str):
                        async with httpx.AsyncClient() as client:
                            response = await client.get(current_image)
                            current_image = response.content
                    elif isinstance(current_image, BytesIO):
                        current_image = current_image.getvalue()
                        
                    current_image = convert_image_format(
                        current_image,
                        target_format=target_format,
                        quality=quality
                    )
                    
                elif op_type == "optimize":
                    quality = operation.get("quality", 85)
                    max_width = operation.get("max_width")
                    max_height = operation.get("max_height")
                    
                    # Calculate max_size
                    max_size = None
                    if max_width or max_height:
                        max_size = (
                            max_width or 10000,  # Large default if only height specified
                            max_height or 10000  # Large default if only width specified
                        )
                    
                    # Convert to bytes if it's not already
                    if isinstance(current_image, str):
                        async with httpx.AsyncClient() as client:
                            response = await client.get(current_image)
                            current_image = response.content
                    elif isinstance(current_image, BytesIO):
                        current_image = current_image.getvalue()
                        
                    current_image = optimize_image(
                        current_image,
                        quality=quality,
                        max_size=max_size
                    )
                    
                elif op_type == "apply_palette":
                    palette_colors = operation.get("colors", [])
                    blend_strength = operation.get("blend_strength", 0.75)
                    
                    # Process the image with the palette
                    current_image = apply_palette_with_masking_optimized(
                        current_image,
                        palette_colors=palette_colors,
                        blend_strength=blend_strength
                    )
                    
                else:
                    self.logger.warning(f"Unknown image operation type: {op_type}")
            
            # Ensure final result is bytes
            if isinstance(current_image, str):
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
    
    def convert_to_format(
        self, 
        image_data: bytes, 
        target_format: str = "png", 
        quality: int = 95
    ) -> bytes:
        """
        Convert an image to a specified format.
        
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
            return convert_image_format(
                image_data=image_data,
                target_format=target_format,
                quality=quality
            )
        except ConversionError as e:
            raise ImageProcessingError(f"Failed to convert image format: {str(e)}")
    
    def generate_thumbnail(
        self, 
        image_data: bytes, 
        width: int, 
        height: int, 
        preserve_aspect_ratio: bool = True,
        format: str = "png"
    ) -> bytes:
        """
        Generate a thumbnail from an image.
        
        Args:
            image_data: Binary image data
            width: Target width
            height: Target height
            preserve_aspect_ratio: Whether to preserve the aspect ratio
            format: Output format
            
        Returns:
            Thumbnail image as bytes
            
        Raises:
            ImageProcessingError: If thumbnail generation fails
        """
        try:
            return generate_thumbnail(
                image_data=image_data,
                size=(width, height),
                format=format,
                preserve_aspect_ratio=preserve_aspect_ratio
            )
        except ConversionError as e:
            raise ImageProcessingError(f"Failed to generate thumbnail: {str(e)}")
    
    async def extract_color_palette(
        self, 
        image_data: bytes, 
        num_colors: int = 5
    ) -> List[str]:
        """
        Extract a color palette from an image.
        
        Args:
            image_data: Binary image data
            num_colors: Number of colors to extract
            
        Returns:
            List of color hex codes
            
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
        """
        Extract metadata from an image.
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dictionary containing image metadata
            
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
        quality: Optional[int] = None
    ) -> bytes:
        """
        Convert an image to a different format.
        
        Args:
            image_data: Image data as bytes, file-like object, or path/URL
            target_format: Format to convert to (PNG, JPEG, etc.)
            quality: Quality level for lossy formats (0-100)
            
        Returns:
            Converted image as bytes
            
        Raises:
            ImageProcessingError: If conversion fails
        """
        try:
            # Ensure image_data is bytes
            if isinstance(image_data, str):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_data)
                    image_data = response.content
            elif hasattr(image_data, 'read'):
                image_data = image_data.read()
                
            return self.convert_to_format(
                image_data=image_data,
                target_format=target_format.lower(),
                quality=quality or 95
            )
        except Exception as e:
            error_msg = f"Failed to convert image format: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg)
    
    async def resize_image(
        self,
        image_data: Union[bytes, BinaryIO, str],
        width: int,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> bytes:
        """
        Resize an image to specified dimensions.
        
        Args:
            image_data: Image data as bytes, file-like object, or path/URL
            width: Target width in pixels
            height: Target height in pixels (optional if maintaining aspect ratio)
            maintain_aspect_ratio: Whether to preserve the aspect ratio
            
        Returns:
            Resized image as bytes
            
        Raises:
            ImageProcessingError: If resizing fails
        """
        try:
            # Ensure image_data is bytes
            if isinstance(image_data, str):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_data)
                    image_data = response.content
            elif hasattr(image_data, 'read'):
                image_data = image_data.read()
                
            # If height is None but maintaining aspect ratio, use a placeholder
            # The thumbnail function will calculate the correct height
            actual_height = height or width
                
            return self.generate_thumbnail(
                image_data=image_data,
                width=width,
                height=actual_height,
                preserve_aspect_ratio=maintain_aspect_ratio
            )
        except Exception as e:
            error_msg = f"Failed to resize image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageProcessingError(error_msg) 