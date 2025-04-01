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
        is_new_session = False
        
        # Log cookie information
        self.logger.info("==== START SESSION MANAGEMENT ====")
        self.logger.info(f"Request cookie session_id: {session_id}")
        self.logger.info(f"Client-provided session_id: {client_session_id}")
        
        # Prioritize client_session_id when provided (frontend generated UUID)
        if client_session_id:
            self.logger.info(f"Using client-provided session ID: {client_session_id}")
            # Check if this client session ID exists in our database
            client_session = self.supabase_client.get_session(client_session_id)
            
            if client_session:
                # Client session exists in DB, use it
                self.logger.info(f"Client session ID found in database, using it: {client_session_id}")
                session_id = client_session_id
                self.supabase_client.update_session_activity(client_session_id)
            else:
                # Client session doesn't exist in DB, create it
                self.logger.info(f"Client session ID not found in database, creating entry: {client_session_id}")
                result = self.supabase_client.create_session_with_id(client_session_id)
                if result:
                    session_id = client_session_id
                    is_new_session = True
                    self.logger.info(f"Created database entry for client session ID: {client_session_id}")
                else:
                    # Fallback to generating UUID if we can't create entry
                    self.logger.warning(f"Failed to create session with client ID {client_session_id}, falling back to new session")
                    session_id = str(uuid.uuid4())
                    is_new_session = True
                    self.logger.info(f"Generated fallback session ID: {session_id}")
        # If no client_session_id, use cookie session_id
        elif session_id:
            self.logger.info(f"Using cookie-provided session ID: {session_id}")
            # Validate session exists and update last_active_at
            session = self.supabase_client.get_session(session_id)
            if not session:
                # Session ID in cookie doesn't exist in database
                self.logger.warning(f"Cookie session ID {session_id} not found in database, creating new session")
                # Create a new session instead
                session = self.supabase_client.create_session()
                if session:
                    # Store old and new session IDs for debugging
                    old_session_id = session_id
                    session_id = session["id"]
                    is_new_session = True
                    self.logger.info(f"Created new session with ID: {session_id} (replacing {old_session_id})")
                else:
                    session_id = str(uuid.uuid4())
                    is_new_session = True
                    self.logger.warning(f"Supabase unavailable, created local session ID: {session_id}")
            else:
                # Update last_active_at for existing session
                self.logger.info(f"Found existing session in database with ID: {session_id}")
                self.logger.info(f"Session data: {session}")
                self.supabase_client.update_session_activity(session_id)
        else:
            # No session ID available, create new
            self.logger.info("No session ID found, creating new session")
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
        
        # Set session cookie
        self.logger.info(f"Setting cookie 'concept_session' with value: {session_id}")
        response.set_cookie(
            key="concept_session",
            value=session_id,
            httponly=False,  # Need to be accessible from JavaScript
            max_age=60*60*24*30,  # 30 days
            samesite="lax",
            secure=False,  # Set to true in production with HTTPS
            path="/"
        )
        
        self.logger.info(f"Returning session_id: {session_id}, is_new_session: {is_new_session}")
        self.logger.info("==== END SESSION MANAGEMENT ====")
        
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