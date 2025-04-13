"""
Persistence service interfaces.

This module defines interfaces for persistence services that store
and retrieve data objects.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union


class PersistenceServiceInterface(ABC):
    """Interface for persistence services."""
    
    @abstractmethod
    async def store_data(self, data: Dict[str, Any]) -> str:
        """
        Store data and return its ID.
        
        Args:
            data: Data to store
            
        Returns:
            ID of the stored data
        """
        pass
    
    @abstractmethod
    async def get_data(self, data_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get data by ID.
        
        Args:
            data_id: ID of the data to retrieve
            user_id: User ID for security validation
            
        Returns:
            Retrieved data
        """
        pass
    
    @abstractmethod
    async def list_data(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List data for a user.
        
        Args:
            user_id: User ID to retrieve data for
            limit: Maximum number of items to return
            
        Returns:
            List of data items
        """
        pass
    
    @abstractmethod
    async def delete_data(self, data_id: str, user_id: str) -> bool:
        """
        Delete data by ID.
        
        Args:
            data_id: ID of the data to delete
            user_id: User ID for security validation
            
        Returns:
            True if deletion was successful
        """
        pass


class ConceptPersistenceServiceInterface(PersistenceServiceInterface):
    """Interface for concept persistence services."""
    
    @abstractmethod
    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """
        Store a concept and return its ID.
        
        Args:
            concept_data: Concept data to store
                
        Returns:
            ID of the stored concept
        """
        pass
    
    @abstractmethod
    async def get_concept_detail(self, concept_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific concept.
        
        Args:
            concept_id: ID of the concept to retrieve
            user_id: User ID for security validation
            
        Returns:
            Concept detail data
        """
        pass
    
    @abstractmethod
    async def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent concepts for a user.
        
        Args:
            user_id: User ID to retrieve concepts for
            limit: Maximum number of concepts to return
            
        Returns:
            List of recent concepts
        """
        pass
    
    @abstractmethod
    async def get_concept_by_task_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a concept by its task ID.
        
        Args:
            task_id: Task ID to retrieve the concept for
            user_id: User ID for security validation
            
        Returns:
            Concept data if found, None otherwise
        """
        pass


class ImagePersistenceServiceInterface(ABC):
    """Interface for image persistence services."""
    
    @abstractmethod
    def store_image(self, image_data: Union[bytes, Any], user_id: str, **kwargs) -> tuple:
        """
        Store an image and return its path and URL.
        
        Args:
            image_data: Image data to store
            user_id: User ID for security validation
            **kwargs: Additional keyword arguments
            
        Returns:
            Tuple of (path, url)
        """
        pass
    
    @abstractmethod
    def get_image(self, image_path: str, **kwargs) -> bytes:
        """
        Get an image by its path.
        
        Args:
            image_path: Path of the image to retrieve
            **kwargs: Additional keyword arguments
            
        Returns:
            Image data as bytes
        """
        pass
    
    @abstractmethod
    def get_signed_url(self, path: str, **kwargs) -> str:
        """
        Get a signed URL for an image.
        
        Args:
            path: Path of the image
            **kwargs: Additional keyword arguments
            
        Returns:
            Signed URL for the image
        """
        pass
    
    @abstractmethod
    def delete_image(self, image_path: str, **kwargs) -> bool:
        """
        Delete an image by its path.
        
        Args:
            image_path: Path of the image to delete
            **kwargs: Additional keyword arguments
            
        Returns:
            True if deletion was successful
        """
        pass 