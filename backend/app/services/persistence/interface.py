"""
Interfaces for persistence services.

This module defines interfaces for storage and persistence services that store
and retrieve concepts, images, and other data.
"""

import abc
from typing import Dict, List, Any, Optional, Union


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


class ConceptPersistenceServiceInterface(abc.ABC):
    """Interface for concept persistence services."""
    
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
            PersistenceError: If storage fails
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
            PersistenceError: If retrieval fails
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
            PersistenceError: If retrieval fails
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
            PersistenceError: If deletion fails
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
            PersistenceError: If retrieval fails
        """
        pass


class ImagePersistenceServiceInterface(abc.ABC):
    """Interface for image persistence services."""
    
    @abc.abstractmethod
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
    
    @abc.abstractmethod
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
    
    @abc.abstractmethod
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
    
    @abc.abstractmethod
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