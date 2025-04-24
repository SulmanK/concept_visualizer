"""Persistence services package.

This package provides services for storing and retrieving concepts and related data.
"""

from fastapi import Depends

from app.core.supabase.client import SupabaseClient, get_supabase_client
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.services.persistence.interface import ConceptPersistenceServiceInterface, ImagePersistenceServiceInterface, StorageServiceInterface

__all__ = [
    "ConceptPersistenceService",
    "ImagePersistenceService",
    "get_concept_persistence_service",
    "get_image_persistence_service",
    "get_concept_storage_service",  # For backward compatibility
    "ConceptPersistenceServiceInterface",
    "StorageServiceInterface",
    "ImagePersistenceServiceInterface",
]


def get_concept_persistence_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> ConceptPersistenceServiceInterface:
    """Get a singleton instance of ConceptPersistenceService.

    Args:
        supabase_client: Supabase client

    Returns:
        ConceptPersistenceService: A service for storing and retrieving concepts
    """
    return ConceptPersistenceService(client=supabase_client)


def get_image_persistence_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> ImagePersistenceServiceInterface:
    """Get a singleton instance of ImagePersistenceService.

    Args:
        supabase_client: Supabase client

    Returns:
        ImagePersistenceService: A service for storing and retrieving images
    """
    return ImagePersistenceService(client=supabase_client)


# For backward compatibility with existing code
get_concept_storage_service = get_concept_persistence_service
