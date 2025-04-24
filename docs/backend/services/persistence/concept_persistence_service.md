# Concept Persistence Service

The `concept_persistence_service.py` module provides a high-level service for storing and retrieving concept data in the Concept Visualizer API.

## Overview

This service acts as an abstraction layer over the Supabase database, providing:

1. Simplified concept storage and retrieval operations
2. Consistent error handling for database operations
3. Transaction management for multi-step operations
4. Security controls for concept access
5. Metadata management for concepts and associated color palettes

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

    Returns:
        ID of the stored concept

    Raises:
        PersistenceError: If storage fails
        DatabaseTransactionError: If a multi-step operation fails and cleanup is required
    """
    # Implementation...
```

This comprehensive method handles:

- Storing the core concept data
- Attaching color palette variations if provided
- Transaction management with rollback capabilities
- Error handling with detailed logging
- Security considerations with PII masking

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
    # Implementation...
```

Retrieves complete concept information including:

- Base concept data
- Associated color palettes
- Image paths and URLs
- Security checking to ensure the user has access

### Listing Recent Concepts

```python
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
    # Implementation...
```

Retrieves a paginated list of recent concepts with:

- Core concept data
- Thumbnail image URLs
- Creation timestamps
- Limited to the specified user for security

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
    # Implementation...
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
    # Implementation...
```

Supports the asynchronous task workflow by:

- Looking up concepts associated with background tasks
- Enabling status checking for long-running operations
- Maintaining security boundaries with user validation

## Transaction Management

The service implements sophisticated transaction management to ensure data consistency:

```python
async def _delete_concept(self, concept_id: str) -> bool:
    """
    Helper method to delete a concept as part of transaction cleanup.

    Args:
        concept_id: ID of the concept to delete

    Returns:
        True if deletion was successful, False otherwise
    """
    # Implementation...
```

When storing complex concept data with multiple components (like color palettes):

1. Core concept data is stored first
2. If color palette storage fails, core concept is automatically deleted
3. Detailed transaction status is recorded in logs
4. Service role escalation is used when necessary for cleanup

## Error Handling

The service defines custom exception types:

```python
class PersistenceError(Exception):
    """Exception raised for persistence errors."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
```

These exceptions provide:

- Specific error types for different failure scenarios
- Detailed error messages for troubleshooting
- Clean integration with the API error handling system

## Security Considerations

The service implements several security measures:

1. **User Access Control**: Each operation validates the requesting user
2. **PII Masking**: Sensitive IDs and paths are masked in logs
3. **Least Privilege**: Uses standard permissions for normal operations
4. **Elevated Privileges**: Uses service roles only when absolutely required
5. **Security Logging**: Records all access attempts

## Related Documentation

- [Persistence Interface](interface.md): Interface definition for this service
- [ConceptStorage](../../core/supabase/concept_storage.md): Underlying storage used by this service
- [Supabase Client](../../core/supabase/client.md): Database client used for persistence
- [Database Exceptions](../../core/exceptions.md): Exceptions used for error handling
- [Security Masking](../../utils/security/mask.md): PII masking utilities
