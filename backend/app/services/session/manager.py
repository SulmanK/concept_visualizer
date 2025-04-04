"""
Session manager implementation.

This module provides functionality for managing user sessions with Supabase,
including creating, retrieving, and updating sessions.
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from fastapi import Response, Cookie

from app.core.supabase.client import SupabaseClient
from app.core.supabase.session_storage import SessionStorage 
from app.core.config import settings
from app.services.interfaces import SessionServiceInterface
from app.utils.security.mask import mask_id


# In-memory cache for session sync responses to reduce duplicate requests
# Format: {session_id: {"data": result_tuple, "expires_at": datetime}}
_session_cache: Dict[str, Dict[str, Any]] = {}


class SessionManager(SessionServiceInterface):
    """Service for managing user sessions."""
    
    def __init__(self, client: SupabaseClient):
        """
        Initialize the session manager.
        
        Args:
            client: Client for interacting with Supabase
        """
        self.supabase_client = client
        self.session_storage = SessionStorage(client)
        self.logger = logging.getLogger("session_service")
    
    async def create_session(self) -> Dict[str, Any]:
        """
        Create a new session.
        
        Returns:
            Session data including ID and created_at timestamp
            
        Raises:
            SessionError: If session creation fails
        """
        try:
            self.logger.info("Creating new session")
            new_session = self.session_storage.create_session()
            
            if not new_session:
                # Fallback: Generate local UUID if Supabase is unavailable
                fallback_id = str(uuid.uuid4())
                self.logger.warning(f"Supabase unavailable, using fallback ID: {mask_id(fallback_id)}")
                return {
                    "id": fallback_id, 
                    "created_at": datetime.utcnow().isoformat(),
                    "is_fallback": True
                }
            
            self.logger.info(f"Created new session with ID: {mask_id(new_session['id'])}")
            return new_session
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            raise SessionError(f"Failed to create session: {str(e)}")
    
    async def get_session(self, session_id: str) -> Dict[str, Any]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: ID of the session to retrieve
            
        Returns:
            Session data
            
        Raises:
            NotFoundError: If session not found
            SessionError: If retrieval fails
        """
        try:
            masked_session_id = mask_id(session_id)
            self.logger.debug(f"Getting session: {masked_session_id}")
            
            session = self.session_storage.get_session(session_id)
            if not session:
                self.logger.warning(f"Session not found: {masked_session_id}")
                raise NotFoundError(f"Session with ID {masked_session_id} not found")
            
            # Update last activity timestamp
            self.session_storage.update_session_activity(session_id)
            
            return session
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving session: {e}")
            raise SessionError(f"Failed to retrieve session: {str(e)}")
    
    async def update_session(
        self, 
        session_id: str, 
        session_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update a session.
        
        Args:
            session_id: ID of the session to update
            session_data: Updated data
            
        Returns:
            Updated session data
            
        Raises:
            NotFoundError: If session not found
            SessionError: If update fails
        """
        try:
            masked_session_id = mask_id(session_id)
            self.logger.debug(f"Updating session: {masked_session_id}")
            
            # Check if session exists
            existing = self.session_storage.get_session(session_id)
            if not existing:
                self.logger.warning(f"Session not found for update: {masked_session_id}")
                raise NotFoundError(f"Session with ID {masked_session_id} not found")
            
            # Update session data
            updated = self.session_storage.update_session(session_id, session_data)
            if not updated:
                raise SessionError(f"Failed to update session {masked_session_id}")
            
            return updated
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error updating session: {e}")
            raise SessionError(f"Failed to update session: {str(e)}")
    
    async def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: ID of the session to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If session not found
            SessionError: If deletion fails
        """
        try:
            masked_session_id = mask_id(session_id)
            self.logger.debug(f"Deleting session: {masked_session_id}")
            
            # Check if session exists
            existing = self.session_storage.get_session(session_id)
            if not existing:
                self.logger.warning(f"Session not found for deletion: {masked_session_id}")
                raise NotFoundError(f"Session with ID {masked_session_id} not found")
            
            # Delete session
            success = self.session_storage.delete_session(session_id)
            if not success:
                raise SessionError(f"Failed to delete session {masked_session_id}")
            
            return True
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error deleting session: {e}")
            raise SessionError(f"Failed to delete session: {str(e)}")
    
    async def get_session_concepts(
        self, 
        session_id: str, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Retrieve concepts associated with a session.
        
        Args:
            session_id: ID of the session
            limit: Maximum number of concepts to return
            offset: Number of concepts to skip
            
        Returns:
            List of concept data
            
        Raises:
            NotFoundError: If session not found
            SessionError: If retrieval fails
        """
        try:
            masked_session_id = mask_id(session_id)
            self.logger.debug(f"Getting concepts for session: {masked_session_id}")
            
            # Check if session exists
            existing = self.session_storage.get_session(session_id)
            if not existing:
                self.logger.warning(f"Session not found when retrieving concepts: {masked_session_id}")
                raise NotFoundError(f"Session with ID {masked_session_id} not found")
            
            # Get concepts associated with the session
            concepts = self.session_storage.get_session_concepts(session_id, limit, offset)
            self.logger.info(f"Found {len(concepts)} concepts for session {masked_session_id}")
            
            return concepts
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error retrieving session concepts: {e}")
            raise SessionError(f"Failed to retrieve session concepts: {str(e)}")
    
    async def get_or_create_session(
        self, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a session by ID or create a new one if it doesn't exist.
        
        Args:
            session_id: Optional ID of the session to retrieve
            
        Returns:
            Session data with additional is_new flag
            
        Raises:
            SessionError: If session retrieval or creation fails
        """
        try:
            if session_id:
                masked_session_id = mask_id(session_id)
                self.logger.debug(f"Getting or creating session with ID: {masked_session_id}")
                
                # Try to get existing session
                try:
                    session = await self.get_session(session_id)
                    self.logger.debug(f"Using existing session: {masked_session_id}")
                    session["is_new"] = False
                    return session
                except NotFoundError:
                    # Session doesn't exist, create it with provided ID
                    self.logger.info(f"Creating new session with provided ID: {masked_session_id}")
                    new_session = self.session_storage.create_session_with_id(session_id)
                    if new_session:
                        new_session["is_new"] = True
                        return new_session
            
            # No ID provided or couldn't create with provided ID
            new_session = await self.create_session()
            new_session["is_new"] = True
            return new_session
        except Exception as e:
            self.logger.error(f"Error in get_or_create_session: {e}")
            raise SessionError(f"Failed to get or create session: {str(e)}")
    
    def set_session_cookie(self, response: Response, session_id: str) -> None:
        """
        Set the session cookie in the response.
        
        Args:
            response: FastAPI response object
            session_id: Session ID to set in the cookie
        """
        # Determine if we're in production based on environment setting
        is_production = False
        
        try:
            # Try to get the environment from settings first
            if hasattr(settings, 'ENVIRONMENT'):
                is_production = settings.ENVIRONMENT.lower() == "production"
            else:
                # Fallback: Check if the Supabase URL is not a development URL
                is_production = not settings.SUPABASE_URL.startswith("https://pstdcfittpjhxzynbdbu.supabase.co")
        except Exception as e:
            self.logger.warning(f"Could not determine environment, defaulting to development: {str(e)}")
        
        self.logger.debug(f"Setting session cookie: {mask_id(session_id)} (secure: {is_production})")
        response.set_cookie(
            key="concept_session",
            value=session_id,
            httponly=False,  # Need to be accessible from JavaScript
            max_age=60*60*24*30,  # 30 days
            samesite="lax",
            secure=is_production,  # True in production, False in development
            path="/"
        )
    
    async def handle_session_request(
        self, 
        response: Response,
        cookie_session_id: Optional[str] = Cookie(None, alias="concept_session"),
        client_session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Handle a session request, synchronizing cookie and client session IDs.
        
        Args:
            response: FastAPI response object for setting cookies
            cookie_session_id: Session ID from cookie
            client_session_id: Session ID provided by client
            
        Returns:
            Session data with resolved session ID and is_new flag
            
        Raises:
            SessionError: If session handling fails
        """
        try:
            # Check if we have identical session and client IDs and if so, use cache
            if cookie_session_id and client_session_id and cookie_session_id == client_session_id:
                cache_key = cookie_session_id
                
                # Check if we have a valid cached response
                now = datetime.utcnow()
                if (cache_key in _session_cache and 
                    now < _session_cache[cache_key]["expires_at"]):
                    self.logger.debug(f"Using cached session response for: {mask_id(cookie_session_id)}")
                    return _session_cache[cache_key]["data"]
            
            # Determine which session ID to use
            if client_session_id:
                try:
                    session = await self.get_or_create_session(client_session_id)
                    self.set_session_cookie(response, session["id"])
                    
                    # Cache the result if both IDs were the same
                    if cookie_session_id and client_session_id and cookie_session_id == client_session_id:
                        _session_cache[cookie_session_id] = {
                            "data": session,
                            "expires_at": datetime.utcnow() + timedelta(seconds=30)
                        }
                    
                    return session
                except Exception as e:
                    self.logger.warning(f"Error with client session ID, falling back to cookie: {str(e)}")
            
            # Use cookie session ID or create new
            session = await self.get_or_create_session(cookie_session_id)
            self.set_session_cookie(response, session["id"])
            return session
        except Exception as e:
            self.logger.error(f"Error handling session request: {e}")
            raise SessionError(f"Failed to handle session request: {str(e)}")


# Custom exception classes
class SessionError(Exception):
    """Raised when session operations fail."""
    pass


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass 