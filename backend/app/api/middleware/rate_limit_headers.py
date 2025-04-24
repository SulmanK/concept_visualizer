"""Rate limit headers middleware.

This middleware adds standard rate limit headers to API responses.
"""

import logging
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

# Configure logging
logger = logging.getLogger(__name__)


class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds rate limit headers to all API responses.

    This middleware extracts rate limit information from the request state
    and adds the appropriate X-RateLimit-* headers to the response.
    """

    def __init__(self, app: ASGIApp):
        """Initialize the middleware.

        Args:
            app: The ASGI application
        """
        super().__init__(app)
        self.logger = logging.getLogger("rate_limit_headers")

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add rate limit headers to the response.

        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler

        Returns:
            Response with rate limit headers added
        """
        # Process the request
        response: Response = await call_next(request)

        # Add rate limit headers if the information is available
        if hasattr(request.state, "limiter_info"):
            info = request.state.limiter_info

            # Extract rate limit information
            limit = info.get("limit", "")
            remaining = info.get("remaining", "")
            reset = info.get("reset", "")

            # Add headers only if we have valid data
            if limit and remaining and reset:
                response.headers["X-RateLimit-Limit"] = str(limit)
                response.headers["X-RateLimit-Remaining"] = str(remaining)
                response.headers["X-RateLimit-Reset"] = str(reset)

                # Log the headers (debug level)
                path = request.url.path
                self.logger.debug(f"Added rate limit headers to {path}: " f"limit={limit}, remaining={remaining}, reset={reset}")

        return response
