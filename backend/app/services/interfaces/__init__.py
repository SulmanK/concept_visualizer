"""
Service interfaces.

This module provides abstract interface definitions for service classes.
"""

# Import interfaces for easy access
from .concept_service import ConceptServiceInterface
from .image_service import ImageServiceInterface
from .storage_service import StorageServiceInterface  # Keep for backwards compatibility
from .concept_persistence_service import ConceptPersistenceServiceInterface
from .persistence_service import (
    PersistenceServiceInterface,
    ImagePersistenceServiceInterface
)
from .task_service import TaskServiceInterface

__all__ = [
    "ConceptServiceInterface", 
    "ImageServiceInterface",
    "StorageServiceInterface",  # Keep for backwards compatibility
    "ConceptPersistenceServiceInterface",
    "TaskServiceInterface",
    "PersistenceServiceInterface",
    "ImagePersistenceServiceInterface"
] 