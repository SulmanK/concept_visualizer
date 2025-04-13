"""
Rate limit application middleware.

This middleware applies rate limits to API requests based on their paths.
It centralizes rate limiting logic, removing it from individual route handlers.
"""

import logging
from typing import Callable, Dict, List
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from app.core.config import settings
from app.core.limiter import check_rate_limit, get_user_id
from app.core.limiter.keys import get_endpoint_key

# Configure logging
logger = logging.getLogger(__name__)

# Define rate limit rules for different endpoints
RATE_LIMIT_RULES = {
    "/concepts/generate-with-palettes": "10/month",
    "/concepts/refine": "10/month",
    "/concepts/store": "10/month",
    "/storage/store": "10/month",
    "/storage/recent": "30/minute",
    "/storage/concept": "30/minute",
    "/export/process": "50/hour",
}

# Define endpoints that need multiple rate limits
MULTIPLE_RATE_LIMITS = {
    "/concepts/generate-with-palettes": [
        {"endpoint": "/concepts/generate", "rate_limit": "10/month"},
        {"endpoint": "/concepts/store", "rate_limit": "10/month"}
    ],
}

# Public paths that should be excluded from rate limiting
PUBLIC_PATHS = [
    "/api/health",
    "/api/health/",
    "/api/health/check",
    "/api/health/rate-limits",
    "/api/health/rate-limits-status",
    "/api/auth/signin-anonymous",
    "/docs",
    "/redoc",
    "/openapi.json",
]


class RateLimitApplyMiddleware(BaseHTTPMiddleware):
    """
    Middleware that applies rate limits to API requests.
    
    This middleware checks if the request path matches any rate limit rules
    and applies the appropriate limits before passing the request to the handler.
    It centralizes the rate limiting logic that was previously in individual route handlers.
    """
    
    def __init__(self, app: ASGIApp):
        """
        Initialize the middleware.
        
        Args:
            app: The ASGI application
        """
        super().__init__(app)
        self.logger = logging.getLogger("rate_limit_apply")
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process the request and apply rate limits if applicable.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware or route handler
            
        Returns:
            Response from the next middleware or route handler
            
        Raises:
            HTTPException: If rate limit is exceeded
        """
        # Skip rate limiting if disabled in settings
        if not settings.RATE_LIMITING_ENABLED:
            self.logger.debug("Rate limiting disabled in settings")
            return await call_next(request)
            
        # Skip rate limiting if limiter is not available
        if not hasattr(request.app.state, 'limiter'):
            self.logger.warning("Rate limiter not available")
            return await call_next(request)
        
        # Skip rate limiting for non-API paths
        path = request.url.path
        if not path.startswith("/api/"):
            return await call_next(request)
            
        # Skip rate limiting for public paths that don't require authentication
        for public_path in PUBLIC_PATHS:
            if path == public_path or path.startswith(public_path):
                self.logger.debug(f"Skipping rate limiting for public path: {path}")
                return await call_next(request)
            
        # Remove /api prefix for matching
        relative_path = path[4:] if path.startswith("/api/") else path
        
        # Skip for OPTIONS method (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
            
        # Check if path has multiple rate limits
        rate_limit_applied = False
        
        # Get user ID for rate limiting
        user_id = get_user_id(request)
        
        # Handle multiple rate limits case first
        for prefix, limits in MULTIPLE_RATE_LIMITS.items():
            if relative_path.startswith(prefix):
                self.logger.debug(f"Applying multiple rate limits for path: {path}")
                
                # Check each rate limit
                most_restrictive_info = None
                for limit_config in limits:
                    endpoint = limit_config["endpoint"]
                    rate_limit = limit_config["rate_limit"]
                    
                    self.logger.info(f"Checking rate limit '{rate_limit}' for {user_id} on {endpoint}")
                    
                    # Check rate limit directly using our core function 
                    limit_info = check_rate_limit(user_id, endpoint, rate_limit)
                    is_rate_limited = limit_info.get("exceeded", False)
                    
                    # If rate limited, raise an exception
                    if is_rate_limited:
                        # Get information about the rate limit for the error message
                        reset_at = limit_info.get("reset_at", 0)
                        
                        # Create a more helpful error message
                        error_message = f"Rate limit exceeded for {endpoint} ({rate_limit}). Try again later."
                        
                        # Add Retry-After header if we have reset info
                        headers = {"Retry-After": str(reset_at)} if reset_at else {}
                        
                        self.logger.warning(f"Rate limit exceeded for {user_id} on {endpoint}")
                        
                        raise HTTPException(
                            status_code=429, 
                            detail=error_message,
                            headers=headers
                        )
                        
                    # Store the limit info for the most restrictive limit (lowest remaining)
                    if most_restrictive_info is None or limit_info.get("remaining", 0) < most_restrictive_info.get("remaining", 0):
                        most_restrictive_info = limit_info
                        
                # Store the most restrictive limit info in request.state for headers middleware
                if most_restrictive_info:
                    request.state.limiter_info = {
                        "limit": most_restrictive_info.get("limit", 0),
                        "remaining": most_restrictive_info.get("remaining", 0),
                        "reset": most_restrictive_info.get("reset_at", 0)
                    }
                    
                rate_limit_applied = True
                break
                
        # Handle single rate limits
        if not rate_limit_applied:
            # Check each rate limit rule prefix
            for rule_prefix, rate_limit in RATE_LIMIT_RULES.items():
                # Check if the path starts with or matches the rule prefix
                matches_exact = relative_path == rule_prefix
                matches_prefix = relative_path.startswith(rule_prefix)
                matches_dynamic = rule_prefix.endswith("/") and relative_path.startswith(rule_prefix[:-1] + "/")
                
                if matches_exact or matches_prefix or matches_dynamic:
                    endpoint = rule_prefix
                    self.logger.info(f"Applying rate limit '{rate_limit}' for {user_id} on path: {path}")
                    
                    # Check the rate limit
                    limit_info = check_rate_limit(user_id, endpoint, rate_limit)
                    is_rate_limited = limit_info.get("exceeded", False)
                    
                    # Store in request.state for the headers middleware
                    request.state.limiter_info = {
                        "limit": limit_info.get("limit", 0),
                        "remaining": limit_info.get("remaining", 0),
                        "reset": limit_info.get("reset_at", 0)
                    }
                    
                    # If rate limited, raise an exception
                    if is_rate_limited:
                        reset_at = limit_info.get("reset_at", 0)
                        error_message = f"Rate limit exceeded ({rate_limit}). Try again later."
                        headers = {"Retry-After": str(reset_at)} if reset_at else {}
                        
                        self.logger.warning(f"Rate limit exceeded for {user_id} on {endpoint}")
                        
                        raise HTTPException(
                            status_code=429, 
                            detail=error_message,
                            headers=headers
                        )
                        
                    rate_limit_applied = True
                    break
        
        # Process the request normally
        return await call_next(request) 