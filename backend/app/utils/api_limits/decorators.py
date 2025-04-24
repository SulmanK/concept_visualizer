"""Rate limit decorators.

This module provides decorators for handling rate limit information.
"""

import logging
from functools import wraps
from typing import Any, Awaitable, Callable, TypeVar, cast

from fastapi import Request

from app.core.limiter import check_rate_limit, get_user_id

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable[..., Awaitable[Any]])


def store_rate_limit_info(endpoint_path: str, limit_string: str) -> Callable[[T], T]:
    """Decorator that stores rate limit information in request.state.

    This decorator checks the current rate limit status and stores it in
    request.state.limiter_info for the middleware to use when adding
    response headers.

    Args:
        endpoint_path: The path of the endpoint (e.g., "/concepts/generate")
        limit_string: The rate limit string (e.g., "10/month")

    Returns:
        Decorator function that wraps the endpoint handler
    """

    def decorator(func: T) -> T:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Find the Request object in args or kwargs
            request = None

            # First check if any args are a Request instance
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break

            # If not found in args, check kwargs for common request parameter names
            if not request:
                for param_name in ["request", "req"]:
                    if param_name in kwargs and isinstance(kwargs[param_name], Request):
                        request = kwargs[param_name]
                        break

            # If we found a request object, get the user ID and store limit info
            if request:
                # Get the user ID for rate limiting
                user_id = get_user_id(request)

                if not user_id:
                    # Log warning but don't block the request
                    logger.warning(f"No user ID found for rate limit info on {endpoint_path}")
                else:
                    try:
                        # Get current rate limit info without incrementing (check_only=True)
                        limit_status = check_rate_limit(
                            user_id=user_id,
                            endpoint=endpoint_path,
                            limit=limit_string,
                            check_only=True,
                        )

                        # Store in request.state for the middleware to use
                        request.state.limiter_info = {
                            "limit": limit_status.get("limit", 0),
                            "remaining": limit_status.get("remaining", 0),
                            "reset": limit_status.get("reset_at", 0),
                        }

                        logger.debug(f"Stored rate limit info for {endpoint_path}: " f"remaining={limit_status.get('remaining', 0)}")
                    except Exception as e:
                        logger.error(f"Error storing rate limit info: {str(e)}")
            else:
                logger.warning(f"Request object not found in handler for {endpoint_path}, rate limit headers won't be added")

            # Call the original handler
            return await func(*args, **kwargs)

        return cast(T, wrapper)

    return decorator
