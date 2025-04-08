"""
Rate limiter package.

This package provides rate limiting functionality for the application.
"""

from typing import Optional, Dict, Any, Tuple
import time

import redis
from slowapi import Limiter
from fastapi import Request

from app.core.config import settings
from app.core.limiter.config import configure_limiter
from app.core.limiter.redis_store import RedisStore, get_redis_client
from app.core.limiter.keys import get_user_id, get_endpoint_key, combine_keys

import logging
logger = logging.getLogger(__name__)

__all__ = [
    "Limiter",
    "RedisStore",
    "get_redis_client",
    "configure_limiter",
    "get_user_id",
    "get_endpoint_key",
    "combine_keys",
    "check_rate_limit",
    "normalize_endpoint"
]


_limiter: Optional[Limiter] = None


def get_limiter() -> Limiter:
    """
    Get the configured limiter instance.
    
    Returns:
        The configured limiter
    """
    global _limiter
    if not _limiter:
        _limiter = configure_limiter()
    return _limiter


def normalize_endpoint(endpoint: str) -> str:
    """
    Normalize an endpoint path for rate limiting.
    
    Ensures that the endpoint is consistently formatted by:
    1. Removing the /api prefix if present
    2. Ensuring the path starts with a slash
    3. Replacing /concept/ with /concepts/ if found
    
    Args:
        endpoint: The endpoint path to normalize
        
    Returns:
        Normalized endpoint path
    """
    original_endpoint = endpoint  # For logging
    
    # Remove /api prefix if present
    if endpoint.startswith("/api/"):
        endpoint = endpoint[4:]  # Remove the "/api" part
    
    # Replace /concept/ with /concepts/
    if "/concept/" in endpoint:
        endpoint = endpoint.replace("/concept/", "/concepts/")
    
    # Ensure path starts with a slash
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
        
    if endpoint != original_endpoint:
        logger.debug(f"Normalized endpoint from '{original_endpoint}' to '{endpoint}'")
    else:
        logger.debug(f"Endpoint '{endpoint}' did not require normalization")
        
    return endpoint


def check_rate_limit(user_id: str, endpoint: str, limit: str, check_only: bool = False) -> Dict[str, Any]:
    """
    Check if a request is rate limited.
    
    Args:
        user_id: The user identifier (usually user ID or IP)
        endpoint: API endpoint being accessed
        limit: Limit string in format "number/period" (e.g., "10/minute")
        check_only: If True, don't increment the counter (for status checks)
            
    Returns:
        Dict with rate limit information
    """
    try:
        # Normalize the endpoint for consistent key generation
        normalized_endpoint = normalize_endpoint(endpoint)
        
        # Log the user ID and endpoint for debugging
        logger.debug(f"Checking rate limit for user '{user_id}' on endpoint '{normalized_endpoint}' (original: '{endpoint}')")
        
        # Parse limit string
        count, period_str = limit.split("/")
        count = int(count)
        
        # Convert period string to seconds
        period_map = {
            "second": 1,
            "minute": 60,
            "hour": 60 * 60,
            "day": 24 * 60 * 60,
            "month": 30 * 24 * 60 * 60,
            "year": 365 * 24 * 60 * 60
        }
        
        period_seconds = period_map.get(period_str.lower(), 60)  # Default to 1 minute
        
        # Get Redis client
        redis_client = get_redis_client()
        if not redis_client:
            # Return safe fallback values if Redis is unavailable
            return {
                "count": 0,
                "limit": count,
                "period": period_str,
                "exceeded": False,
                "remaining": count,
                "reset_at": int(time.time() + period_seconds)
            }
        
        # Create RedisStore instance
        store = RedisStore(redis_client)
        
        # Call the store's check_rate_limit method
        is_allowed, quota = store.check_rate_limit(
            user_id=user_id,
            endpoint=normalized_endpoint,
            limit=count,
            period=period_seconds,
            check_only=check_only
        )
        
        # Format response
        return {
            "count": quota["used"],
            "limit": count,
            "period": period_str,
            "exceeded": not is_allowed,
            "remaining": quota["remaining"],
            "reset_at": quota["reset_at"]
        }
    except Exception as e:
        logger.error(f"Error checking rate limit: {str(e)}")
        # Return safe fallback values on error
        return {
            "count": 0,
            "limit": int(count) if 'count' in locals() else 10,
            "period": period_str if 'period_str' in locals() else "minute",
            "exceeded": False,
            "error": str(e),
            "remaining": int(count) if 'count' in locals() else 10,
            "reset_at": int(time.time() + 60)  # Default to 1 minute
        } 