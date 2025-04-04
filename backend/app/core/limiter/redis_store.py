"""
Redis integration for rate limiting in the Concept Visualizer API.

This module provides functions for interacting with Redis for rate limiting purposes.
"""

import logging
import redis
import redis.connection
from typing import Optional

from app.core.config import settings
from app.core.exceptions import ConfigurationError, RateLimitError
from app.core.limiter.keys import calculate_ttl, generate_rate_limit_keys

# Configure logging
logger = logging.getLogger(__name__)

# Store a single Redis client instance to avoid creating multiple connections
_redis_client = None

def get_redis_client() -> Optional[redis.Redis]:
    """
    Create and return a Redis client configured with Upstash Redis credentials.
    
    Returns:
        redis.Redis: Configured Redis client or None if connection fails
        
    Raises:
        ConfigurationError: If Redis is improperly configured
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
        except redis.exceptions.ConnectionError as e:
            error_message = f"Redis connection error: {str(e)}"
            logger.error(error_message)
            # We return None here rather than raising an exception because we want
            # the application to fall back to memory storage rather than fail
            return None
        except Exception as e:
            logger.error(f"Redis ping failed: {str(e)}")
            return None
            
    except redis.exceptions.ConnectionError as e:
        error_message = f"Failed to connect to Redis: {str(e)}"
        logger.error(error_message)
        # Fallback to memory storage
        logger.warning("Falling back to memory storage for rate limiting")
        return None
    except Exception as e:
        error_message = f"Unexpected error connecting to Redis: {str(e)}"
        logger.error(error_message)
        if "invalid URL scheme" in str(e) or "NoneType" in str(e):
            raise ConfigurationError(
                message="Invalid Redis configuration",
                config_key="UPSTASH_REDIS_ENDPOINT",
                details={"error": str(e)}
            )
        # Fallback to memory storage for other errors
        logger.warning("Falling back to memory storage for rate limiting")
        return None


def increment_rate_limit(user_id: str, endpoint: str, period: str = "month") -> bool:
    """
    Manually increment a rate limit counter in Redis.
    
    Args:
        user_id: The user identifier (usually session ID or IP)
        endpoint: The endpoint being rate limited (e.g., "/api/concept/generate")
        period: The time period (minute, hour, day, month)
        
    Returns:
        bool: True if successful, False otherwise
        
    Raises:
        RateLimitError: If there's an error updating the rate limit
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            logger.warning("Cannot increment rate limit: Redis not available")
            return False
            
        # Get keys and TTL
        keys = generate_rate_limit_keys(user_id, endpoint, period)
        ttl = calculate_ttl(period)
        
        # Try to increment all possible key formats
        success = False
        failed_keys = []
        
        for key in keys:
            try:
                # Increment and set expiry
                result = redis_client.incr(key)
                redis_client.expire(key, ttl)
                logger.debug(f"Incremented rate limit key: {key} = {result}")
                success = True
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis error incrementing key {key}: {str(e)}")
                failed_keys.append(key)
            except Exception as e:
                logger.error(f"Failed to increment key {key}: {str(e)}")
                failed_keys.append(key)
        
        if not success and failed_keys:
            raise RateLimitError(
                message="Failed to increment any rate limit keys",
                endpoint=endpoint,
                details={"user_id": user_id, "period": period, "failed_keys": failed_keys}
            )
                
        return success
    except RateLimitError:
        # Re-raise RateLimitError
        raise
    except redis.exceptions.RedisError as e:
        error_message = f"Redis error during rate limit operation: {str(e)}"
        logger.error(error_message)
        raise RateLimitError(
            message=error_message,
            endpoint=endpoint,
            details={"user_id": user_id, "period": period}
        )
    except Exception as e:
        error_message = f"Error incrementing rate limit: {str(e)}"
        logger.error(error_message)
        raise RateLimitError(
            message=error_message,
            endpoint=endpoint,
            details={"user_id": user_id, "period": period}
        ) 