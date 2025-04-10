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
            concept_data: Concept data to store, including:
                - user_id: User ID to associate with the concept
                - logo_description: User's logo description
                - theme_description: User's theme description
                - image_path: Path to the generated base image
                - image_url: URL to the generated base image (optional)
                - color_palettes: Optional list of color palette dictionaries
                
        Returns:
            ID of the stored concept
            
        Raises:
            StorageError: If storage fails
        """
        pass
    
    @abc.abstractmethod
    async def get_concept_detail(self, concept_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific concept.
        
        Args:
            concept_id: ID of the concept to retrieve
            user_id: User ID for security validation
            
        Returns:
            Concept detail data
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If retrieval fails
        """
        pass
    
    @abc.abstractmethod
    async def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent concepts for a user.
        
        Args:
            user_id: User ID to retrieve concepts for
            limit: Maximum number of concepts to return
            
        Returns:
            List of recent concepts
            
        Raises:
            StorageError: If retrieval fails
        """
        pass
    
    @abc.abstractmethod
    async def delete_all_concepts(self, user_id: str) -> bool:
        """
        Delete all concepts for a user.
        
        Args:
            user_id: User ID to delete concepts for
            
        Returns:
            True if successful
            
        Raises:
            StorageError: If deletion fails
        """
        pass
    
    @abc.abstractmethod
    async def get_concept_by_task_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a concept by its task ID.
        
        Args:
            task_id: Task ID of the concept to retrieve
            user_id: User ID for security validation
            
        Returns:
            Concept data or None if not found
            
        Raises:
            StorageError: If retrieval fails
        """
        pass 