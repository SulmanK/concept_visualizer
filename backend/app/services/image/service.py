"""
Image service implementation.

This module provides the implementation of the ImageServiceInterface
which coordinates image processing and conversion.
"""

import logging
import json
import httpx
from typing import List, Dict, Any, Optional, Union, Tuple
from io import BytesIO
from datetime import datetime
import uuid

from fastapi import UploadFile
from PIL import Image as PILImage

# Fix circular import - import interfaces directly from their modules
from app.services.image.interface import ImageServiceInterface, ImageProcessingServiceInterface
from app.services.persistence.interface import ImagePersistenceServiceInterface
from app.core.exceptions import ImageStorageError
from app.utils.security.mask import mask_id
from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)


class ImageError(Exception):
    """Base exception for image service errors."""
    pass


class ImageService(ImageServiceInterface):
    """
    Service for processing and manipulating images.
    
    This service provides operations for processing, converting,
    and transforming image data.
    """
    
    def __init__(
        self, 
        persistence_service: ImagePersistenceServiceInterface,
        processing_service: ImageProcessingServiceInterface
    ):
        """
        Initialize the image service.
        
        Args:
            persistence_service: Service for image persistence operations
            processing_service: Service for image processing operations
        """
        self.persistence = persistence_service
        self.processing = processing_service
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
            ImageError: If processing fails
        """
        try:
            return await self.processing.process_image(image_data, operations)
        except Exception as e:
            error_msg = f"Error processing image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg)
            
    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> Tuple[str, str]:
        """
        Store an image and return its path and signed URL.
        
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
            # Use the persistence service to store the image
            return self.persistence.store_image(
                image_data=image_data,
                user_id=user_id,
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
            # Convert relative signed URLs to full URLs if needed
            if image_url_or_path.startswith("/object/sign/"):
                full_url = f"{settings.SUPABASE_URL}{image_url_or_path}"
                self.logger.info(f"Converting relative signed URL to full URL: {full_url}")
                image_url_or_path = full_url
            
            # Check if it's an external URL or a storage path
            if image_url_or_path.startswith(("http://", "https://")):
                # It's an external URL, fetch it
                async_fetch = False
                try:
                    response = httpx.get(image_url_or_path)
                    if response.status_code != 200:
                        raise ImageError(f"Failed to fetch image from URL: {response.status_code}")
                    return response.content
                except Exception as e:
                    if "Running in async context" in str(e):
                        # Need to use async client
                        async_fetch = True
                    else:
                        # Re-raise if it's not an async context error
                        raise
                
                if async_fetch:
                    # This will be executed inside an async function
                    # We need to use AsyncClient but can't await here
                    # Return a placeholder or throw an informative error
                    raise ImageError("Unable to fetch image URL in synchronous context. Use async method.")
            
            # Check if it's a signed URL from our Supabase storage
            elif '/object/sign/' in image_url_or_path:
                # Extract the real path from signed URL
                path_parts = image_url_or_path.split('/object/sign/')
                if len(path_parts) > 1:
                    bucket_path = path_parts[1].split('?')[0]  # Remove query params
                    bucket_parts = bucket_path.split('/', 1)
                    if len(bucket_parts) > 1:
                        bucket_name = bucket_parts[0]
                        path = bucket_parts[1]
                        
                        # Determine if it's a palette image
                        is_palette = bucket_name == settings.STORAGE_BUCKET_PALETTE
                        
                        self.logger.info(f"Extracted path from signed URL: {path}")
                        # Use persistence service directly with the path
                        return self.persistence.get_image(path, is_palette=is_palette)
                
                # If we can't extract a path or it doesn't match expected format,
                # try to use the URL directly
                response = httpx.get(image_url_or_path)
                if response.status_code != 200:
                    raise ImageError(f"Failed to fetch image from signed URL: {response.status_code}")
                return response.content
            
            # Otherwise it's a storage path
            else:
                return self.persistence.get_image(image_url_or_path, is_palette=is_palette)
                
        except Exception as e:
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
            return self.processing.convert_to_format(
                image_data=image_data,
                target_format=target_format,
                quality=quality
            )
        except Exception as e:
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
            return self.processing.generate_thumbnail(
                image_data=image_data,
                width=width,
                height=height,
                format=format,
                preserve_aspect_ratio=preserve_aspect_ratio
            )
        except Exception as e:
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
            return await self.processing.extract_color_palette(image_data, num_colors)
        except Exception as e:
            error_msg = f"Failed to extract color palette: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg)
    
    async def create_palette_variations(
        self, 
        base_image_data: bytes, 
        palettes: List[Dict[str, Any]], 
        user_id: str,
        blend_strength: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Create variations of an image with different color palettes.
        
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
            self.logger.info(f"Creating {len(palettes)} palette variations for user: {masked_user_id}")
            
            # Preprocess the base image to ensure it's valid
            try:
                img = PILImage.open(BytesIO(base_image_data))
                if img.mode != "RGB":
                    img = img.convert("RGB")
                
                # Re-encode to ensure we have valid image data
                buffer = BytesIO()
                img.save(buffer, format="PNG")
                validated_image_data = buffer.getvalue()
                self.logger.info(f"Successfully validated base image for processing, size: {len(validated_image_data)} bytes")
                
            except Exception as e:
                self.logger.error(f"Error validating base image: {str(e)}")
                validated_image_data = base_image_data  # Fall back to original data
            
            # Prepare the metadata prefix with timestamp for unique filenames
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            
            # Process each palette
            for idx, palette in enumerate(palettes):
                try:
                    # Extract palette data
                    palette_name = palette.get("name", f"Palette {idx+1}")
                    palette_colors = palette.get("colors", [])
                    palette_description = palette.get("description", "")
                    
                    if not palette_colors:
                        self.logger.warning(f"Empty color palette: {palette_name}, skipping")
                        continue
                    
                    # Apply the palette to the base image using the processing service
                    colorized_image = await self.processing.process_image(
                        validated_image_data,
                        operations=[{
                            "type": "apply_palette",
                            "colors": palette_colors,
                            "blend_strength": blend_strength
                        }]
                    )
                    
                    if not colorized_image:
                        self.logger.error(f"Failed to apply palette: {palette_name}")
                        continue
                        
                    # Generate a unique filename
                    unique_id = str(uuid.uuid4())
                    filename = f"palette_{timestamp}_{unique_id}.png"
                    
                    # Store with metadata
                    metadata = {
                        "palette_name": palette_name,
                        "description": palette_description,
                        "colors": json.dumps(palette_colors)
                    }
                    
                    palette_path, palette_url = self.persistence.store_image(
                        image_data=colorized_image,
                        user_id=user_id,
                        file_name=filename,
                        metadata=metadata,
                        is_palette=True
                    )
                    
                    if not palette_path or not palette_url:
                        self.logger.error(f"Failed to store palette variation: {palette_name}")
                        continue
                        
                    # Add to result
                    result_palettes.append({
                        "name": palette_name,
                        "colors": palette_colors,
                        "description": palette_description,
                        "image_path": palette_path,
                        "image_url": palette_url
                    })
            
                except Exception as e:
                    self.logger.error(f"Error processing palette {palette_name}: {str(e)}")
                    # Continue with other palettes
            
            self.logger.info(f"Successfully created {len(result_palettes)} palette variations")
            return result_palettes
            
        except Exception as e:
            self.logger.error(f"Error in create_palette_variations: {str(e)}")
            raise ImageError(f"Error creating palette variations: {str(e)}")
            
    async def apply_palette_to_image(
        self, 
        image_data: bytes,
        palette_colors: list, 
        blend_strength: float = 0.75
    ) -> bytes:
        """
        Apply a color palette to an image.
        
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
                operations=[{
                    "type": "apply_palette",
                "colors": palette_colors,
                    "blend_strength": blend_strength
                }]
            )
        except Exception as e:
            self.logger.error(f"Error applying palette to image: {str(e)}")
            raise ImageError(f"Failed to apply palette to image: {str(e)}")

    def get_image_url(self, image_path: str, is_palette: bool = False) -> str:
        """
        Get a signed URL for an image in storage.
        
        Args:
            image_path: Path to the image in storage
            is_palette: Whether this is a palette image
            
        Returns:
            Signed URL for the image
            
        Raises:
            ImageError: If URL generation fails
        """
        try:
            # Use the persistence service to get the signed URL
            return self.persistence.get_signed_url(image_path, is_palette=is_palette)
            
        except Exception as e:
            self.logger.error(f"Error getting signed image URL: {str(e)}")
            raise ImageError(f"Failed to get signed image URL: {str(e)}")

    async def generate_and_store_image(
        self,
        prompt: str, 
        user_id: str,
        concept_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Generate an image using an external API and store it.
        
        This method is a placeholder since we've refactored the architecture to move image 
        generation responsibilities to the ConceptService. This implementation simply throws 
        an appropriate error message to guide developers to use the correct service.
        
        Args:
            prompt: Text prompt for image generation
            user_id: User ID for storage
            concept_id: Optional concept ID for association
            metadata: Optional metadata to store with the image
            
        Returns:
            Tuple of (image_path, image_url)
            
        Raises:
            ImageError: Always raises this error since this method should not be called directly
        """
        error_msg = (
            "The ImageService no longer handles image generation. "
            "Please use ConceptService.generate_concept instead."
        )
        self.logger.error(error_msg)
        raise ImageError(error_msg)
        
    async def refine_and_store_image(
        self, 
        original_image_path: str, 
        refinement_prompt: str,
        user_id: str,
        concept_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[str, str]:
        """
        Refine an existing image using an external API and store the result.
        
        This method is a placeholder since we've refactored the architecture to move image 
        refinement responsibilities to the ConceptService. This implementation simply throws 
        an appropriate error message to guide developers to use the correct service.
        
        Args:
            original_image_path: Path of the original image to refine
            refinement_prompt: Text instructions for refinement
            user_id: User ID for storage
            concept_id: Optional concept ID for association
            metadata: Optional metadata to store with the image
            
        Returns:
            Tuple of (image_path, image_url)
            
        Raises:
            ImageError: Always raises this error since this method should not be called directly
        """
        error_msg = (
            "The ImageService no longer handles image refinement. "
            "Please use ConceptService.refine_concept instead."
        )
        self.logger.error(error_msg)
        raise ImageError(error_msg)

    # Cache for storing recently downloaded images to avoid repeated downloads
    _image_cache = {}
    _cache_size_limit = 20  # Maximum number of images to keep in cache

    async def get_image_async(self, image_url_or_path: str) -> bytes:
        """
        Asynchronously get image data from a URL or path.
        
        Args:
            image_url_or_path: URL or storage path of the image
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageError: If retrieval fails
        """
        # Check cache first
        if image_url_or_path in self._image_cache:
            self.logger.debug(f"Cache hit for {image_url_or_path}")
            return self._image_cache[image_url_or_path]
            
        try:
            # Handle URLs
            if image_url_or_path.startswith(("http://", "https://")):
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url_or_path)
                    if response.status_code != 200:
                        raise ImageError(f"Failed to fetch image from URL: {response.status_code}")
                    
                    # Add to cache
                    image_data = response.content
                    if len(self._image_cache) >= self._cache_size_limit:
                        # Remove oldest item if cache is full
                        self._image_cache.pop(next(iter(self._image_cache)))
                    self._image_cache[image_url_or_path] = image_data
                    
                    return image_data
            # Handle storage paths
            else:
                # For now, we don't have an async version of the persistence.get_image method
                # So we'll just call the synchronous version
                image_data = self.persistence.get_image(image_url_or_path)
                
                # Add to cache
                if len(self._image_cache) >= self._cache_size_limit:
                    # Remove oldest item if cache is full
                    self._image_cache.pop(next(iter(self._image_cache)))
                self._image_cache[image_url_or_path] = image_data
                
                return image_data
        except Exception as e:
            error_msg = f"Failed to get image asynchronously: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg) 