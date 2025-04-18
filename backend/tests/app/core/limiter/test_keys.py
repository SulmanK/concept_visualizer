"""
Tests for rate limiting key generation functions.
"""

import pytest
from unittest.mock import MagicMock, patch

from app.core.limiter.keys import (
    get_user_id,
    get_endpoint_key,
    combine_keys,
    calculate_ttl,
    generate_rate_limit_keys
)


def test_get_user_id_from_request_state():
    """Test getting user ID from request state."""
    # Arrange
    mock_request = MagicMock()
    mock_request.state.user = {"id": "user-123"}
    
    # Act
    result = get_user_id(mock_request)
    
    # Assert
    assert result == "user:user-123"


def test_get_user_id_from_auth_header():
    """Test getting user ID from authorization header when not in request state."""
    # Arrange
    mock_request = MagicMock()
    mock_request.state.user = None  # No user in state
    mock_request.headers = {"Authorization": "Bearer fake-token"}
    
    # Mock the JWT extraction function
    with patch("app.core.limiter.keys.extract_user_id_from_token") as mock_extract:
        mock_extract.return_value = "user-456"
        
        # Act
        result = get_user_id(mock_request)
        
        # Assert
        assert result == "user:user-456"
        mock_extract.assert_called_once_with("fake-token", validate=False)


def test_get_user_id_fallback_to_ip():
    """Test falling back to IP address when no user ID is available."""
    # Arrange
    mock_request = MagicMock()
    mock_request.state.user = None  # No user in state
    mock_request.headers = {}  # No authorization header
    
    # Mock the IP extraction function
    with patch("app.core.limiter.keys.get_remote_address") as mock_get_ip:
        mock_get_ip.return_value = "192.168.1.1"
        
        # Act
        result = get_user_id(mock_request)
        
        # Assert
        assert result == "ip:192.168.1.1"
        mock_get_ip.assert_called_once_with(mock_request)


def test_get_endpoint_key_with_route():
    """Test getting endpoint key when route is available."""
    # Arrange
    mock_request = MagicMock()
    mock_request.scope = {"route": MagicMock()}
    mock_request.scope["route"].path = "/api/concepts/generate"
    
    # Act
    result = get_endpoint_key(mock_request)
    
    # Assert
    assert result == "endpoint:/api/concepts/generate"


def test_get_endpoint_key_without_route():
    """Test getting endpoint key when route is not available."""
    # Arrange
    mock_request = MagicMock()
    mock_request.scope = {"path": "/api/concepts/generate"}
    # No route in scope
    
    # Act
    result = get_endpoint_key(mock_request)
    
    # Assert
    assert result == "endpoint:/api/concepts/generate"


def test_combine_keys():
    """Test combining user ID and endpoint key."""
    # Arrange
    user_id = "user:user-123"
    endpoint_key = "endpoint:/api/concepts/generate"
    
    # Act
    result = combine_keys(user_id, endpoint_key)
    
    # Assert
    assert result == "user:user-123:endpoint:/api/concepts/generate"


def test_calculate_ttl_minute():
    """Test calculating TTL for 'minute' period."""
    assert calculate_ttl("minute") == 60


def test_calculate_ttl_hour():
    """Test calculating TTL for 'hour' period."""
    assert calculate_ttl("hour") == 3600


def test_calculate_ttl_day():
    """Test calculating TTL for 'day' period."""
    assert calculate_ttl("day") == 86400


def test_calculate_ttl_month():
    """Test calculating TTL for 'month' period."""
    assert calculate_ttl("month") == 2592000  # 30 days


def test_calculate_ttl_default():
    """Test calculating TTL for an unknown period."""
    assert calculate_ttl("unknown") == 2592000  # Default to month


def test_generate_rate_limit_keys_regular_endpoint():
    """Test generating rate limit keys for a regular endpoint."""
    # Arrange
    user_id = "user:user-123"
    endpoint = "/api/concepts/generate"
    period = "minute"
    
    # Act
    keys = generate_rate_limit_keys(user_id, endpoint, period)
    
    # Assert
    assert len(keys) == 3
    assert f"{user_id}:{period}" in keys
    assert f"POST:{endpoint}:{user_id}:{period}" in keys
    assert f"{endpoint}:{user_id}:{period}" in keys


def test_generate_rate_limit_keys_svg_endpoint():
    """Test generating rate limit keys for SVG-related endpoints."""
    # Arrange
    user_id = "user:user-123"
    endpoint = "/api/export/svg"
    period = "hour"
    
    # Act
    keys = generate_rate_limit_keys(user_id, endpoint, period)
    
    # Assert
    assert len(keys) == 3
    assert f"svg:{user_id}:{period}" in keys
    assert f"svg:POST:{endpoint}:{user_id}:{period}" in keys
    assert f"svg:{endpoint}:{user_id}:{period}" in keys


def test_generate_rate_limit_keys_convert_endpoint():
    """Test generating rate limit keys for conversion endpoints."""
    # Arrange
    user_id = "user:user-123"
    endpoint = "/api/export/convert"
    period = "day"
    
    # Act
    keys = generate_rate_limit_keys(user_id, endpoint, period)
    
    # Assert
    assert len(keys) == 3
    assert f"svg:{user_id}:{period}" in keys  # Special prefix for conversion
    assert f"svg:POST:{endpoint}:{user_id}:{period}" in keys
    assert f"svg:{endpoint}:{user_id}:{period}" in keys 