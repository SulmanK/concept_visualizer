"""
Interface for data storage services.
"""

import abc
from typing import Any, Dict, List, Optional, Union

class StorageServiceInterface(abc.ABC):
    """Interface for data storage services."""
    
    @abc.abstractmethod
    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """
        Store a concept and return its ID.
        
        Args:
            concept_data: Data to store
            
        Returns:
            ID of the stored concept
            
        Raises:
            StorageError: If storage fails
        """
        pass
    
    @abc.abstractmethod
    async def get_concept(self, concept_id: str) -> Dict[str, Any]:
        """
        Retrieve a concept by ID.
        
        Args:
            concept_id: ID of the concept to retrieve
            
        Returns:
            Concept data
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If retrieval fails
        """
        pass
    
    @abc.abstractmethod
    async def update_concept(self, concept_id: str, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a concept.
        
        Args:
            concept_id: ID of the concept to update
            concept_data: Updated data
            
        Returns:
            Updated concept data
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If update fails
        """
        pass
    
    @abc.abstractmethod
    async def delete_concept(self, concept_id: str) -> bool:
        """
        Delete a concept.
        
        Args:
            concept_id: ID of the concept to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If deletion fails
        """
        pass
    
    @abc.abstractmethod
    async def list_concepts(
        self, 
        session_id: Optional[str] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List concepts, optionally filtered by session.
        
        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of concepts to return
            offset: Number of concepts to skip
            
        Returns:
            List of concept data
            
        Raises:
            StorageError: If retrieval fails
        """
        pass
    
    @abc.abstractmethod
    async def associate_with_session(
        self, 
        concept_id: str, 
        session_id: str
    ) -> bool:
        """
        Associate a concept with a session.
        
        Args:
            concept_id: ID of the concept
            session_id: ID of the session
            
        Returns:
            True if association successful
            
        Raises:
            NotFoundError: If concept or session not found
            StorageError: If association fails
        """
        pass 