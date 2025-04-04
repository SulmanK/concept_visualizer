"""
Image service implementation.

This module provides the implementation of the ImageServiceInterface
which coordinates image generation, storage, and processing.
"""

import logging
import json
import httpx
from typing import List, Dict, Any, Optional, Union, Tuple
from io import BytesIO
from datetime import datetime

from fastapi import UploadFile
from supabase import Client
from PIL import Image as PILImage

from app.services.interfaces import ImageServiceInterface
from app.services.image.storage import ImageStorageService, ImageStorageError, ImageNotFoundError
from app.services.image.processing import apply_palette_with_masking_optimized, extract_dominant_colors
from app.services.image.conversion import (
    convert_image_format,
    generate_thumbnail,
    optimize_image,
    get_image_metadata,
    ConversionError
)
from app.services.jigsawstack.client import JigsawStackClient
from app.utils.security.mask import mask_id, mask_path

# Set up logging
logger = logging.getLogger(__name__)

class ImageError(Exception):
    """Base exception for image service errors."""
    pass

class ImageGenerationError(ImageError):
    """Exception raised for image generation errors."""
    pass

class ImageProcessingError(ImageError):
    """Exception raised for image processing errors."""
    pass


class ImageService(ImageServiceInterface):
    """
    Service for generating, processing, and storing images.
    
    This service coordinates between image generation, storage,
    and various image processing operations.
    """
    
    def __init__(
        self, 
        jigsawstack_client: JigsawStackClient,
        supabase_client: Client,
        storage_service: ImageStorageService
    ):
        """
        Initialize the image service.
        
        Args:
            jigsawstack_client: Client for JigsawStack API
            supabase_client: Supabase client
            storage_service: Service for image storage operations
        """
        self.jigsawstack = jigsawstack_client
        self.supabase = supabase_client
        self.storage = storage_service
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
            
    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> str:
        """
        Store an image and return its public URL.
        
        Args:
            image_data: Image data as bytes, BytesIO, or UploadFile
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image
            
        Returns:
            Public URL of the stored image
            
        Raises:
            ImageError: If storage fails
        """
        try:
            # Use the storage service to store the image
            return self.storage.store_image(
                image_data=image_data,
                concept_id=concept_id,
                file_name=file_name,
                metadata=metadata,
                is_palette=is_palette
            )
        except ImageStorageError as e:
            # Re-raise as ImageError
            raise ImageError(f"Failed to store image: {str(e)}")
            
    def get_image(self, image_url_or_path: str, is_palette: bool = False) -> bytes:
        """
        Retrieve an image by URL or storage path.
        
        Args:
            image_url_or_path: URL or storage path of the image
            is_palette: Whether this is a palette image
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageError: If retrieval fails
        """
        try:
            # Check if it's an external URL or a storage path
            if image_url_or_path.startswith(("http://", "https://")):
                # It's an external URL, download it
                response = httpx.get(image_url_or_path, timeout=10.0)
                response.raise_for_status()
                return response.content
            else:
                # It's a storage path, use the storage service
                return self.storage.get_image(image_url_or_path, is_palette=is_palette)
                
        except (httpx.HTTPError, ImageStorageError) as e:
            error_msg = f"Failed to get image {image_url_or_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg)
            
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
            ImageError: If conversion fails
        """
        try:
            return convert_image_format(
                image_data=image_data,
                target_format=target_format,
                quality=quality
            )
        except ConversionError as e:
            raise ImageError(f"Failed to convert image format: {str(e)}")
            
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
            ImageError: If thumbnail generation fails
        """
        try:
            return generate_thumbnail(
                image_data=image_data,
                size=(width, height),
                format=format,
                preserve_aspect_ratio=preserve_aspect_ratio
            )
        except ConversionError as e:
            raise ImageError(f"Failed to generate thumbnail: {str(e)}")
            
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
            ImageError: If color extraction fails
        """
        try:
            return await extract_dominant_colors(image_data, num_colors)
        except Exception as e:
            error_msg = f"Failed to extract color palette: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg)
        
    async def generate_and_store_image(
        self, 
        prompt: str,
        concept_id: Optional[str] = None,
        session_id: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        store: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate an image based on a prompt and store it in Supabase.
        
        Args:
            prompt: Text prompt for image generation
            concept_id: Optional concept ID to associate with the image
            session_id: Optional session ID to organize images
            width: Image width
            height: Image height
            store: Whether to store the generated image
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image
            
        Returns:
            Tuple of (storage_path, public_url) or (None, None) on error
            
        Raises:
            ImageGenerationError: If image generation fails
            ImageError: If image storage fails
        """
        try:
            # Generate image using JigsawStack
            self.logger.info(f"Generating image with prompt: {prompt}")
            
            generation_result = await self.jigsawstack.generate_image(
                prompt=prompt,
                width=width,
                height=height
            )
            
            if not generation_result or 'url' not in generation_result:
                raise ImageGenerationError("Failed to generate image: Invalid response from generation service")
                
            # Only store if requested
            if store:
                # Check if we got binary data directly
                if 'binary_data' in generation_result:
                    image_data = generation_result['binary_data']
                    self.logger.info("Using direct binary image data from generation result")
                else:
                    # Download the generated image from URL
                    image_url = generation_result['url']
                    self.logger.info(f"Downloading generated image from URL: {image_url}")
                    
                    # Handle file:// URLs for temp files
                    if image_url.startswith('file://'):
                        # Load from local file
                        local_path = image_url[7:]  # Remove 'file://' prefix
                        with open(local_path, 'rb') as f:
                            image_data = f.read()
                        # Clean up the temp file
                        try:
                            import os
                            os.remove(local_path)
                            self.logger.debug(f"Cleaned up temporary file: {local_path}")
                        except Exception as e:
                            self.logger.warning(f"Failed to clean up temporary file {local_path}: {str(e)}")
                    else:
                        # Download from remote URL
                        async with httpx.AsyncClient() as client:
                            response = await client.get(image_url)
                            response.raise_for_status()
                            image_data = response.content
                
                # Store it in our storage
                try:
                    # Add prompt and generation details to metadata
                    if metadata is None:
                        metadata = {}
                    
                    metadata.update({
                        "prompt": prompt,
                        "generation_service": "jigsawstack",
                        "width": width,
                        "height": height,
                    })
                    
                    # Create a folder path with session_id if provided
                    storage_concept_id = concept_id
                    if session_id and concept_id:
                        storage_concept_id = f"{session_id}/{concept_id}"
                        self.logger.info(f"Storing image with session {mask_id(session_id)} and concept {mask_id(concept_id)}")
                    elif session_id:
                        storage_concept_id = session_id
                        self.logger.info(f"Storing image with session {mask_id(session_id)}")
                    
                    # Store the image
                    stored_url = self.storage.store_image(
                        image_data=image_data,
                        concept_id=storage_concept_id,
                        metadata=metadata,
                        is_palette=is_palette
                    )
                    
                    # Extract the image path from the URL
                    # The URL format is typically: {base_url}/storage/v1/object/public/{bucket}/{path}
                    if stored_url:
                        from urllib.parse import urlparse
                        parsed_url = urlparse(stored_url)
                        path_parts = parsed_url.path.split('/')
                        # Find the bucket name in the path
                        bucket_index = -1
                        bucket_name = self.storage.palette_bucket if is_palette else self.storage.concept_bucket
                        for i, part in enumerate(path_parts):
                            if part == bucket_name:
                                bucket_index = i
                                break
                        
                        # Extract the path after the bucket name
                        if bucket_index >= 0 and bucket_index < len(path_parts) - 1:
                            image_path = '/'.join(path_parts[bucket_index+1:])
                        else:
                            # Fallback: use the last part of the URL as the path
                            image_path = path_parts[-1]
                            
                        self.logger.info(f"Generated and stored image at path: {mask_path(image_path)}")
                        return image_path, stored_url
                    
                    self.logger.error("Failed to store image: No URL returned")
                    return None, None
                    
                except ImageStorageError as e:
                    self.logger.error(f"Failed to store generated image: {str(e)}")
                    return None, generation_result.get('url')
            else:
                # Not storing, just return None for path and the generation URL
                return None, generation_result.get('url')
            
        except Exception as e:
            error_msg = f"Failed to generate and store image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageGenerationError(error_msg)

    async def apply_color_palette(
        self, 
        base_image_path: str, 
        palette_colors: List[str], 
        session_id: str,
        blend_strength: float = 0.75
    ) -> str:
        """
        Apply a color palette to an image and store the result.
        
        Args:
            base_image_path: Path to the source image in storage
            palette_colors: List of hex color codes to apply
            session_id: Session ID for organizing images
            blend_strength: How strongly to apply the colors (0.0-1.0)
            
        Returns:
            Path to the color-modified image in storage if successful
            
        Raises:
            ImageProcessingError: If processing fails
            ImageStorageError: If storage fails
        """
        try:
            self.logger.info(f"Applying color palette to image: {mask_path(base_image_path)}")
            
            # Get the source image URL for the concept image
            try:
                base_image_url = self.get_image_url(base_image_path, "concept-images")
                self.logger.info(f"Retrieved image URL for: {mask_path(base_image_path)}")
            except Exception as e:
                self.logger.error(f"Failed to get image URL for {mask_path(base_image_path)}: {str(e)}")
                raise ImageProcessingError(f"Failed to get image URL: {str(e)}")
            
            # Apply the palette using the optimized masking approach
            from app.services.image.processing import apply_palette_with_masking_optimized
            try:
                palette_image_data = apply_palette_with_masking_optimized(
                    base_image_url,
                    palette_colors,
                    blend_strength=blend_strength
                )
                self.logger.info(f"Successfully applied palette to image ({len(palette_image_data)} bytes)")
            except Exception as e:
                self.logger.error(f"Error in palette application algorithm: {str(e)}")
                raise ImageProcessingError(f"Failed to apply palette algorithm: {str(e)}")
            
            # Generate a unique filename for the palette variation
            import uuid
            unique_id = str(uuid.uuid4())
            file_name = f"palette_{unique_id}.png"
            palette_image_path = f"{session_id}/{file_name}"
            
            # Store the modified image
            try:
                stored_url = self.storage.store_image(
                    image_data=palette_image_data,
                    concept_id=session_id,
                    file_name=file_name,
                    is_palette=True
                )
                
                if not stored_url:
                    raise ImageProcessingError("Failed to store palette image")
                    
                self.logger.info(f"Successfully stored palette image at: {mask_path(palette_image_path)}")
            except Exception as e:
                self.logger.error(f"Failed to store palette image: {str(e)}")
                raise ImageStorageError(f"Failed to store palette image: {str(e)}")
                
            return palette_image_path
            
        except Exception as e:
            self.logger.error(f"Error applying color palette: {str(e)}")
            if isinstance(e, (ImageProcessingError, ImageStorageError)):
                raise
            raise ImageProcessingError(f"Failed to apply color palette: {str(e)}")

    def get_image_url(self, image_path: str, bucket_name: str) -> str:
        """
        Get the public URL for an image in storage.
        
        Args:
            image_path: Path to the image in storage
            bucket_name: Name of the bucket (e.g., "concept-images" or "palette-images")
            
        Returns:
            Public URL for the image
            
        Raises:
            ImageError: If URL generation fails
        """
        try:
            # Determine if this is a palette image based on the bucket name
            is_palette = bucket_name == "palette-images"
            
            # Use the storage service to get the URL
            return self.storage.get_public_url(image_path, is_palette=is_palette)
            
        except Exception as e:
            self.logger.error(f"Error getting image URL: {str(e)}")
            raise ImageError(f"Failed to get image URL: {str(e)}") 