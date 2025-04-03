"""
Health check endpoints for the API.

This module provides health check endpoints to monitor the API's status.
"""

from fastapi import APIRouter, Request
from slowapi.util import get_remote_address
from datetime import datetime
import calendar
import redis
import logging
from backend.app.core.rate_limiter import get_redis_client

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/")
@router.head("/")
async def health_check(request: Request):
    """
    Health check endpoint.
    
    Returns:
        dict: A dictionary with the status of the API.
    """
    return {"status": "ok"}


@router.get("/rate-limits")
async def rate_limits(request: Request):
    """Get current rate limit information for the client.
    
    This endpoint returns information about the remaining requests
    allowed for each rate-limited endpoint based on the client's IP.
    
    Returns:
        dict: Rate limit information by endpoint.
    """
    user_ip = get_remote_address(request)
    limiter = request.app.state.limiter
    
    # Try to directly check Redis for rate limit keys
    direct_redis_client = get_redis_client()
    if direct_redis_client:
        try:
            # Log a direct connection to Redis
            logger.info(f"Using direct Redis connection to check rate limits for {user_ip}")
            
            # Instead of using scan_iter (which isn't supported by SlowAPI storage),
            # we'll directly check specific known key patterns
            keys_to_check = [
                f"*{user_ip}*month*",  # For monthly limits
                f"*{user_ip}*hour*",    # For hourly limits
                f"*{user_ip}*minute*",  # For minute limits
                f"*{user_ip}*day*",     # For daily limits
            ]
            
            for pattern in keys_to_check:
                try:
                    # Use scan_iter directly on Redis client, not on SlowAPI storage
                    for key in direct_redis_client.scan_iter(match=pattern):
                        value = direct_redis_client.get(key)
                        logger.info(f"Direct Redis - Found key: {key} = {value}")
                except Exception as e:
                    logger.warning(f"Error scanning Redis with pattern {pattern}: {str(e)}")
        except Exception as e:
            logger.error(f"Error accessing Redis directly: {str(e)}")
    
    # Get all the configured limits
    limits_info = {
        "user_identifier": user_ip,
        "limits": {
            "generate_concept": _get_limit_info(limiter, direct_redis_client, "10/month", user_ip, "generate_concept"),
            "refine_concept": _get_limit_info(limiter, direct_redis_client, "10/hour", user_ip, "refine_concept"),
            "store_concept": _get_limit_info(limiter, direct_redis_client, "10/month", user_ip, "store_concept"),
            "get_concepts": _get_limit_info(limiter, direct_redis_client, "30/minute", user_ip, "get_concepts"),
            "sessions": _get_limit_info(limiter, direct_redis_client, "60/hour", user_ip, "sessions"),
            "svg_conversion": _get_limit_info(limiter, direct_redis_client, "20/hour", user_ip, "svg_conversion"),
        },
        "default_limits": ["200/day", "50/hour", "10/minute"]
    }
    
    return limits_info


def _get_limit_info(limiter, direct_redis, limit_string, user_identifier, limit_type):
    """Get information about a specific rate limit.
    
    Args:
        limiter: The slowapi limiter instance
        direct_redis: Direct Redis client for backup checks
        limit_string: The limit string (e.g., "10/month")
        user_identifier: The user identifier (IP address)
        limit_type: The type of limit being checked (e.g., "generate_concept")
        
    Returns:
        dict: Rate limit information.
    """
    try:
        # Extract limit data
        count, period = limit_string.split("/")
        count = int(count)
        
        # Map our limit types to the corresponding endpoint paths
        endpoint_paths = {
            "generate_concept": [
                # The main concept generation endpoint
                "/api/concept/generate",
                # Include the generate-with-palettes endpoint 
                "/api/concept/generate-with-palettes"
            ],
            "refine_concept": ["/api/concept/refine"],
            "store_concept": ["/api/concept/store"],
            "get_concepts": ["/api/concept/list"],
            "sessions": ["/api/session", "/api/session/sync"],
            "svg_conversion": ["/api/svg/convert"]
        }
        
        # First try with the direct Redis client
        current = 0
        if direct_redis:
            try:
                # Generate the Redis keys that might store our limits
                keys_to_try = []
                
                # Basic key
                keys_to_try.append(f"{user_identifier}:{period}")
                
                # Add endpoint-specific keys
                if limit_type in endpoint_paths:
                    for path in endpoint_paths[limit_type]:
                        # Different key formats that might be used
                        keys_to_try.extend([
                            f"POST:{path}:{user_identifier}:{period}",
                            f"{path}:{user_identifier}:{period}",
                            f"{user_identifier}:{path}:{period}"
                        ])
                
                # Try each key directly with the Redis client
                for key in keys_to_try:
                    try:
                        val = direct_redis.get(key)
                        if val is not None:
                            logger.info(f"Direct Redis - Found key: {key} = {val}")
                            try:
                                val_int = int(val)
                                if val_int > current:
                                    current = val_int
                            except (ValueError, TypeError):
                                pass
                    except Exception as e:
                        logger.debug(f"Error checking key {key}: {str(e)}")
            except Exception as e:
                logger.warning(f"Error querying Redis directly: {str(e)}")
        
        # If we didn't find anything, also try with SlowAPI's internal storage
        if current == 0 and hasattr(limiter, '_storage'):
            try:
                # Get the storage backend (Redis or memory)
                storage = limiter._storage
                
                # Only attempt basic operations, not scan_iter which isn't supported
                # Just check a few key formats that are most likely to be used by SlowAPI
                simple_keys = [
                    f"{user_identifier}:{period}",
                ]
                
                if limit_type in endpoint_paths:
                    for path in endpoint_paths[limit_type]:
                        simple_keys.append(f"POST:{path}:{user_identifier}:{period}")
                
                for key in simple_keys:
                    try:
                        val = storage.get(key)
                        if val is not None:
                            logger.info(f"SlowAPI Storage - Found key: {key} = {val}")
                            try:
                                val_int = int(val)
                                if val_int > current:
                                    current = val_int
                            except (ValueError, TypeError):
                                pass
                    except Exception as e:
                        # Don't log individual errors here to reduce noise
                        pass
            except Exception as e:
                logger.warning(f"Error using SlowAPI storage: {str(e)}")
        
        # Calculate remaining
        remaining = max(0, count - current)
        
        return {
            "limit": limit_string,
            "remaining": remaining,
            "reset_after": _get_reset_time(period),
        }
    except Exception as e:
        logger.error(f"General error getting rate limit info: {str(e)}")
        return {
            "limit": limit_string,
            "remaining": count,  # Default to full availability
            "reset_after": _get_reset_time(period),
            "error": f"Could not retrieve limit info: {str(e)}"
        }


def _get_reset_time(period):
    """Calculate approximate reset time in seconds.
    
    Args:
        period: The period string (minute, hour, day, month)
        
    Returns:
        int: Approximate seconds until reset
    """
    now = datetime.now()
    
    if period == "minute":
        # Reset at the next minute
        return 60 - now.second
    elif period == "hour":
        # Reset at the next hour
        return (60 - now.minute) * 60 - now.second
    elif period == "day":
        # Reset at midnight
        seconds_in_day = 24 * 60 * 60
        seconds_passed = now.hour * 3600 + now.minute * 60 + now.second
        return seconds_in_day - seconds_passed
    elif period == "month":
        # Reset at the 1st of next month (very approximate)
        days_in_month = calendar.monthrange(now.year, now.month)[1]
        days_left = days_in_month - now.day
        return days_left * 24 * 60 * 60 + (24 - now.hour) * 60 * 60 