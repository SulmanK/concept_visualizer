"""Image processing and manipulation services.

This module provides services for processing and manipulating images.
"""

from app.services.image.interface import ImageProcessingServiceInterface, ImageServiceInterface
from app.services.image.processing_service import ImageProcessingError, ImageProcessingService
from app.services.image.service import ImageError, ImageService

# Export symbols that should be available to importers of this package
__all__ = [
    "ImageService",
    "ImageError",
    "ImageProcessingService",
    "ImageProcessingError",
    "get_image_service",
    "get_image_processing_service",
    "ImageServiceInterface",
    "ImageProcessingServiceInterface",
]


def get_image_processing_service() -> ImageProcessingServiceInterface:
    """Get image processing service instance.

    Returns:
        ImageProcessingServiceInterface: Service for processing images
    """
    return ImageProcessingService()


def get_image_service() -> ImageServiceInterface:
    """Get image service instance.

    Returns:
        ImageServiceInterface: Service for processing and manipulating images
    """
    from app.core.supabase.client import get_supabase_client

    # Get the Supabase client directly
    supabase_client = get_supabase_client()

    # Use the client to create the persistence service properly
    from app.services.persistence.image_persistence_service import ImagePersistenceService

    persistence_service = ImagePersistenceService(client=supabase_client)

    processing_service = get_image_processing_service()

    # Create the service with properly initialized dependencies
    return ImageService(persistence_service=persistence_service, processing_service=processing_service)
