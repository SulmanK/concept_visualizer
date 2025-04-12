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
import uuid

from fastapi import UploadFile
from supabase import Client
from PIL import Image as PILImage

from app.services.interfaces import ImageServiceInterface
from app.services.interfaces.image_service import ImageProcessingServiceInterface
from app.services.image.storage import ImageStorageService, ImageStorageError, ImageNotFoundError
from app.services.image.processing_service import ImageProcessingError
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
        storage_service: ImageStorageService,
        processing_service: ImageProcessingServiceInterface
    ):
        """
        Initialize the image service.
        
        Args:
            jigsawstack_client: Client for JigsawStack API
            supabase_client: Supabase client
            storage_service: Service for image storage operations
            processing_service: Service for image processing operations
        """
        self.jigsawstack = jigsawstack_client
        self.supabase = supabase_client
        self.storage = storage_service
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
            ImageProcessingError: If processing fails
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
            # Use the storage service to store the image
            return self.storage.store_image(
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
        
    async def generate_and_store_image(self, prompt: str, user_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate an image based on a prompt and store it in Supabase.
        
        Args:
            prompt: Image generation prompt
            user_id: Current user ID
            
        Returns:
            Tuple of (storage_path, signed_url) or (None, None) on error
            
        Raises:
            ImageProcessingError: If image generation fails
            StorageError: If storing the image fails
        """
        try:
            # Log the image generation request
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Generating image with prompt: {prompt}")
            
            # Generate the image
            response = await self.jigsawstack.generate_image(prompt=prompt)
            
            # Check if we received image data directly or need to download it
            image_data = None
            if "binary_data" in response:
                image_data = response["binary_data"]
            elif "url" in response:
                # Download the image from the URL
                self.logger.info(f"Downloading image from URL: {response['url']}")
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(response["url"])
                    if img_response.status_code == 200:
                        image_data = img_response.content
                    else:
                        raise ImageProcessingError(f"Failed to download image: HTTP {img_response.status_code}")
            
            if not image_data:
                self.logger.error("Failed to generate image: No binary data returned")
                raise ImageProcessingError("Failed to generate image: No binary data returned")
            
            self.logger.info(f"Image generated successfully. Binary data received: {len(image_data)} bytes")
            
            # Determine image format
            img = PILImage.open(BytesIO(image_data))
            format_ext = img.format.lower() if img.format else "png"
            
            # Generate a unique filename
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.{format_ext}"
            
            # Store the image
            try:
                storage_path, signed_url = self.storage.store_image(
                    image_data=image_data,
                    user_id=user_id,
                    file_name=filename,
                    metadata={"prompt": prompt}
                )
                
                if not storage_path or not signed_url:
                    self.logger.error("Failed to store generated image")
                    raise ImageProcessingError("Failed to store generated image")
                
                self.logger.info(f"Image stored successfully: {mask_path(storage_path)}")
                return storage_path, signed_url
                
            except ImageStorageError as e:
                self.logger.error(f"Failed to store image: {str(e)}")
                raise ImageProcessingError(f"Failed to store image: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error in generate_and_store_image: {str(e)}")
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(f"Error generating and storing image: {str(e)}")
    
    async def refine_and_store_image(
        self, 
        prompt: str, 
        original_image_url: str, 
        user_id: str,
        strength: float = 0.7
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Refine an image based on a prompt and store the result in Supabase.
        
        Args:
            prompt: Refinement prompt
            original_image_url: URL of the original image
            user_id: Current user ID
            strength: How much to change the original (0.0-1.0)
            
        Returns:
            Tuple of (storage_path, signed_url) or (None, None) on error
            
        Raises:
            ImageProcessingError: If image refinement fails
            StorageError: If storing the image fails
        """
        try:
            # Log the refinement request
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Refining image with prompt: {prompt}")
            
            # Refine the image
            response = await self.jigsawstack.refine_image(
                prompt=prompt,
                image_url=original_image_url,
                strength=strength
            )
            
            # Check if we received image data directly or need to download it
            image_data = None
            if isinstance(response, bytes):
                # The refine_image method might directly return bytes
                image_data = response
            elif isinstance(response, dict):
                if "binary_data" in response:
                    image_data = response["binary_data"]
                elif "url" in response:
                    # Download the image from the URL
                    self.logger.info(f"Downloading refined image from URL: {response['url']}")
                    async with httpx.AsyncClient() as client:
                        img_response = await client.get(response["url"])
                        if img_response.status_code == 200:
                            image_data = img_response.content
                        else:
                            raise ImageProcessingError(f"Failed to download refined image: HTTP {img_response.status_code}")
            
            if not image_data:
                self.logger.error("Failed to refine image: No binary data returned")
                raise ImageProcessingError("Failed to refine image: No binary data returned")
            
            self.logger.info(f"Image refined successfully. Binary data received: {len(image_data)} bytes")
            
            # Determine image format
            img = PILImage.open(BytesIO(image_data))
            format_ext = img.format.lower() if img.format else "png"
            
            # Generate a unique filename
            unique_id = str(uuid.uuid4())
            filename = f"{unique_id}.{format_ext}"
            
            # Store the refined image
            try:
                storage_path, signed_url = self.storage.store_image(
                    image_data=image_data,
                    user_id=user_id,
                    file_name=filename,
                    metadata={"prompt": prompt, "refinement": True}
                )
                
                if not storage_path or not signed_url:
                    self.logger.error("Failed to store refined image")
                    raise ImageProcessingError("Failed to store refined image")
                
                self.logger.info(f"Refined image stored successfully: {mask_path(storage_path)}")
                return storage_path, signed_url
                
            except ImageStorageError as e:
                self.logger.error(f"Failed to store refined image: {str(e)}")
                raise ImageProcessingError(f"Failed to store refined image: {str(e)}")
            
        except Exception as e:
            self.logger.error(f"Error in refine_and_store_image: {str(e)}")
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(f"Error refining and storing image: {str(e)}")
    
    async def create_palette_variations(
        self, 
        base_image_path: str, 
        palettes: List[Dict[str, Any]], 
        user_id: str,
        blend_strength: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Create variations of an image with different color palettes.
        
        Args:
            base_image_path: Storage path of the base image
            palettes: List of color palette dictionaries
            user_id: Current user ID
            blend_strength: How strongly to apply the new colors (0.0-1.0)
            
        Returns:
            List of palettes with added image_path and image_url fields
            
        Raises:
            ImageProcessingError: If applying palettes fails
            StorageError: If storing the variations fails
        """
        result_palettes = []
        masked_user_id = mask_id(user_id)
        masked_base_path = mask_path(base_image_path)
        
        try:
            # Get the base image once and reuse it for all palettes
            self.logger.info(f"Creating {len(palettes)} palette variations for user: {masked_user_id}")
            
            # Get the base image directly using service role key for maximum reliability
            # This avoids issues with signed URLs and permissions
            try:
                # First try direct download using service role
                bucket_name = settings.STORAGE_BUCKET_CONCEPT
                base_image_data = await self.download_with_service_role(bucket_name, base_image_path)
                self.logger.info(f"Successfully downloaded base image with service role: {len(base_image_data)} bytes")
            except Exception as e:
                self.logger.warning(f"Service role download failed: {str(e)}, trying fallback method")
                
                # Fall back to getting a signed URL and downloading it
                base_image_url = self.get_image_url(base_image_path, "concept-images")
                if not base_image_url:
                    self.logger.error(f"Failed to get URL for base image: {masked_base_path}")
                    raise ImageProcessingError("Failed to get URL for base image")
                    
                # Download the base image from the URL
                base_image_data = await self.get_image_async(base_image_url)
                if not base_image_data:
                    self.logger.error("Failed to download base image")
                    raise ImageProcessingError("Failed to download base image")
            
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
                        "colors": json.dumps(palette_colors),
                        "base_image_path": base_image_path
                    }
                    
                    palette_path, palette_url = self.storage.store_image(
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
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(f"Error creating palette variations: {str(e)}")
            
    async def apply_color_palette(
        self, 
        base_image: tuple,
        palette_colors: list, 
        user_id: str,
        blend_strength: float = 0.75
    ) -> tuple:
        """
        Apply a color palette to an image and store the result.
        
        Args:
            base_image: Tuple of (image_url, image_path)
            palette_colors: List of hex color codes
            user_id: User ID for access control
            blend_strength: Strength of the palette application (0-1)
            
        Returns:
            Tuple[str, str]: (image_path, image_url) - The storage path and signed URL
            
        Raises:
            ImageError: If processing or storage fails
        """
        try:
            # Create a palette dictionary with the required format
            palette = {
                "name": "Custom Palette",
                "colors": palette_colors,
                "description": "Custom color palette"
            }
            
            # Use the image_path from the tuple
            image_url, image_path = base_image
            
            # Create a list with just one palette
            palettes = [palette]
            
            # Use the create_palette_variations method which already handles downloading the image
            result_palettes = await self.create_palette_variations(
                image_path,
                palettes,
                user_id,
                blend_strength
            )
            
            # Return the first (and only) result
            if result_palettes and len(result_palettes) > 0:
                return (
                    result_palettes[0]["image_path"],
                    result_palettes[0]["image_url"]
                )
            else:
                raise ImageProcessingError("Failed to apply color palette")
                
        except Exception as e:
            self.logger.error(f"Error in apply_color_palette: {str(e)}")
            if isinstance(e, ImageProcessingError):
                raise
            raise ImageProcessingError(f"Error applying color palette: {str(e)}")

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

    # Cache for storing recently downloaded images to avoid repeated downloads
    _image_cache = {}
    _cache_size_limit = 20  # Maximum number of images to keep in cache

    async def get_image_async(self, image_url_or_path: str, is_palette: bool = False) -> bytes:
        """
        Asynchronously retrieve an image by URL or storage path with caching.
        
        Args:
            image_url_or_path: URL or storage path of the image
            is_palette: Whether this is a palette image
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageError: If retrieval fails
        """
        # Check the cache first
        cache_key = f"{image_url_or_path}:{is_palette}"
        if cache_key in self._image_cache:
            self.logger.debug(f"Using cached image data for: {mask_path(image_url_or_path)}")
            return self._image_cache[cache_key]
            
        try:
            # Convert relative signed URLs to full URLs if needed
            if image_url_or_path.startswith("/object/sign/") or image_url_or_path.startswith("/storage/v1/object/"):
                image_url_or_path = f"{settings.SUPABASE_URL}{image_url_or_path}"
                self.logger.info(f"Converted relative URL to full URL: {mask_path(image_url_or_path)}")
            
            # Extract token from URL if present (for authenticated endpoints)
            token = None
            if "?token=" in image_url_or_path:
                url_parts = image_url_or_path.split("?token=", 1)
                if len(url_parts) > 1:
                    image_url_or_path = url_parts[0]
                    token = url_parts[1].split("&")[0]  # Extract just the token
                    self.logger.info(f"Extracted token from URL (length: {len(token) if token else 0})")
            
            # Check if it's an external URL or a storage path
            if image_url_or_path.startswith(("http://", "https://")):
                # It's an external URL, fetch it asynchronously with a timeout
                headers = {}
                if token:
                    headers["Authorization"] = f"Bearer {token}"
                
                self.logger.info(f"Fetching image from URL: {mask_path(image_url_or_path)}")
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.get(
                        image_url_or_path, 
                        follow_redirects=True,
                        headers=headers
                    )
                    
                    if response.status_code != 200:
                        # If there was a 404 or 403, try alternative authentication approach
                        if response.status_code in (404, 403, 401) and '/storage/v1/object/' in image_url_or_path:
                            self.logger.warning(f"Access denied ({response.status_code}), trying service role key")
                            
                            # Try to parse the path from the URL
                            try:
                                # Extract path elements from URL
                                url_parts = image_url_or_path.split('/storage/v1/object/')
                                if len(url_parts) > 1:
                                    path_parts = url_parts[1].split('/', 1)
                                    if len(path_parts) > 1:
                                        bucket = path_parts[0]
                                        path = path_parts[1]
                                        self.logger.info(f"Extracted bucket={bucket}, path={mask_path(path)}")
                                        
                                        # Use service role key
                                        service_role_key = settings.SUPABASE_SERVICE_ROLE
                                        if service_role_key:
                                            download_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket}/{path}"
                                            self.logger.info(f"Attempting to download with service role key: {mask_path(download_url)}")
                                            
                                            async with httpx.AsyncClient(timeout=30.0) as service_client:
                                                service_response = await service_client.get(
                                                    download_url,
                                                    headers={
                                                        "Authorization": f"Bearer {service_role_key}",
                                                        "apikey": service_role_key
                                                    },
                                                    follow_redirects=True
                                                )
                                                
                                                if service_response.status_code == 200:
                                                    self.logger.info("Successfully downloaded with service role key")
                                                    image_data = service_response.content
                                                    
                                                    # Cache the successful result
                                                    if len(self._image_cache) >= self._cache_size_limit:
                                                        # Remove oldest entry if cache is full
                                                        oldest_key = next(iter(self._image_cache))
                                                        del self._image_cache[oldest_key]
                                                    self._image_cache[cache_key] = image_data
                                                    return image_data
                                                else:
                                                    self.logger.warning(f"Service role download failed: {service_response.status_code}")
                            except Exception as path_e:
                                self.logger.warning(f"Failed to parse path from URL: {str(path_e)}")
                        
                        raise ImageError(f"Failed to fetch image from URL: {response.status_code}")
                    
                    image_data = response.content
                    self.logger.info(f"Successfully downloaded image: {len(image_data)} bytes")
            
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
                        
                        self.logger.info(f"Extracted path from signed URL: {mask_path(path)}")
                        # Use storage service directly with the path
                        try:
                            image_data = self.storage.get_image(path, is_palette=is_palette)
                            self.logger.info(f"Successfully retrieved image via storage service")
                        except Exception as storage_e:
                            # If storage service fails, try with service role key
                            self.logger.warning(f"Storage service failed: {str(storage_e)}, trying service role key")
                            
                            service_role_key = settings.SUPABASE_SERVICE_ROLE
                            if service_role_key:
                                try:
                                    # Prepare direct download URL
                                    download_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket_name}/{path}"
                                    
                                    # Use sync request here as we're in an async method already
                                    headers = {
                                        "Authorization": f"Bearer {service_role_key}",
                                        "apikey": service_role_key
                                    }
                                    
                                    async with httpx.AsyncClient(timeout=30.0) as client:
                                        response = await client.get(download_url, headers=headers)
                                        
                                        if response.status_code == 200:
                                            self.logger.info("Successfully downloaded with service role key")
                                            image_data = response.content
                                        else:
                                            raise ImageError(f"Service role download failed: {response.status_code}")
                                except Exception as role_e:
                                    raise ImageError(f"Service role download failed: {str(role_e)}")
                            else:
                                raise ImageError("No service role key available and storage service failed")
                    else:
                        # If we can't extract a path, try to use the URL directly
                        async with httpx.AsyncClient(timeout=30.0) as client:
                            response = await client.get(image_url_or_path)
                            if response.status_code != 200:
                                raise ImageError(f"Failed to fetch image from signed URL: {response.status_code}")
                            image_data = response.content
            
            # Otherwise it's a storage path
            else:
                image_data = self.storage.get_image(image_url_or_path, is_palette=is_palette)
                self.logger.info(f"Retrieved image directly from storage: {len(image_data)} bytes")
            
            # Cache the image data to avoid re-downloading
            if len(self._image_cache) >= self._cache_size_limit:
                # Remove oldest entry if cache is full
                oldest_key = next(iter(self._image_cache))
                del self._image_cache[oldest_key]
                
            self._image_cache[cache_key] = image_data
            return image_data
                
        except Exception as e:
            error_msg = f"Failed to get image: {str(e)}"
            self.logger.error(f"Error fetching {mask_path(image_url_or_path)}: {error_msg}")
            raise ImageError(error_msg)

    async def download_with_service_role(self, bucket_name: str, path: str) -> bytes:
        """
        Directly download an image using the service role key, bypassing RLS policies.
        
        This method is useful for administrative functions or when normal access methods fail.
        
        Args:
            bucket_name: Name of the bucket
            path: Path to the image within the bucket
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageError: If download fails
        """
        try:
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                raise ImageError("Service role key not available in settings")
            
            # Normalize path
            if path.startswith('/'):
                path = path[1:]
            
            self.logger.info(f"Attempting direct download with service role key: bucket={bucket_name}, path={mask_path(path)}")
            
            # Create a direct download URL
            download_url = f"{settings.SUPABASE_URL}/storage/v1/object/{bucket_name}/{path}"
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    download_url,
                    headers={
                        "Authorization": f"Bearer {service_role_key}",
                        "apikey": service_role_key
                    }
                )
                
                if response.status_code != 200:
                    raise ImageError(f"Failed to download with service role key: {response.status_code}")
                    
                self.logger.info(f"Successfully downloaded image with service role key: {len(response.content)} bytes")
                return response.content
                
        except Exception as e:
            error_msg = f"Service role download failed: {str(e)}"
            self.logger.error(error_msg)
            raise ImageError(error_msg) 