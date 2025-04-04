"""
Interface for session management services.
"""

import abc
from typing import Any, Dict, List, Optional

class SessionServiceInterface(abc.ABC):
    """Interface for session management services."""
    
    @abc.abstractmethod
    async def create_session(self) -> Dict[str, Any]:
        """
        Create a new session.
        
        Returns:
            Session data including ID and created_at timestamp
            
        Raises:
            SessionError: If session creation fails
        """
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    async def get_or_create_session(
        self, 
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get a session by ID or create a new one if it doesn't exist.
        
        Args:
            session_id: Optional ID of the session to retrieve
            
        Returns:
            Session data
            
        Raises:
            SessionError: If session retrieval or creation fails
        """
        pass 