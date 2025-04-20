# Rate Limiter Decorators

The `decorators.py` module provides function decorators that implement rate limiting for FastAPI endpoints in the Concept Visualizer API.

## Overview

Rate limiting decorators are used to:

1. Apply rate limits to specific API endpoints
2. Handle Redis connection errors gracefully
3. Provide fallback behavior when rate limiting is unavailable

## Decorators

### Safe Rate Limit

```python
def safe_ratelimit(func: Callable[[Request], Awaitable[Any]]) -> Callable[[Request], Awaitable[Any]]:
    """
    Decorator to handle Redis connection errors during rate limiting.
    
    This decorator wraps rate-limited endpoint handlers to gracefully handle Redis
    connection errors, falling back to allowing the request rather than failing.
    
    Args:
        func: The endpoint handler function to decorate
        
    Returns:
        Callable: Wrapped function that handles Redis connection errors
    """
    # Implementation...
```

This decorator ensures that if Redis (the rate limit storage) is unavailable, the request continues to be processed rather than failing with an error. This resilience is important for maintaining API availability even when supporting services have issues.

## Usage

### Direct Usage

```python
from fastapi import APIRouter
from app.core.limiter.decorators import safe_ratelimit

router = APIRouter()

@router.post("/example")
@safe_ratelimit
async def example_endpoint(request: Request):
    # This endpoint will be protected with rate limiting,
    # but will still work even if Redis is down
    return {"message": "Success"}
```

### Used by the Rate Limiting System

In practice, these decorators are usually not used directly. Instead, they're integrated into the rate limiting system in `config.py`, which patches the SlowAPI limiter to use these decorators:

```python
# In app.core.limiter.config
def setup_limiter_for_app(app: FastAPI) -> None:
    # ...
    
    # Patch the limiter's limit method with our safe version
    original_limit = limiter.limit
    
    def safe_limit(*args, **kwargs):
        """Wrap the limit method to handle Redis connection errors."""
        limit_decorator = original_limit(*args, **kwargs)
        
        def wrapper(func):
            # Apply our safe_ratelimit decorator first, then the original limit
            safe_func = safe_ratelimit(func)
            # ...
```

## Error Handling

The decorator specifically handles Redis connection errors:

```python
try:
    # Call the rate-limited function
    result = await func(request, *args, **kwargs)
    return result
except redis.exceptions.ConnectionError as e:
    logger.error(f"Redis connection error during rate limiting: {str(e)}")
    logger.warning("Bypassing rate limit due to Redis connection error")
    # Continue processing the request without rate limiting
    # ...
```

When a Redis connection error occurs:
1. The error is logged
2. Rate limiting is bypassed
3. The request is allowed to proceed
4. The original handler function is called

## Fallback Behavior

If Redis is unavailable, the decorator attempts to call the original handler function:

```python
# If Redis is down, try to call the original function (before rate limiting)
if hasattr(func, '__wrapped__') and callable(func.__wrapped__):
    return await func.__wrapped__(request, *args, **kwargs)
else:
    # If no wrapped function, just call the function directly
    return await func(request, *args, **kwargs)
```

This ensures that API functionality continues even when rate limiting is unavailable.

## Benefits of Safe Rate Limiting

1. **Resilience**: The API continues to function even when Redis is down
2. **Graceful Degradation**: Rate limiting is bypassed rather than causing errors
3. **Transparent to Users**: Clients don't need to handle special cases for rate limiting failures

## Related Documentation

- [Config](config.md): Rate limiter configuration that uses these decorators
- [Keys](keys.md): Key functions used for rate limiting
- [Redis Store](redis_store.md): The Redis client used for rate limiting storage 