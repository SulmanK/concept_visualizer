"""
Image processing and storage services.

This package provides services for processing, storing, and retrieving images.
"""

from functools import lru_cache
from fastapi import Depends

from app.core.config import settings
from app.services.interfaces import ImageServiceInterface
from app.services.image.service import ImageService
from app.services.image.storage import ImageStorageService
from app.services.image.processing import apply_palette_with_masking_optimized
from app.services.image.conversion import (
    convert_image_format,
    generate_thumbnail,
    optimize_image
)
from app.services.jigsawstack.client import JigsawStackClient, get_jigsawstack_client
from app.core.supabase.client import SupabaseClient, get_supabase_client

__all__ = [
    "ImageService",
    "get_image_service",
    "ImageStorageService",
    "apply_palette_with_masking_optimized",
    "convert_image_format",
    "generate_thumbnail",
    "optimize_image"
]


@lru_cache()
def get_image_service(
    jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client),
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> ImageServiceInterface:
    """
    Get a singleton instance of ImageService.
    
    Args:
        jigsawstack_client: JigsawStack API client
        supabase_client: Supabase client
        
    Returns:
        ImageService: A service for processing and storing images
    """
    # Create storage service
    storage_service = ImageStorageService(supabase_client)
    
    return ImageService(
        jigsawstack_client=jigsawstack_client,
        supabase_client=supabase_client,
        storage_service=storage_service
    ) 