# Supabase Client

The `client.py` module provides the core client for interacting with Supabase services in the Concept Visualizer API.

## Overview

This module includes:

1. A base `SupabaseClient` class for general Supabase operations
2. An authentication-focused `SupabaseAuthClient` class
3. Factory functions for getting properly configured client instances

## SupabaseClient

The primary class for interacting with Supabase:

```python
class SupabaseClient:
    """Base client for interacting with Supabase."""

    def __init__(self, url: str = None, key: str = None, session_id: Optional[str] = None):
        """Initialize Supabase client with configured settings."""
        # Implementation...
```

### Key Features

- **Automatic Configuration**: Uses application settings by default
- **Session Tracking**: Can be initialized with a session ID for tracking
- **Error Handling**: Wraps Supabase errors in application-specific exceptions
- **Service Role Access**: Provides a method to get a client with elevated permissions

### Usage

```python
from app.core.supabase import SupabaseClient

# Create a client with default settings
client = SupabaseClient()

# Execute a query
result = client.client.from_("concepts").select("*").execute()
```

### Service Role Client

For administrative operations, you can get a client with elevated privileges:

```python
# Get a client with service role permissions
service_client = client.get_service_role_client()

# Perform administrative operations
service_client.from_("users").update({"role": "admin"}).eq("id", user_id).execute()
```

## SupabaseAuthClient

Specialized client for authentication operations:

```python
class SupabaseAuthClient:
    """Client for Supabase authentication."""

    def __init__(self, url: str = None, key: str = None):
        """Initialize the Supabase authentication client."""
        # Implementation...
```

### Key Features

- **Token Verification**: Verifies JWT tokens and extracts user data
- **Request Processing**: Extracts and validates authentication from HTTP requests
- **Secure Error Handling**: Provides detailed authentication error information

### Token Verification

```python
# Verify a JWT token
try:
    user_data = auth_client.verify_token(token)
    # Use user data
except AuthenticationError as e:
    # Handle authentication error
```

### Request Processing

```python
from fastapi import Request

# Extract user from request
async def endpoint(request: Request):
    try:
        user = auth_client.get_user_from_request(request)
        if user:
            # Process authenticated request
        else:
            # Handle unauthenticated request
    except AuthenticationError as e:
        # Handle authentication error
```

## Factory Functions

The module provides convenient factory functions to get client instances:

### get_supabase_client

```python
def get_supabase_client(session_id: Optional[str] = None) -> SupabaseClient:
    """Get a configured Supabase client.

    Args:
        session_id: Optional session ID to associate with the client

    Returns:
        Configured SupabaseClient instance
    """
    # Implementation...
```

### get_supabase_auth_client

```python
def get_supabase_auth_client() -> SupabaseAuthClient:
    """Get a configured Supabase authentication client.

    Returns:
        Configured SupabaseAuthClient instance
    """
    # Implementation...
```

## Error Handling

The module handles various error scenarios:

- **Client Initialization Failures**: Wraps initialization errors in `DatabaseError`
- **Authentication Failures**: Wraps authentication errors in `AuthenticationError`
- **Token Issues**: Provides specific error codes for token expiration, invalidity, etc.

## Security Considerations

The client implementation includes several security measures:

1. **Sensitive Data Masking**: User IDs and session IDs are masked in logs
2. **JWT Verification**: Tokens are verified using the JWT secret
3. **Required Claims**: JWT verification enforces required claims like expiration and subject

## Service Integration

The Supabase client is a critical component in several persistence services:

### Persistence Services

- **ConceptPersistenceService**: Uses the client to store and retrieve concept data

  ```python
  from app.core.supabase.client import SupabaseClient

  class ConceptPersistenceService:
      def __init__(self, client: SupabaseClient):
          self.client = client
          # ...
  ```

- **ImagePersistenceService**: Uses the client to manage image storage operations

### Dependency Injection

The `get_supabase_client` factory function is used in FastAPI dependency injection:

```python
from fastapi import Depends
from app.core.supabase.client import get_supabase_client, SupabaseClient

# In a dependency provider function
def get_concept_persistence_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
):
    return ConceptPersistenceService(client=supabase_client)
```

This pattern ensures that:

- Services have access to a properly configured Supabase client
- Session IDs can be propagated through the dependency chain
- Client configurations are centrally managed

## Related Documentation

- [Concept Storage](concept_storage.md): Uses the client for concept data operations
- [Image Storage](image_storage.md): Uses the client for image storage operations
- [Configuration](../config.md): Application settings used by the client
- [Exceptions](../exceptions.md): Custom exceptions used for error handling
- [Persistence Services](../../services/persistence/interface.md): Services that use the Supabase client
