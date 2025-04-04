"""
Rate limiting decorators for the Concept Visualizer API.

This module provides decorators to handle rate limiting and Redis connection errors.
"""

import logging
import redis
from fastapi import Request
from typing import Any, Callable, Awaitable

# Configure logging
logger = logging.getLogger(__name__)

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
    async def wrapper(request: Request, *args: Any, **kwargs: Any) -> Any:
        try:
            # Make sure we're properly awaiting the decorated function
            result = await func(request, *args, **kwargs)
            return result
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection error during rate limiting: {str(e)}")
            logger.warning("Bypassing rate limit due to Redis connection error")
            # Continue processing the request without rate limiting
            # Make sure we're also properly awaiting the wrapped function
            if hasattr(func, '__wrapped__') and callable(func.__wrapped__):
                return await func.__wrapped__(request, *args, **kwargs)
            else:
                # If no wrapped function, just call the original
                return await func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Unexpected error during rate limiting: {str(e)}")
            # Re-raise other exceptions
            raise
    
    # Preserve metadata
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    
    return wrapper 