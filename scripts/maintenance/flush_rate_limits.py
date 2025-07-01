#!/usr/bin/env python3
"""Monthly rate-limit flush script.

This script connects to Upstash Redis and removes all keys matching the pattern
'ratelimit:*' to reset user quotas at the beginning of each calendar month.

Usage:
    python scripts/maintenance/flush_rate_limits.py

Environment Variables:
    CONCEPT_UPSTASH_REDIS_ENDPOINT: Redis hostname (without protocol)
    CONCEPT_UPSTASH_REDIS_PASSWORD: Redis password
    CONCEPT_UPSTASH_REDIS_PORT: Redis port (optional, defaults to 6379)
"""

import logging
import os
import sys
import time

import redis

# Configure logging with structured format
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Configuration
BATCH_SIZE = 1000
PATTERN = "ratelimit:*"


def get_redis_client() -> redis.Redis:
    """Create Redis client using environment variables.

    Returns:
        Redis client instance

    Raises:
        ValueError: If required environment variables are missing
        redis.RedisError: If connection fails
    """
    # Get configuration from environment
    endpoint = os.environ.get("CONCEPT_UPSTASH_REDIS_ENDPOINT")
    password = os.environ.get("CONCEPT_UPSTASH_REDIS_PASSWORD")
    port = int(os.environ.get("CONCEPT_UPSTASH_REDIS_PORT", "6379"))

    if not endpoint:
        raise ValueError(
            "CONCEPT_UPSTASH_REDIS_ENDPOINT environment variable is required"
        )
    if not password:
        raise ValueError(
            "CONCEPT_UPSTASH_REDIS_PASSWORD environment variable is required"
        )

    # Build Redis URL for Upstash (using rediss:// for TLS connection)
    redis_url = f"rediss://:{password}@{endpoint}:{port}"

    logger.info(f"Connecting to Redis at {endpoint}:{port}")

    # Create client
    client = redis.from_url(
        redis_url,
        socket_timeout=30,
        socket_connect_timeout=30,
        retry_on_timeout=True,
        retry_on_error=[redis.ConnectionError],
        health_check_interval=30,
        decode_responses=True,
    )

    # Test connection
    try:
        client.ping()
        logger.info("Redis connection established successfully")
    except redis.RedisError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise

    return client


def flush_rate_limit_keys(client: redis.Redis) -> int:
    """Flush all rate-limit keys using batched SCAN and UNLINK.

    Args:
        client: Redis client instance

    Returns:
        Number of keys deleted
    """
    cursor = 0
    deleted = 0
    batch_count = 0

    logger.info(f"Starting flush of keys matching pattern '{PATTERN}'")

    while True:
        # Scan for keys matching the pattern
        cursor, keys = client.scan(cursor=cursor, match=PATTERN, count=BATCH_SIZE)

        if keys:
            batch_count += 1
            batch_size = len(keys)

            # Use UNLINK for non-blocking deletion, fall back to DEL if unavailable
            try:
                if hasattr(client, "unlink"):
                    client.unlink(*keys)
                else:
                    client.delete(*keys)

                deleted += batch_size
                logger.info(
                    f"Batch {batch_count}: deleted {batch_size} keys (total: {deleted})"
                )

            except redis.RedisError as e:
                logger.error(f"Failed to delete batch {batch_count}: {e}")
                # Continue with next batch rather than failing completely
                continue

        # If cursor is 0, we've scanned the entire keyspace
        if cursor == 0:
            break

    logger.info(
        f"Flush complete: processed {batch_count} batches, deleted {deleted} keys total"
    )
    return deleted


def main() -> None:
    """Main function to execute the rate-limit flush."""
    start_time = time.time()

    try:
        logger.info("Monthly rate-limit flush starting")

        # Get Redis client
        client = get_redis_client()

        # Perform the flush
        deleted_count = flush_rate_limit_keys(client)

        # Calculate duration
        duration = time.time() - start_time

        # Log completion with structured data
        logger.info(
            "Monthly rate-limit flush completed successfully",
            extra={
                "keys_deleted": deleted_count,
                "duration_seconds": round(duration, 2),
                "pattern": PATTERN,
                "batch_size": BATCH_SIZE,
            },
        )

        # Exit with appropriate code
        if deleted_count == 0:
            logger.warning(
                "No keys were deleted - this may indicate no rate-limit data or a configuration issue"
            )
            # Don't fail if no keys to delete (might be legitimate)

        sys.exit(0)

    except Exception as e:
        duration = time.time() - start_time
        logger.error(
            f"Monthly rate-limit flush failed: {str(e)}",
            extra={
                "duration_seconds": round(duration, 2),
                "error_type": type(e).__name__,
            },
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
