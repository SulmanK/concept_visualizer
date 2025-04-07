"""
Image service for generating, storing, and processing images.

This module provides a service for handling all image-related operations,
including generating images with JigsawStack, storing them in Supabase,
and applying color palettes.
"""

import logging
from fastapi import Depends
from typing import List, Dict, Optional, Tuple, Any
import uuid
from io import BytesIO
from PIL import Image

from ..core.supabase import SupabaseClient, get_supabase_client
from ..core.supabase.image_storage import ImageStorage
from .jigsawstack.client import JigsawStackClient, get_jigsawstack_client
from .image_processing import apply_palette_with_masking_optimized
from ..utils.security.mask import mask_id, mask_path
from ..services.interfaces import ImageServiceInterface

# Configure logging
logger = logging.getLogger(__name__)

class ImageProcessingError(Exception):
    """Exception raised for image processing errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class StorageError(Exception):
    """Exception raised for storage errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ImageService(ImageServiceInterface):
    """Service for image generation and storage."""
    
    def __init__(
        self, 
        supabase_client: SupabaseClient = Depends(get_supabase_client),
        jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client)
    ):
        """Initialize image service with required clients.
        
        Args:
            supabase_client: Client for Supabase operations
            jigsawstack_client: Client for JigsawStack API
        """
        self.supabase_client = supabase_client
        self.image_storage = ImageStorage(supabase_client)
        self.jigsawstack_client = jigsawstack_client
        self.logger = logging.getLogger("image_service")
    
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
            # Generate image using JigsawStack
            self.logger.info(f"Generating image with prompt: {prompt}")
            image_data = await self.jigsawstack_client.generate_image(logo_description=prompt)
            
            if not image_data:
                self.logger.error("Failed to generate image: No binary data returned")
                raise ImageProcessingError("Failed to generate image: No binary data returned")
            
            self.logger.info(f"Image generated successfully. Binary data received: {len(image_data)} bytes")
                
            # Generate a unique filename and upload to Supabase Storage
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Uploading image to Supabase Storage, bucket: [concept-images], user: {masked_user_id}")
            
            # Determine image format
            img = Image.open(BytesIO(image_data))
            format_ext = img.format.lower() if img.format else "png"
            
            # Generate a unique filename with the correct extension
            unique_id = str(uuid.uuid4())
            unique_filename = f"{user_id}/{unique_id}.{format_ext}"
            masked_filename = mask_path(unique_filename)
            
            # Upload to Supabase Storage
            result = self.supabase_client.client.storage.from_("concept-images").upload(
                path=unique_filename,
                file=image_data,
                file_options={"content-type": f"image/{format_ext}"}
            )
            
            if not result:
                self.logger.error("Failed to upload image to Supabase Storage")
                raise StorageError("Failed to upload image to Supabase Storage")
                
            # Set the storage path
            storage_path = unique_filename
                
            # Get signed URL
            self.logger.info(f"Getting signed URL for image: {masked_filename}")
            signed_url = self.image_storage.get_image_url(storage_path, "concept-images")
            
            return storage_path, signed_url
        except Exception as e:
            self.logger.error(f"Error in generate_and_store_image: {e}")
            if isinstance(e, (ImageProcessingError, StorageError)):
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
            # Refine image using JigsawStack
            self.logger.info(f"Refining image with prompt: {prompt}")
            image_data = await self.jigsawstack_client.refine_image(
                prompt=prompt,
                image_url=original_image_url,
                strength=strength
            )
            
            if not image_data:
                self.logger.error("Failed to refine image: No binary data returned")
                raise ImageProcessingError("Failed to refine image: No binary data returned")
            
            self.logger.info(f"Image refined successfully. Binary data received: {len(image_data)} bytes")
                
            # Generate a unique filename and upload to Supabase Storage
            try:
                # Determine image format
                img = Image.open(BytesIO(image_data))
                format_ext = img.format.lower() if img.format else "png"
                
                # Generate a unique ID and filename
                unique_id = str(uuid.uuid4())
                filename = f"{unique_id}.{format_ext}"
                unique_filename = f"{user_id}/{filename}"
                
                # Log the operation with masked paths
                masked_user_id = mask_id(user_id)
                masked_filename = mask_path(unique_filename)
                self.logger.info(f"Uploading refined image to Storage, bucket: concept-images, user: {masked_user_id}")
                
                # Store the image using the store_image method
                signed_url = self.image_storage.store_image(
                    image_data=image_data,
                    user_id=user_id,
                    file_name=filename
                )
                
                if not signed_url:
                    self.logger.error("Failed to upload refined image to Supabase Storage")
                    raise StorageError("Failed to upload refined image to Supabase Storage")
                
                # Set the storage path to the consistent filename
                storage_path = unique_filename
                self.logger.info(f"Getting signed URL for refined image: {masked_filename}")
                
                return storage_path, signed_url
            except Exception as e:
                self.logger.error(f"Failed to upload refined image: {str(e)}")
                raise StorageError(f"Failed to upload refined image: {str(e)}")
        except Exception as e:
            self.logger.error(f"Error in refine_and_store_image: {e}")
            if isinstance(e, (ImageProcessingError, StorageError)):
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
        
        # Get image URL from storage path
        masked_base_path = mask_path(base_image_path)
        masked_user_id = mask_id(user_id)
        
        base_image_url = self.image_storage.get_image_url(base_image_path, "concept-images")
        if not base_image_url:
            self.logger.error(f"Failed to get URL for base image: {masked_base_path}")
            raise StorageError(f"Failed to get URL for base image: {masked_base_path}")
            
        try:
            # Download the base image
            self.logger.info(f"Downloading base image for user: {masked_user_id}")
            base_image_data = await self.jigsawstack_client.download_image(base_image_url)
            
            if not base_image_data:
                self.logger.error("Failed to download base image")
                raise ImageProcessingError("Failed to download base image")
                
            # Process each palette
            for idx, palette in enumerate(palettes):
                try:
                    # Extract palette data
                    palette_name = palette.get("name", f"Palette {idx+1}")
                    palette_colors = palette.get("colors", [])
                    palette_description = palette.get("description", "")
                    
                    self.logger.info(f"Processing palette: {palette_name} with {len(palette_colors)} colors")
                    
                    if not palette_colors:
                        self.logger.warning(f"Empty color palette: {palette_name}, skipping")
                        continue
                        
                    # Apply color palette to the image
                    colorized_image = await apply_palette_with_masking_optimized(
                        base_image_data, 
                        palette_colors,
                        blend_strength
                    )
                    
                    if not colorized_image:
                        self.logger.error(f"Failed to apply palette: {palette_name}")
                        continue
                    
                    # Generate a unique filename for this variation
                    unique_id = str(uuid.uuid4())
                    img = Image.open(BytesIO(colorized_image))
                    format_ext = img.format.lower() if img.format else "png"
                    filename = f"{unique_id}.{format_ext}"
                    unique_filename = f"{user_id}/{filename}"
                    
                    self.logger.info(f"Uploading palette variation: {palette_name}")
                    # Upload to Supabase Storage in the palette-images bucket
                    result = self.supabase_client.client.storage.from_("palette-images").upload(
                        path=unique_filename,
                        file=colorized_image,
                        file_options={"content-type": f"image/{format_ext}"}
                    )
                    
                    if not result:
                        self.logger.error(f"Failed to upload palette image: {palette_name}")
                        continue
                    
                    # Get a signed URL for the palette image
                    palette_image_url = self.image_storage.get_image_url(unique_filename, "palette-images")
                    
                    # Add the result to our list
                    result_palettes.append({
                        "name": palette_name,
                        "colors": palette_colors,
                        "description": palette_description,
                        "image_path": unique_filename,
                        "image_url": palette_image_url
                    })
                    
                    self.logger.info(f"Successfully processed palette: {palette_name}")
                    
                except Exception as e:
                    self.logger.error(f"Error processing palette {palette_name}: {e}")
                    # Continue with other palettes
            
            if not result_palettes:
                self.logger.warning("No palette variations were successfully created")
            else:
                self.logger.info(f"Created {len(result_palettes)} palette variations")
                
            return result_palettes
            
        except Exception as e:
            self.logger.error(f"Error in create_palette_variations: {e}")
            if isinstance(e, (ImageProcessingError, StorageError)):
                raise
            raise ImageProcessingError(f"Error creating palette variations: {str(e)}")


async def get_image_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
    jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client)
) -> ImageServiceInterface:
    """
    Get an instance of ImageService.
    
    Args:
        supabase_client: Client for Supabase operations
        jigsawstack_client: Client for JigsawStack API
        
    Returns:
        ImageService: A service for image generation and storage
    """
    return ImageService(supabase_client, jigsawstack_client) 