# Concept Storage

The `concept_storage.py` module provides specialized storage and retrieval operations for concept data in the Concept Visualizer API.

## Overview

This module is responsible for:

1. Storing and retrieving concept data from Supabase
2. Managing the relationship between concepts and their image variations
3. Enforcing Row Level Security (RLS) policies for user data
4. Optimizing database operations for performance
5. Supporting both regular and administrative data operations

## ConceptStorage Class

The primary class for managing concept data:

```python
class ConceptStorage:
    """Handles concept-related operations in Supabase database."""

    def __init__(self, client: SupabaseClient):
        """
        Initialize with a Supabase client.

        Args:
            client: SupabaseClient instance
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
```

## Key Operations

### Storing Concepts

```python
def store_concept(
    self,
    concept_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Store a new concept in the database.

    Args:
        concept_data: Dictionary containing:
            - user_id: UUID of the user who created the concept
            - logo_description: Text description of the logo
            - theme_description: Text description of the theme
            - image_path: Path to the image in Storage
            - image_url: Optional URL to the image (signed URL)
            - is_anonymous: Whether the user is anonymous

    Returns:
        The created concept object or None if creation failed

    Raises:
        DatabaseError: If database operation fails
    """
    # Implementation...
```

This method inserts a new concept record and returns the created object.

### Storing Color Variations

```python
def store_color_variations(
    self,
    variations: List[Dict[str, Any]]
) -> Optional[List[Dict[str, Any]]]:
    """
    Store color variations for a concept.

    Args:
        variations: List of variation dictionaries, each containing:
            - concept_id: UUID of the parent concept
            - palette_name: Name of the color palette
            - colors: JSON array of hex color codes
            - image_path: Path to the variation image in Storage
            - image_url: Optional URL to the image (signed URL)

    Returns:
        List of created variation objects or None if creation failed

    Raises:
        DatabaseError: If database operation fails
    """
    # Implementation...
```

This method inserts multiple color variations for a concept in a single operation.

### Retrieving Recent Concepts

```python
def get_recent_concepts(
    self,
    user_id: str,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get most recent concepts for a user with their variations.

    Args:
        user_id: UUID of the user
        limit: Maximum number of concepts to return

    Returns:
        List of concept objects with their color variations

    Raises:
        DatabaseError: If database operation fails
    """
    # Implementation...
```

This method retrieves the most recent concepts for a user, including their color variations, ordered by creation date.

### Retrieving Concept Details

```python
def get_concept_detail(
    self,
    concept_id: str,
    user_id: str
) -> Optional[Dict[str, Any]]:
    """
    Get detailed information about a specific concept.

    Args:
        concept_id: UUID of the concept
        user_id: UUID of the requesting user

    Returns:
        Concept object with color variations or None if not found

    Raises:
        DatabaseError: If database operation fails
    """
    # Implementation...
```

This method retrieves a specific concept with all its color variations, ensuring the requesting user has access.

### Administrative Operations

The class provides methods with administrative privileges for operations requiring service role access:

```python
def _store_concept_with_service_role(
    self,
    concept_data: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Store a concept using the service role to bypass RLS.

    Args:
        concept_data: Concept data to store

    Returns:
        Created concept or None if failed
    """
    # Implementation...
```

```python
def _get_recent_concepts_with_service_role(
    self,
    user_id: str,
    limit: int
) -> List[Dict[str, Any]]:
    """
    Get recent concepts using the service role to bypass RLS.

    Args:
        user_id: UUID of the user
        limit: Maximum number of concepts to return

    Returns:
        List of concept objects with variations
    """
    # Implementation...
```

These methods use the service role for improved performance or administrative access.

## Database Schema

The module interacts with the following database tables:

### Concepts Table

```sql
CREATE TABLE concepts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    logo_description TEXT NOT NULL,
    theme_description TEXT,
    image_path TEXT NOT NULL,
    image_url TEXT,
    is_anonymous BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Color Variations Table

```sql
CREATE TABLE color_variations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    concept_id UUID NOT NULL REFERENCES concepts(id) ON DELETE CASCADE,
    palette_name TEXT NOT NULL,
    colors JSONB NOT NULL,
    description TEXT,
    image_path TEXT NOT NULL,
    image_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

## Usage Examples

### Creating a New Concept

```python
from app.core.supabase import get_supabase_client, ConceptStorage

# Initialize the client and storage
client = get_supabase_client()
storage = ConceptStorage(client)

# Prepare concept data
concept_data = {
    "user_id": "550e8400-e29b-41d4-a716-446655440000",
    "logo_description": "A minimalist logo for a tech startup with a rocket theme",
    "theme_description": "Modern, sleek design with blue tones",
    "image_path": "concepts/550e8400-e29b-41d4-a716-446655440000/base_logo.png",
    "image_url": "https://example.com/storage/concepts/550e8400-e29b-41d4-a716-446655440000/base_logo.png",
    "is_anonymous": False
}

# Store the concept
try:
    new_concept = storage.store_concept(concept_data)

    if new_concept:
        concept_id = new_concept["id"]
        print(f"Created concept with ID: {concept_id}")
    else:
        print("Failed to create concept")

except Exception as e:
    print(f"Error: {str(e)}")
```

### Adding Color Variations

```python
# Prepare color variations
variations = [
    {
        "concept_id": concept_id,
        "palette_name": "Blue Ocean",
        "colors": ["#1A2B3C", "#4D5E6F", "#7D8E9F"],
        "description": "A cool blue palette",
        "image_path": f"concepts/550e8400-e29b-41d4-a716-446655440000/var_blue_ocean.png",
        "image_url": f"https://example.com/storage/concepts/550e8400-e29b-41d4-a716-446655440000/var_blue_ocean.png"
    },
    {
        "concept_id": concept_id,
        "palette_name": "Sunset Red",
        "colors": ["#C41E3A", "#FF5733", "#FFC300"],
        "description": "A warm red palette",
        "image_path": f"concepts/550e8400-e29b-41d4-a716-446655440000/var_sunset_red.png",
        "image_url": f"https://example.com/storage/concepts/550e8400-e29b-41d4-a716-446655440000/var_sunset_red.png"
    }
]

# Store the variations
try:
    new_variations = storage.store_color_variations(variations)

    if new_variations:
        print(f"Created {len(new_variations)} color variations")
    else:
        print("Failed to create color variations")

except Exception as e:
    print(f"Error: {str(e)}")
```

### Retrieving User's Recent Concepts

```python
# Get user's recent concepts
try:
    user_id = "550e8400-e29b-41d4-a716-446655440000"
    recent_concepts = storage.get_recent_concepts(user_id, limit=5)

    print(f"Retrieved {len(recent_concepts)} recent concepts")

    for concept in recent_concepts:
        print(f"Concept ID: {concept['id']}")
        print(f"Description: {concept['logo_description']}")
        print(f"Variations: {len(concept.get('variations', []))}")
        print()

except Exception as e:
    print(f"Error: {str(e)}")
```

### Getting Concept Details

```python
# Get details for a specific concept
try:
    concept_id = "a1b2c3d4-e5f6-4a5b-9c8d-1a2b3c4d5e6f"
    user_id = "550e8400-e29b-41d4-a716-446655440000"

    concept_detail = storage.get_concept_detail(concept_id, user_id)

    if concept_detail:
        print(f"Concept: {concept_detail['logo_description']}")
        print(f"Theme: {concept_detail.get('theme_description', 'No theme')}")
        print(f"Created: {concept_detail['created_at']}")
        print(f"Variations:")

        for variation in concept_detail.get('variations', []):
            print(f"  - {variation['palette_name']}: {variation['colors']}")
    else:
        print("Concept not found or access denied")

except Exception as e:
    print(f"Error: {str(e)}")
```

## Performance Considerations

### Service Role Operations

For performance-critical operations, the module provides service role methods that bypass Row Level Security:

```python
# Direct service role access for better performance
recent_concepts = storage._get_recent_concepts_with_service_role(user_id, limit=10)
```

These methods should be used carefully as they bypass security checks.

### Query Optimization

The module implements several query optimizations:

1. **Batched Inserts**: Uses PostgreSQL's batch insert capability for multiple variations
2. **Joint Queries**: Efficiently retrieves concepts with their variations in minimal queries
3. **Explicit Selection**: Selects only required fields to minimize data transfer
4. **Request Coalescing**: Combines related operations to reduce round trips

Example of optimized query:

```python
# Optimized query that retrieves concepts and variations together
def get_concept_with_variations(self, concept_id: str):
    result = self.client.rpc(
        "get_concept_with_variations",
        {"p_concept_id": concept_id}
    ).execute()

    # Process and return the result...
```

## Security Considerations

### Row Level Security

The module is designed to work with Supabase Row Level Security policies:

```sql
-- Example RLS policy for concepts table
CREATE POLICY "Users can only access their own concepts"
  ON concepts
  FOR ALL
  USING (auth.uid() = user_id);
```

### Data Validation

The module validates input data before storing it:

```python
# Example validation
def _validate_concept_data(self, concept_data: Dict[str, Any]) -> bool:
    required_fields = ["user_id", "logo_description", "image_path"]

    for field in required_fields:
        if field not in concept_data or not concept_data[field]:
            return False

    return True
```

### Error Handling

The module includes comprehensive error handling:

```python
try:
    # Attempt database operation
    result = self.client.from_("concepts").insert(concept_data).execute()

    if "error" in result:
        self.logger.error(f"Database error: {result['error']}")
        return None

    return result["data"][0] if result.get("data") else None

except Exception as e:
    # Log the error with masked sensitive data
    masked_user_id = mask_id(concept_data.get("user_id", ""))
    self.logger.error(f"Failed to store concept for user {masked_user_id}: {str(e)}")

    # Propagate as database error
    raise DatabaseError(f"Failed to store concept: {str(e)}")
```

## Related Documentation

- [Supabase Client](client.md): Base client used by the concept storage
- [Image Storage](image_storage.md): Storage for concept images
- [Concept Persistence Service](../../services/persistence/concept_persistence_service.md): Higher-level service that uses this storage
- [Concept Service](../../services/concept/service.md): Business logic for concepts
