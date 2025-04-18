"""
Tests for the Redis-based rate limiting store implementation.
"""

import time
import pytest
from unittest.mock import MagicMock, patch

from app.core.limiter.redis_store import RedisStore, get_redis_client


@pytest.fixture
def mock_redis_client():
    """Create a mock Redis client for testing."""
    redis_client = MagicMock()
    return redis_client


@pytest.fixture
def redis_store(mock_redis_client):
    """Create a RedisStore with a mock Redis client for testing."""
    return RedisStore(mock_redis_client, prefix="test:")


def test_make_key(redis_store):
    """Test the _make_key method to ensure it correctly prefixes keys."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    
    # Act
    result = redis_store._make_key(key)
    
    # Assert
    assert result == "test:user:123:endpoint:/api/test"
    assert result.startswith(redis_store.prefix)


def test_increment_success(redis_store, mock_redis_client):
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


def test_increment_exception(redis_store, mock_redis_client):
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


def test_get_success(redis_store, mock_redis_client):
    """Test the get method with a successful Redis operation."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.get.return_value = "42"
    
    # Act
    result = redis_store.get(key)
    
    # Assert
    mock_redis_client.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result == 42


def test_get_not_found(redis_store, mock_redis_client):
    """Test the get method when the key does not exist in Redis."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.get.return_value = None
    
    # Act
    result = redis_store.get(key)
    
    # Assert
    mock_redis_client.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result == 0


def test_get_exception(redis_store, mock_redis_client):
    """Test the get method when Redis raises an exception."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.get.side_effect = Exception("Redis error")
    
    # Act
    result = redis_store.get(key)
    
    # Assert
    mock_redis_client.get.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result == 0  # Should return safe fallback


def test_get_with_expiry_success(redis_store, mock_redis_client):
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


def test_get_with_expiry_not_found(redis_store, mock_redis_client):
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


def test_get_with_expiry_exception(redis_store, mock_redis_client):
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


def test_get_quota_success(redis_store, mock_redis_client):
    """Test the get_quota method with a successful Redis operation."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600
    
    # Mock get_with_expiry to return a count and TTL
    with patch.object(redis_store, 'get_with_expiry') as mock_get_with_expiry:
        mock_get_with_expiry.return_value = (30, 1800)  # (count, ttl)
        current_time = time.time()
        
        # Act
        quota = redis_store.get_quota(user_id, endpoint, limit, period)
        
        # Assert
        mock_get_with_expiry.assert_called_once_with(f"{user_id}:{endpoint}")
        assert quota["total"] == limit
        assert quota["remaining"] == 70  # limit - count
        assert quota["used"] == 30
        assert quota["reset_at"] >= int(current_time + 1800)


def test_get_quota_exception(redis_store, mock_redis_client):
    """Test the get_quota method when an exception occurs."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600
    
    # Mock get_with_expiry to raise an exception
    with patch.object(redis_store, 'get_with_expiry') as mock_get_with_expiry:
        mock_get_with_expiry.side_effect = Exception("Failed to get quota")
        current_time = time.time()
        
        # Act
        quota = redis_store.get_quota(user_id, endpoint, limit, period)
        
        # Assert
        assert quota["total"] == limit
        assert quota["remaining"] == 50  # Conservative half remaining
        assert quota["used"] == 50
        assert quota["reset_at"] >= int(current_time)


def test_check_rate_limit_allowed(redis_store, mock_redis_client):
    """Test the check_rate_limit method when the request is allowed."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600
    
    # Mock the get and increment methods
    with patch.object(redis_store, 'get') as mock_get, \
         patch.object(redis_store, 'increment') as mock_increment:
        # Configure mock get to return a count below the limit
        mock_get.return_value = 50
        # Configure mock increment to return the incremented count
        mock_increment.return_value = 51
        
        # Act
        is_allowed, quota = redis_store.check_rate_limit(user_id, endpoint, limit, period)
        
        # Assert
        assert is_allowed is True
        mock_get.assert_called_once_with(f"{user_id}:{endpoint}")
        mock_increment.assert_called_once_with(f"{user_id}:{endpoint}", period)
        assert quota["remaining"] == 49
        assert quota["total"] == limit
        assert quota["used"] == 51


def test_check_rate_limit_limit_exceeded(redis_store, mock_redis_client):
    """Test the check_rate_limit method when the request exceeds the limit."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600
    
    # Mock the get and increment methods
    with patch.object(redis_store, 'get') as mock_get, \
         patch.object(redis_store, 'get_quota') as mock_get_quota:
        # Configure mock get to return a count at the limit
        mock_get.return_value = 100
        # Configure mock get_quota to return a quota object
        mock_get_quota.return_value = {
            "total": limit,
            "remaining": 0,
            "used": 100,
            "reset_at": int(time.time() + period)
        }
        
        # Act
        is_allowed, quota = redis_store.check_rate_limit(user_id, endpoint, limit, period)
        
        # Assert
        assert is_allowed is False
        mock_get.assert_called_once_with(f"{user_id}:{endpoint}")
        # Should not increment if check_only=False and already at limit
        mock_get_quota.assert_called_once_with(user_id, endpoint, limit, period)
        assert quota["remaining"] == 0


def test_check_rate_limit_check_only(redis_store, mock_redis_client):
    """Test the check_rate_limit method with check_only=True."""
    # Arrange
    user_id = "user:123"
    endpoint = "/api/test"
    limit = 100
    period = 3600
    
    # Mock the get method
    with patch.object(redis_store, 'get') as mock_get, \
         patch.object(redis_store, 'increment') as mock_increment:
        # Configure mock get to return a count below the limit
        mock_get.return_value = 50
        
        # Act
        is_allowed, quota = redis_store.check_rate_limit(user_id, endpoint, limit, period, check_only=True)
        
        # Assert
        assert is_allowed is True
        mock_get.assert_called_once_with(f"{user_id}:{endpoint}")
        # Should not increment if check_only=True
        mock_increment.assert_not_called()
        assert quota["remaining"] == 50
        assert quota["total"] == limit
        assert quota["used"] == 50
        assert "reset_at" in quota


def test_reset_success(redis_store, mock_redis_client):
    """Test the reset method with a successful Redis operation."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.delete.return_value = 1  # Key was deleted
    
    # Act
    result = redis_store.reset(key)
    
    # Assert
    mock_redis_client.delete.assert_called_once_with(f"{redis_store.prefix}{key}")
    assert result is True


def test_reset_not_found(redis_store, mock_redis_client):
    """Test the reset method when the key does not exist."""
    # Arrange
    key = "user:123:endpoint:/api/test"
    mock_redis_client.delete.return_value = 0  # No key was deleted
    
    # Act
    result = redis_store.reset(key)
    
    # Assert
    mock_redis_client.delete.assert_called_once_with(f"{redis_store.prefix}{key}")
    # Note: The implementation always returns True regardless of whether the key was found
    assert result is True


def test_clear_all_success(redis_store, mock_redis_client):
    """Test the clear_all method with a successful Redis operation."""
    # Arrange
    mock_redis_client.scan.return_value = (0, [f"{redis_store.prefix}key1", f"{redis_store.prefix}key2"])
    mock_redis_client.delete.return_value = 2  # Two keys were deleted
    
    # Act
    result = redis_store.clear_all()
    
    # Assert
    mock_redis_client.scan.assert_called_once_with(0, match=f"{redis_store.prefix}*", count=100)
    mock_redis_client.delete.assert_called_once_with(f"{redis_store.prefix}key1", f"{redis_store.prefix}key2")
    assert result is True


def test_clear_all_no_keys(redis_store, mock_redis_client):
    """Test the clear_all method when no keys match the pattern."""
    # Arrange
    mock_redis_client.scan.return_value = (0, [])  # No keys found
    
    # Act
    result = redis_store.clear_all()
    
    # Assert
    mock_redis_client.scan.assert_called_once_with(0, match=f"{redis_store.prefix}*", count=100)
    mock_redis_client.delete.assert_not_called()
    assert result is True


def test_clear_all_exception(redis_store, mock_redis_client):
    """Test the clear_all method when Redis raises an exception."""
    # Arrange
    mock_redis_client.scan.side_effect = Exception("Redis error")
    
    # Act
    result = redis_store.clear_all()
    
    # Assert
    mock_redis_client.scan.assert_called_once_with(0, match=f"{redis_store.prefix}*", count=100)
    assert result is False


def test_get_redis_client():
    """Test the get_redis_client function with valid settings."""
    # Arrange
    mock_redis = MagicMock()
    mock_redis_class = MagicMock(return_value=mock_redis)
    
    # Mock the Redis class and settings
    with patch('app.core.limiter.redis_store.redis.Redis', mock_redis_class), \
         patch('app.core.limiter.redis_store.settings') as mock_settings:
        # Configure settings
        mock_settings.UPSTASH_REDIS_ENDPOINT = "redis.upstash.com"
        mock_settings.UPSTASH_REDIS_PORT = 1234
        mock_settings.UPSTASH_REDIS_PASSWORD = "password123"
        
        # Act
        result = get_redis_client()
        
        # Assert
        mock_redis_class.assert_called_once_with(
            host=mock_settings.UPSTASH_REDIS_ENDPOINT,
            port=mock_settings.UPSTASH_REDIS_PORT,
            password=mock_settings.UPSTASH_REDIS_PASSWORD,
            socket_timeout=2,
            socket_connect_timeout=2,
            retry_on_timeout=True,
            ssl=True,
            decode_responses=True
        )
        mock_redis.ping.assert_called_once()
        assert result == mock_redis


def test_get_redis_client_missing_settings():
    """Test the get_redis_client function with missing settings."""
    # Arrange
    with patch('app.core.limiter.redis_store.settings') as mock_settings:
        # Configure settings with missing values
        mock_settings.UPSTASH_REDIS_ENDPOINT = ""
        mock_settings.UPSTASH_REDIS_PASSWORD = "password123"
        
        # Act
        result = get_redis_client()
        
        # Assert
        assert result is None


def test_get_redis_client_connection_error():
    """Test the get_redis_client function when a connection error occurs."""
    # Arrange
    mock_redis = MagicMock()
    mock_redis.ping.side_effect = Exception("Connection refused")
    mock_redis_class = MagicMock(return_value=mock_redis)
    
    # Mock the Redis class and settings
    with patch('app.core.limiter.redis_store.redis.Redis', mock_redis_class), \
         patch('app.core.limiter.redis_store.settings') as mock_settings:
        # Configure settings
        mock_settings.UPSTASH_REDIS_ENDPOINT = "redis.upstash.com"
        mock_settings.UPSTASH_REDIS_PORT = 1234
        mock_settings.UPSTASH_REDIS_PASSWORD = "password123"
        
        # Act
        result = get_redis_client()
        
        # Assert
        mock_redis.ping.assert_called_once()
        assert result is None 