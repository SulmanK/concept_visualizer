"""Dependencies for API routes.

This module provides dependencies that can be used by API routes.
"""

import base64
import json
from typing import Any, Dict, Optional

from fastapi import Depends, Header, Request

from app.core.supabase.client import SupabaseClient, get_supabase_client
from app.services.concept import get_concept_service
from app.services.concept.interface import ConceptServiceInterface
from app.services.image import get_image_service
from app.services.image.interface import ImageServiceInterface
from app.services.jigsawstack.client import JigsawStackClient, get_jigsawstack_client
from app.services.persistence import get_concept_persistence_service, get_image_persistence_service
from app.services.persistence.interface import ConceptPersistenceServiceInterface, ImagePersistenceServiceInterface
from app.services.task import get_task_service
from app.services.task.interface import TaskServiceInterface
from app.utils.security.mask import mask_id


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Extract the current user from the request session.

    Args:
        request: The FastAPI request object

    Returns:
        The user data if authenticated, None otherwise
    """
    # Check if session middleware is installed and session exists
    if request and "session" in request.scope and "user" in request.scope["session"]:
        user_data: Dict[str, Any] = request.scope["session"]["user"]
        return user_data
    return None


def decode_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Simple decode of JWT token without verification.

    Args:
        token: JWT token to decode

    Returns:
        Decoded payload or None if decoding failed
    """
    try:
        # Get payload part (second segment)
        parts = token.split(".")
        if len(parts) != 3:
            return None

        # Decode the payload
        padded = parts[1] + "=" * (4 - len(parts[1]) % 4)
        decoded = base64.b64decode(padded)
        payload: Dict[str, Any] = json.loads(decoded)
        return payload
    except Exception as e:
        print(f"Error decoding token: {str(e)}")
        return None


# Create a CommonDependencies class for dependency injection
class CommonDependencies:
    """Common dependencies for API routes.

    This class provides common dependencies that can be used by API routes.
    It can be used to inject dependencies into route handlers.
    """

    def __init__(
        self,
        supabase_client: SupabaseClient = Depends(get_supabase_client),
        jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client),
        concept_service: ConceptServiceInterface = Depends(get_concept_service),
        concept_persistence_service: ConceptPersistenceServiceInterface = Depends(get_concept_persistence_service),
        image_service: ImageServiceInterface = Depends(get_image_service),
        image_persistence_service: ImagePersistenceServiceInterface = Depends(get_image_persistence_service),
        task_service: TaskServiceInterface = Depends(get_task_service),
        authorization: Optional[str] = Header(None),
    ):
        """Initialize CommonDependencies with required services.

        Args:
            supabase_client: Supabase client for database operations
            jigsawstack_client: JigsawStack API client
            concept_service: Service for concept generation and refinement
            concept_persistence_service: Service for concept persistence
            image_service: Service for image processing
            image_persistence_service: Service for image persistence
            task_service: Service for background task management
            authorization: Authorization header for extracting tokens
        """
        self.supabase_client = supabase_client
        self.jigsawstack_client = jigsawstack_client
        self.concept_service = concept_service
        self.concept_persistence_service = concept_persistence_service
        self.image_service = image_service
        self.image_persistence_service = image_persistence_service
        self.task_service = task_service
        self.user: Optional[Dict[str, Any]] = None

        # Extract user information from the authorization header if present
        self.user_id = None
        if authorization and authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            # Decode the token without verification (for development only)
            payload = decode_jwt_token(token)
            if payload and "sub" in payload:
                self.user_id = payload["sub"]
                print(f"User authenticated: {mask_id(self.user_id)}")

    def process_request(self, request: Request) -> None:
        """Process the request to extract user information.

        Args:
            request: FastAPI request object
        """
        if request:
            # Try to get user from session
            self.user = get_current_user(request)

            # Check for user in request.state (added by auth middleware)
            if not self.user and hasattr(request, "state") and hasattr(request.state, "user"):
                # We know this is a Dict[str, Any] but mypy can't infer this
                self.user = getattr(request.state, "user")

            # If no user_id from token but we have a user from session, use that
            if not self.user_id and self.user and "id" in self.user:
                self.user_id = self.user["id"]
