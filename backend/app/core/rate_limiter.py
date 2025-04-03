"""
Rate limiter configuration module.

This module configures the rate limiter for the API using SlowAPI with Redis.
"""

import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import FastAPI, Request
import redis
from backend.app.core.config import settings
import time

# Configure logging
logger = logging.getLogger(__name__)

def get_redis_client():
    """
    Create and return a Redis client configured with Upstash Redis credentials.
    
    Returns:
        redis.Redis: Configured Redis client
    """
    try:
        redis_client = redis.Redis(
            host=settings.UPSTASH_REDIS_ENDPOINT,
            port=settings.UPSTASH_REDIS_PORT,
            password=settings.UPSTASH_REDIS_PASSWORD,
            ssl=True,
            decode_responses=True,
            socket_timeout=5,  # Add timeout to avoid hanging connections
            socket_keepalive=True,  # Keep connection alive
            retry_on_timeout=True,  # Retry on timeout
            max_connections=10  # Limit number of connections in pool
        )
        # Test the connection
        redis_client.ping()
        logger.info("Successfully connected to Redis")
        return redis_client
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
                logger.info(f"Incremented rate limit key: {key} = {result}")
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
            return await func(request, *args, **kwargs)
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Redis connection error during rate limiting: {str(e)}")
            logger.warning("Bypassing rate limit due to Redis connection error")
            # Continue processing the request without rate limiting
            return await func.__wrapped__(request, *args, **kwargs)
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
    if redis_client:
        # Format: redis://:{password}@{host}:{port}
        storage_uri = f"redis://:{settings.UPSTASH_REDIS_PASSWORD}@{settings.UPSTASH_REDIS_ENDPOINT}:{settings.UPSTASH_REDIS_PORT}"
        logger.info("Using Redis for rate limiting storage")
    else:
        logger.warning("Using memory storage for rate limiting")
    
    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=storage_uri,
        # Default limits
        default_limits=["200/day", "50/hour", "10/minute"],
        strategy="fixed-window"  # Use fixed window strategy for more reliability
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
            return limit_decorator(safe_func)
            
        return wrapper
        
    limiter.limit = safe_limit
    
    # Attach our custom increment function to the limiter for manual tracking
    limiter.increment_rate_limit = increment_rate_limit
    
    return limiter 