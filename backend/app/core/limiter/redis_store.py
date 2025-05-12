"""Redis-based rate limiter implementation.

This module provides a Redis-based rate limiter for API rate limiting.
"""

import logging
import time
from typing import Any, Dict, Optional, Tuple, cast

import redis
from redis import Redis

from app.core.config import settings

logger = logging.getLogger(__name__)


def mask_key(key: str) -> str:
    """Mask a key for logging to avoid exposing sensitive information.

    Args:
        key: The key to mask

    Returns:
        Masked key with middle portion replaced by asterisks
    """
    if len(key) < 8:
        return key  # Key is too short to mask meaningfully
    return f"{key[:3]}***{key[-3:]}"


def get_redis_client() -> Optional[Redis]:
    """Create Redis client using application settings.

    Returns:
        Redis client instance or None if connection fails
    """
    try:
        # Build Redis URL for Upstash (using rediss:// for TLS connection)
        redis_url = f"rediss://:{settings.UPSTASH_REDIS_PASSWORD}@{settings.UPSTASH_REDIS_ENDPOINT}:{settings.UPSTASH_REDIS_PORT}"
        logger.debug(f"Connecting to Redis at: {mask_key(settings.UPSTASH_REDIS_ENDPOINT)}")

        # Create client using connection URL
        client = cast(
            Redis,
            redis.from_url(
                redis_url,
                socket_timeout=3,  # Slightly increased timeout for reliability
                socket_connect_timeout=3,
                retry_on_timeout=True,  # Changed to boolean - some versions use boolean instead of max_tries
                health_check_interval=15,
                decode_responses=True,  # Automatically decode responses to strings
            ),
        )

        # Test connection
        client.ping()
        logger.info("Redis connection established successfully")
        return client
    except redis.RedisError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error connecting to Redis: {str(e)}")
        return None


class RedisStore:
    """Redis-based rate limiter store."""

    def __init__(self, redis_client: redis.Redis, prefix: str = "ratelimit:"):
        """Initialize the Redis store.

        Args:
            redis_client: Redis client instance
            prefix: Key prefix for all rate limit keys
        """
        self.redis = redis_client
        self.prefix = prefix
        self.logger = logging.getLogger(__name__)
        self.logger.debug(f"RedisStore initialized with prefix: {prefix}")

    def _make_key(self, key: str) -> str:
        """Create a prefixed Redis key.

        Args:
            key: The base key

        Returns:
            Prefixed key for Redis storage
        """
        return f"{self.prefix}{key}"

    def _log_operation(self, operation: str, key: str, result: Any = None) -> None:
        """Log a Redis operation for debugging.

        Args:
            operation: Operation name (get, set, etc.)
            key: Redis key involved in the operation
            result: Operation result for logging
        """
        # Only log for debug level to avoid excessive logging
        if self.logger.level <= logging.DEBUG:
            masked_key = mask_key(key)
            self.logger.debug(f"Redis {operation}: {masked_key} = {result}")

    def increment(self, key: str, expiry: int, amount: int = 1) -> int:
        """Increment a counter in Redis with expiration.

        Args:
            key: Counter key
            expiry: Expiration time in seconds
            amount: Amount to increment by

        Returns:
            New counter value after increment
        """
        redis_key = self._make_key(key)
        try:
            # Use a pipeline to make the operations atomic
            pipe = self.redis.pipeline()
            pipe.incrby(redis_key, amount)
            pipe.expire(redis_key, expiry)
            result = pipe.execute()

            # Get the new value from the pipeline result
            # The incrby command returns the new value after increment
            new_value = cast(int, result[0])
            self._log_operation("increment", redis_key, new_value)
            return new_value

        except Exception as e:
            self.logger.error(f"Redis increment failed: {e}")
            # Return a safe fallback value
            return 1

    def get(self, key: str) -> int:
        """Get current counter value.

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
            # Since we're using decode_responses=True, value should be a string
            # that we can safely convert to int
            if isinstance(value, (str, int)):
                result = int(value)
            else:
                result = 0
            self._log_operation("get", redis_key, result)
            return result
        except Exception as e:
            self.logger.error(f"Redis get failed: {e}")
            return 0

    def get_with_expiry(self, key: str) -> Tuple[int, int]:
        """Get counter value with remaining expiry time.

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

            # Handle value - might be None if key doesn't exist
            value_str = result[0]
            # Ensure we have the right type before conversion
            # Strict type check to avoid conversion errors with incompatible types
            if value_str is not None and isinstance(value_str, (str, int)):
                value = int(value_str)
            else:
                value = 0
            # Handle TTL - might be -1 (no expiry) or -2 (key doesn't exist)
            ttl_value = result[1]
            # Make sure we properly cast ttl_value to int to avoid type errors
            # First, check if it's already an integer or can be safely converted
            if isinstance(ttl_value, int):
                ttl_int = ttl_value
            elif isinstance(ttl_value, str) and ttl_value.isdigit():
                ttl_int = int(ttl_value)
            else:
                # Default to 0 if we can't convert it safely
                ttl_int = 0

            ttl = max(0, ttl_int) if ttl_int > 0 else 0

            self._log_operation("get_with_expiry", redis_key, f"value={value}, ttl={ttl}")
            return (value, ttl)

        except Exception as e:
            self.logger.error(f"Redis get_with_expiry failed: {e}")
            return (0, 0)

    def get_quota(self, user_id: str, endpoint: str, limit: int, period: int) -> Dict[str, Any]:
        """Get quota information for a user and endpoint.

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
        period: int,
        check_only: bool = False,
    ) -> Tuple[bool, Dict[str, Any]]:
        """Check if a request is rate limited.

        Args:
            user_id: The user identifier (usually user ID or IP)
            endpoint: API endpoint being accessed
            limit: Maximum requests allowed
            period: Time period in seconds
            check_only: If True, don't increment the counter (for status checks)

        Returns:
            Tuple of (is_allowed, quota_info)
        """
        # Create a key combining user and endpoint
        key = f"{user_id}:{endpoint}"
        redis_key = self._make_key(key)

        # Log the key being used for improved debugging
        self.logger.debug(f"Rate limit check using key: {mask_key(key)} (prefixed as {mask_key(redis_key)})")

        try:
            # Get current value
            count = self.get(key)

            # Check if already over limit
            if count >= limit:
                # Get full quota info
                quota = self.get_quota(user_id, endpoint, limit, period)
                self._log_operation("check_rate_limit", redis_key, "DENIED")
                return (False, quota)

            if check_only:
                # Don't increment for check-only requests
                self._log_operation("check_rate_limit", redis_key, "CHECK_ONLY")
                # Use the current count for quota info
                quota = {
                    "total": limit,
                    "remaining": max(0, limit - count),
                    "used": count,
                    "reset_at": int(time.time() + period),
                }
                return (True, quota)

            # Increment counter for normal requests
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
            return (
                True,
                {
                    "total": limit,
                    "remaining": 1,
                    "used": limit - 1,
                    "reset_at": int(time.time() + period),
                },
            )

    def reset(self, key: str) -> bool:
        """Reset a rate limit counter.

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
        """Clear all rate limit keys.

        Returns:
            True if successful, False otherwise
        """
        try:
            # Find all keys with the rate limit prefix
            all_keys = self.redis.keys(f"{self.prefix}*")
            # If there are keys, delete them
            if all_keys:
                # Ensure all_keys is treated as a valid argument list
                deleted = self.redis.delete(*all_keys) if isinstance(all_keys, list) else 0
                self._log_operation("clear_all", f"{self.prefix}*", f"deleted {deleted} keys")
                return True
            self._log_operation("clear_all", f"{self.prefix}*", "no keys found")
            return True
        except Exception as e:
            self.logger.error(f"Redis clear_all failed: {e}")
            return False

    def decrement_specific_limit(self, user_id: str, endpoint_rule: str, limit_string_rule: str, amount: int = 1) -> bool:
        """Decrement a specific rate limit for a user and endpoint rule.

        This method is used to refund rate limits when a request is rejected due to
        business rules (e.g., a 409 Conflict when a user has an active task).

        Args:
            user_id: The user identifier
            endpoint_rule: The endpoint rule (e.g., "/concepts/generate")
            limit_string_rule: The limit string (e.g., "10/month")
            amount: Amount to decrement, defaults to 1

        Returns:
            True if successful, False otherwise
        """
        try:
            from app.core.limiter import normalize_endpoint
            from app.core.limiter.redis_store import mask_key

            # Normalize the endpoint for consistent key generation
            normalized_endpoint = normalize_endpoint(endpoint_rule)

            # Construct the Redis key - same format as used in check_rate_limit
            base_key = f"{user_id}:{normalized_endpoint}"
            redis_key = self._make_key(base_key)

            # Log the operation with masked key
            self.logger.info(f"Attempting to decrement rate limit: user='{mask_key(user_id)}', endpoint='{endpoint_rule}', limit='{limit_string_rule}', amount={amount}")

            # Check if the key exists and get its current value
            current_value_str = self.redis.get(redis_key)
            if current_value_str is None:
                self.logger.warning(f"Rate limit key {mask_key(redis_key)} not found or expired. Cannot decrement.")
                return False

            # Convert to integer
            if not isinstance(current_value_str, (str, int, bytes)):
                self.logger.warning(f"Unexpected type for rate limit value: {type(current_value_str)}. Cannot decrement.")
                return False

            current_value = int(current_value_str)

            # Only decrement if value is positive
            if current_value <= 0:
                self.logger.info(f"Rate limit key {mask_key(redis_key)} is already at or below 0 ({current_value}). No decrement needed.")
                return True

            # Calculate amount to decrement (don't go below 0)
            to_decrement = min(amount, current_value)

            # Decrement the counter
            new_value = self.redis.decrby(redis_key, to_decrement)

            self.logger.info(f"Successfully decremented key {mask_key(redis_key)} from {current_value} to {new_value}.")
            return True

        except Exception as e:
            self.logger.error(f"Failed to decrement specific rate limit for user {mask_key(user_id)} on {endpoint_rule}: {e}")
            return False
