"""
Rate limiting utilities for API endpoints.

This module provides functions for applying rate limits to API endpoints.
"""

import logging
from typing import Dict, Any, Optional, List
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
    
    logger.debug(f"Checking rate limit '{rate_limit}' for {key_prefix}")
    
    # Apply rate limiting - use check_request instead of sliding_window_check_rate
    limiter = req.app.state.limiter
    
    # Use the appropriate method based on what's available
    if hasattr(limiter, 'check_request'):
        # Modern SlowAPI
        is_rate_limited = limiter.check_request(req, rate_limit)
    else:
        # Fallback to direct increment with manual check
        from app.core.limiter import check_rate_limit
        limit_info = check_rate_limit(key, endpoint, rate_limit)
        is_rate_limited = limit_info.get("exceeded", False)
    
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


async def apply_multiple_rate_limits(
    req: Request,
    rate_limits: List[Dict[str, str]]
) -> Dict[str, Any]:
    """
    Apply multiple rate limits for a single endpoint.
    
    This function is used when an endpoint needs to track usage against
    multiple different resource quotas (e.g., concept generation + storage).
    
    Args:
        req: FastAPI request object
        rate_limits: List of dictionaries with keys:
            - endpoint: Name of the endpoint for rate limiting
            - rate_limit: Rate limit string (e.g., "10/minute")
            - period: Optional time period override
        
    Returns:
        Dict containing combined rate limit information
        
    Raises:
        HTTPException: If any rate limit is exceeded
    """
    # Skip rate limiting if disabled
    if not settings.RATE_LIMITING_ENABLED:
        logger.debug("Multiple rate limiting disabled")
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
    
    # Check each rate limit
    results = {}
    limiter = req.app.state.limiter
    
    # Import check_rate_limit for direct checks
    from app.core.limiter import check_rate_limit
    
    for limit_config in rate_limits:
        endpoint = limit_config["endpoint"]
        rate_limit = limit_config["rate_limit"]
        # Period is extracted but might be used in the future
        # Passing it to check_rate_limit is not necessary as it's parsed from rate_limit
        _ = limit_config.get("period")
        
        logger.debug(f"Checking rate limit '{rate_limit}' for {key_prefix} on {endpoint}")
        
        # Check rate limit directly using our core function
        limit_info = check_rate_limit(key, endpoint, rate_limit)
        is_rate_limited = limit_info.get("exceeded", False)
        
        # If rate limited, raise an exception
        if is_rate_limited:
            # Get information about the rate limit for the error message
            reset_at = limit_info.get("reset_at", 0)
            
            # Create a more helpful error message
            error_message = f"Rate limit exceeded for {endpoint} ({rate_limit}). Try again later."
            
            # Add Retry-After header if we have reset info
            headers = {"Retry-After": str(reset_at)} if reset_at else {}
            
            logger.warning(f"Rate limit exceeded for {key_prefix} {user_id} on {endpoint}")
            
            raise HTTPException(
                status_code=429, 
                detail=error_message,
                headers=headers
            )
        
        # Store result for this rate limit
        results[endpoint] = {
            "enabled": True,
            "limited": False,
            "rate_limit": rate_limit,
            "current": limit_info.get("count", 0),
            "remaining": limit_info.get("remaining", 0),
            "reset_at": limit_info.get("reset_at", 0)
        }
    
    # All rate limits passed
    return {
        "enabled": True,
        "limited": False,
        "checked_limits": results
    } 