"""
Health check endpoints for the API.

This module provides health check endpoints to monitor the API's status.
"""

from fastapi import APIRouter, Request
from slowapi.util import get_remote_address
from datetime import datetime, timedelta
import calendar
import logging
from app.core.rate_limiter import get_redis_client
from typing import Dict, Any


# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory cache for health check responses
_health_cache = {
    "status": "ok",
    "timestamp": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(seconds=30)
}

# In-memory cache for rate limit responses
_rate_limits_cache: Dict[str, Dict[str, Any]] = {}


@router.get("/")
@router.head("/")
async def health_check(request: Request):
    """
    Health check endpoint.
    
    This endpoint uses in-memory caching to reduce the load on the server during busy periods.
    If there are many health check requests while the server is processing heavy tasks like image generation,
    it will return a cached response instead of creating a new one each time.
    
    Returns:
        dict: A dictionary with the status of the API.
    """
    global _health_cache
    
    # Check if the cache is still valid
    now = datetime.utcnow()
    if now < _health_cache["expires_at"]:
        return {"status": _health_cache["status"]}
    
    # Update the cache
    _health_cache = {
        "status": "ok",
        "timestamp": now,
        "expires_at": now + timedelta(seconds=30)
    }
    
    return {"status": "ok"}


@router.get("/rate-limits")
async def rate_limits(request: Request, force_refresh: bool = False):
    """Get current rate limit information for the client.
    
    This endpoint returns information about the remaining requests
    allowed for each rate-limited endpoint based on the client's session ID.
    It uses caching to reduce the load during busy periods.
    
    Args:
        request: The FastAPI request
        force_refresh: If True, bypass the cache and get fresh data
    
    Returns:
        dict: Rate limit information by endpoint.
    """
    global _rate_limits_cache
    
    # Use session ID if available, otherwise fall back to IP address
    session_id = request.cookies.get("concept_session")
    user_ip = get_remote_address(request)
    
    # Create a unique cache key based on session or IP
    cache_key = f"session:{session_id}" if session_id else f"ip:{user_ip}"
    
    # Check if we have a cached response for this session/IP
    now = datetime.utcnow()
    if not force_refresh and cache_key in _rate_limits_cache and now < _rate_limits_cache[cache_key]["expires_at"]:
        logger.debug(f"Using cached rate limits for {_mask_id(cache_key)}")
        return _rate_limits_cache[cache_key]["data"]
    
    if force_refresh:
        logger.info(f"Force refreshing rate limits for {_mask_id(cache_key)}")
    else:
        logger.info(f"Generating fresh rate limits data for {_mask_id(cache_key)}")
    
    limiter = request.app.state.limiter
    
    # Try to directly check Redis for rate limit keys
    direct_redis_client = get_redis_client()
    redis_available = direct_redis_client is not None
    
    # Default rate limit data to use if Redis is not available
    default_limits = {
        "generate_concept": {"limit": "10/month", "remaining": 10, "reset_after": _get_reset_time("month")},
        "store_concept": {"limit": "10/month", "remaining": 10, "reset_after": _get_reset_time("month")},
        "refine_concept": {"limit": "10/hour", "remaining": 10, "reset_after": _get_reset_time("hour")},
        "svg_conversion": {"limit": "20/hour", "remaining": 20, "reset_after": _get_reset_time("hour")}
    }
    
    # Get only the requested rate limits
    limits_info = {
        "user_identifier": _mask_id(cache_key),  # Mask the session ID in the response
        "session_id": session_id is not None,  # Include whether session was found
        "redis_available": redis_available,  # Include Redis availability status
        "limits": default_limits if not redis_available else {
            "generate_concept": _get_limit_info(limiter, direct_redis_client, "10/month", cache_key, "generate_concept"),
            "store_concept": _get_limit_info(limiter, direct_redis_client, "10/month", cache_key, "store_concept"),
            "refine_concept": _get_limit_info(limiter, direct_redis_client, "10/hour", cache_key, "refine_concept"),
            "svg_conversion": _get_limit_info(limiter, direct_redis_client, "20/hour", cache_key, "svg_conversion"),
        },
        "default_limits": ["200/day", "50/hour", "10/minute"],
        "last_updated": now.isoformat(),  # Add timestamp to show when data was refreshed
        "cache_expires": (now + timedelta(seconds=5)).isoformat()  # Add cache expiry information
    }
    
    # Cache the result for this key (cache for 5 seconds instead of 1 minute)
    _rate_limits_cache[cache_key] = {
        "data": limits_info,
        "timestamp": now,
        "expires_at": now + timedelta(seconds=5)
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
        
        # If Redis is not available, return default full availability
        if not direct_redis:
            return {
                "limit": limit_string,
                "remaining": count,
                "reset_after": _get_reset_time(period),
                "note": "Redis unavailable - showing default limits"
            }
            
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
            "svg_conversion": [
                "/api/svg/convert-to-svg", 
                "/api/svg/convert"  # Include both possible paths
            ]
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
                
                # Special case for SVG conversion which uses a specific prefix to avoid affecting other rate limits
                if limit_type == "svg_conversion":
                    keys_to_try.append(f"svg:{user_identifier}:{period}")
                
                # Try each key directly with the Redis client
                for key in keys_to_try:
                    try:
                        val = direct_redis.get(key)
                        if val is not None:
                            logger.debug(f"Direct Redis - Found key: {_mask_key(key)} = {val}")
                            try:
                                val_int = int(val)
                                if val_int > current:
                                    current = val_int
                            except (ValueError, TypeError):
                                pass
                    except Exception:
                        # Suppress individual key errors
                        pass
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
                            logger.debug(f"SlowAPI Storage - Found key: {_mask_key(key)} = {val}")
                            try:
                                val_int = int(val)
                                if val_int > current:
                                    current = val_int
                            except (ValueError, TypeError):
                                pass
                    except Exception:
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
        

def _mask_ip(ip_address):
    """Mask an IP address for privacy in logs.
    
    Args:
        ip_address: The IP address to mask
        
    Returns:
        str: Masked IP address
    """
    if not ip_address:
        return "unknown"
    
    # For IPv4 addresses
    if '.' in ip_address:
        parts = ip_address.split('.')
        if len(parts) == 4:
            return f"{parts[0]}.{parts[1]}.**.**"
    
    # For IPv6 addresses
    if ':' in ip_address:
        return ip_address.split(':')[0] + ':****:****'
    
    # If not a recognized format, mask most of it
    if len(ip_address) > 4:
        return ip_address[:4] + '*' * (len(ip_address) - 4)
    
    return "****"


def _mask_id(id_value):
    """Mask an identifier (session ID or IP) for privacy in logs.
    
    Args:
        id_value: The identifier to mask
        
    Returns:
        str: Masked identifier
    """
    if not id_value:
        return "unknown"
        
    # Check if this is a session ID or IP format
    if id_value.startswith("session:"):
        # Extract and mask the session ID part
        session_id = id_value[8:]
        if len(session_id) <= 4:
            return "session:[ID_TOO_SHORT]"
        return f"session:{session_id[:4]}{'*' * (len(session_id) - 4)}"
    elif id_value.startswith("ip:"):
        # Extract and mask the IP part
        ip = id_value[3:]
        masked_ip = _mask_ip(ip)
        return f"ip:{masked_ip}"
    
    # Default masking for other formats
    if len(id_value) > 4:
        return id_value[:4] + '*' * (len(id_value) - 4)
    
    return "****"


def _mask_key(key):
    """Mask a Redis key that might contain sensitive information.
    
    Args:
        key: The Redis key to mask
        
    Returns:
        str: Masked Redis key
    """
    if not key:
        return "unknown"
    
    # Check if key is in format "session:{session_id}:..."
    if "session:" in key:
        parts = key.split(":")
        for i, part in enumerate(parts):
            if i > 0 and parts[i-1] == "session" and len(part) > 4:
                # This part is likely a session ID
                parts[i] = part[:4] + '*' * (len(part) - 4)
    
    # If key contains an IP address, mask it
    else:
        parts = key.split(':')
        masked_parts = []
        
        for part in parts:
            if '.' in part and len(part.split('.')) == 4:
                # Likely an IPv4 address
                masked_parts.append(_mask_ip(part))
            else:
                masked_parts.append(part)
        
        return ':'.join(masked_parts)
    
    return ':'.join(parts) 