"""
Image processing and storage services.

This module provides services for processing, storing, and retrieving images.
"""

from functools import lru_cache
from typing import Optional

from supabase import Client
from app.services.image.service import ImageService, ImageError
from app.services.image.processing_service import ImageProcessingService, ImageProcessingError
from app.services.image.storage import ImageStorageService
from app.services.jigsawstack.client import JigsawStackClient
from app.services.jigsawstack.service import get_jigsawstack_service
from app.core.dependencies import get_supabase_client

# Export symbols that should be available to importers of this package
__all__ = [
    "ImageService", 
    "ImageError",
    "ImageProcessingService",
    "ImageProcessingError",
    "get_image_service",
    "get_image_processing_service"
]

@lru_cache()
def get_image_processing_service() -> ImageProcessingService:
    """
    Get image processing service instance.
    
    Returns:
        ImageProcessingService: Service for processing images
    """
    return ImageProcessingService()

@lru_cache()
def get_image_service(
    jigsawstack_client: Optional[JigsawStackClient] = None,
    supabase_client: Optional[Client] = None,
    processing_service: Optional[ImageProcessingService] = None
) -> ImageService:
    """
    Get image service instance.
    
    Args:
        jigsawstack_client: JigsawStack client to use, created if None
        supabase_client: Supabase client to use, created if None
        processing_service: Image processing service to use, created if None
        
    Returns:
        ImageService: Service for generating, processing, and storing images
    """
    if jigsawstack_client is None:
        jigsawstack_client = get_jigsawstack_service().client
    
    if supabase_client is None:
        supabase_client = get_supabase_client()
    
    if processing_service is None:
        processing_service = get_image_processing_service()
    
    storage_service = ImageStorageService(supabase_client)
    
    return ImageService(
        jigsawstack_client=jigsawstack_client,
        supabase_client=supabase_client,
        storage_service=storage_service,
        processing_service=processing_service
    ) 