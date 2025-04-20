# Redis Store for Rate Limiting

The `redis_store.py` module provides a Redis-based storage backend for the rate limiting system in the Concept Visualizer API. It enables reliable, distributed rate limiting across multiple API instances.

## Overview

This module includes:

1. A connection manager that establishes connections to Redis
2. A `RedisStore` class that handles storage and retrieval of rate limiting data
3. Helper methods for managing rate limit counters with proper TTL (time-to-live)
4. Quota and rate limit checking functionality
5. Comprehensive error handling and fallbacks

## Connection Management

The module provides a `get_redis_client()` function to create and configure Redis connections:

```python
def get_redis_client() -> Optional[redis.Redis]:
    """
    Get a configured Redis client for rate limiting.
    
    Returns:
        Configured Redis client or None if Redis is not available
    """
    # Implementation...
```

This function:
- Checks for required configuration settings
- Creates a connection with proper timeouts and SSL configuration
- Tests the connection with a ping
- Returns None if configuration is missing or connection fails
- Handles errors gracefully with informative logging

## RedisStore Class

The `RedisStore` class is the core implementation:

```python
class RedisStore:
    """Redis-based storage for rate limiting data."""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "ratelimit:"):
        """
        Initialize with Redis client.
        
        Args:
            redis_client: Configured Redis client
            prefix: Key prefix for rate limit data in Redis
        """
        # Implementation...
```

### Key Operations

#### Incrementing Counters

```python
def increment(self, key: str, expiry: int, amount: int = 1) -> int:
    """
    Increment counter and set expiry.
    
    Args:
        key: Counter key
        expiry: Expiry time in seconds
        amount: Amount to increment by
        
    Returns:
        New counter value
    """
    # Implementation...
```

This method:
- Atomically increments a counter and sets its expiration time 
- Uses Redis pipeline for atomic operations
- Returns the new counter value
- Handles errors with safe fallbacks

#### Retrieving Counter Values

```python
def get(self, key: str) -> int:
    """
    Get current counter value.
    
    Args:
        key: Counter key
        
    Returns:
        Current counter value or 0 if not found
    """
    # Implementation...
```

```python
def get_with_expiry(self, key: str) -> Tuple[int, int]:
    """
    Get counter value with remaining expiry time.
    
    Args:
        key: Counter key
        
    Returns:
        Tuple of (current value, remaining seconds)
    """
    # Implementation...
```

These methods retrieve counter values and TTL information.

#### Rate Limit Checking

```python
def check_rate_limit(
    self, 
    user_id: str, 
    endpoint: str, 
    limit: int, 
    period: int,
    check_only: bool = False
) -> Tuple[bool, Dict[str, Any]]:
    """
    Check if a request is rate limited.
    
    Args:
        user_id: The user identifier (usually user ID or IP)
        endpoint: API endpoint being accessed
        limit: Maximum requests allowed
        period: Time period in seconds
        check_only: If True, don't increment the counter (for status checks)
        
    Returns:
        Tuple of (is_allowed, quota_info)
    """
    # Implementation...
```

This is the primary method used to enforce rate limits. It:
- Checks if a user has exceeded their quota for an endpoint
- Optionally increments the counter for actual requests
- Returns a boolean indicating if the request is allowed
- Provides detailed quota information for rate limit headers
- Handles errors with safe fallbacks (allowing requests if Redis fails)

#### Quota Information

```python
def get_quota(
    self, 
    user_id: str,
    endpoint: str, 
    limit: int,
    period: int
) -> Dict[str, Any]:
    """
    Get quota information for a user and endpoint.
    
    Args:
        user_id: The user identifier (usually user ID or IP)
        endpoint: API endpoint being accessed
        limit: Maximum requests allowed
        period: Time period in seconds
        
    Returns:
        Dict with quota information
    """
    # Implementation...
```

This method calculates and returns quota information:
- Total number of requests allowed
- Number of requests remaining
- Number of requests used
- Timestamp when the rate limit will reset

#### Maintenance Operations

```python
def reset(self, key: str) -> bool:
    """
    Reset a rate limit counter.
    
    Args:
        key: Counter key to reset
        
    Returns:
        True if successful, False otherwise
    """
    # Implementation...
```

```python
def clear_all(self) -> bool:
    """
    Clear all rate limit data (for testing).
    
    Returns:
        True if successful, False otherwise
    """
    # Implementation...
```

These methods provide maintenance capabilities for resetting counters.

## Usage Examples

### Creating a Redis Store

```python
from app.core.limiter.redis_store import get_redis_client, RedisStore

# Create a Redis client
redis_client = get_redis_client()

# Create the store if we have a valid client
if redis_client:
    store = RedisStore(redis_client)
```

### Checking Rate Limits

```python
# Check if a request should be allowed
user_id = "user:123"
endpoint = "/api/concept/generate"
limit = 10
period = 60  # seconds

is_allowed, quota = store.check_rate_limit(user_id, endpoint, limit, period)

if is_allowed:
    # Process the request
    pass
else:
    # Return a rate limit exceeded response
    response = {
        "error": "Rate limit exceeded",
        "quota": quota
    }
```

### Setting Rate Limit Headers

```python
# After checking a rate limit, add headers to the response
quota = store.get_quota(user_id, endpoint, limit, period)

headers = {
    "X-RateLimit-Limit": str(quota["total"]),
    "X-RateLimit-Remaining": str(quota["remaining"]),
    "X-RateLimit-Reset": str(quota["reset_at"])
}

# Return these headers with the response
```

## Error Handling

The module implements robust error handling throughout:

1. Redis connection errors are caught and logged
2. When Redis is unavailable, the system falls back to in-memory storage
3. If rate limit checking fails, requests are allowed by default
4. Quota values provide conservative estimates when accurate values can't be retrieved

This ensures the API remains functional even when Redis is experiencing issues.

## Key Security

The module includes security best practices:

1. Redis credentials are handled securely
2. Connection details are masked in logs
3. User IDs and rate limit keys are masked to avoid leaking sensitive information

## Related Documentation

- [Config](config.md): Configuration for the rate limiter
- [Keys](keys.md): Key functions used to identify rate-limited resources
- [Decorators](decorators.md): Rate limit decorators that use the Redis store
- [Rate Limit Apply Middleware](../../api/middleware/rate_limit_apply.md): Middleware that uses this store 