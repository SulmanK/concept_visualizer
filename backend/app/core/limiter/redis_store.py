"""
Redis-based storage for rate limiting.

This module provides a Redis implementation for the rate limiter storage.
"""

import json
import logging
import time
from typing import Dict, List, Optional, Any, Tuple, Union
import redis

from app.core.config import settings
from app.utils.security.mask import mask_key, mask_id


# Configure logging
logger = logging.getLogger(__name__)


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get a configured Redis client for rate limiting.
    
    Returns:
        Configured Redis client or None if Redis is not available
    """
    # Check if Redis is configured
    if not settings.UPSTASH_REDIS_ENDPOINT or not settings.UPSTASH_REDIS_PASSWORD:
        logger.info("Redis settings not configured, rate limiting will use in-memory storage")
        return None
    
    # Construct Redis URL from settings
    # For Upstash, the format is typically redis://username:password@endpoint:port
    # with a default username of 'default'
    redis_url = f"redis://default:{settings.UPSTASH_REDIS_PASSWORD}@{settings.UPSTASH_REDIS_ENDPOINT}:{settings.UPSTASH_REDIS_PORT}"
    
    # Log with masked endpoint - use mask_id which is better for hostnames
    masked_endpoint = mask_id(settings.UPSTASH_REDIS_ENDPOINT, visible_chars=8)
    logger.debug(f"Connecting to Redis using endpoint: {masked_endpoint}")
    
    try:
        # Create Redis client
        client = redis.Redis(
            host=settings.UPSTASH_REDIS_ENDPOINT,
            port=settings.UPSTASH_REDIS_PORT,
            password=settings.UPSTASH_REDIS_PASSWORD,
            socket_timeout=2,
            socket_connect_timeout=2,
            retry_on_timeout=True,
            ssl=True,  # Important for Upstash - they require SSL
            decode_responses=True  # Automatically decode responses to strings
        )
        
        # Try a ping to make sure the connection works
        client.ping()
        logger.info(f"Successfully connected to Redis at {masked_endpoint}")
        return client
    except Exception as e:
        logger.error(f"Error connecting to Redis: {str(e)}")
        return None


class RedisStore:
    """Redis-based storage for rate limiting data."""
    
    def __init__(self, redis_client: redis.Redis, prefix: str = "ratelimit:"):
        """
        Initialize with Redis client.
        
        Args:
            redis_client: Configured Redis client
            prefix: Key prefix for rate limit data in Redis
        """
        self.redis = redis_client
        self.prefix = prefix
        self.logger = logging.getLogger("redis_store")
        
    def _make_key(self, key: str) -> str:
        """
        Create a namespaced Redis key.
        
        Args:
            key: Base key to namespace
            
        Returns:
            Prefixed Redis key
        """
        return f"{self.prefix}{key}"
    
    def _log_operation(self, operation: str, key: str, result: Any = None) -> None:
        """
        Log a Redis operation with masked key.
        
        Args:
            operation: Name of the operation
            key: Redis key being operated on
            result: Optional result to include in log
        """
        masked_key = mask_key(key)
        if result is not None:
            self.logger.debug(f"Redis {operation} on {masked_key}: {result}")
        else:
            self.logger.debug(f"Redis {operation} on {masked_key}")
            
    def increment(self, key: str, expiry: int, amount: int = 1) -> int:
        """
        Increment counter and set expiry.
        
        Args:
            key: Counter key
            expiry: Expiry time in seconds
            amount: Amount to increment by
            
        Returns:
            New counter value
        """
        redis_key = self._make_key(key)
        try:
            # Use a pipeline to ensure atomicity
            pipe = self.redis.pipeline()
            pipe.incrby(redis_key, amount)
            pipe.expire(redis_key, expiry)
            result = pipe.execute()
            
            new_value = result[0]
            self._log_operation("increment", redis_key, new_value)
            return new_value
            
        except Exception as e:
            self.logger.error(f"Redis increment failed: {e}")
            # Return a safe fallback value
            return 1
    
    def get(self, key: str) -> int:
        """
        Get current counter value.
        
        Args:
            key: Counter key
            
        Returns:
            Current counter value or 0 if not found
        """
        redis_key = self._make_key(key)
        try:
            value = self.redis.get(redis_key)
            if value is None:
                return 0
            result = int(value)
            self._log_operation("get", redis_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Redis get failed: {e}")
            return 0
    
    def get_with_expiry(self, key: str) -> Tuple[int, int]:
        """
        Get counter value with remaining expiry time.
        
        Args:
            key: Counter key
            
        Returns:
            Tuple of (current value, remaining seconds)
        """
        redis_key = self._make_key(key)
        try:
            # Use a pipeline to reduce round trips
            pipe = self.redis.pipeline()
            pipe.get(redis_key)
            pipe.ttl(redis_key)
            result = pipe.execute()
            
            value = int(result[0]) if result[0] else 0
            ttl = max(0, result[1]) if result[1] and result[1] > 0 else 0
            
            self._log_operation("get_with_expiry", redis_key, f"value={value}, ttl={ttl}")
            return (value, ttl)
            
        except Exception as e:
            self.logger.error(f"Redis get_with_expiry failed: {e}")
            return (0, 0)
    
    def get_quota(
        self, 
        user_id: str,
        endpoint: str, 
        limit: int,
        period: int
    ) -> Dict[str, Any]:
        """
        Get quota information for a user and endpoint.
        
        Args:
            user_id: The user identifier (usually user ID or IP)
            endpoint: API endpoint being accessed
            limit: Maximum requests allowed
            period: Time period in seconds
            
        Returns:
            Dict with quota information
        """
        # Create a key combining user and endpoint
        key = f"{user_id}:{endpoint}"
        redis_key = self._make_key(key)
        
        try:
            # Get current count and TTL
            count, ttl = self.get_with_expiry(key)
            
            # Calculate reset time
            reset_at = int(time.time() + ttl) if ttl > 0 else int(time.time() + period)
            
            # Calculate remaining
            remaining = max(0, limit - count)
            
            quota = {
                "total": limit,
                "remaining": remaining,
                "used": count,
                "reset_at": reset_at,
            }
            
            self._log_operation("get_quota", redis_key, quota)
            return quota
            
        except Exception as e:
            self.logger.error(f"Redis get_quota failed: {e}")
            # Return conservative defaults
            return {
                "total": limit,
                "remaining": limit // 2,  # Assume half used to be safe
                "used": limit // 2,
                "reset_at": int(time.time() + period),
            }

    def check_rate_limit(
        self, 
        user_id: str, 
        endpoint: str, 
        limit: int, 
        period: int
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if a request is rate limited.
        
        Args:
            user_id: The user identifier (usually user ID or IP)
            endpoint: API endpoint being accessed
            limit: Maximum requests allowed
            period: Time period in seconds
            
        Returns:
            Tuple of (is_allowed, quota_info)
        """
        # Create a key combining user and endpoint
        key = f"{user_id}:{endpoint}"
        redis_key = self._make_key(key)
        
        try:
            # Get current value
            count = self.get(key)
            
            # Check if already over limit
            if count >= limit:
                # Get full quota info
                quota = self.get_quota(user_id, endpoint, limit, period)
                self._log_operation("check_rate_limit", redis_key, "DENIED")
                return (False, quota)
            
            # Increment counter
            new_count = self.increment(key, period)
            
            # Check if increment puts us over the limit
            remaining = max(0, limit - new_count)
            reset_at = int(time.time() + period)
            
            quota = {
                "total": limit,
                "remaining": remaining,
                "used": new_count,
                "reset_at": reset_at,
            }
            
            is_allowed = new_count <= limit
            result = "ALLOWED" if is_allowed else "DENIED"
            self._log_operation("check_rate_limit", redis_key, result)
            
            return (is_allowed, quota)
            
        except Exception as e:
            self.logger.error(f"Redis check_rate_limit failed: {e}")
            # Default to allowing the request but with minimal remaining quota
            return (True, {
                "total": limit,
                "remaining": 1,
                "used": limit - 1,
                "reset_at": int(time.time() + period),
            })
            
    def reset(self, key: str) -> bool:
        """
        Reset a rate limit counter.
        
        Args:
            key: Counter key to reset
            
        Returns:
            True if successful, False otherwise
        """
        redis_key = self._make_key(key)
        try:
            self.redis.delete(redis_key)
            self._log_operation("reset", redis_key)
            return True
        except Exception as e:
            self.logger.error(f"Redis reset failed: {e}")
            return False
            
    def clear_all(self) -> bool:
        """
        Clear all rate limit data (for testing).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all keys with our prefix
            pattern = f"{self.prefix}*"
            cursor = 0
            cleared = 0
            
            while True:
                cursor, keys = self.redis.scan(cursor, match=pattern, count=100)
                if keys:
                    self.redis.delete(*keys)
                    cleared += len(keys)
                    
                if cursor == 0:
                    break
                    
            self.logger.warning(f"Cleared {cleared} rate limit keys")
            return True
            
        except Exception as e:
            self.logger.error(f"Redis clear_all failed: {e}")
            return False 