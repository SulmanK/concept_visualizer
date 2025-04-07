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
    "check_rate_limit"
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


def check_rate_limit(user_id: str, endpoint: str, limit: str) -> Dict[str, Any]:
    """
    Check if a request is rate limited.
    
    Args:
        user_id: The user identifier (usually user ID or IP)
        endpoint: API endpoint being accessed
        limit: Limit string in format "number/period" (e.g., "10/minute")
            
    Returns:
        Dict with rate limit information
    """
    try:
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
            endpoint=endpoint,
            limit=count,
            period=period_seconds
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