"""
Health check endpoints for the API.

This module provides health check endpoints to monitor the API's status.
"""

from fastapi import APIRouter, Request
from slowapi.util import get_remote_address
from datetime import datetime
import calendar

router = APIRouter()


@router.get("/health")
@router.head("/health")
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
    
    # Get all the configured limits
    limits_info = {
        "user_identifier": user_ip,
        "limits": {
            "generate_concept": _get_limit_info(limiter, "10/month", user_ip),
            "refine_concept": _get_limit_info(limiter, "10/hour", user_ip),
            "store_concept": _get_limit_info(limiter, "10/month", user_ip),
            "get_concepts": _get_limit_info(limiter, "30/minute", user_ip),
            "sessions": _get_limit_info(limiter, "60/hour", user_ip),
            "svg_conversion": _get_limit_info(limiter, "20/hour", user_ip),
        },
        "default_limits": ["200/day", "50/hour", "10/minute"]
    }
    
    return limits_info


def _get_limit_info(limiter, limit_string, user_identifier):
    """Get information about a specific rate limit.
    
    Args:
        limiter: The slowapi limiter instance
        limit_string: The limit string (e.g., "10/month")
        user_identifier: The user identifier (IP address)
        
    Returns:
        dict: Rate limit information.
    """
    try:
        # Extract limit data
        count, period = limit_string.split("/")
        count = int(count)
        
        # Get the storage backend (Redis or memory)
        storage = limiter.storage
        
        # Create a key similar to how slowapi would do it
        key = f"{user_identifier}:{period}"
        
        # Try to get current usage
        current = storage.get(key) or 0
        
        # Calculate remaining
        remaining = max(0, count - int(current))
        
        return {
            "limit": limit_string,
            "remaining": remaining,
            "reset_after": _get_reset_time(period),
        }
    except Exception as e:
        return {
            "limit": limit_string,
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