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
from app.core.config import settings

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
        session_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> Tuple[str, str]:
        """
        Store an image and return its path and signed URL.
        
        Args:
            image_data: Image data as bytes, BytesIO, or UploadFile
            session_id: Session ID for access control
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
            # Use the storage service to store the image
            return self.storage.store_image(
                image_data=image_data,
                session_id=session_id,
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
                        # Use storage service directly with the path
                        return self.storage.get_image(path, is_palette=is_palette)
                
                # If we can't extract a path or it doesn't match expected format,
                # try to use the URL directly
                response = httpx.get(image_url_or_path)
                if response.status_code != 200:
                    raise ImageError(f"Failed to fetch image from signed URL: {response.status_code}")
                return response.content
            
            # Otherwise it's a storage path
            else:
                return self.storage.get_image(image_url_or_path, is_palette=is_palette)
                
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
        session_id: str,
        concept_id: Optional[str] = None,
        width: int = 512,
        height: int = 512,
        store: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> Tuple[str, str]:
        """
        Generate an image from a prompt and optionally store it.
        
        Args:
            prompt: Text prompt for image generation
            session_id: Session ID for access control
            concept_id: Optional concept ID to associate with the image
            width: Image width
            height: Image height
            store: Whether to store the image
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image
            
        Returns:
            Tuple of (image_path, image_url)
            
        Raises:
            ImageGenerationError: If generation fails
            ImageError: If storage fails
        """
        try:
            # Mask sensitive data in logs
            masked_session_id = mask_id(session_id)
            masked_concept_id = mask_id(concept_id) if concept_id else None
            
            self.logger.info(
                f"Generating image for session={masked_session_id}, "
                f"concept={masked_concept_id}, size={width}x{height}, "
                f"prompt_length={len(prompt) if prompt else 0}"
            )
            
            # Generate image
            response = await self.jigsawstack.generate_image(
                prompt=prompt,
                width=width,
                height=height
            )
            
            # Check if we received valid image data
            if not response:
                raise ImageGenerationError("No response received from generation API")
                
            # The JigsawStack client returns binary data in 'binary_data' field
            image_data = None
            if response.get("binary_data"):
                image_data = response["binary_data"]
            elif response.get("image_data"):
                image_data = response["image_data"]
            elif response.get("url") and response["url"].startswith("http"):
                # We got a URL, try to download the image
                self.logger.info(f"Downloading image from URL: {response['url']}")
                try:
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        img_response = await client.get(response["url"])
                        if img_response.status_code == 200:
                            image_data = img_response.content
                except Exception as e:
                    self.logger.error(f"Failed to download image from URL: {str(e)}")
            
            if not image_data:
                raise ImageGenerationError("No image data received from generation API")
            
            # Store the image if requested
            image_path = None
            image_url = None
            
            if store and image_data:
                # Get timestamp for unique filename
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                
                # Create a descriptive filename
                if is_palette:
                    file_name = f"palette_{timestamp}.png"
                else:
                    file_name = f"concept_{timestamp}.png"
                
                # Create metadata including the prompt
                storage_metadata = {
                    "prompt": prompt[:255] if prompt else "",  # Truncate long prompts
                    "width": width,
                    "height": height,
                    "generated_at": timestamp
                }
                
                # Add any custom metadata
                if metadata:
                    storage_metadata.update(metadata)
                
                # Store the image and get the path and URL
                image_path, image_url = self.store_image(
                    image_data=image_data,
                    session_id=session_id,
                    concept_id=concept_id,
                    file_name=file_name,
                    metadata=storage_metadata,
                    is_palette=is_palette
                )
                
                self.logger.info(
                    f"Stored generated image: path={mask_path(image_path)}, "
                    f"url={mask_path(image_url) if image_url else 'None'}"
                )
            
            return image_path, image_url
            
        except Exception as e:
            error_msg = f"Failed to generate or store image: {str(e)}"
            self.logger.error(error_msg)
            
            if "generation" in str(e).lower():
                raise ImageGenerationError(error_msg)
            else:
                raise ImageError(error_msg)
                
    async def apply_color_palette(
        self, 
        base_image_path: Union[str, Tuple[str, str]], 
        palette_colors: List[str], 
        session_id: str,
        blend_strength: float = 0.75
    ) -> Tuple[str, str]:
        """
        Apply a color palette to an image and store the result.
        
        Args:
            base_image_path: Path to the base image in storage, full URL, or tuple of (url, path)
            palette_colors: List of hex color codes
            session_id: Session ID for access control
            blend_strength: Strength of the palette application (0-1)
            
        Returns:
            Tuple[str, str]: (image_path, image_url) - The storage path and signed URL
            
        Raises:
            ImageError: If processing or storage fails
        """
        try:
            self.logger.info(f"Applying color palette to image: {base_image_path}")
            
            # Check if this is a newly stored image with path in generate_and_store_image
            # Get the relative path section that might be used for direct access
            stored_image_path = None
            
            # Check for the image path returned with the URL from generate_and_store_image
            if isinstance(base_image_path, tuple) and len(base_image_path) == 2:
                self.logger.info("Image provided as (url, path) tuple, using path for direct access")
                url, stored_path = base_image_path
                base_image_path = url  # Use the URL for the rest of the function
                stored_image_path = stored_path  # Keep the path for direct access
            
            # Extract actual path from URL if needed
            is_signed_url = False
            actual_path = None
            base_url = None
            
            # Check if it's a full URL with domain
            if isinstance(base_image_path, str) and base_image_path.startswith(("http://", "https://")):
                is_signed_url = '/object/sign/' in base_image_path
                base_url = base_image_path
            # Check if it's a relative URL starting with /object/sign/
            elif isinstance(base_image_path, str) and base_image_path.startswith("/object/sign/"):
                is_signed_url = True
                # Convert to full URL
                base_url = f"{settings.SUPABASE_URL}{base_image_path}"
                self.logger.info(f"Converting relative URL to full URL: {base_url}")
            
            if is_signed_url:
                # Extract the real path from signed URL
                path_parts = base_image_path.split('/object/sign/')
                if len(path_parts) > 1:
                    bucket_path = path_parts[1].split('?')[0]  # Remove query params
                    bucket_parts = bucket_path.split('/', 1)
                    if len(bucket_parts) > 1:
                        # Skip storing bucket_name since we don't use it here
                        # Just get the path without bucket
                        actual_path = bucket_parts[1]
                        self.logger.info(f"Extracted path from signed URL: {actual_path}")
            
            # Get the base image - try multiple methods in order of reliability
            try:
                # ATTEMPT 1: If we have the stored path directly from generate_and_store_image,
                # use it for the most reliable access
                if stored_image_path:
                    self.logger.info(f"Using direct storage path: {stored_image_path}")
                    try:
                        # Use the new method for direct access via admin API
                        base_image_data = self.storage.get_image_by_path(stored_image_path, is_palette=False)
                        self.logger.info("Successfully retrieved image using direct path")
                    except Exception as e:
                        self.logger.warning(f"Failed to get image by direct path, will try alternatives: {str(e)}")
                        raise e  # Re-raise to try next method
                
                # ATTEMPT 2: If we have a valid path from the signed URL, try direct access
                elif actual_path:
                    # Ensure path includes session_id
                    path_parts = actual_path.split('/')
                    if len(path_parts) > 0 and path_parts[0] != session_id:
                        # Add session_id prefix if missing
                        path_with_session = f"{session_id}/{actual_path}"
                    else:
                        path_with_session = actual_path
                        
                    self.logger.info(f"Trying direct storage access with path: {path_with_session}")
                    try:
                        # Try direct access with admin privileges
                        base_image_data = self.storage.get_image_by_path(path_with_session, is_palette=False)
                        self.logger.info("Successfully retrieved image using extracted path")
                    except Exception as e:
                        self.logger.warning(f"Failed with direct path access, will try HTTP: {str(e)}")
                        raise e  # Re-raise to try next method
                
                # ATTEMPT 3: For signed URLs, try direct HTTP request
                elif is_signed_url and base_url:
                    self.logger.info(f"Attempting to fetch image via HTTP from signed URL: {base_url}")
                    try:
                        # Use the async method to fetch the image
                        base_image_data = await self.get_image_async(base_url)
                        self.logger.info("Successfully retrieved image from signed URL via HTTP")
                    except Exception as e:
                        self.logger.warning(f"Failed to fetch from signed URL via HTTP: {str(e)}")
                        raise e  # Re-raise to try other methods
                
                # ATTEMPT 4: For non-signed URLs or simple paths
                else:
                    # Try the async method first if it looks like a URL
                    if isinstance(base_image_path, str) and base_image_path.startswith(("http://", "https://")):
                        self.logger.info(f"Attempting to fetch from URL: {base_image_path}")
                        base_image_data = await self.get_image_async(base_image_path)
                    else:
                        # Must be a simple path
                        full_path = base_image_path
                        if isinstance(full_path, str) and not full_path.startswith(session_id):
                            full_path = f"{session_id}/{full_path}"
                        self.logger.info(f"Retrieving using standard storage access: {full_path}")
                        base_image_data = self.storage.get_image(full_path)
            
            except Exception as e:
                # All attempts failed
                error_msg = f"All methods failed to retrieve image: {str(e)}"
                self.logger.error(error_msg)
                raise ImageError(error_msg)
            
            # Apply the palette
            try:
                # Ensure the image data is valid before processing
                if base_image_data is None:
                    raise ImageError("Image data is None, cannot apply palette")
                
                # Debug the image data
                self.logger.info(f"Image data type: {type(base_image_data)}, size: {len(base_image_data) if hasattr(base_image_data, '__len__') else 'unknown'}")
                
                # Ensure we have valid image data by opening and re-encoding with PIL
                try:
                    from PIL import Image
                    from io import BytesIO
                    
                    # Try to open the image to validate it
                    img = Image.open(BytesIO(base_image_data))
                    # Convert to RGB if it's not already
                    if img.mode != "RGB":
                        img = img.convert("RGB")
                    
                    # Re-encode to ensure we have valid image data
                    buffer = BytesIO()
                    img.save(buffer, format="PNG")
                    validated_image_data = buffer.getvalue()
                    
                    self.logger.info(f"Successfully validated and converted image, size: {len(validated_image_data)}")
                    
                    # Now pass the validated image data to the palette function
                    adjusted_image = apply_palette_with_masking_optimized(
                        validated_image_data,
                        palette_colors=palette_colors,
                        blend_strength=blend_strength
                    )
                except Exception as e:
                    self.logger.error(f"Error validating image data: {str(e)}")
                    # Try with the original data
                    adjusted_image = apply_palette_with_masking_optimized(
                        base_image_data,
                        palette_colors=palette_colors,
                        blend_strength=blend_strength
                    )
            except Exception as e:
                raise ImageError(f"Failed to apply palette: {str(e)}")
            
            # Generate a unique file name
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = f"adjusted_{timestamp}.png"
            
            # Extract concept_id from base_image_path if available
            # Path format is session_id/concept_id/filename or session_id/filename
            # Use the extracted path to get parts
            path_for_concept = actual_path or stored_image_path or (base_image_path if isinstance(base_image_path, str) else "")
            path_parts = path_for_concept.split('/')
            concept_id = None
            if len(path_parts) >= 3:
                # Format is session_id/concept_id/filename
                concept_id = path_parts[1]
            
            # Store the adjusted image in the palette-images bucket
            self.logger.info(f"Storing palette-adjusted image for session={mask_id(session_id)}, concept={mask_id(concept_id) if concept_id else None}")
            # Flag to indicate this is a palette image
            palette_image_path, palette_image_url = self.store_image(
                image_data=adjusted_image,
                session_id=session_id,
                concept_id=concept_id,
                file_name=file_name,
                metadata={
                    "base_image": str(base_image_path)[:255] if isinstance(base_image_path, str) else "tuple",
                    "palette_colors": ",".join(palette_colors),
                    "blend_strength": blend_strength,
                    "operation": "palette_adjustment"
                },
                is_palette=True
            )
            
            self.logger.info(f"Stored adjusted image at path: {palette_image_path}")
            
            return palette_image_path, palette_image_url
            
        except Exception as e:
            error_msg = f"Failed to apply color palette: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg)

    def get_image_url(self, image_path: str, bucket_name: str) -> str:
        """
        Get a signed URL for an image in storage.
        
        Args:
            image_path: Path to the image in storage
            bucket_name: Name of the bucket (e.g., "concept-images" or "palette-images")
            
        Returns:
            Signed URL for the image with 3-day expiration
            
        Raises:
            ImageError: If URL generation fails
        """
        try:
            # Determine if this is a palette image based on the bucket name
            # Compare with settings values instead of hardcoded strings
            is_palette = bucket_name == settings.STORAGE_BUCKET_PALETTE
            
            # Use the storage service to get the signed URL
            return self.storage.get_signed_url(image_path, is_palette=is_palette)
            
        except Exception as e:
            self.logger.error(f"Error getting signed image URL: {str(e)}")
            raise ImageError(f"Failed to get signed image URL: {str(e)}")

    def get_image_with_token(
        self,
        path: str,
        token: str,
        is_palette: bool = False
    ) -> bytes:
        """
        Get image data using a JWT token for authentication.
        
        Args:
            path: Path to the image in storage
            token: JWT token for authentication
            is_palette: Whether this is a palette image
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageError: If retrieval fails
        """
        try:
            return self.storage.get_image_with_token(
                path=path,
                token=token,
                is_palette=is_palette
            )
        except (ImageStorageError, ImageNotFoundError) as e:
            # Re-raise as ImageError
            raise ImageError(f"Failed to get image with token: {str(e)}")

    async def get_image_async(self, image_url_or_path: str, is_palette: bool = False) -> bytes:
        """
        Asynchronously retrieve an image by URL or storage path.
        
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
                # It's an external URL, fetch it asynchronously
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url_or_path)
                    if response.status_code != 200:
                        raise ImageError(f"Failed to fetch image from URL: {response.status_code}")
                    return response.content
            
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
                        # Use storage service directly with the path
                        return self.storage.get_image(path, is_palette=is_palette)
                
                # If we can't extract a path or it doesn't match expected format,
                # try to use the URL directly
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url_or_path)
                    if response.status_code != 200:
                        raise ImageError(f"Failed to fetch image from signed URL: {response.status_code}")
                    return response.content
            
            # Otherwise it's a storage path
            else:
                return self.storage.get_image(image_url_or_path, is_palette=is_palette)
                
        except Exception as e:
            error_msg = f"Failed to get image asynchronously {image_url_or_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg) 