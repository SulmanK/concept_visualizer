"""
Key generation for rate limiting in the Concept Visualizer API.

This module provides functions for extracting session IDs and generating keys
for rate limiting purposes.
"""

import logging
from fastapi import Request
from slowapi.util import get_remote_address

# Configure logging
logger = logging.getLogger(__name__)

def get_session_id(request: Request) -> str:
    """
    Get the user's session ID from cookies for rate limiting.
    Falls back to IP address if session ID isn't available.
    
    Args:
        request: The FastAPI request
        
    Returns:
        str: Session ID or IP address to use as rate limit key
    """
    # First try to get the session_id from cookies
    session_id = request.cookies.get("concept_session")
    
    if session_id:
        logger.debug(f"Using session_id for rate limiting: {session_id[:4]}****")
        return f"session:{session_id}"
    
    # Fall back to IP address if no session ID
    ip = get_remote_address(request)
    logger.debug(f"No session ID found, using IP for rate limiting: {ip}")
    return f"ip:{ip}"


def calculate_ttl(period: str) -> int:
    """
    Calculate the time-to-live (TTL) in seconds based on the rate limit period.
    
    Args:
        period: The time period (minute, hour, day, month)
        
    Returns:
        int: TTL in seconds
    """
    if period == "minute":
        return 60
    elif period == "hour":
        return 3600
    elif period == "day":
        return 86400
    else:  # month
        return 2592000  # 30 days


def generate_rate_limit_keys(user_id: str, endpoint: str, period: str) -> list[str]:
    """
    Generate all possible key formats for rate limiting.
    
    Args:
        user_id: The user identifier (usually session ID or IP)
        endpoint: The endpoint being rate limited (e.g., "/api/concept/generate")
        period: The time period (minute, hour, day, month)
        
    Returns:
        list[str]: List of possible rate limit keys
    """
    return [
        # Format used by our rate limit checker
        f"{user_id}:{period}",
        
        # Formats that match SlowAPI's internal storage patterns
        f"POST:{endpoint}:{user_id}:{period}", 
        
        # Format with path and IP
        f"{endpoint}:{user_id}:{period}"
    ] 