# Rate Limiter Keys

The `keys.py` module provides key generation functions for the rate limiting system in the Concept Visualizer API. These keys determine how rate limits are identified and applied to different users and endpoints.

## Overview

Rate limiting requires unique identifiers (keys) to track usage across different dimensions:

- Per-user limits (tracked by user ID)
- Per-endpoint limits (tracked by API route)
- Per-IP limits (for unauthenticated requests)
- Combined limits (e.g., user + endpoint)

This module provides functions to generate these keys in a consistent format.

## Key Functions

### User Identification

```python
def get_user_id(request: Request) -> str:
    """
    Get the user's ID from request state for rate limiting.
    Falls back to extracting from JWT token, then to IP address if no user ID is available.

    Args:
        request: FastAPI request object

    Returns:
        str: User ID or IP address to use as rate limit key
    """
    # Implementation details...
```

This function tries several methods to identify the user:

1. First tries to get the user ID from request state (set by auth middleware)
2. If not available, tries to extract from the JWT token in the Authorization header
3. Falls back to the client's IP address if no user identity is available

### Endpoint Identification

```python
def get_endpoint_key(request: Request) -> str:
    """
    Get a unique key for the current endpoint.

    Args:
        request: FastAPI request object

    Returns:
        str: Unique key for the endpoint
    """
    # Implementation details...
```

This function generates a key that uniquely identifies the API endpoint being called.

### Key Combination

```python
def combine_keys(user_id: str, endpoint_key: str) -> str:
    """
    Combine user and endpoint keys for granular rate limiting.

    Args:
        user_id: The user identifier (usually user ID or IP)
        endpoint_key: The endpoint identifier

    Returns:
        str: Combined key for rate limiting
    """
    return f"{user_id}:{endpoint_key}"
```

This function combines user and endpoint keys to create more granular rate limits.

### TTL Calculation

```python
def calculate_ttl(period: str) -> int:
    """
    Calculate the time-to-live (TTL) in seconds based on the rate limit period.

    Args:
        period: The time period (minute, hour, day, month)

    Returns:
        int: TTL in seconds
    """
    # Implementation details...
```

This function converts time period strings to seconds for Redis TTL values.

### Rate Limit Key Generation

```python
def generate_rate_limit_keys(user_id: str, endpoint: str, period: str) -> list[str]:
    """
    Generate all possible key formats for rate limiting.

    Args:
        user_id: The user identifier (usually session ID or IP)
        endpoint: The endpoint being rate limited (e.g., "/api/concept/generate")
        period: The time period (minute, hour, day, month)

    Returns:
        list[str]: List of possible rate limit keys
    """
    # Implementation details...
```

This function generates all possible key formats for comprehensive rate limiting.

## Key Formats

### User Identification Keys

- `user:{user_id}` - When a user ID is available
- `ip:{ip_address}` - When only an IP address is available

### Endpoint Keys

- `endpoint:{path}` - Standard endpoint key

### Combined Keys

- `{user_id}:{endpoint_key}` - Combined for per-user, per-endpoint limits
- `{user_id}:{period}` - For general per-user limits
- `POST:{endpoint}:{user_id}:{period}` - Format used by SlowAPI internally
- `{endpoint}:{user_id}:{period}` - Alternative format with path and user

### Special Keys

Special handling for certain endpoints, like SVG conversion:

```python
# SVG-specific keys
f"svg:{user_id}:{period}"
f"svg:POST:{endpoint}:{user_id}:{period}"
f"svg:{endpoint}:{user_id}:{period}"
```

## Usage Examples

### Using Keys in Rate Limit Decorators

```python
from app.core.limiter.decorators import rate_limit

@app.post("/api/concept/generate")
@rate_limit(limit="5/minute", key_func="user_endpoint")
async def generate_concept():
    # This endpoint uses combined user+endpoint keys
    # The key will be something like "user:123:endpoint:/api/concept/generate"
    # ...
```

### Manual Key Generation

```python
from fastapi import Depends, Request
from app.core.limiter.keys import get_user_id, get_endpoint_key, combine_keys

async def check_limit(request: Request):
    # Get keys for the current request
    user_key = get_user_id(request)
    endpoint_key = get_endpoint_key(request)
    combined_key = combine_keys(user_key, endpoint_key)

    # Use keys to check limits
    # ...
```

## Related Documentation

- [Redis Store](redis_store.md): Storage backend that uses these keys
- [Decorators](decorators.md): Rate limit decorators that use these key functions
- [Config](config.md): Configuration for the rate limiter system
