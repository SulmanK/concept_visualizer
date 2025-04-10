"""
Service interfaces.

This module provides abstract interface definitions for service classes.
"""

# Import interfaces for easy access
from .concept_service import ConceptServiceInterface
from .image_service import ImageServiceInterface
from .storage_service import StorageServiceInterface
from .task_service import TaskServiceInterface

__all__ = [
    "ConceptServiceInterface", 
    "ImageServiceInterface",
    "StorageServiceInterface",
    "TaskServiceInterface"
] 