"""
Session management service.

This module provides a service for managing user sessions with Supabase,
including creating sessions, retrieving existing sessions, and
handling session cookies.
"""

import logging
import uuid
from typing import Optional, Tuple

from fastapi import Depends, Cookie, Response
from ..core.supabase import get_supabase_client, SupabaseClient
from ..core.config import settings


# Configure logging
logger = logging.getLogger(__name__)


class SessionService:
    """Service for managing user sessions."""
    
    def __init__(self, supabase_client: SupabaseClient = Depends(get_supabase_client)):
        """Initialize session service with a Supabase client.
        
        Args:
            supabase_client: Client for interacting with Supabase
        """
        self.supabase_client = supabase_client
        self.logger = logging.getLogger("session_service")
    
    async def get_or_create_session(
        self, 
        response: Response,
        session_id: Optional[str] = Cookie(None, alias="concept_session"),
        client_session_id: Optional[str] = None
    ) -> Tuple[str, bool]:
        """Get existing session or create a new one.
        
        Args:
            response: FastAPI response object for setting cookies
            session_id: Optional existing session ID from cookies
            client_session_id: Optional session ID provided by client
            
        Returns:
            Tuple of (session_id, is_new_session)
        """
        # Log initial state
        self.logger.info("==== SESSION MANAGEMENT START ====")
        self.logger.info(f"Cookie session_id: {session_id}")
        self.logger.info(f"Client session_id: {client_session_id}")
        
        # Determine which session ID to use
        final_session_id = await self._resolve_session_id(
            cookie_session_id=session_id,
            client_session_id=client_session_id
        )
        
        # Set the cookie and return the result
        self._set_session_cookie(response, final_session_id)
        
        self.logger.info(f"Final session_id: {final_session_id['id']}, is_new: {final_session_id['is_new']}")
        self.logger.info("==== SESSION MANAGEMENT END ====")
        
        return final_session_id["id"], final_session_id["is_new"]
    
    async def _resolve_session_id(
        self, 
        cookie_session_id: Optional[str], 
        client_session_id: Optional[str]
    ) -> dict:
        """Determine which session ID to use based on priority.
        
        Args:
            cookie_session_id: Session ID from cookie
            client_session_id: Session ID provided by client
            
        Returns:
            Dictionary with the resolved session ID and whether it's new
        """
        # Priority 1: Check client-provided session ID if available
        if client_session_id:
            self.logger.info(f"Checking client-provided session ID: {client_session_id}")
            client_session = self.supabase_client.get_session(client_session_id)
            
            if client_session:
                self.logger.info(f"Using existing client session ID: {client_session_id}")
                self.supabase_client.update_session_activity(client_session_id)
                return {"id": client_session_id, "is_new": False}
            
            # Client session doesn't exist in DB, try to create it
            self.logger.info(f"Creating new session with client ID: {client_session_id}")
            result = self.supabase_client.create_session_with_id(client_session_id)
            if result:
                self.logger.info(f"Successfully created session with client ID: {client_session_id}")
                return {"id": client_session_id, "is_new": True}
        
        # Priority 2: Check cookie session ID if available
        if cookie_session_id:
            self.logger.info(f"Checking cookie session ID: {cookie_session_id}")
            cookie_session = self.supabase_client.get_session(cookie_session_id)
            
            if cookie_session:
                self.logger.info(f"Using existing cookie session ID: {cookie_session_id}")
                self.supabase_client.update_session_activity(cookie_session_id)
                return {"id": cookie_session_id, "is_new": False}
        
        # Priority 3: Create a new session
        self.logger.info("Creating new session")
        new_session = self.supabase_client.create_session()
        
        if new_session:
            self.logger.info(f"Created new session with ID: {new_session['id']}")
            return {"id": new_session["id"], "is_new": True}
        
        # Fallback: Generate local UUID if Supabase is unavailable
        fallback_id = str(uuid.uuid4())
        self.logger.warning(f"Supabase unavailable, using fallback ID: {fallback_id}")
        return {"id": fallback_id, "is_new": True}
    
    def _set_session_cookie(self, response: Response, session_data: dict) -> None:
        """Set the session cookie in the response.
        
        Args:
            response: FastAPI response object
            session_data: Dictionary with session ID and is_new flag
        """
        session_id = session_data["id"]
        
        # Determine if we're in production based on the Supabase URL
        # If not "pstdcfittpjhxzynbdbu.supabase.co" (development) we assume it's production
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
        
        self.logger.info(f"Setting session cookie: {session_id} (secure: {is_production})")
        response.set_cookie(
            key="concept_session",
            value=session_id,
            httponly=False,  # Need to be accessible from JavaScript
            max_age=60*60*24*30,  # 30 days
            samesite="lax",
            secure=is_production,  # True in production, False in development
            path="/"
        )
    
    def get_session_client(self, session_id: str) -> SupabaseClient:
        """Get a Supabase client configured with the session ID in headers.
        
        Args:
            session_id: Session ID to include in client headers
            
        Returns:
            Supabase client with session ID in headers
        """
        return get_supabase_client(session_id=session_id)


async def get_session_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client)
) -> SessionService:
    """Factory function for SessionService.
    
    Args:
        supabase_client: Supabase client dependency
        
    Returns:
        Configured SessionService instance
    """
    return SessionService(supabase_client) 