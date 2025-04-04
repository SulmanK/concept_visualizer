"""
Session storage operations for Supabase.

This module provides functionality for managing sessions in Supabase.
"""

import logging
import uuid
from typing import Optional, Dict, Any

from .client import SupabaseClient
from ...utils.security.mask import mask_id


# Configure logging
logger = logging.getLogger(__name__)


class SessionStorage:
    """Handles session-related operations in Supabase."""
    
    def __init__(self, client: SupabaseClient):
        """Initialize with a Supabase client.
        
        Args:
            client: Configured SupabaseClient instance
        """
        self.client = client
        self.logger = logging.getLogger("supabase_session")
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID.
        
        Args:
            session_id: UUID of the session to retrieve
            
        Returns:
            Session data or None if not found
        """
        try:
            result = self.client.client.table("sessions").select("*").eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error retrieving session: {e}")
            return None
    
    def create_session(self) -> Optional[Dict[str, Any]]:
        """Create a new session.
        
        Returns:
            New session data with ID
        """
        try:
            result = self.client.client.table("sessions").insert({}).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return None
    
    def create_session_with_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Create a session with a specific ID.
        
        Args:
            session_id: Specific UUID to use for the session
            
        Returns:
            Created session data or None on error
        """
        try:
            # Make sure the session_id is a valid UUID format
            try:
                # Validate by parsing the UUID
                uuid_obj = uuid.UUID(session_id)
                # Ensure it's in the standard string format
                session_id = str(uuid_obj)
            except ValueError:
                self.logger.error(f"Invalid UUID format for session_id: {mask_id(session_id)}")
                return None
                
            # Insert the session with the provided ID
            result = self.client.client.table("sessions").insert({"id": session_id}).execute()
            
            # Log the result for debugging
            if result.data:
                self.logger.info(f"Created session with client-provided ID: {mask_id(session_id)}")
            else:
                self.logger.warning(f"No data returned when creating session with ID: {mask_id(session_id)}")
                
            return result.data[0] if result.data else None
            
        except Exception as e:
            self.logger.error(f"Error creating session with ID {mask_id(session_id)}: {e}")
            return None
    
    def update_session_activity(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Update session's last_active_at timestamp.
        
        Args:
            session_id: UUID of the session to update
            
        Returns:
            Updated session data or None on error
        """
        try:
            result = self.client.client.table("sessions").update(
                {"last_active_at": "now()"}
            ).eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error updating session activity: {e}")
            return None
    
    def delete_all_sessions(self) -> bool:
        """Delete all sessions from the database.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.client.table("sessions").delete().execute()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting all sessions: {e}")
            return False 