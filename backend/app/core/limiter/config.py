"""
Rate limiter configuration for the Concept Visualizer API.

This module provides the main setup function for rate limiting with SlowAPI and Redis.
"""

import logging
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter.keys import get_session_id
from app.core.limiter.decorators import safe_ratelimit
from app.core.limiter.redis_store import get_redis_client
from app.core.config import settings

# Configure logging
logger = logging.getLogger(__name__)

def setup_rate_limiter(app: FastAPI) -> Limiter:
    """
    Configure rate limiting for the FastAPI application.
    
    This function sets up SlowAPI rate limiting with Redis for storage,
    configures error handling, and applies safe wrappers to handle connection issues.
    
    Args:
        app: FastAPI application instance
        
    Returns:
        Limiter: Configured rate limiter instance
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
    
    # Pass the modified limiter back
    return limiter 