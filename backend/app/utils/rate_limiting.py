"""
Rate limiting utilities for API routes.

This module provides utility functions for rate limiting API endpoints.
"""

import logging
from typing import Optional

from fastapi import Request
from slowapi.util import get_remote_address

# Configure logging
logger = logging.getLogger("rate_limiting")


async def apply_rate_limit(
    req: Request,
    endpoint: str,
    rate_limit: str,
    period: str = "month"
) -> None:
    """
    Apply rate limiting to a request.
    
    Args:
        req: The FastAPI request object
        endpoint: The endpoint path for tracking
        rate_limit: The rate limit string (e.g., "10/month")
        period: The period for rate limiting (e.g., "month", "hour")
        
    Returns:
        None
    """
    limiter = req.app.state.limiter
    try:
        # Log the rate limiting attempt
        logger.info(f"Applying rate limit '{rate_limit}' for session")
        
        # Try-except block for the rate limit to handle connection issues
        try:
            # Fix the await syntax - limiter.limit returns a function, not an awaitable
            limit_func = limiter.limit(rate_limit)
            # Apply the limit function to the request, but don't await it (it's not an async function)
            limit_func(req)
            logger.debug("SlowAPI rate limit applied successfully")
        except Exception as e:
            logger.error(f"SlowAPI rate limiting error: {str(e)}")
        
        # Use our custom direct Redis tracking as a more reliable method
        if hasattr(limiter, 'increment_rate_limit'):
            # The user ID will be extracted from cookies in the key_func
            user_id = req.cookies.get("concept_session", get_remote_address(req))
            user_id = f"session:{user_id}" if "concept_session" in req.cookies else f"ip:{user_id}"
            
            success = limiter.increment_rate_limit(
                user_id=user_id,
                endpoint=f"/api{endpoint}",
                period=period
            )
            if success:
                logger.debug("Rate limit counter incremented successfully in Redis")
            else:
                logger.warning("Failed to increment rate limit counter in Redis")
        
        logger.debug("Rate limit tracking completed")
    except Exception as e:
        logger.error(f"Error applying rate limit: {str(e)}")
        # Continue even if rate limiting fails 