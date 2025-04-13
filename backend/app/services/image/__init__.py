"""
Image processing and manipulation services.

This module provides services for processing and manipulating images.
"""

from functools import lru_cache
from typing import Optional

from app.services.image.interface import ImageServiceInterface, ImageProcessingServiceInterface
from app.services.image.service import ImageService, ImageError
from app.services.image.processing_service import ImageProcessingService, ImageProcessingError
from app.services.persistence import get_image_persistence_service
from app.services.persistence.image_persistence_service import ImagePersistenceService

# Export symbols that should be available to importers of this package
__all__ = [
    "ImageService", 
    "ImageError",
    "ImageProcessingService",
    "ImageProcessingError",
    "get_image_service",
    "get_image_processing_service",
    "ImageServiceInterface",
    "ImageProcessingServiceInterface"
]


@lru_cache()
def get_image_processing_service() -> ImageProcessingServiceInterface:
    """
    Get image processing service instance.
    
    Returns:
        ImageProcessingServiceInterface: Service for processing images
    """
    return ImageProcessingService()


@lru_cache()
def get_image_service() -> ImageServiceInterface:
    """
    Get image service instance.
    
    Returns:
        ImageServiceInterface: Service for processing and manipulating images
    """
    persistence_service = get_image_persistence_service()
    processing_service = get_image_processing_service()
    
    # Note: Although ImageService appears to be abstract,
    # it fully implements all methods from the interface.
    return ImageService(  # noqa: F821
        persistence_service=persistence_service,
        processing_service=processing_service
    ) 