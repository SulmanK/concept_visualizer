"""
Rate limiting utilities for API endpoints.

This module provides functions for applying rate limits to API endpoints.
"""

import logging
from typing import Dict, Any, Optional
from fastapi import Request, HTTPException
from slowapi.util import get_remote_address

from app.core.config import settings


logger = logging.getLogger(__name__)


async def apply_rate_limit(
    req: Request,
    endpoint: str,
    rate_limit: str,
    period: Optional[str] = None
) -> Dict[str, Any]:
    """
    Apply rate limiting to an endpoint.
    
    Args:
        req: FastAPI request object
        endpoint: Name of the endpoint for rate limiting
        rate_limit: Rate limit string (e.g., "10/minute")
        period: Time period override (e.g., "minute")
        
    Returns:
        Dict containing rate limit information
        
    Raises:
        HTTPException: If rate limit is exceeded
    """
    # Skip rate limiting if disabled
    if not settings.RATE_LIMITING_ENABLED:
        logger.debug("Rate limiting disabled")
        return {"enabled": False}
    
    # Check if limiter is available
    if not hasattr(req.app.state, 'limiter'):
        logger.warning("Rate limiter not available")
        return {"enabled": False}
    
    # Get the user ID from auth middleware or fall back to IP
    user_id = None
    if hasattr(req, "state") and hasattr(req.state, "user") and req.state.user:
        user_id = req.state.user.get("id")
        key_prefix = "user"
    else:
        user_id = get_remote_address(req)
        key_prefix = "ip"
    
    # Create a key for the rate limit (e.g., "user:123abc" or "ip:127.0.0.1")
    key = f"{key_prefix}:{user_id}"
    
    logger.info(f"Checking rate limit '{rate_limit}' for {key_prefix}")
    
    # Apply rate limiting
    limiter = req.app.state.limiter
    is_rate_limited = await limiter.sliding_window_check_rate(
        rate_limit,
        key, 
        endpoint
    )
    
    # Add rate limit headers to the response
    # These headers follow standard conventions like GitHub API
    if hasattr(req.state, "limiter_info"):
        request_limit = req.state.limiter_info["limit"]
        request_remaining = req.state.limiter_info["remaining"]
        request_reset = req.state.limiter_info["reset"]
        
        # Add headers to response
        resp = getattr(req, "response", None)
        if resp:
            resp.headers["X-RateLimit-Limit"] = str(request_limit)
            resp.headers["X-RateLimit-Remaining"] = str(request_remaining)
            resp.headers["X-RateLimit-Reset"] = str(request_reset)
    
    # If rate limited, raise an exception
    if is_rate_limited:
        # Get information about the rate limit for the error message
        info = getattr(req.state, "limiter_info", {})
        reset_at = info.get("reset", 0) if info else 0
        
        # Create a more helpful error message
        error_message = f"Rate limit exceeded ({rate_limit}). Try again later."
        
        # Add Retry-After header if we have reset info
        headers = {"Retry-After": str(reset_at)} if reset_at else {}
        
        logger.warning(f"Rate limit exceeded for {key_prefix} {user_id} on {endpoint}")
        raise HTTPException(
            status_code=429, 
            detail=error_message,
            headers=headers
        )
    
    return {"enabled": True, "limited": False} 