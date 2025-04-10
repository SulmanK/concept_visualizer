"""
Shared dependencies for API routes.

This module provides common dependencies that can be reused across different
API route handlers to reduce code duplication and improve maintainability.
"""

import logging
from typing import Dict, Any, Optional

from fastapi import Depends, Request
from slowapi.util import get_remote_address

from app.core.config import settings
from app.core.supabase.client import get_supabase_client
from app.services.concept import get_concept_service
from app.services.image import get_image_service
from app.services.storage import get_concept_storage_service
from app.services.task import get_task_service
from app.services.interfaces import (
    ConceptServiceInterface,
    ImageServiceInterface,
    StorageServiceInterface,
    TaskServiceInterface
)
from app.services.jigsawstack.client import get_jigsawstack_client
from app.api.middleware.auth_middleware import get_current_user

# Configure logging
logger = logging.getLogger("api_dependencies")


def get_request_ip(request: Request) -> str:
    """
    Extract the client IP address from the request.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        The client IP address as a string
    """
    return get_remote_address(request)


def get_common_services():
    """
    Get all common services used across multiple endpoints.
    
    This dependency combines multiple service dependencies into a single
    function to reduce boilerplate in route handlers.
    
    Returns:
        A dictionary containing all common services
    """
    return {
        "concept_service": get_concept_service(),
        "image_service": get_image_service(),
        "storage_service": get_concept_storage_service(),
        "task_service": get_task_service(),
        "supabase_client": get_supabase_client()
    }


class CommonDependencies:
    """
    Container class for common dependencies used in route handlers.
    
    This class allows dependency injection of multiple services at once
    while still maintaining the ability to access them individually.
    """
    
    def __init__(
        self,
        concept_service: ConceptServiceInterface = Depends(get_concept_service),
        image_service: ImageServiceInterface = Depends(get_image_service),
        storage_service: StorageServiceInterface = Depends(get_concept_storage_service),
        task_service: TaskServiceInterface = Depends(get_task_service),
        request: Request = None,
    ):
        """
        Initialize with all common service dependencies.
        
        Args:
            concept_service: Service for concept generation and refinement
            image_service: Service for image processing and storage
            storage_service: Service for concept storage operations
            task_service: Service for managing background tasks
            request: FastAPI request object for accessing user information
        """
        self.concept_service = concept_service
        self.image_service = image_service
        self.storage_service = storage_service
        self.task_service = task_service
        self.request = request
        self.user = get_current_user(request) if request else None
        
    @property
    def user_id(self) -> Optional[str]:
        """
        Get the current user ID.
        
        Returns:
            The current user ID if authenticated, None otherwise
        """
        if self.user and "id" in self.user:
            return self.user["id"]
        return None 