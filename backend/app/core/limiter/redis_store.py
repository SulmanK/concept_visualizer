"""
Redis integration for rate limiting in the Concept Visualizer API.

This module provides functions for interacting with Redis for rate limiting purposes.
"""

import logging
import redis
import redis.connection
from typing import Optional, Tuple, Dict

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

def get_rate_limit_count(user_id: str, endpoint: str, period: str = "month") -> Tuple[int, int]:
    """
    Get the current rate limit count for a user and endpoint.
    
    Args:
        user_id: The user identifier (usually session ID or IP)
        endpoint: The endpoint being rate limited (e.g., "/api/concept/generate")
        period: The time period (minute, hour, day, month)
        
    Returns:
        Tuple[int, int]: Current count and TTL in seconds
        
    Raises:
        RateLimitError: If there's an error retrieving the rate limit
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            logger.warning("Cannot get rate limit count: Redis not available")
            return 0, 0
            
        keys = generate_rate_limit_keys(user_id, endpoint, period)
        
        # Try all possible key formats
        for key in keys:
            try:
                # Get current count and TTL
                count = redis_client.get(key)
                if count is not None:
                    count = int(count)
                    ttl = redis_client.ttl(key)
                    logger.debug(f"Found rate limit key: {key} = {count}, TTL: {ttl}s")
                    return count, ttl
            except (redis.exceptions.RedisError, ValueError) as e:
                logger.error(f"Error getting rate limit for key {key}: {str(e)}")
                continue
                
        # No keys found, rate limit not yet set
        logger.debug(f"No rate limit keys found for {user_id} on {endpoint}")
        return 0, 0
        
    except redis.exceptions.RedisError as e:
        error_message = f"Redis error getting rate limit: {str(e)}"
        logger.error(error_message)
        return 0, 0
    except Exception as e:
        error_message = f"Error getting rate limit: {str(e)}"
        logger.error(error_message)
        return 0, 0

def check_rate_limit(user_id: str, endpoint: str, limit: str) -> Dict:
    """
    Check if a user has exceeded their rate limit.
    
    Args:
        user_id: The user identifier (usually session ID or IP)
        endpoint: The endpoint being rate limited (e.g., "/api/concept/generate")
        limit: The rate limit string (e.g., "10/month")
        
    Returns:
        Dict: Rate limit status containing:
            - exceeded: Whether limit is exceeded (bool)
            - count: Current count (int)
            - limit: Maximum allowed (int)
            - period: Time period (str)
            - reset_at: Seconds until reset (int)
            
    Raises:
        RateLimitError: If there's an error checking the rate limit
    """
    try:
        # Parse the limit string (e.g., "10/month" -> limit=10, period="month")
        parts = limit.split("/")
        if len(parts) != 2:
            logger.error(f"Invalid rate limit format: {limit}")
            return {"exceeded": False, "error": "Invalid rate limit format"}
            
        max_requests = int(parts[0])
        period = parts[1]
        
        # Get current count
        current_count, ttl = get_rate_limit_count(user_id, endpoint, period)
        
        # Determine if limit is exceeded
        is_exceeded = current_count >= max_requests
        
        if is_exceeded:
            logger.warning(f"Rate limit exceeded for {user_id} on {endpoint}: {current_count}/{max_requests} {period}")
        else:
            logger.debug(f"Rate limit check for {user_id} on {endpoint}: {current_count}/{max_requests} {period}")
            
        return {
            "exceeded": is_exceeded,
            "count": current_count,
            "limit": max_requests,
            "period": period,
            "reset_at": ttl
        }
    except Exception as e:
        error_message = f"Error checking rate limit: {str(e)}"
        logger.error(error_message)
        # Default to not exceeded on error to prevent false positives
        return {"exceeded": False, "error": str(e)}

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