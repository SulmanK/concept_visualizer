# Supabase Integration

The `supabase` package provides integration with Supabase for the Concept Visualizer API, handling database operations, authentication, and storage.

## Overview

Supabase is used as the primary data store and authentication provider for the application. This package provides:

1. **Core Client**: Base client for interacting with Supabase services
2. **Concept Storage**: Specialized storage for concept data
3. **Image Storage**: Specialized storage for image data

## Key Components

### 1. Client

The [`client.py`](client.md) module provides:

- `SupabaseClient`: Base client for Supabase interactions
- `SupabaseAuthClient`: Client specifically for authentication operations
- Factory functions to get properly configured client instances

```python
from app.core.supabase import get_supabase_client

# Get a client instance
client = get_supabase_client(session_id="user-session-123")

# Use it to interact with Supabase
result = client.from_("concepts").select("*").execute()
```

### 2. Concept Storage

The [`concept_storage.py`](concept_storage.md) module provides:

- `ConceptStorage`: Class for managing concept data in Supabase
- Methods for CRUD operations on concepts
- Specialized operations for concept refinement and organization

```python
from app.core.supabase import ConceptStorage

# Create storage with session
storage = ConceptStorage(session_id="user-session-123")

# Store a concept
concept_id = await storage.store_concept(
    user_id="user-123",
    prompt="A minimalist logo for a tech startup",
    image_url="https://example.com/image.png"
)
```

### 3. Image Storage

The [`image_storage.py`](image_storage.md) module provides:

- `ImageStorage`: Class for managing image files in Supabase Storage
- Methods for uploading, downloading, and managing image assets
- Support for various image formats and transformations

```python
from app.core.supabase import ImageStorage

# Create storage with session
storage = ImageStorage(session_id="user-session-123")

# Upload an image
path = await storage.upload_image(
    bucket="concepts",
    concept_id="concept-123",
    image_data=binary_image_data,
    content_type="image/png"
)
```

## Authentication Flow

The Supabase integration handles authentication through:

1. JWT token validation
2. Session management
3. User identification and authorization

The auth client provides methods to verify tokens and extract user information from requests.

## Error Handling

All Supabase operations include comprehensive error handling with custom exceptions:

- `DatabaseError`: For database operation failures
- `StorageError`: For storage operation failures
- `AuthenticationError`: For authentication failures

These exceptions provide detailed context about what went wrong for easier debugging.

## Configuration

Supabase integration is configured through environment variables:

- `CONCEPT_SUPABASE_URL`: URL of your Supabase project
- `CONCEPT_SUPABASE_KEY`: API key for Supabase access
- `CONCEPT_SUPABASE_JWT_SECRET`: Secret for JWT validation
- `CONCEPT_SUPABASE_SERVICE_ROLE`: Service role key for admin operations

## Related Documentation

- [Client](client.md): Base Supabase client implementation
- [Concept Storage](concept_storage.md): Concept data storage implementation
- [Image Storage](image_storage.md): Image storage implementation
- [Configuration](../config.md): Application configuration including Supabase settings
