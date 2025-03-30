"""
Image service for generating, storing, and processing images.

This module provides a service for handling all image-related operations,
including generating images with JigsawStack, storing them in Supabase,
and applying color palettes.
"""

import logging
from fastapi import Depends
from typing import List, Dict, Optional, Tuple, Any

from ..core.supabase import get_supabase_client, SupabaseClient
from .jigsawstack.client import JigsawStackClient, get_jigsawstack_client

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
        self.jigsawstack_client = jigsawstack_client
        self.logger = logging.getLogger("image_service")
    
    async def generate_and_store_image(self, prompt: str, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate an image and store it in Supabase.
        
        Args:
            prompt: Image generation prompt
            session_id: Current session ID
            
        Returns:
            Tuple of (storage_path, public_url) or (None, None) on error
        """
        try:
            # Generate image using JigsawStack
            self.logger.info(f"Generating image with prompt: {prompt}")
            image_data = await self.jigsawstack_client.generate_image(prompt=prompt)
            
            if not image_data:
                self.logger.error("Failed to generate image: No binary data returned")
                return None, None
            
            self.logger.info(f"Image generated successfully. Binary data received: {len(image_data)} bytes")
                
            # Generate a unique filename and upload to Supabase Storage
            self.logger.info(f"Uploading image to Supabase Storage, bucket: concept-images, session: {session_id}")
            
            import uuid
            from io import BytesIO
            from PIL import Image
            
            # Determine image format
            img = Image.open(BytesIO(image_data))
            format_ext = img.format.lower() if img.format else "png"
            
            # Generate a unique filename with the correct extension
            unique_filename = f"{session_id}/{uuid.uuid4()}.{format_ext}"
            
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
                
            # Get public URL
            self.logger.info(f"Getting public URL for image: {storage_path}")
            public_url = self.supabase_client.get_image_url(storage_path, "concept-images")
            
            return storage_path, public_url
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
            Tuple of (storage_path, public_url) or (None, None) on error
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
                
            # Generate a unique filename and upload to Supabase Storage
            self.logger.info(f"Uploading refined image to Storage, bucket: concept-images, session: {session_id}")
            
            import uuid
            from io import BytesIO
            from PIL import Image
            
            # Determine image format
            img = Image.open(BytesIO(image_data))
            format_ext = img.format.lower() if img.format else "png"
            
            # Generate a unique filename with the correct extension
            unique_filename = f"{session_id}/{uuid.uuid4()}.{format_ext}"
            
            # Upload to Supabase Storage
            result = self.supabase_client.client.storage.from_("concept-images").upload(
                path=unique_filename,
                file=image_data,
                file_options={"content-type": f"image/{format_ext}"}
            )
            
            if not result:
                self.logger.error("Failed to upload refined image to Supabase Storage")
                return None, None
                
            # Set the storage path
            storage_path = unique_filename
                
            # Get public URL
            self.logger.info(f"Getting public URL for refined image: {storage_path}")
            public_url = self.supabase_client.get_image_url(storage_path, "concept-images")
            
            return storage_path, public_url
        except Exception as e:
            self.logger.error(f"Error in refine_and_store_image: {e}")
            return None, None
    
    async def create_palette_variations(
        self, 
        base_image_path: str, 
        palettes: List[Dict[str, Any]], 
        session_id: str
    ) -> List[Dict[str, Any]]:
        """Create variations of an image with different color palettes.
        
        Args:
            base_image_path: Storage path of the base image
            palettes: List of color palette dictionaries
            session_id: Current session ID
            
        Returns:
            List of palettes with added image_path and image_url fields
        """
        result_palettes = []
        
        for palette in palettes:
            self.logger.info(f"Creating palette variation for palette: {palette['name']}")
            
            # Apply palette to image
            palette_image_path = await self.supabase_client.apply_color_palette(
                base_image_path,
                palette["colors"],
                session_id
            )
            
            if palette_image_path:
                # Get public URL
                palette_image_url = self.supabase_client.get_image_url(
                    palette_image_path, 
                    "palette-images"
                )
                
                self.logger.info(f"Created palette variation: {palette_image_path}")
                
                # Add paths to palette dict
                palette_copy = palette.copy()
                palette_copy["image_path"] = palette_image_path
                palette_copy["image_url"] = palette_image_url
                result_palettes.append(palette_copy)
            else:
                self.logger.error(f"Failed to create palette variation for palette: {palette['name']}")
                
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