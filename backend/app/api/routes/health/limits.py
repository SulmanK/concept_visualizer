"""Rate limit checking endpoints.

This module provides endpoints to check the current rate limit status.
"""

# mypy: disable-error-code="no-any-return"

import logging
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Request
from redis import Redis
from slowapi.util import get_remote_address

# Import error handling
from app.api.errors import ServiceUnavailableError
from app.api.routes.health.utils import get_reset_time, mask_id, mask_key
from app.core.limiter import check_rate_limit, get_redis_client

# Configure logging
logger = logging.getLogger("health_limits_api")

# Create router
router = APIRouter()

# In-memory cache for rate limits responses
_rate_limits_cache: Dict[str, Dict[str, Any]] = {}


@router.get("/rate-limits")
async def rate_limits(request: Request, force_refresh: bool = False) -> Dict[str, Any]:
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
async def rate_limits_status(request: Request, force_refresh: bool = False) -> Dict[str, Any]:
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


async def _get_rate_limits(request: Request, force_refresh: bool = False, check_only: bool = False) -> Dict[str, Any]:
    """Shared implementation for rate limit checking endpoints.

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
        # Get user ID from request state if available (auth middleware)
        user_id: Optional[str] = None
        auth_user_id: Optional[str] = None
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

        # Fall back to IP address if no user ID found
        ip_address: Optional[str] = None
        if not user_id:
            ip_address = get_remote_address(request)
            user_id = ip_address
            logger.debug(f"Using IP address for rate limits: {user_id}")

        # Create a unique cache key based on user ID
        # Ensure we always use a consistent format for the user ID
        if auth_user_id:
            cache_key = f"user:{auth_user_id}"
        else:
            cache_key = f"ip:{ip_address or get_remote_address(request)}"

        logger.debug(f"Rate limit cache key (before masking): {cache_key}")

        # Check if we have a cached response for this user/IP
        now = datetime.utcnow()
        if not force_refresh and cache_key in _rate_limits_cache and now < _rate_limits_cache[cache_key]["expires_at"]:
            logger.debug(f"Using cached rate limits for {mask_id(cache_key)}")
            return _rate_limits_cache[cache_key]["data"]

        if force_refresh:
            logger.debug(f"Force refreshing rate limits for {mask_id(cache_key)}")
        else:
            logger.debug(f"Generating fresh rate limits data for {mask_id(cache_key)}")

        limiter = request.app.state.limiter

        # Try to directly check Redis for rate limit keys
        direct_redis_client = get_redis_client()
        redis_available = direct_redis_client is not None

        # Default rate limit data to use if Redis is not available
        default_limits = {
            "generate_concept": {
                "limit": "10/month",
                "remaining": 10,
                "reset_after": get_reset_time("month"),
            },
            "store_concept": {
                "limit": "10/month",
                "remaining": 10,
                "reset_after": get_reset_time("month"),
            },
            "refine_concept": {
                "limit": "10/hour",
                "remaining": 10,
                "reset_after": get_reset_time("hour"),
            },
            "export_action": {
                "limit": "50/hour",
                "remaining": 50,
                "reset_after": get_reset_time("hour"),
            },
        }

        # Get only the requested rate limits
        limits_info = {
            "user_identifier": mask_id(cache_key),  # Mask the user ID in the response
            "authenticated": user_id is not None and not cache_key.startswith("ip:"),
            "redis_available": redis_available,  # Include Redis availability status
            "limits": (
                default_limits
                if not redis_available
                else {
                    "generate_concept": get_limit_info(
                        limiter,
                        direct_redis_client,
                        "10/month",
                        cache_key,
                        "generate_concept",
                        check_only,
                    ),
                    "store_concept": get_limit_info(
                        limiter,
                        direct_redis_client,
                        "10/month",
                        cache_key,
                        "store_concept",
                        check_only,
                    ),
                    "refine_concept": get_limit_info(
                        limiter,
                        direct_redis_client,
                        "10/hour",
                        cache_key,
                        "refine_concept",
                        check_only,
                    ),
                    "export_action": get_limit_info(
                        limiter,
                        direct_redis_client,
                        "50/hour",
                        cache_key,
                        "export_action",
                        check_only,
                    ),
                }
            ),
            "default_limits": ["200/day", "50/hour", "10/minute"],
            "last_updated": now.isoformat(),  # Add timestamp to show when data was refreshed
            "cache_expires": (now + timedelta(seconds=5)).isoformat(),  # Add cache expiry information
        }

        # Cache the result for this key (cache for 5 seconds instead of 1 minute)
        _rate_limits_cache[cache_key] = {
            "data": limits_info,
            "timestamp": now,
            "expires_at": now + timedelta(seconds=5),
        }

        return limits_info
    except Exception as e:
        logger.error(f"Error getting rate limit information: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail="Error retrieving rate limit information")


def get_limit_info(
    limiter: Any,
    direct_redis: Optional[Redis],
    limit_string: str,
    user_identifier: str,
    limit_type: str,
    check_only: bool = False,
) -> Dict[str, Any]:  # noqa: C901
    """Get information about a specific rate limit.

    Args:
        limiter: The slowapi limiter instance
        direct_redis: Direct Redis client for backup checks
        limit_string: The limit string (e.g., "10/month")
        user_identifier: The user identifier (IP address)
        limit_type: The type of limit being checked (e.g., "generate_concept")
        check_only: If True, don't increment counters during checks

    Returns:
        Dict[str, Any]: Information about the rate limit status
    """
    try:
        # Extract limit data
        count_str, period = limit_string.split("/")
        count = int(count_str)

        # If Redis is not available, return default full availability
        if not direct_redis:
            return {
                "limit": limit_string,
                "remaining": count,
                "reset_after": get_reset_time(period),
                "note": "Redis unavailable - showing default limits",
            }

        # Try checking rate limit using the new check_rate_limit function
        current_count = _check_rate_limit_with_paths(user_identifier, limit_type, limit_string, check_only)

        # If we got a valid count, return the results
        if current_count >= 0:
            return {
                "limit": limit_string,
                "remaining": max(0, count - current_count),
                "reset_after": get_reset_time(period),
                "current_count": current_count,
                "period": period,
                "exceeded": current_count >= count,
            }

        # Fall back to direct Redis checks
        current_count = _check_with_direct_redis(direct_redis, user_identifier, limit_type, period)

        # If direct Redis check fails, try with SlowAPI's internal storage
        if current_count == 0 and hasattr(limiter, "_storage"):
            current_count = _check_with_slowapi_storage(limiter, user_identifier, limit_type, period)

        # Return the results
        return {
            "limit": limit_string,
            "remaining": max(0, count - current_count),
            "reset_after": get_reset_time(period),
            "current_count": current_count,
            "period": period,
        }
    except Exception as e:
        logger.error(f"Error in get_limit_info: {str(e)}")
        # Return safe defaults
        try:
            count_int = int(count_str) if "count_str" in locals() else 10
        except (ValueError, TypeError):
            count_int = 10

        return {
            "limit": limit_string if "limit_string" in locals() else "10/month",
            "remaining": count_int,
            "reset_after": get_reset_time("month"),
            "error": str(e),
            "note": "Error retrieving limits - showing defaults",
        }


def _check_rate_limit_with_paths(user_identifier: str, limit_type: str, limit_string: str, check_only: bool = False) -> int:
    """Check rate limit against all relevant API paths.

    Args:
        user_identifier: The user identifier
        limit_type: The type of limit to check
        limit_string: The limit string (e.g., "10/month")
        check_only: If True, don't increment counters during checks

    Returns:
        The current count or -1 if all checks failed
    """
    # Map our limit types to the corresponding endpoint paths
    endpoint_paths: Dict[str, List[str]] = {
        "generate_concept": [
            # The main concept generation endpoint
            "/concepts/generate",
            # Include the generate-with-palettes endpoint
            "/concepts/generate-with-palettes",
        ],
        "refine_concept": ["/concepts/refine"],
        "store_concept": ["/concepts/store"],
        "get_concepts": ["/concepts/list"],
        "sessions": ["/sessions/sync"],  # Only sync endpoint seems relevant here
        "export_action": ["/export/process"],
    }

    if limit_type not in endpoint_paths:
        return -1  # Not found

    max_count = 0
    final_limit_status: Optional[Dict[str, Any]] = None

    # Iterate through all paths associated with this limit type
    for path in endpoint_paths[limit_type]:
        limit_status: Dict[str, Any] = check_rate_limit(
            user_id=user_identifier,
            endpoint=path,
            limit=limit_string,
            check_only=check_only,
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
        return max_count

    # All checks failed
    logger.warning(f"All rate limit checks failed for {limit_type}, falling back to direct Redis check.")
    return -1


def _check_with_direct_redis(direct_redis: Redis, user_identifier: str, limit_type: str, period: str) -> int:
    """Check rate limit directly with Redis.

    Args:
        direct_redis: Redis client
        user_identifier: The user identifier
        limit_type: The type of limit to check
        period: The time period for the limit

    Returns:
        The current count
    """
    current = 0

    try:
        # Generate the Redis keys that might store our limits
        keys_to_try = _generate_key_patterns(user_identifier, limit_type, period)

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
                        val_str = val.decode() if isinstance(val, bytes) else str(val)
                        val_int = int(val_str)
                        if val_int > current:
                            current = val_int
                    except (ValueError, TypeError):
                        pass
            except Exception:
                # Suppress individual key errors
                pass
    except Exception as e:
        logger.warning(f"Error querying Redis directly: {str(e)}")

    return current


def _generate_key_patterns(user_identifier: str, limit_type: str, period: str) -> List[str]:
    """Generate Redis key patterns to check.

    Args:
        user_identifier: The user identifier
        limit_type: The type of limit to check
        period: The time period for the limit

    Returns:
        List of key patterns to check
    """
    # Map our limit types to the corresponding endpoint paths
    endpoint_paths: Dict[str, List[str]] = {
        "generate_concept": [
            # The main concept generation endpoint
            "/concepts/generate",
            # Include the generate-with-palettes endpoint
            "/concepts/generate-with-palettes",
        ],
        "refine_concept": ["/concepts/refine"],
        "store_concept": ["/concepts/store"],
        "get_concepts": ["/concepts/list"],
        "sessions": ["/sessions/sync"],  # Only sync endpoint seems relevant here
        "export_action": ["/export/process"],
    }

    keys_to_try: List[str] = []

    # Basic key
    keys_to_try.append(f"{user_identifier}:{period}")

    # Add endpoint-specific keys
    if limit_type in endpoint_paths:
        for path in endpoint_paths[limit_type]:
            # Different key formats that might be used
            keys_to_try.extend(
                [
                    f"POST:{path}:{user_identifier}:{period}",
                    f"{path}:{user_identifier}:{period}",
                    f"{user_identifier}:{path}:{period}",
                    # Also try with /api prefix that might be used in some implementations
                    f"POST:/api{path}:{user_identifier}:{period}",
                    f"/api{path}:{user_identifier}:{period}",
                    f"{user_identifier}:/api{path}:{period}",
                ]
            )

    # Special case for SVG conversion which uses a specific prefix to avoid affecting other rate limits
    if limit_type == "svg_conversion":
        keys_to_try.append(f"svg:{user_identifier}:{period}")
        # Add the new SVG-specific keys
        if limit_type in endpoint_paths and endpoint_paths[limit_type]:
            for path in endpoint_paths[limit_type]:
                keys_to_try.extend(
                    [
                        f"svg:POST:{path}:{user_identifier}:{period}",
                        f"svg:{path}:{user_identifier}:{period}",
                        # Try with /api prefix too
                        f"svg:POST:/api{path}:{user_identifier}:{period}",
                        f"svg:/api{path}:{user_identifier}:{period}",
                    ]
                )

    return keys_to_try


def _check_with_slowapi_storage(limiter: Any, user_identifier: str, limit_type: str, period: str) -> int:
    """Check rate limit using SlowAPI's internal storage.

    Args:
        limiter: The SlowAPI limiter instance
        user_identifier: The user identifier
        limit_type: The type of limit to check
        period: The time period for the limit

    Returns:
        The current count
    """
    current = 0

    try:
        # Get the storage backend (Redis or memory)
        storage = limiter._storage

        # Define endpoint paths mapping (same as in other functions)
        endpoint_paths: Dict[str, List[str]] = {
            "generate_concept": [
                "/concepts/generate",
                "/concepts/generate-with-palettes",
            ],
            "refine_concept": ["/concepts/refine"],
            "store_concept": ["/concepts/store"],
            "get_concepts": ["/concepts/list"],
            "sessions": ["/sessions/sync"],
            "export_action": ["/export/process"],
        }

        # Only attempt basic operations, not scan_iter which isn't supported
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
                        val_str = val.decode() if isinstance(val, bytes) else str(val)
                        val_int = int(val_str)
                        if val_int > current:
                            current = val_int
                    except (ValueError, TypeError):
                        pass
            except Exception:
                # Suppress key errors
                pass
    except Exception as e:
        logger.warning(f"Error querying SlowAPI storage: {str(e)}")

    return current
