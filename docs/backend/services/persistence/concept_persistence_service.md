# Concept Persistence Service

The `concept_persistence_service.py` module provides a high-level service for storing and retrieving concept data in the Concept Visualizer API.

## Overview

This service acts as an abstraction layer over the Supabase database, providing:

1. Simplified concept storage and retrieval operations
2. Consistent error handling for database operations
3. Transaction management for multi-step operations
4. Security controls for concept access
5. Metadata management for concepts and associated color palettes

## Exception Types

The service defines specific exception types for error handling:

```python
class PersistenceError(Exception):
    """Exception raised for persistence errors."""
    pass

class NotFoundError(Exception):
    """Exception raised when a resource is not found."""
    pass
```

## ConceptPersistenceService Class

The primary class for concept persistence operations:

```python
class ConceptPersistenceService(ConceptPersistenceServiceInterface):
    """Service for storing and retrieving concepts."""

    def __init__(self, client: SupabaseClient):
        """
        Initialize the concept persistence service.

        Args:
            client: Supabase client instance
        """
        self.supabase = client
        self.concept_storage = ConceptStorage(client)
        self.logger = logging.getLogger("concept_persistence_service")
```

## Key Operations

### Storing Concepts

```python
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
            - is_anonymous: Whether the concept is anonymous (default: True)

    Returns:
        ID of the stored concept

    Raises:
        PersistenceError: If storage fails
        DatabaseTransactionError: If a multi-step operation fails and cleanup is required
    """
```

This comprehensive method handles:

- Storing the core concept data in the database
- Attaching color palette variations if provided
- Transaction management with rollback capabilities
- Error handling with detailed logging
- Security considerations with PII masking

#### Transaction Management

When storing complex concept data with multiple components (like color palettes):

1. Core concept data is stored first
2. Color palettes are stored in a separate transaction
3. If color palette storage fails, core concept is automatically deleted
4. Detailed transaction status is recorded in logs

```python
async def _delete_concept(self, concept_id: str) -> bool:
    """
    Helper method to delete a concept as part of transaction cleanup.

    Args:
        concept_id: ID of the concept to delete

    Returns:
        True if deletion was successful, False otherwise
    """
```

### Retrieving Concept Details

```python
async def get_concept_detail(self, concept_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific concept.

    Args:
        concept_id: ID of the concept to retrieve
        user_id: User ID for security validation

    Returns:
        Concept detail data including color variations

    Raises:
        NotFoundError: If concept not found
        PersistenceError: If retrieval fails
    """
```

Retrieves complete concept information including:

- Base concept data (ID, descriptions, creation time)
- Associated color palettes with image URLs
- Security checking to ensure the user has access to the concept
- URL generation for images stored in Supabase Storage

### Listing Recent Concepts

```python
async def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Get recent concepts for a user.

    Args:
        user_id: User ID to retrieve concepts for
        limit: Maximum number of concepts to return

    Returns:
        List of recent concepts with their color variations

    Raises:
        PersistenceError: If retrieval fails
    """
```

Retrieves a paginated list of recent concepts with:

- Core concept data (ID, descriptions, creation time)
- Image URLs for the concepts
- Color variations with their own image URLs
- Limited to the specified user for security
- Ordered by creation time (newest first)

### Deleting Concepts

```python
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
```

Handles bulk deletion operations with:

- User validation
- Cascading deletion (concepts and related color palettes)
- Result verification
- Extensive error handling

### Task-Based Concept Retrieval

```python
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
```

Supports the asynchronous task workflow by:

- Looking up concepts associated with background tasks
- Enabling status checking for long-running operations
- Maintaining security boundaries with user validation

## Integration with Supabase

The service uses the `ConceptStorage` class to handle direct interactions with the Supabase database:

```python
# Using concept_storage for database operations
concept = self.concept_storage.store_concept(core_concept_data)

# Directly using Supabase client for cleanup operations
result = self.supabase.table(settings.DB_TABLE_CONCEPTS).delete().eq("id", concept_id).execute()
```

This allows for:

1. Separation of concerns between service logic and database operations
2. Centralized database access patterns
3. Consistent error handling across different database operations

## Example Usage

```python
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.core.supabase.client import get_supabase_client

# Create an instance of the service
supabase_client = get_supabase_client()
persistence_service = ConceptPersistenceService(supabase_client)

# Store a concept
concept_id = await persistence_service.store_concept({
    "user_id": "user-123",
    "logo_description": "Modern tech logo with geometric shapes",
    "theme_description": "Blue and gray professional theme",
    "image_path": "concepts/user-123/image.png",
    "color_palettes": [
        {
            "name": "Cool Blues",
            "colors": ["#003366", "#336699", "#66CCFF"],
            "description": "Professional blue palette",
            "image_path": "palettes/user-123/palette1.png"
        }
    ]
})

# Retrieve concept details
concept = await persistence_service.get_concept_detail(concept_id, "user-123")

# Get recent concepts
recent_concepts = await persistence_service.get_recent_concepts("user-123", 5)
```

## Related Documentation

- [Persistence Interface](interface.md): Interface implemented by this service
- [Image Persistence Service](image_persistence_service.md): Complementary service for storing images
- [Supabase Client](../../core/supabase/client.md): Client for interacting with Supabase
- [Concept Storage](../../core/supabase/concept_storage.md): Direct database operations
