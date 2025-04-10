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
    
    Note: This endpoint itself counts against your rate limits.
    For a non-counting version, use /rate-limits-status instead.
    
    Args:
        request: The FastAPI request
        force_refresh: If True, bypass the cache and get fresh data
    
    Returns:
        dict: Rate limit information by endpoint.
        
    Raises:
        ServiceUnavailableError: If there was an error getting rate limit information
    """
    return await _get_rate_limits(request, force_refresh)


@router.get("/rate-limits-status", include_in_schema=True)
async def rate_limits_status(request: Request, force_refresh: bool = False):
    """Get current rate limit information without counting against limits.
    
    This endpoint returns information about the remaining requests
    allowed for each rate-limited endpoint based on the client's session ID.
    It uses caching to reduce the load during busy periods.
    
    Unlike /rate-limits, this endpoint does not count against your rate limits.
    
    Args:
        request: The FastAPI request
        force_refresh: If True, bypass the cache and get fresh data
    
    Returns:
        dict: Rate limit information by endpoint.
        
    Raises:
        ServiceUnavailableError: If there was an error getting rate limit information
    """
    return await _get_rate_limits(request, force_refresh, check_only=True)


async def _get_rate_limits(request: Request, force_refresh: bool = False, check_only: bool = False):
    """
    Shared implementation for rate limit checking endpoints.
    
    Args:
        request: The FastAPI request
        force_refresh: If True, bypass the cache and get fresh data
        check_only: If True, don't increment counters during checks
    
    Returns:
        dict: Rate limit information by endpoint.
        
    Raises:
        ServiceUnavailableError: If there was an error getting rate limit information
    """
    try:
        global _rate_limits_cache
        
        # Get user ID from request state if available (auth middleware)
        user_id = None
        auth_user_id = None
        if hasattr(request, "state") and hasattr(request.state, "user") and request.state.user:
            auth_user_id = request.state.user.get("id")
            user_id = auth_user_id
            logger.debug(f"Using authenticated user ID for rate limits: {user_id}")
        else:
            # Check if we have an authorization header - could happen if auth middleware didn't run
            # but user is actually authenticated
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                from app.core.supabase.client import get_supabase_auth_client
                try:
                    # Try to get user from token
                    supabase_auth = get_supabase_auth_client()
                    user = supabase_auth.get_user_from_request(request)
                    if user and user.get("id"):
                        auth_user_id = user.get("id")
                        user_id = auth_user_id
                        logger.debug(f"Using authenticated user ID from token for rate limits: {user_id}")
                except Exception as e:
                    logger.warning(f"Error extracting user from token: {str(e)}")
            
        # Fall back to session ID if available
        session_id = None
        if not user_id:
            session_id = request.cookies.get("concept_session")
            if session_id:
                user_id = session_id
                logger.debug(f"Using session cookie ID for rate limits: {user_id}")
            
        # Finally fall back to IP address
        ip_address = None
        if not user_id:
            ip_address = get_remote_address(request)
            user_id = ip_address
            logger.debug(f"Using IP address for rate limits: {user_id}")
        
        # Create a unique cache key based on user ID
        # Ensure we always use a consistent format for the user ID
        if auth_user_id:
            cache_key = f"user:{auth_user_id}"
        elif session_id:
            cache_key = f"user:{session_id}"
        else:
            cache_key = f"ip:{ip_address or get_remote_address(request)}"
            
        logger.debug(f"Rate limit cache key (before masking): {cache_key}")
        
        # Check if we have a cached response for this user/IP
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
            "export_action": {"limit": "50/hour", "remaining": 50, "reset_after": get_reset_time("hour")}
        }
        
        # Get only the requested rate limits
        limits_info = {
            "user_identifier": mask_id(cache_key),  # Mask the user ID in the response
            "authenticated": user_id is not None and not cache_key.startswith("ip:"),
            "redis_available": redis_available,  # Include Redis availability status
            "limits": default_limits if not redis_available else {
                "generate_concept": get_limit_info(limiter, direct_redis_client, "10/month", cache_key, "generate_concept", check_only),
                "store_concept": get_limit_info(limiter, direct_redis_client, "10/month", cache_key, "store_concept", check_only),
                "refine_concept": get_limit_info(limiter, direct_redis_client, "10/hour", cache_key, "refine_concept", check_only),
                "export_action": get_limit_info(limiter, direct_redis_client, "50/hour", cache_key, "export_action", check_only),
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


def get_limit_info(limiter, direct_redis, limit_string, user_identifier, limit_type, check_only=False):
    """Get information about a specific rate limit.
    
    Args:
        limiter: The slowapi limiter instance
        direct_redis: Direct Redis client for backup checks
        limit_string: The limit string (e.g., "10/month")
        user_identifier: The user identifier (IP address)
        limit_type: The type of limit being checked (e.g., "generate_concept")
        check_only: If True, don't increment counters during checks
        
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
                "/concepts/generate",
                # Include the generate-with-palettes endpoint 
                "/concepts/generate-with-palettes"
            ],
            "refine_concept": ["/concepts/refine"],
            "store_concept": ["/concepts/store"],
            "get_concepts": ["/concepts/list"],
            "sessions": ["/sessions/sync"],  # Only sync endpoint seems relevant here
            "export_action": [
                "/export/process"
            ]
        }
        
        # Use our new check_rate_limit function
        if limit_type in endpoint_paths:
            max_count = 0
            final_limit_status = None
            
            # Iterate through all paths associated with this limit type
            for path in endpoint_paths[limit_type]:
                limit_status = check_rate_limit(
                    user_id=user_identifier,
                    endpoint=path,
                    limit=limit_string,
                    check_only=check_only
                )
                
                # If successful, update max_count and store the status
                if "error" not in limit_status:
                    current_count = limit_status.get("count", 0)
                    logger.debug(f"    Path '{path}' check successful. Count: {current_count}")
                    if current_count > max_count:
                        max_count = current_count
                        final_limit_status = limit_status
                        logger.debug(f"    Updated max_count to {max_count} based on path '{path}'")
                else:
                    logger.warning(f"Error checking rate limit for path {path}: {limit_status.get('error')}")
            
            # If we got at least one successful check, use the status with the highest count
            if final_limit_status is not None:
                logger_msg = "check-only" if check_only else "regular"
                logger.debug(f"Using {logger_msg} rate limit check result for {mask_id(user_identifier)} on {limit_type} (max count: {max_count})")
                return {
                    "limit": limit_string,
                    "remaining": max(0, count - max_count),
                    "reset_after": get_reset_time(period),
                    "current_count": max_count,
                    "period": final_limit_status.get("period", period),
                    "exceeded": final_limit_status.get("exceeded", False)
                }
            else:
                logger.warning(f"All rate limit checks failed for {limit_type}, falling back to direct Redis check.")
        
        # Fall back to previous implementation (direct Redis check) if the new method fails
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
                            f"{user_identifier}:{path}:{period}",
                            # Also try with /api prefix that might be used in some implementations
                            f"POST:/api{path}:{user_identifier}:{period}",
                            f"/api{path}:{user_identifier}:{period}",
                            f"{user_identifier}:/api{path}:{period}"
                        ])
                
                # Special case for SVG conversion which uses a specific prefix to avoid affecting other rate limits
                if limit_type == "svg_conversion":
                    keys_to_try.append(f"svg:{user_identifier}:{period}")
                    # Add the new SVG-specific keys
                    if endpoint_paths[limit_type]:
                        for path in endpoint_paths[limit_type]:
                            keys_to_try.extend([
                                f"svg:POST:{path}:{user_identifier}:{period}",
                                f"svg:{path}:{user_identifier}:{period}",
                                # Try with /api prefix too
                                f"svg:POST:/api{path}:{user_identifier}:{period}",
                                f"svg:/api{path}:{user_identifier}:{period}"
                            ])
                
                # Try each key directly with the Redis client
                for key in keys_to_try:
                    try:
                        # Try first with the default key
                        val = direct_redis.get(key)
                        
                        # If not found, try with ratelimit: prefix that's used by RedisStore
                        if val is None:
                            prefixed_key = f"ratelimit:{key}"
                            val = direct_redis.get(prefixed_key)
                            if val is not None:
                                logger.debug(f"Direct Redis - Found key with ratelimit: prefix: {mask_key(prefixed_key)} = {val}")
                        
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
                            logger.debug(f"SlowAPI storage - Found key: {mask_key(key)} = {val}")
                            try:
                                val_int = int(val)
                                if val_int > current:
                                    current = val_int
                            except (ValueError, TypeError):
                                pass
                    except Exception:
                        # Suppress key errors
                        pass
            except Exception as e:
                logger.warning(f"Error querying SlowAPI storage: {str(e)}")
        
        # Return the results
        return {
            "limit": limit_string,
            "remaining": max(0, count - current),
            "reset_after": get_reset_time(period),
            "current_count": current,
            "period": period
        }
    except Exception as e:
        logger.error(f"Error in get_limit_info: {str(e)}")
        # Return safe defaults
        try:
            count_int = int(count) if 'count' in locals() else 10
        except (ValueError, TypeError):
            count_int = 10
            
        return {
            "limit": limit_string if 'limit_string' in locals() else "10/month",
            "remaining": count_int,
            "reset_after": get_reset_time("month"),
            "error": str(e),
            "note": "Error retrieving limits - showing defaults"
        } 