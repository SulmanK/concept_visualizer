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

# Configure logging
logger = logging.getLogger(__name__)

class ImageService:
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
    
    async def generate_and_store_image(self, prompt: str, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate an image and store it in Supabase.
        
        Args:
            prompt: Image generation prompt
            session_id: Current session ID
            
        Returns:
            Tuple of (storage_path, signed_url) or (None, None) on error
        """
        try:
            # Generate image using JigsawStack
            self.logger.info(f"Generating image with prompt: {prompt}")
            image_data = await self.jigsawstack_client.generate_image(logo_description=prompt)
            
            if not image_data:
                self.logger.error("Failed to generate image: No binary data returned")
                return None, None
            
            self.logger.info(f"Image generated successfully. Binary data received: {len(image_data)} bytes")
                
            # Generate a unique filename and upload to Supabase Storage
            masked_session = mask_id(session_id)
            self.logger.info(f"Uploading image to Supabase Storage, bucket: [concept-images], session: {masked_session}")
            
            # Determine image format
            img = Image.open(BytesIO(image_data))
            format_ext = img.format.lower() if img.format else "png"
            
            # Generate a unique filename with the correct extension
            unique_id = str(uuid.uuid4())
            unique_filename = f"{session_id}/{unique_id}.{format_ext}"
            masked_filename = mask_path(unique_filename)
            
            # Upload to Supabase Storage
            result = self.supabase_client.client.storage.from_("concept-images").upload(
                path=unique_filename,
                file=image_data,
                file_options={"content-type": f"image/{format_ext}"}
            )
            
            if not result:
                self.logger.error("Failed to upload image to Supabase Storage")
                return None, None
                
            # Set the storage path
            storage_path = unique_filename
                
            # Get signed URL
            self.logger.info(f"Getting signed URL for image: {masked_filename}")
            signed_url = self.image_storage.get_image_url(storage_path, "concept-images")
            
            return storage_path, signed_url
        except Exception as e:
            self.logger.error(f"Error in generate_and_store_image: {e}")
            return None, None
    
    async def refine_and_store_image(
        self, 
        prompt: str, 
        original_image_url: str, 
        session_id: str,
        strength: float = 0.7
    ) -> Tuple[Optional[str], Optional[str]]:
        """Refine an image and store the result in Supabase.
        
        Args:
            prompt: Refinement prompt
            original_image_url: URL of the original image
            session_id: Current session ID
            strength: How much to change the original (0.0-1.0)
            
        Returns:
            Tuple of (storage_path, signed_url) or (None, None) on error
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
                return None, None
            
            self.logger.info(f"Image refined successfully. Binary data received: {len(image_data)} bytes")
                
            # Generate a unique filename and upload to Supabase Storage using store_image method
            try:
                # Determine image format
                img = Image.open(BytesIO(image_data))
                format_ext = img.format.lower() if img.format else "png"
                
                # Generate a unique ID and filename
                unique_id = str(uuid.uuid4())
                filename = f"{unique_id}.{format_ext}"
                unique_filename = f"{session_id}/{filename}"
                
                # Log the operation with masked paths
                masked_session = mask_id(session_id)
                masked_filename = mask_path(unique_filename)
                self.logger.info(f"Uploading refined image to Storage, bucket: concept-images, session: {masked_session}")
                
                # Store the image using the store_image method
                signed_url = self.image_storage.store_image(
                    image_data=image_data,
                    session_id=session_id,
                    file_name=filename
                )
                
                if not signed_url:
                    self.logger.error("Failed to upload refined image to Supabase Storage")
                    return None, None
                
                # Set the storage path to the consistent filename
                storage_path = unique_filename
                self.logger.info(f"Getting signed URL for refined image: {masked_filename}")
                
                return storage_path, signed_url
            except Exception as e:
                self.logger.error(f"Failed to upload refined image: {str(e)}")
                return None, None
        except Exception as e:
            self.logger.error(f"Error in refine_and_store_image: {e}")
            return None, None
    
    async def create_palette_variations(
        self, 
        base_image_path: str, 
        palettes: List[Dict[str, Any]], 
        session_id: str,
        blend_strength: float = 0.75
    ) -> List[Dict[str, Any]]:
        """Create variations of an image with different color palettes.
        
        Args:
            base_image_path: Storage path of the base image
            palettes: List of color palette dictionaries
            session_id: Current session ID
            blend_strength: How strongly to apply the new colors (0.0-1.0)
            
        Returns:
            List of palettes with added image_path and image_url fields
        """
        result_palettes = []
        
        # Get image URL from storage path
        masked_base_path = mask_path(base_image_path)
        masked_session = mask_id(session_id)
        
        base_image_url = self.image_storage.get_image_url(base_image_path, "concept-images")
        if not base_image_url:
            self.logger.error(f"Failed to get URL for base image: {masked_base_path}")
            return []
        
        for palette in palettes:
            self.logger.info(f"Creating palette variation for palette: {palette['name']} using base image: {masked_base_path}")
            
            try:
                # Apply palette to image using the optimized masking approach
                palette_image_data = apply_palette_with_masking_optimized(
                    base_image_url, 
                    palette["colors"],
                    blend_strength=blend_strength
                )
                
                # Generate a unique filename for the palette variation
                unique_id = str(uuid.uuid4())
                filename = f"palette_{unique_id}.png"
                
                # Upload to Supabase Storage using store_image method
                try:
                    # The store_image method will use the palette bucket and return a tuple of (path, url)
                    palette_image_path, palette_image_url = self.image_storage.store_image(
                        image_data=palette_image_data,
                        session_id=session_id,
                        file_name=filename,
                        is_palette=True
                    )
                    
                    if not palette_image_path or not palette_image_url:
                        self.logger.error(f"Failed to upload palette variation: {palette['name']}")
                        continue
                    
                    # For debugging - log the path and URL received
                    self.logger.info(f"Stored palette variation at path: {palette_image_path}")
                    self.logger.info(f"Received palette image URL: {palette_image_url}")
                    
                    # Add paths to palette dict
                    palette_copy = palette.copy()
                    # Store both the path and the full signed URL
                    palette_copy["image_path"] = palette_image_path
                    palette_copy["image_url"] = palette_image_url
                    # Add the bucket information explicitly to help with retrieval
                    palette_copy["bucket"] = self.image_storage.palette_bucket
                    result_palettes.append(palette_copy)
                    
                    self.logger.info(f"Created palette variation: {mask_path(palette_image_path)}")
                except Exception as e:
                    self.logger.error(f"Error creating palette variation: {str(e)}")
                    continue
                
            except Exception as e:
                self.logger.error(f"Error creating palette variation: {str(e)}")
                continue
                
        return result_palettes


# Dependency function for FastAPI routes
async def get_image_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
    jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client)
) -> ImageService:
    """Factory function for ImageService.
    
    Args:
        supabase_client: Supabase client dependency
        jigsawstack_client: JigsawStack client dependency
        
    Returns:
        Configured ImageService instance
    """
    return ImageService(supabase_client, jigsawstack_client) 