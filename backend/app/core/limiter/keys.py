"""Rate limiter key generation utilities.

This module provides functions for generating keys used by the rate limiter
to uniquely identify users and endpoints.
"""

import logging

from fastapi import Request

from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)


def get_user_id(request: Request) -> str:
    """Get user identifier for rate limiting.

    Extracts the user ID from request authentication, or falls back to IP address.
    The key is used to track rate limits per user.

    Args:
        request: The FastAPI request

    Returns:
        User ID or IP address for rate limiting
    """
    # First try to get authenticated user ID from request state
    if hasattr(request.state, "user") and request.state.user:
        # Handle user info as either a dict or an object
        user_info = request.state.user

        # Try to get ID from user info (if it's a dict)
        if isinstance(user_info, dict) and "id" in user_info:
            user_id = user_info["id"]
            logger.debug(f"Using authenticated user_id from dict for rate limiting: {user_id[:4]}****")
            return f"user:{user_id}"

        # Try as an object attribute
        user_id = getattr(user_info, "id", None)
        if user_id:
            logger.debug(f"Using authenticated user_id from object for rate limiting: {user_id[:4]}****")
            return f"user:{user_id}"

        # Try direct user_info if it might be the ID itself
        if isinstance(user_info, str):
            logger.debug(f"Using authenticated user_id from string for rate limiting: {user_info[:4]}****")
            return f"user:{user_info}"

    # Next try to get user ID from auth token
    if hasattr(request.state, "token") and request.state.token:
        token_info = request.state.token

        # Try to get ID from token (if it's a dict)
        if isinstance(token_info, dict) and "sub" in token_info:
            token_id = token_info["sub"]
            logger.debug(f"Using user_id extracted from JWT token 'sub' for rate limiting: {token_id[:4]}****")
            return f"token:{token_id}"

        # Try as an object attribute
        token_id = getattr(token_info, "id", None) or getattr(token_info, "sub", None)
        if token_id:
            logger.debug(f"Using user_id extracted from JWT token for rate limiting: {token_id[:4]}****")
            return f"token:{token_id}"

    # If no user ID, use the IP address
    client_ip = get_client_ip(request)
    logger.debug(f"No user ID found, using IP for rate limiting: {client_ip}")
    return f"ip:{client_ip}"


def get_client_ip(request: Request) -> str:
    """Extract client IP address from request.

    Handles proxies and various header formats.

    Args:
        request: The FastAPI request

    Returns:
        Client IP address
    """
    # Check for X-Forwarded-For header (standard for proxies)
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Use the first IP in the list (client IP)
        return forwarded_for.split(",")[0].strip()

    # Check for X-Real-IP header (common with Nginx)
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()

    # Fallback to client host from connection
    return request.client.host if request.client else "unknown"


def get_endpoint_key(request: Request) -> str:
    """Get endpoint key for rate limiting.

    Normalizes the path by removing query parameters and standardizing format.

    Args:
        request: The FastAPI request

    Returns:
        Normalized endpoint path
    """
    # Start with full path
    path = request.url.path

    # Remove API prefix for more consistent rate limiting
    api_prefix = settings.API_PREFIX
    if path.startswith(api_prefix):
        path = path[len(api_prefix) :]

    # Ensure path starts with slash
    if not path.startswith("/"):
        path = f"/{path}"

    return path


def combine_keys(user_key: str, endpoint_key: str) -> str:
    """Combine user and endpoint keys for rate limiting.

    Creates a composite key for per-user, per-endpoint rate limiting.

    Args:
        user_key: The user identification key
        endpoint_key: The endpoint path key

    Returns:
        Combined rate limit key
    """
    return f"{user_key}:{endpoint_key}"


def mask_key(key: str, visible_chars: int = 4) -> str:
    """Mask a key for logging to protect user information.

    Args:
        key: The key to mask
        visible_chars: Number of characters to show at start and end

    Returns:
        Masked key with middle portion replaced by asterisks
    """
    if len(key) <= visible_chars * 2:
        return key  # Key is too short to mask meaningfully

    # Show first and last few characters
    return f"{key[:visible_chars]}***{key[-visible_chars:]}"


def calculate_ttl(period: str) -> int:
    """Calculate the time-to-live (TTL) in seconds based on the rate limit period.

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
    """Generate all possible key formats for rate limiting.

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
            f"svg:{endpoint}:{user_id}:{period}",
        ]

    # Standard keys for all other endpoints
    return [
        # Format used by our rate limit checker
        f"{user_id}:{period}",
        # Formats that match SlowAPI's internal storage patterns
        f"POST:{endpoint}:{user_id}:{period}",
        # Format with path and IP
        f"{endpoint}:{user_id}:{period}",
    ]
