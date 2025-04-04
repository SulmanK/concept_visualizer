"""
Storage services package.

This package provides services for storing and retrieving concepts and related data.
"""

from functools import lru_cache
from fastapi import Depends

from app.services.interfaces import StorageServiceInterface
from app.services.storage.concept_storage import ConceptStorageService
from app.core.supabase.client import get_supabase_client, SupabaseClient

__all__ = ["ConceptStorageService", "get_concept_storage_service"]


@lru_cache()
def get_concept_storage_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> StorageServiceInterface:
    """
    Get a singleton instance of ConceptStorageService.
    
    Args:
        supabase_client: Supabase client
        
    Returns:
        ConceptStorageService: A service for storing and retrieving concepts
    """
    return ConceptStorageService(client=supabase_client) 