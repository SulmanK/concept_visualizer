"""
Session management services.

This package provides services for managing sessions and related data.
"""

from functools import lru_cache
from fastapi import Depends

from app.services.interfaces import SessionServiceInterface
from app.services.session.manager import SessionManager
from app.core.supabase.client import SupabaseClient, get_supabase_client

__all__ = ["SessionManager", "get_session_service"]


@lru_cache()
def get_session_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
) -> SessionServiceInterface:
    """
    Get a singleton instance of SessionManager.
    
    Args:
        supabase_client: Supabase client
        
    Returns:
        SessionManager: A service for managing sessions
    """
    return SessionManager(client=supabase_client) 