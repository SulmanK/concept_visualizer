"""
Concept generation and refinement services.

This package provides services for generating and refining visual concepts.
"""

from functools import lru_cache
from fastapi import Depends

from app.services.jigsawstack.client import JigsawStackClient, get_jigsawstack_client
from app.services.image.interface import ImageServiceInterface
from app.services.image import get_image_service
from app.services.persistence.interface import ConceptPersistenceServiceInterface, ImagePersistenceServiceInterface
from app.services.persistence import get_concept_persistence_service, get_image_persistence_service
from app.services.concept.interface import ConceptServiceInterface
from app.services.concept.service import ConceptService

__all__ = ["ConceptService", "get_concept_service", "ConceptServiceInterface"]


@lru_cache()
def get_concept_service(
    client: JigsawStackClient = Depends(get_jigsawstack_client),
    # Inject the required services using Depends()
    image_service: ImageServiceInterface = Depends(get_image_service),
    concept_persistence_service: ConceptPersistenceServiceInterface = Depends(get_concept_persistence_service),
    image_persistence_service: ImagePersistenceServiceInterface = Depends(get_image_persistence_service),
) -> ConceptServiceInterface:
    """
    Get a singleton instance of ConceptService.
    
    Args:
        client: JigsawStack API client
        image_service: Service for image processing
        concept_persistence_service: Service for concept persistence
        image_persistence_service: Service for image persistence
        
    Returns:
        ConceptService: A service for generating and refining concepts
    """
    return ConceptService(
        client=client,
        image_service=image_service,
        concept_persistence_service=concept_persistence_service,
        image_persistence_service=image_persistence_service
    ) 