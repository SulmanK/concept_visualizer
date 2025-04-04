"""
Core Supabase client implementation.

This module provides the base SupabaseClient class for interacting with Supabase.
"""

import logging
from typing import Optional

from supabase import create_client
from postgrest.exceptions import APIError as PostgrestAPIError

from ..config import settings, get_masked_value
from ..exceptions import DatabaseError, StorageError
from ...utils.security.mask import mask_id


# Configure logging
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Base client for interacting with Supabase."""
    
    def __init__(self, url: str = None, key: str = None, session_id: Optional[str] = None):
        """Initialize Supabase client with configured settings.
        
        Args:
            url: Supabase project URL (defaults to settings.SUPABASE_URL)
            key: Supabase API key (defaults to settings.SUPABASE_KEY)
            session_id: Optional session ID to store for later use
            
        Raises:
            DatabaseError: If client initialization fails
        """
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY
        self.logger = logging.getLogger("supabase_client")
        self.session_id = session_id
        
        try:
            # Initialize Supabase client
            self.client = create_client(self.url, self.key)
            
            # Log initialization with masked session ID if present
            if session_id:
                self.logger.debug(f"Initialized Supabase client with session: {mask_id(session_id)}")
            else:
                self.logger.debug("Initialized Supabase client without session ID")
        except Exception as e:
            error_message = f"Failed to initialize Supabase client: {str(e)}"
            self.logger.error(error_message)
            raise DatabaseError(
                message=error_message,
                details={"url": self.url, "session_id": mask_id(self.session_id) if self.session_id else None}
            )
    
    def _mask_path(self, path: str) -> str:
        """Mask a storage path to protect session ID privacy.
        
        Args:
            path: Storage path potentially containing session ID
            
        Returns:
            Masked path with session ID portion obscured
        """
        if not path or "/" not in path:
            return path
            
        # Split path at first slash to separate session ID from filename
        parts = path.split("/", 1)
        if len(parts) >= 2:
            session_part = parts[0]
            file_part = parts[1]
            return f"{get_masked_value(session_part)}/{file_part}"
        return path
    
    def purge_all_data(self, session_id: Optional[str] = None) -> bool:
        """Purge all data for a session or all data in the system.
        
        WARNING: This is a destructive operation! Use with caution.
        
        Args:
            session_id: Optional session ID to purge only data for this session
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            DatabaseError: If database operation fails
            StorageError: If storage operation fails
        """
        from .session_storage import SessionStorage
        from .concept_storage import ConceptStorage
        from .image_storage import ImageStorage
        
        session_storage = SessionStorage(self)
        concept_storage = ConceptStorage(self)
        image_storage = ImageStorage(self)
        
        try:
            if session_id:
                self.logger.warning(f"Purging all data for session ID {mask_id(session_id)}")
                
                try:
                    # Delete storage objects first (no DB constraints)
                    image_storage.delete_all_storage_objects("concepts", session_id)
                except Exception as e:
                    self.logger.error(f"Error deleting storage objects: {str(e)}")
                    raise StorageError(
                        message=f"Failed to delete storage objects for session: {str(e)}",
                        operation="delete_all",
                        bucket="concepts",
                        path=session_id,
                    )
                
                try:
                    # Delete concepts (and color_variations via cascading delete)
                    concept_storage.delete_all_concepts(session_id)
                except PostgrestAPIError as e:
                    self.logger.error(f"Database error deleting concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Failed to delete concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                except Exception as e:
                    self.logger.error(f"Error deleting concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Unexpected error deleting concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                
                # Session will remain unless explicitly deleted
                self.logger.info(f"Successfully purged all data for session ID {mask_id(session_id)}")
            else:
                self.logger.warning("PURGING ALL DATA FROM THE SYSTEM!")
                
                try:
                    # Delete all storage objects
                    image_storage.delete_all_storage_objects("concepts")
                except Exception as e:
                    self.logger.error(f"Error deleting all storage objects: {str(e)}")
                    raise StorageError(
                        message=f"Failed to delete all storage objects: {str(e)}",
                        operation="delete_all",
                        bucket="concepts",
                    )
                
                try:
                    # Delete all concepts (and color_variations via cascading delete)
                    self.client.table("concepts").delete().execute()
                except PostgrestAPIError as e:
                    self.logger.error(f"Database error deleting all concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Failed to delete all concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                except Exception as e:
                    self.logger.error(f"Error deleting all concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Unexpected error deleting all concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                
                try:
                    # Delete all sessions
                    session_storage.delete_all_sessions()
                except Exception as e:
                    self.logger.error(f"Error deleting all sessions: {str(e)}")
                    raise DatabaseError(
                        message=f"Failed to delete all sessions: {str(e)}",
                        operation="delete",
                        table="sessions",
                    )
                
                self.logger.warning("Successfully purged ALL data from the system")
                
            return True
        except (DatabaseError, StorageError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error purging data: {str(e)}")
            raise DatabaseError(
                message=f"Unexpected error during data purge: {str(e)}",
                details={"session_id": mask_id(session_id) if session_id else "all_sessions"}
            )


def get_supabase_client(session_id: Optional[str] = None) -> SupabaseClient:
    """Create a Supabase client with the specified session ID.
    
    Args:
        session_id: Optional session ID to use
        
    Returns:
        Configured SupabaseClient instance
        
    Raises:
        DatabaseError: If client initialization fails
    """
    return SupabaseClient(session_id=session_id) 