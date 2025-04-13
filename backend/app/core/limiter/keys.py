"""
Key generation for rate limiting in the Concept Visualizer API.

This module provides functions for extracting session IDs and generating keys
for rate limiting purposes.
"""

import logging
from fastapi import Request
from slowapi.util import get_remote_address

# Import JWT utilities to extract user ID from tokens if needed
from app.utils.jwt_utils import extract_user_id_from_token

# Configure logging
logger = logging.getLogger(__name__)


def get_user_id(request: Request) -> str:
    """
    Get the user's ID from request state for rate limiting.
    Falls back to extracting from JWT token, then to IP address if no user ID is available.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: User ID or IP address to use as rate limit key
    """
    # First try to get the user_id from request state (set by auth middleware)
    if hasattr(request, "state") and hasattr(request.state, "user") and request.state.user:
        user_id = request.state.user.get("id")
        if user_id:
            logger.debug(f"Using user_id from request state for rate limiting: {user_id[:4]}****")
            return f"user:{user_id}"
    
    # If no user in state, try to extract from Authorization header
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        user_id = extract_user_id_from_token(token, validate=False)
        if user_id:
            logger.debug(f"Using user_id extracted from JWT token for rate limiting: {user_id[:4]}****")
            return f"user:{user_id}"
    
    # Fall back to IP address if no user ID
    ip = get_remote_address(request)
    logger.debug(f"No user ID found, using IP for rate limiting: {ip}")
    return f"ip:{ip}"


def get_endpoint_key(request: Request) -> str:
    """
    Get a unique key for the current endpoint.
    
    Args:
        request: FastAPI request object
        
    Returns:
        str: Unique key for the endpoint
    """
    route = request.scope.get("route")
    if route and hasattr(route, "path"):
        path = route.path
        return f"endpoint:{path}"
    
    # Fallback to the raw path if route not available
    path = request.scope.get("path", "unknown")
    return f"endpoint:{path}"


def combine_keys(user_id: str, endpoint_key: str) -> str:
    """
    Combine user and endpoint keys for granular rate limiting.
    
    Args:
        user_id: The user identifier (usually user ID or IP)
        endpoint_key: The endpoint identifier
        
    Returns:
        str: Combined key for rate limiting
    """
    return f"{user_id}:{endpoint_key}"


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
    # Special case for SVG conversion endpoints to avoid conflicting with other endpoints
    if "svg" in endpoint.lower() or "convert" in endpoint.lower():
        return [
            # SVG-specific keys to avoid affecting other rate limits
            f"svg:{user_id}:{period}",
            
            # Make the standard format keys specific to SVG
            f"svg:POST:{endpoint}:{user_id}:{period}", 
            f"svg:{endpoint}:{user_id}:{period}"
        ]
    
    # Standard keys for all other endpoints
    return [
        # Format used by our rate limit checker
        f"{user_id}:{period}",
        
        # Formats that match SlowAPI's internal storage patterns
        f"POST:{endpoint}:{user_id}:{period}", 
        
        # Format with path and IP
        f"{endpoint}:{user_id}:{period}"
    ] 