"""
Rate limit checking endpoints.

This module provides endpoints to check the current rate limit status.
"""

import traceback
from fastapi import APIRouter, Request
from slowapi.util import get_remote_address
from datetime import datetime, timedelta
import logging
from typing import Dict, Any

from app.core.limiter import get_redis_client, check_rate_limit
from app.api.routes.health.utils import get_reset_time, mask_id, mask_key

# Import error handling
from app.api.errors import ServiceUnavailableError

# Configure logging
logger = logging.getLogger("health_limits_api")

# Create router
router = APIRouter()

# In-memory cache for rate limit responses
_rate_limits_cache: Dict[str, Dict[str, Any]] = {}


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
        
    Raises:
        ServiceUnavailableError: If there was an error getting rate limit information
    """
    try:
        global _rate_limits_cache
        
        # Use session ID if available, otherwise fall back to IP address
        session_id = request.cookies.get("concept_session")
        user_ip = get_remote_address(request)
        
        # Create a unique cache key based on session or IP
        cache_key = f"session:{session_id}" if session_id else f"ip:{user_ip}"
        
        # Check if we have a cached response for this session/IP
        now = datetime.utcnow()
        if not force_refresh and cache_key in _rate_limits_cache and now < _rate_limits_cache[cache_key]["expires_at"]:
            logger.debug(f"Using cached rate limits for {mask_id(cache_key)}")
            return _rate_limits_cache[cache_key]["data"]
        
        if force_refresh:
            logger.info(f"Force refreshing rate limits for {mask_id(cache_key)}")
        else:
            logger.info(f"Generating fresh rate limits data for {mask_id(cache_key)}")
        
        limiter = request.app.state.limiter
        
        # Try to directly check Redis for rate limit keys
        direct_redis_client = get_redis_client()
        redis_available = direct_redis_client is not None
        
        # Default rate limit data to use if Redis is not available
        default_limits = {
            "generate_concept": {"limit": "10/month", "remaining": 10, "reset_after": get_reset_time("month")},
            "store_concept": {"limit": "10/month", "remaining": 10, "reset_after": get_reset_time("month")},
            "refine_concept": {"limit": "10/hour", "remaining": 10, "reset_after": get_reset_time("hour")},
            "svg_conversion": {"limit": "20/hour", "remaining": 20, "reset_after": get_reset_time("hour")}
        }
        
        # Get only the requested rate limits
        limits_info = {
            "user_identifier": mask_id(cache_key),  # Mask the session ID in the response
            "session_id": session_id is not None,  # Include whether session was found
            "redis_available": redis_available,  # Include Redis availability status
            "limits": default_limits if not redis_available else {
                "generate_concept": get_limit_info(limiter, direct_redis_client, "10/month", cache_key, "generate_concept"),
                "store_concept": get_limit_info(limiter, direct_redis_client, "10/month", cache_key, "store_concept"),
                "refine_concept": get_limit_info(limiter, direct_redis_client, "10/hour", cache_key, "refine_concept"),
                "svg_conversion": get_limit_info(limiter, direct_redis_client, "20/hour", cache_key, "svg_conversion"),
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
    except Exception as e:
        logger.error(f"Error getting rate limit information: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail="Error retrieving rate limit information")


def get_limit_info(limiter, direct_redis, limit_string, user_identifier, limit_type):
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
                "reset_after": get_reset_time(period),
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
        
        # Use our new check_rate_limit function for more accurate limit checking
        if limit_type in endpoint_paths:
            # Just use the first endpoint path for simplicity
            path = endpoint_paths[limit_type][0]
            
            # Use our new check_rate_limit function
            limit_status = check_rate_limit(
                user_id=user_identifier,
                endpoint=path,
                limit=limit_string
            )
            
            # If successful, use the results directly
            if "error" not in limit_status:
                logger.debug(f"Using new rate limit check for {mask_id(user_identifier)} on {limit_type}")
                return {
                    "limit": limit_string,
                    "remaining": max(0, count - limit_status.get("count", 0)),
                    "reset_after": get_reset_time(period),
                    "current_count": limit_status.get("count", 0),
                    "period": limit_status.get("period", period),
                    "exceeded": limit_status.get("exceeded", False)
                }
            else:
                logger.warning(f"Error using new rate limit check: {limit_status.get('error')}")
        
        # Fall back to previous implementation if the new method fails
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
                    # Add the new SVG-specific keys
                    if endpoint_paths[limit_type]:
                        for path in endpoint_paths[limit_type]:
                            keys_to_try.extend([
                                f"svg:POST:{path}:{user_identifier}:{period}",
                                f"svg:{path}:{user_identifier}:{period}"
                            ])
                
                # Try each key directly with the Redis client
                for key in keys_to_try:
                    try:
                        val = direct_redis.get(key)
                        if val is not None:
                            logger.debug(f"Direct Redis - Found key: {mask_key(key)} = {val}")
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
                            logger.debug(f"SlowAPI Storage - Found key: {mask_key(key)} = {val}")
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
            "reset_after": get_reset_time(period),
            "current_count": current,
            "exceeded": current >= count
        }
    except Exception as e:
        logger.error(f"General error getting rate limit info: {str(e)}")
        return {
            "limit": limit_string,
            "remaining": count,  # Default to full availability
            "reset_after": get_reset_time(period),
            "error": f"Could not retrieve limit info: {str(e)}"
        } 