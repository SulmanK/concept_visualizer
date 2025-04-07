"""
Rate limiter configuration for the Concept Visualizer API.

This module provides the main setup function for rate limiting with SlowAPI and Redis.
"""

import logging
from fastapi import FastAPI
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter.keys import get_user_id
from app.core.limiter.decorators import safe_ratelimit
from app.core.limiter.redis_store import get_redis_client
from app.core.config import settings
from app.utils.security.mask import mask_id

# Configure logging
logger = logging.getLogger(__name__)

def configure_limiter(debug: bool = False) -> Limiter:
    """
    Configure the rate limiter with appropriate settings.
    
    Args:
        debug: Whether to enable debug mode
        
    Returns:
        Configured Limiter instance
    """
    # Set up Redis store
    redis_client = get_redis_client()
    
    # Default rate limits if not configured in settings
    default_limits = getattr(settings, "DEFAULT_RATE_LIMITS", ["200/day", "50/hour", "10/minute"])
    
    # Rate limiting enabled by default
    rate_limiting_enabled = getattr(settings, "RATE_LIMITING_ENABLED", True)
    
    if redis_client:
        try:
            # Test Redis connection
            redis_client.ping()
            logger.info("Connected to Redis for rate limiting")
            
            # Create Redis-backed rate limiter
            # Use memory storage but with our custom Redis client
            limiter = Limiter(
                key_func=get_user_id,  # Use user ID for rate limiting
                storage_uri="memory://",  # Use memory URI but with Redis storage options
                storage_options={"client": redis_client},
                strategy="fixed-window",
                enabled=rate_limiting_enabled,
                default_limits=default_limits
            )
            
            logger.info("Rate limiter configured with Redis backend")
            return limiter
            
        except Exception as e:
            logger.warning(f"Redis connection failed, falling back to in-memory storage: {str(e)}")
    
    # Fallback to memory storage
    logger.info("Configuring rate limiter with memory storage")
    limiter = Limiter(
        key_func=get_user_id,
        storage_uri="memory://",
        strategy="fixed-window",
        enabled=rate_limiting_enabled,
        default_limits=default_limits
    )
    
    return limiter

def setup_limiter_for_app(app: FastAPI) -> None:
    """
    Set up rate limiting for a FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    # Configure limiter
    limiter = configure_limiter()
    
    # Add limiter to app state
    app.state.limiter = limiter
    
    # Register rate limit exceeded handler
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