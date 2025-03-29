"""
Session management service.

This module provides a service for managing user sessions with Supabase,
including creating sessions, retrieving existing sessions, and
handling session cookies.
"""

from fastapi import Depends, Cookie, Response
from typing import Optional, Tuple
import uuid
import logging
from ..core.supabase import get_supabase_client, SupabaseClient

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
        session_id: Optional[str] = Cookie(None, alias="concept_session")
    ) -> Tuple[str, bool]:
        """Get existing session or create a new one.
        
        Args:
            response: FastAPI response object for setting cookies
            session_id: Optional existing session ID from cookies
            
        Returns:
            Tuple of (session_id, is_new_session)
        """
        is_new_session = False
        
        if not session_id:
            self.logger.info("No session ID found in cookie, creating new session")
            # Create new session
            session = self.supabase_client.create_session()
            if session:
                session_id = session["id"]
                is_new_session = True
                self.logger.info(f"Created new session with ID: {session_id}")
            else:
                # Fallback to a local UUID if Supabase is unavailable
                session_id = str(uuid.uuid4())
                is_new_session = True
                self.logger.warning(f"Supabase unavailable, created local session ID: {session_id}")
        else:
            self.logger.info(f"Found existing session ID in cookie: {session_id}")
            # Validate session exists and update last_active_at
            session = self.supabase_client.get_session(session_id)
            if not session:
                # Session ID in cookie doesn't exist in database
                self.logger.warning(f"Session ID {session_id} not found in database, creating new session")
                # Create a new session instead
                session = self.supabase_client.create_session()
                if session:
                    session_id = session["id"]
                    is_new_session = True
                    self.logger.info(f"Created new session with ID: {session_id}")
                else:
                    session_id = str(uuid.uuid4())
                    is_new_session = True
                    self.logger.warning(f"Supabase unavailable, created local session ID: {session_id}")
            else:
                # Update last_active_at for existing session
                self.logger.info(f"Updating last_active_at for session ID: {session_id}")
                self.supabase_client.update_session_activity(session_id)
        
        # Set session cookie
        response.set_cookie(
            key="concept_session",
            value=session_id,
            httponly=True,
            max_age=60*60*24*30,  # 30 days
            samesite="lax",
            secure=True  # Set to False in development if needed
        )
        
        return session_id, is_new_session
    
    def get_session_client(self, session_id: str) -> SupabaseClient:
        """Get a Supabase client configured with the session ID in headers.
        
        Args:
            session_id: Session ID to include in client headers
            
        Returns:
            Supabase client with session ID in headers
        """
        return get_supabase_client(session_id=session_id)


# Dependency function for FastAPI routes
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