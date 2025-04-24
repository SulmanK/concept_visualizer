"""Rate limiter decorators.

This module provides decorators for custom rate limiting behaviors.
"""

import functools
import logging
from typing import Any, Callable, TypeVar, cast

from fastapi import Request

logger = logging.getLogger(__name__)

# Type variable for route handlers
F = TypeVar("F", bound=Callable[..., Any])


def safe_ratelimit(func: F) -> F:
    """Decorator to safely handle rate limiting errors.

    This decorator wraps a route handler to catch and handle any
    errors that occur during rate limiting operations to ensure the
    API endpoint doesn't fail if the rate limiter encounters issues.

    Args:
        func: The route handler function to wrap

    Returns:
        Wrapped route handler that handles rate limiting errors
    """

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            # Look for rate limiting related errors
            error_str = str(e).lower()
            if "rate limit" in error_str or "redis" in error_str:
                # Log the error but let the request through
                logger.error(f"Rate limiting error (allowing request): {e}")
                # Get the request from the arguments
                request = next((arg for arg in args if isinstance(arg, Request)), None)
                if request:
                    logger.error(f"Request path: {request.url.path}")
                # Continue processing the request
                # We remove the wrapper and call the original function directly
                return await func(*args, **kwargs)
            else:
                # Not a rate limiting error, re-raise
                raise

    return cast(F, wrapper)
