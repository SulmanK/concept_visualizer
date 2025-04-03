"""
Shared dependencies for API routes.

This module provides common dependencies that can be reused across different
API route handlers to reduce code duplication and improve maintainability.
"""

import logging
from typing import Tuple, Optional

from fastapi import Depends, Cookie, Request, Response
from slowapi.util import get_remote_address

from app.services.concept_service import ConceptService, get_concept_service
from app.services.session_service import SessionService, get_session_service
from app.services.image_service import ImageService, get_image_service
from app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service
from app.core.supabase import get_supabase_client

# Configure logging
logger = logging.getLogger("api_dependencies")


def get_session_id(session_id: Optional[str] = Cookie(None, alias="concept_session")) -> Optional[str]:
    """
    Extract the session ID from the request cookies.
    
    Args:
        session_id: The session ID cookie value
        
    Returns:
        The session ID if it exists, otherwise None
    """
    return session_id


async def get_or_create_session(
    response: Response,
    session_service: SessionService = Depends(get_session_service),
    session_id: Optional[str] = Depends(get_session_id),
    client_session_id: Optional[str] = None
) -> Tuple[str, bool]:
    """
    Get an existing session or create a new one.
    
    Args:
        response: FastAPI response object for setting cookies
        session_service: Service for managing sessions
        session_id: Session ID from cookies
        client_session_id: Optional client-provided session ID for synchronization
        
    Returns:
        Tuple of (session_id, is_new_session)
    """
    return await session_service.get_or_create_session(
        response, 
        session_id=session_id,
        client_session_id=client_session_id
    )


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
        "session_service": get_session_service(),
        "image_service": get_image_service(),
        "storage_service": get_concept_storage_service(),
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
        concept_service: ConceptService = Depends(get_concept_service),
        session_service: SessionService = Depends(get_session_service),
        image_service: ImageService = Depends(get_image_service),
        storage_service: ConceptStorageService = Depends(get_concept_storage_service)
    ):
        """Initialize with all common service dependencies."""
        self.concept_service = concept_service
        self.session_service = session_service
        self.image_service = image_service
        self.storage_service = storage_service 