"""
Rate limiting utilities for API routes.

This module provides utility functions for rate limiting API endpoints.
"""

import logging
from typing import Optional
from fastapi import Request, HTTPException
from slowapi.util import get_remote_address
from app.core.limiter import check_rate_limit, increment_rate_limit
from app.core.exceptions import RateLimitError

# Configure logging
logger = logging.getLogger("rate_limiting")


async def apply_rate_limit(
    req: Request,
    endpoint: str,
    rate_limit: str,
    period: str = "month"
) -> None:
    """
    Apply rate limiting to a request. If the limit is exceeded, this raises an exception.
    
    Args:
        req: The FastAPI request object
        endpoint: The endpoint path for tracking
        rate_limit: The rate limit string (e.g., "10/month")
        period: The period for rate limiting (e.g., "month", "hour")
        
    Returns:
        None
        
    Raises:
        HTTPException: If the rate limit is exceeded
    """
    if not hasattr(req.app.state, 'limiter'):
        logger.warning("No limiter found in app state, skipping rate limiting")
        return
        
    try:
        # Extract user identifier
        user_id = req.cookies.get("concept_session", get_remote_address(req))
        user_id = f"session:{user_id}" if "concept_session" in req.cookies else f"ip:{user_id}"
        
        # First check if the limit has been exceeded
        logger.info(f"Checking rate limit '{rate_limit}' for session")
        limit_status = check_rate_limit(
            user_id=user_id,
            endpoint=f"/api{endpoint}",
            limit=rate_limit
        )
        
        # If limit is exceeded, raise a 429 Too Many Requests error
        if limit_status.get("exceeded", False):
            logger.warning(f"Rate limit exceeded: {limit_status['count']}/{limit_status['limit']} {limit_status['period']}")
            
            # Get seconds until reset
            reset_seconds = limit_status.get("reset_at", 0)
            
            # Create a detailed error message
            detail = {
                "message": f"Rate limit exceeded: {limit_status['count']}/{limit_status['limit']} requests per {limit_status['period']}",
                "limit": limit_status['limit'],
                "current": limit_status['count'],
                "period": limit_status['period'],
                "reset_after_seconds": reset_seconds
            }
            
            # Raise a 429 error with reset information
            raise HTTPException(
                status_code=429,
                detail=detail,
                headers={"Retry-After": str(reset_seconds)}
            )
        
        # Only increment the counter if the request is allowed
        success = increment_rate_limit(
            user_id=user_id,
            endpoint=f"/api{endpoint}",
            period=period
        )
        
        if success:
            logger.debug("Rate limit counter incremented successfully")
        else:
            logger.warning("Failed to increment rate limit counter in Redis")
        
    except HTTPException:
        # Re-raise HTTP exceptions (like our 429 error)
        raise
    except Exception as e:
        logger.error(f"Error applying rate limit: {str(e)}")
        # Continue even if rate limiting fails - don't block legitimate requests
        # due to rate limiting infrastructure errors 