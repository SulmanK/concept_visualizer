"""
Persistence services package.

This package provides services for storing and retrieving concepts and related data.
"""

from functools import lru_cache
from fastapi import Depends

from app.services.interfaces import ImagePersistenceServiceInterface, StorageServiceInterface
from app.services.interfaces.concept_persistence_service import ConceptPersistenceServiceInterface
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.core.supabase.client import get_supabase_client, SupabaseClient

__all__ = [
    "ConceptPersistenceService", 
    "ImagePersistenceService", 
    "get_concept_persistence_service", 
    "get_image_persistence_service",
    "get_concept_storage_service"  # For backward compatibility
]


@lru_cache()
def get_concept_persistence_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> ConceptPersistenceServiceInterface:
    """
    Get a singleton instance of ConceptPersistenceService.
    
    Args:
        supabase_client: Supabase client
        
    Returns:
        ConceptPersistenceService: A service for storing and retrieving concepts
    """
    return ConceptPersistenceService(client=supabase_client)


@lru_cache()
def get_image_persistence_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> ImagePersistenceServiceInterface:
    """
    Get a singleton instance of ImagePersistenceService.
    
    Args:
        supabase_client: Supabase client
        
    Returns:
        ImagePersistenceService: A service for storing and retrieving images
    """
    return ImagePersistenceService(client=supabase_client)


# For backward compatibility with existing code
get_concept_storage_service = get_concept_persistence_service 