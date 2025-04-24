# Rate Limiter Configuration

The `config.py` module in the limiter package provides the configuration and setup for the rate limiting system in the Concept Visualizer API.

## Overview

This module:

1. Configures a Redis-backed rate limiter using SlowAPI
2. Defines non-counting endpoints (health checks, etc.)
3. Provides fallback options for when Redis is unavailable
4. Sets up exception handlers for rate limit errors
5. Modifies the rate limiter to safely handle connection failures

## Key Components

### The Limiter Factory

The `configure_limiter` function creates a SlowAPI Limiter instance with appropriate configuration:

```python
def configure_limiter(debug: bool = False) -> Limiter:
    """
    Configure the rate limiter with appropriate settings.

    Args:
        debug: Whether to enable debug mode

    Returns:
        Configured Limiter instance
    """
    # Set up Redis store
    redis_client = get_redis_client()

    # Default rate limits if not configured in settings
    default_limits = getattr(settings, "DEFAULT_RATE_LIMITS", ["200/day", "50/hour", "10/minute"])

    # Rate limiting enabled by default
    rate_limiting_enabled = getattr(settings, "RATE_LIMITING_ENABLED", True)

    # Create limiter with Redis or memory backend
    # ...
```

### Setup Function

The `setup_limiter_for_app` function installs the rate limiter into a FastAPI application:

```python
def setup_limiter_for_app(app: FastAPI) -> None:
    """
    Set up rate limiting for a FastAPI application.

    Args:
        app: FastAPI application instance
    """
    # Configure limiter
    limiter = configure_limiter()

    # Add limiter to app state
    app.state.limiter = limiter

    # Register rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    # Load non-counting endpoints
    # ...
```

### Non-Counting Endpoints

The module tracks paths that should not count against rate limits:

```python
def is_non_counting_endpoint(request: Request) -> bool:
    """
    Check if the current request is for a non-counting endpoint.

    Args:
        request: The FastAPI request

    Returns:
        True if the endpoint should not count against rate limits
    """
    path = request.url.path

    # Check if the path is in the non-counting list
    for endpoint in NON_COUNTING_ENDPOINTS:
        if path == endpoint or path.startswith(endpoint):
            logger.debug(f"Request to non-counting endpoint: {path}")
            return True

    return False
```

### Safe Rate Limiting

The module patches the SlowAPI limiter to handle Redis failures gracefully:

```python
def safe_limit(*args, **kwargs):
    """Wrap the limit method to handle Redis connection errors."""
    limit_decorator = original_limit(*args, **kwargs)

    def wrapper(func):
        # Apply our safe_ratelimit decorator first, then the original limit
        safe_func = safe_ratelimit(func)

        # Modified handler that checks for non-counting endpoints
        # ...

        return wrapped

    return wrapper
```

## Usage

### Initializing the Rate Limiter

In the application factory:

```python
from app.core.limiter.config import setup_limiter_for_app

def create_app() -> FastAPI:
    app = FastAPI()

    # Set up rate limiting
    setup_limiter_for_app(app)

    return app
```

### Default Rate Limits

The module provides sensible defaults if none are configured:

```python
default_limits = ["200/day", "50/hour", "10/minute"]
```

These can be customized through the application settings.

### Non-Counting Endpoints

Health check endpoints and other diagnostic endpoints don't count against rate limits:

```python
NON_COUNTING_ENDPOINTS = [
    "/api/health/check",
    "/api/health/limits",
    # ...
]
```

## Fallback Behavior

If Redis is unavailable, the system falls back to in-memory storage:

```python
try:
    # Test Redis connection
    redis_client.ping()
    # Use Redis
except Exception as e:
    logger.warning(f"Redis connection failed, falling back to in-memory storage: {str(e)}")
    # Use in-memory storage
```

This ensures rate limiting continues to function even if Redis is down, although limits won't be synchronized across multiple instances.

## Related Documentation

- [Redis Store](redis_store.md): Redis client used by the rate limiter
- [Decorators](decorators.md): Endpoint-specific rate limit decorators
- [Keys](keys.md): Key functions used to identify rate-limited resources
- [Application Config](../config.md): General application settings
