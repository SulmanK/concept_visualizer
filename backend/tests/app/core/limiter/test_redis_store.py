"""Tests for the Redis-based rate limiting store implementation."""

import time
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from app.core.limiter.redis_store import RedisStore, get_redis_client


@pytest.fixture
def mock_redis_client() -> MagicMock:
    """Create a mock Redis client for testing."""
    redis_client = MagicMock()
    return redis_client


@pytest.fixture
def redis_store(mock_redis_client: MagicMock) -> RedisStore:
    """Create a RedisStore with a mock Redis client for testing."""
    return RedisStore(mock_redis_client, prefix="test:")


def test_make_key(redis_store: RedisStore) -> None:
    """Test the _make_key method to ensure it correctly prefixes keys."""
    # Arrange
    key = "user:123:endpoint:/api/test"

    # Act
    result = redis_store._make_key(key)

    # Assert
    assert result == "test:user:123:endpoint:/api/test"
    assert result.startswith(redis_store.prefix)


def test_increment_success(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the increment method with a successful Redis operation."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    expiry = 60
    amount = 1

    # Configure the mock pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = [5, True]  # [incrby result, expire result]
    mock_redis_client.pipeline.return_value = mock_pipeline

    # Act
    result = redis_store.increment(key, expiry, amount)

    # Assert
    mock_redis_client.pipeline.assert_called_once()
    mock_pipeline.incrby.assert_called_once_with(f"{redis_store.prefix}{key}", amount)
    mock_pipeline.expire.assert_called_once_with(f"{redis_store.prefix}{key}", expiry)
    mock_pipeline.execute.assert_called_once()
    assert result == 5


def test_increment_exception(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the increment method when Redis raises an exception."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    expiry = 60

    # Configure the mock pipeline to raise an exception
    mock_pipeline = MagicMock()
    mock_pipeline.execute.side_effect = Exception("Redis error")
    mock_redis_client.pipeline.return_value = mock_pipeline

    # Act
    result = redis_store.increment(key, expiry)

    # Assert
    mock_redis_client.pipeline.assert_called_once()
    assert result == 1  # Should return safe fallback


def test_get_success(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get method with a successful Redis operation."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.get.return_value = "42"

    # Act
    result = redis_store.get(key)

    # Assert
    mock_redis_client.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result == 42


def test_get_not_found(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get method when the key does not exist in Redis."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.get.return_value = None

    # Act
    result = redis_store.get(key)

    # Assert
    mock_redis_client.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result == 0


def test_get_exception(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get method when Redis raises an exception."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.get.side_effect = Exception("Redis error")

    # Act
    result = redis_store.get(key)

    # Assert
    mock_redis_client.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result == 0  # Should return safe fallback


def test_get_with_expiry_success(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get_with_expiry method with a successful Redis operation."""
    # Arrange
    key = "user:123:endpoint:/api/test"

    # Configure the mock pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = ["10", 30]  # [get result, ttl result]
    mock_redis_client.pipeline.return_value = mock_pipeline

    # Act
    value, ttl = redis_store.get_with_expiry(key)

    # Assert
    mock_redis_client.pipeline.assert_called_once()
    mock_pipeline.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    mock_pipeline.ttl.assert_called_once_with(f"{redis_store.prefix}{key}")
    mock_pipeline.execute.assert_called_once()
    assert value == 10
    assert ttl == 30


def test_get_with_expiry_not_found(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get_with_expiry method when the key does not exist in Redis."""
    # Arrange
    key = "user:123:endpoint:/api/test"

    # Configure the mock pipeline
    mock_pipeline = MagicMock()
    mock_pipeline.execute.return_value = [None, -2]  # Key doesn't exist
    mock_redis_client.pipeline.return_value = mock_pipeline

    # Act
    value, ttl = redis_store.get_with_expiry(key)

    # Assert
    mock_pipeline.execute.assert_called_once()
    assert value == 0
    assert ttl == 0


def test_get_with_expiry_exception(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get_with_expiry method when Redis raises an exception."""
    # Arrange
    key = "user:123:endpoint:/api/test"

    # Configure the mock pipeline to raise an exception
    mock_pipeline = MagicMock()
    mock_pipeline.execute.side_effect = Exception("Redis error")
    mock_redis_client.pipeline.return_value = mock_pipeline

    # Act
    value, ttl = redis_store.get_with_expiry(key)

    # Assert
    mock_pipeline.execute.assert_called_once()
    assert value == 0
    assert ttl == 0


def test_get_quota_success(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get_quota method with a successful Redis operation."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600

    # Mock get_with_expiry to return a count and TTL
    with patch.object(redis_store, "get_with_expiry") as mock_get_with_expiry:
        mock_get_with_expiry.return_value = (30, 1800)  # (count, ttl)
        current_time = time.time()

        # Act
        quota = redis_store.get_quota(user_id, endpoint, limit, period)

        # Assert
        mock_get_with_expiry.assert_called_once_with(f"{user_id}:{endpoint}")
        assert quota["total"] == limit
        assert quota["remaining"] == limit - 30
        assert quota["used"] == 30
        assert quota["reset_at"] > int(current_time)


def test_get_quota_exception(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the get_quota method when an exception occurs."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600

    # Mock get_with_expiry to raise an exception
    with patch.object(redis_store, "get_with_expiry") as mock_get_with_expiry:
        mock_get_with_expiry.side_effect = Exception("Redis error")
        current_time = time.time()

        # Act
        quota = redis_store.get_quota(user_id, endpoint, limit, period)

        # Assert
        mock_get_with_expiry.assert_called_once_with(f"{user_id}:{endpoint}")
        assert quota["total"] == limit
        assert quota["remaining"] == limit // 2
        assert quota["used"] == limit // 2
        assert quota["reset_at"] > int(current_time)


def test_check_rate_limit_allowed(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test check_rate_limit when request is allowed."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600

    # First mock get to check if already over limit
    with patch.object(redis_store, "get") as mock_get:
        mock_get.return_value = 50  # Below limit
        # Then mock increment as it will be called after get
        with patch.object(redis_store, "increment") as mock_increment:
            mock_increment.return_value = 51  # Current usage after increment

            # Act
            allowed, quota = redis_store.check_rate_limit(user_id, endpoint, limit, period)

            # Assert
            mock_get.assert_called_once_with(f"{user_id}:{endpoint}")
            mock_increment.assert_called_once_with(f"{user_id}:{endpoint}", period)
            assert allowed is True
            assert quota["total"] == limit
            assert quota["remaining"] == limit - 51
            assert quota["used"] == 51


def test_check_rate_limit_limit_exceeded(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test check_rate_limit when limit is exceeded."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600

    # Mock get to return a value at the limit
    with patch.object(redis_store, "get") as mock_get:
        mock_get.return_value = 101  # Over limit already
        # Mock get_quota which will be called when over limit
        with patch.object(redis_store, "get_quota") as mock_get_quota:
            mock_quota = {
                "total": limit,
                "remaining": 0,
                "used": 101,
                "reset_at": int(time.time() + period),
            }
            mock_get_quota.return_value = mock_quota

            # Act
            allowed, quota = redis_store.check_rate_limit(user_id, endpoint, limit, period)

            # Assert
            mock_get.assert_called_once_with(f"{user_id}:{endpoint}")
            # Increment shouldn't be called when already over limit
            mock_get_quota.assert_called_once_with(user_id, endpoint, limit, period)
            assert allowed is False
            assert quota == mock_quota


def test_check_rate_limit_check_only(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test check_rate_limit in check-only mode (no increment)."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600
    check_only = True

    # Mock get to return current usage
    with patch.object(redis_store, "get") as mock_get:
        mock_get.return_value = 75  # Current usage

        # Act
        allowed, quota = redis_store.check_rate_limit(user_id, endpoint, limit, period, check_only=check_only)

        # Assert
        mock_get.assert_called_once_with(f"{user_id}:{endpoint}")
        assert allowed is True
        assert quota["total"] == limit
        assert quota["remaining"] == limit - 75  # limit - current


def test_reset_success(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the reset method with a successful Redis operation."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.delete.return_value = 1  # Key was deleted

    # Act
    result = redis_store.reset(key)

    # Assert
    mock_redis_client.delete.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result is True


def test_reset_not_found(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the reset method when the key does not exist."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.delete.return_value = 0  # No key was deleted

    # Act
    result = redis_store.reset(key)

    # Assert
    mock_redis_client.delete.assert_called_once_with(f"{redis_store.prefix}{key}")
    # In the implementation, we always return True for reset(), even if no key was deleted
    assert result is True


def test_clear_all_success(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the clear_all method with a successful Redis operation."""
    # Arrange
    # Mock the keys operation to return some keys
    mock_redis_client.keys.return_value = [
        b"test:user:123:endpoint:/api/test1",
        b"test:user:123:endpoint:/api/test2",
    ]
    mock_redis_client.delete.return_value = 2  # 2 keys deleted

    # Act
    success = redis_store.clear_all()

    # Assert
    mock_redis_client.keys.assert_called_once_with(f"{redis_store.prefix}*")
    mock_redis_client.delete.assert_called_once()
    assert success is True


def test_clear_all_no_keys(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the clear_all method when no keys match the pattern."""
    # Arrange
    # Mock the keys operation to return no keys
    mock_redis_client.keys.return_value = []

    # Act
    success = redis_store.clear_all()

    # Assert
    mock_redis_client.keys.assert_called_once_with(f"{redis_store.prefix}*")
    # Delete shouldn't be called when no keys
    mock_redis_client.delete.assert_not_called()
    assert success is True


def test_clear_all_exception(redis_store: RedisStore, mock_redis_client: MagicMock) -> None:
    """Test the clear_all method when Redis raises an exception."""
    # Arrange
    # Mock the keys operation to raise an exception
    mock_redis_client.keys.side_effect = Exception("Redis error")

    # Act
    success = redis_store.clear_all()

    # Assert
    mock_redis_client.keys.assert_called_once_with(f"{redis_store.prefix}*")
    assert success is False


def test_get_redis_client() -> None:
    """Test the get_redis_client function with valid settings."""
    # Arrange
    # Mock settings for testing with all required attributes correctly defined as attributes
    mock_settings = MagicMock()
    mock_settings.UPSTASH_REDIS_ENDPOINT = "localhost"
    mock_settings.UPSTASH_REDIS_PORT = 6379
    mock_settings.UPSTASH_REDIS_PASSWORD = "password"

    # Mock redis.from_url to return a mock client
    mock_client = MagicMock()
    # Mock the ping method to verify connection
    mock_client.ping.return_value = True

    with patch("app.core.limiter.redis_store.redis.from_url") as mock_from_url:
        mock_from_url.return_value = mock_client

        # Mock the settings module
        with patch("app.core.limiter.redis_store.settings", mock_settings):
            # Act
            client = get_redis_client()

            # Assert
            expected_url = "rediss://:password@localhost:6379"
            mock_from_url.assert_called_once()
            # Check that the first argument contains the expected Redis URL
            assert expected_url in mock_from_url.call_args[0][0]
            assert client == mock_client


class MockSettingsMissing:
    """Class to simulate settings with missing attributes."""

    def __getattribute__(self, name: str) -> Any:
        """Override to raise AttributeError for specific attributes.

        Args:
            name: The attribute name being accessed

        Returns:
            The attribute value if not blocked

        Raises:
            AttributeError: When accessing UPSTASH_REDIS_PASSWORD
        """
        if name == "UPSTASH_REDIS_PASSWORD":
            raise AttributeError("'MockSettingsMissing' object has no attribute 'UPSTASH_REDIS_PASSWORD'")
        return super().__getattribute__(name)


def test_get_redis_client_missing_settings() -> None:
    """Test the get_redis_client function when Redis settings are missing."""
    # Create a mock settings object that raises AttributeError when UPSTASH_REDIS_PASSWORD is accessed
    missing_settings = MockSettingsMissing()

    # Mock the settings module
    with patch("app.core.limiter.redis_store.settings", missing_settings):
        # Act/Assert
        # The implementation returns None on error
        client = get_redis_client()
        assert client is None


def test_get_redis_client_connection_error() -> None:
    """Test the get_redis_client function when Redis connection fails."""
    # Arrange
    # Mock settings with proper attributes
    mock_settings = MagicMock()
    mock_settings.UPSTASH_REDIS_ENDPOINT = "localhost"
    mock_settings.UPSTASH_REDIS_PORT = 6379
    mock_settings.UPSTASH_REDIS_PASSWORD = "password"

    # Mock redis.from_url to return a mock client
    mock_client = MagicMock()
    # Mock the ping method to raise an exception (connection failed)
    mock_client.ping.side_effect = Exception("Connection error")

    with patch("app.core.limiter.redis_store.redis.from_url") as mock_from_url:
        mock_from_url.return_value = mock_client

        # Mock the settings module
        with patch("app.core.limiter.redis_store.settings", mock_settings):
            # Act/Assert
            # The implementation returns None on error
            client = get_redis_client()
            assert client is None
