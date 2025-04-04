"""
Concept generation and refinement services.

This package provides services for generating and refining visual concepts.
"""

from functools import lru_cache
from fastapi import Depends

from app.services.jigsawstack.client import JigsawStackClient, get_jigsawstack_client
from app.services.interfaces import ConceptServiceInterface
from app.services.concept.service import ConceptService

__all__ = ["ConceptService", "get_concept_service"]


@lru_cache()
def get_concept_service(
    client: JigsawStackClient = Depends(get_jigsawstack_client),
) -> ConceptServiceInterface:
    """
    Get a singleton instance of ConceptService.
    
    Args:
        client: JigsawStack API client
        
    Returns:
        ConceptService: A service for generating and refining concepts
    """
    return ConceptService(client=client) 