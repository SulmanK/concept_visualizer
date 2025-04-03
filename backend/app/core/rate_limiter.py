"""
Rate limiter configuration module.

This module configures the rate limiter for the API using SlowAPI with Redis.
"""

import logging
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from fastapi import FastAPI
import redis
from backend.app.core.config import settings

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
            decode_responses=True
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
        default_limits=["200/day", "50/hour", "10/minute"]
    )
    
    # Add limiter to the application state
    app.state.limiter = limiter
    
    # Register the rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    return limiter 