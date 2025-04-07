"""
Service interfaces package.

This package provides interface definitions for all service classes in the application.
"""

# Import interfaces for easy access
from .concept_service import ConceptServiceInterface
from .image_service import ImageServiceInterface
from .storage_service import StorageServiceInterface

__all__ = [
    "ConceptServiceInterface", 
    "ImageServiceInterface",
    "StorageServiceInterface",
] 