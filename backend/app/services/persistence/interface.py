"""Interfaces for persistence services.

This module defines interfaces for storage and persistence services that store
and retrieve concepts, images, and other data.
"""

import abc
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

from fastapi import UploadFile


class StorageServiceInterface(abc.ABC):
    """Interface for data storage services."""

    @abc.abstractmethod
    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """Store a concept and return its ID.

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
        """Get detailed information about a specific concept.

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
        """Get recent concepts for a user.

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
        """Delete all concepts for a user.

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
        """Get a concept by its task ID.

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
        """Store a concept and return its ID.

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
        """Get detailed information about a specific concept.

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
        """Get recent concepts for a user.

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
        """Delete all concepts for a user.

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
        """Get a concept by its task ID.

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
    async def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "image/png",
        is_palette: bool = False,
    ) -> Tuple[str, str]:
        """Store an image and return its path and URL.

        Args:
            image_data: Image data as bytes, BytesIO, or UploadFile
            user_id: User ID for the image owner
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            content_type: Content type of the image
            is_palette: Whether this is a palette image

        Returns:
            Tuple of (path, url) for the stored image

        Raises:
            PersistenceError: If storage fails
        """
        pass

    @abc.abstractmethod
    async def get_image(self, image_path: str) -> bytes:
        """Get image data by path.

        Args:
            image_path: Path to the image

        Returns:
            Image data as bytes

        Raises:
            NotFoundError: If image not found
            PersistenceError: If retrieval fails
        """
        pass

    @abc.abstractmethod
    def get_image_url(self, image_path: str, expiration: int = 3600) -> str:
        """Get a temporary URL for an image.

        Args:
            image_path: Path to the image
            expiration: Expiration time in seconds

        Returns:
            Temporary URL for the image

        Raises:
            NotFoundError: If image not found
            PersistenceError: If URL generation fails
        """
        pass

    @abc.abstractmethod
    def delete_image(self, image_path: str) -> bool:
        """Delete an image by path.

        Args:
            image_path: Path to the image to delete

        Returns:
            True if successful

        Raises:
            PersistenceError: If deletion fails
        """
        pass

    @abc.abstractmethod
    def list_images(
        self,
        user_id: str,
        concept_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_metadata: bool = False,
    ) -> List[Dict[str, Any]]:
        """List images for a user or concept.

        Args:
            user_id: User ID to list images for
            concept_id: Optional concept ID to filter by
            limit: Maximum number of images to return
            offset: Offset for pagination
            include_metadata: Whether to include image metadata

        Returns:
            List of image information dictionaries

        Raises:
            PersistenceError: If listing fails
            StorageError: If listing fails
        """
        pass
