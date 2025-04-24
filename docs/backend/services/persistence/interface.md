# Persistence Service Interfaces

The `interface.py` module defines the interfaces for persistence services in the Concept Visualizer API, ensuring consistent contracts for data storage and retrieval.

## Overview

This module provides abstract base classes that define the contracts for:

1. Core concept data persistence operations
2. Image persistence operations
3. General storage service capabilities

These interfaces enable:

- Dependency inversion for clean architecture
- Multiple implementations (e.g., for testing)
- Clear contracts for service consumers
- Documentation of expected behavior

## Interfaces

### StorageServiceInterface

Base interface for generic storage operations:

```python
class StorageServiceInterface(abc.ABC):
    """Interface for data storage services."""

    @abc.abstractmethod
    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """
        Store a concept and return its ID.

        Args:
            concept_data: Concept data to store

        Returns:
            ID of the stored concept

        Raises:
            StorageError: If storage fails
        """
        pass

    # Other abstract methods...
```

This base interface defines the minimal contract for concept storage operations.

### ConceptPersistenceServiceInterface

Specialized interface for concept-related persistence:

```python
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
```

This interface specifies the required operations for concept data persistence.

### ImagePersistenceServiceInterface

Specialized interface for image-related persistence:

```python
class ImagePersistenceServiceInterface(abc.ABC):
    """Interface for image persistence services."""

    @abc.abstractmethod
    def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "image/png",
        is_palette: bool = False
    ) -> Tuple[str, str]:
        """
        Store an image and return its path and URL.

        Args:
            image_data: Image data to store
            user_id: User ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            content_type: MIME type of the image
            is_palette: Whether the image is a palette (uses palette-images bucket)

        Returns:
            Tuple of (image_path, image_url)

        Raises:
            ImageStorageError: If image storage fails
        """
        pass

    @abc.abstractmethod
    async def get_image(self, image_path: str) -> bytes:
        """
        Retrieve an image by path.

        Args:
            image_path: Path of the image to retrieve

        Returns:
            Image data as bytes

        Raises:
            ImageNotFoundError: If image not found
            ImageStorageError: If retrieval fails
        """
        pass

    @abc.abstractmethod
    def get_image_url(self, image_path: str, expiration: int = 3600) -> str:
        """
        Get a URL for an image.

        Args:
            image_path: Path of the image
            expiration: Expiration time in seconds

        Returns:
            URL to access the image

        Raises:
            ImageStorageError: If URL generation fails
        """
        pass

    @abc.abstractmethod
    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image.

        Args:
            image_path: Path of the image to delete

        Returns:
            True if deletion was successful

        Raises:
            ImageStorageError: If deletion fails
        """
        pass

    @abc.abstractmethod
    def list_images(
        self,
        user_id: str,
        concept_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_metadata: bool = False
    ) -> List[Dict[str, Any]]:
        """
        List images for a user or concept.

        Args:
            user_id: User ID to list images for
            concept_id: Optional concept ID to filter by
            limit: Maximum number of images to return
            offset: Offset for pagination
            include_metadata: Whether to include metadata

        Returns:
            List of image information objects

        Raises:
            ImageStorageError: If listing fails
        """
        pass
```

This interface specifies the required operations for image persistence.

## Usage in Dependency Injection

These interfaces are used with FastAPI's dependency injection system:

```python
# In a route function
async def generate_concept(
    request: ConceptRequest,
    # Inject the interface, resolved to a concrete implementation
    persistence: ConceptPersistenceServiceInterface = Depends(get_concept_persistence_service)
):
    # Use the service through its interface
    concept_id = await persistence.store_concept({
        "user_id": request.user_id,
        "logo_description": request.logo_description,
        # ...other data
    })

    return {"concept_id": concept_id}
```

## Testing with Interfaces

The interfaces facilitate unit testing with mocks:

```python
# In a test file
from unittest.mock import AsyncMock

# Create a mock that conforms to the interface
mock_persistence = AsyncMock(spec=ConceptPersistenceServiceInterface)
mock_persistence.store_concept.return_value = "test-concept-id"

# Use the mock in a test
async def test_generate_concept():
    result = await generate_concept(
        request=ConceptRequest(...),
        persistence=mock_persistence
    )

    assert result["concept_id"] == "test-concept-id"
    mock_persistence.store_concept.assert_called_once()
```

## Related Documentation

- [ConceptPersistenceService](concept_persistence_service.md): Implementation of ConceptPersistenceServiceInterface
- [ImagePersistenceService](image_persistence_service.md): Implementation of ImagePersistenceServiceInterface
- [Concept Storage](../../core/supabase/concept_storage.md): Lower-level storage used by persistence services
