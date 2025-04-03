"""
Rate limiter configuration module.

This module configures the rate limiter for the API using SlowAPI with Redis.
"""

import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request, Cookie
import redis
from app.core.config import settings
import time
from typing import Optional
import redis.connection

# Configure logging
logger = logging.getLogger(__name__)

# Store a single Redis client instance to avoid creating multiple connections
_redis_client = None

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


def get_redis_client():
    """
    Create and return a Redis client configured with Upstash Redis credentials.
    
    Returns:
        redis.Redis: Configured Redis client
    """
    global _redis_client
    
    # Return the existing client if we already have one
    if _redis_client is not None:
        try:
            # Ping to make sure the connection is still alive
            _redis_client.ping()
            logger.debug("Using existing Redis connection")
            return _redis_client
        except Exception as e:
            logger.warning(f"Existing Redis connection failed: {str(e)}. Creating new connection.")
            _redis_client = None
            
    try:
        # Check if we should connect to Redis at all, or skip it completely
        if not settings.UPSTASH_REDIS_ENDPOINT or settings.UPSTASH_REDIS_ENDPOINT == "your-redis-url.upstash.io":
            logger.warning("Redis connection disabled - missing or default configuration")
            return None

        # Create a simple Redis client without using a connection pool
        # This avoids compatibility issues with different Redis library versions
        _redis_client = redis.Redis(
            host=settings.UPSTASH_REDIS_ENDPOINT,
            port=settings.UPSTASH_REDIS_PORT,
            password=settings.UPSTASH_REDIS_PASSWORD,
            ssl=True,
            decode_responses=True,
            socket_timeout=3,
            socket_keepalive=True,
            retry_on_timeout=True
        )
        
        # Test the connection
        logger.info("Testing Redis connection...")
        try:
            result = _redis_client.ping()
            if result:
                logger.info("Successfully connected to Redis")
                return _redis_client
            else:
                logger.warning("Redis ping returned False, connection may be unreliable")
                return None
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return None
            
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {str(e)}")
        # Fallback to memory storage
        logger.warning("Falling back to memory storage for rate limiting")
        return None


# Add a utility function to manually increment rate limit counters
def increment_rate_limit(user_id, endpoint, period="month"):
    """
    Manually increment a rate limit counter in Redis.
    
    Args:
        user_id: The user identifier (usually IP address)
        endpoint: The endpoint being rate limited (e.g., "/api/concept/generate")
        period: The time period (minute, hour, day, month)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            logger.warning("Cannot increment rate limit: Redis not available")
            return False
            
        # Use formats that match both SlowAPI's storage and our health endpoint checks
        keys = [
            # Format used by our rate limit checker
            f"{user_id}:{period}",
            
            # Formats that match SlowAPI's internal storage patterns
            f"POST:{endpoint}:{user_id}:{period}", 
            
            # Format with path and IP
            f"{endpoint}:{user_id}:{period}"
        ]
        
        # Calculate TTL based on period
        if period == "minute":
            ttl = 60
        elif period == "hour":
            ttl = 3600
        elif period == "day":
            ttl = 86400
        else:  # month
            ttl = 2592000  # 30 days
        
        # Try to increment all possible key formats
        success = False
        for key in keys:
            try:
                # Increment and set expiry
                result = redis_client.incr(key)
                redis_client.expire(key, ttl)
                logger.debug(f"Incremented rate limit key: {key} = {result}")
                success = True
            except Exception as e:
                logger.error(f"Failed to increment key {key}: {str(e)}")
                
        return success
    except Exception as e:
        logger.error(f"Error incrementing rate limit: {str(e)}")
        return False


# Wrapper for rate limiting that handles Redis connection errors
def safe_ratelimit(func):
    """Decorator to handle Redis connection errors during rate limiting."""
    async def wrapper(request: Request, *args, **kwargs):
        try:
            # Make sure we're properly awaiting the decorated function
            result = await func(request, *args, **kwargs)
            return result
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection error during rate limiting: {str(e)}")
            logger.warning("Bypassing rate limit due to Redis connection error")
            # Continue processing the request without rate limiting
            # Make sure we're also properly awaiting the wrapped function
            if hasattr(func, '__wrapped__') and callable(func.__wrapped__):
                return await func.__wrapped__(request, *args, **kwargs)
            else:
                # If no wrapped function, just call the original
                return await func(request, *args, **kwargs)
        except Exception as e:
            logger.error(f"Unexpected error during rate limiting: {str(e)}")
            # Re-raise other exceptions
            raise
    return wrapper


def setup_rate_limiter(app: FastAPI):
    """
    Configure rate limiting for the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Create Redis client
    redis_client = get_redis_client()
    
    # Configure storage for rate limiter
    storage_uri = None
    try:
        if redis_client:
            # Format: redis://:{password}@{host}:{port}
            storage_uri = f"redis://:{settings.UPSTASH_REDIS_PASSWORD}@{settings.UPSTASH_REDIS_ENDPOINT}:{settings.UPSTASH_REDIS_PORT}"
            logger.info("Using Redis for rate limiting storage")
        else:
            logger.warning("Using memory storage for rate limiting")
        
        # Initialize rate limiter with session ID instead of IP address
        limiter = Limiter(
            key_func=get_session_id,  # Use session ID for rate limiting
            storage_uri=storage_uri,
            # Default limits
            default_limits=["200/day", "50/hour", "10/minute"],
            strategy="fixed-window"  # Use fixed window strategy for more reliability
        )
    except Exception as e:
        # Fallback to in-memory storage if Redis fails
        logger.error(f"Error configuring Redis for SlowAPI: {str(e)}")
        logger.warning("Falling back to memory storage for SlowAPI rate limiter")
        limiter = Limiter(
            key_func=get_session_id,
            # No storage URI = in-memory storage
            default_limits=["200/day", "50/hour", "10/minute"],
            strategy="fixed-window"
        )
    
    # Add limiter to the application state
    app.state.limiter = limiter
    
    # Register the rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Patch the limiter's limit method with our safe version
    original_limit = limiter.limit
    
    def safe_limit(*args, **kwargs):
        """Wrap the limit method to handle Redis connection errors."""
        limit_decorator = original_limit(*args, **kwargs)
        
        def wrapper(func):
            # Apply our safe_ratelimit decorator first, then the original limit
            safe_func = safe_ratelimit(func)
            wrapped = limit_decorator(safe_func)
            
            # Make sure to preserve the original function as __wrapped__
            if not hasattr(wrapped, '__wrapped__'):
                wrapped.__wrapped__ = func
                
            return wrapped
            
        return wrapper
        
    limiter.limit = safe_limit
    
    # Attach our custom increment function to the limiter for manual tracking
    limiter.increment_rate_limit = increment_rate_limit
    
    return limiter 