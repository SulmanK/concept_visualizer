"""Tests for rate limiting key generation functions."""

from unittest.mock import MagicMock

from app.core.limiter.keys import calculate_ttl, combine_keys, generate_rate_limit_keys, get_endpoint_key, get_user_id


def test_get_user_id_from_request_state() -> None:
    """Test getting user ID from request state."""
    # Arrange
    mock_request = MagicMock()
    mock_request.state.user = {"id": "user-123"}

    # Act
    result = get_user_id(mock_request)

    # Assert
    assert result == "user:user-123"


def test_get_user_id_from_auth_header() -> None:
    """Test getting user ID from authorization header when not in request state."""
    # Arrange
    mock_request = MagicMock()
    mock_request.state.user = None  # No user in state
    mock_request.state.token = {"sub": "user-456"}  # Token in state
    mock_request.headers = {"Authorization": "Bearer fake-token"}

    # Act
    result = get_user_id(mock_request)

    # Assert
    assert result == "token:user-456"


def test_get_user_id_fallback_to_ip() -> None:
    """Test falling back to IP address when no user ID is available."""
    # Arrange
    mock_request = MagicMock()
    mock_request.state.user = None  # No user in state
    mock_request.state.token = None  # No token in state
    mock_request.headers = {"X-Forwarded-For": "192.168.1.1"}

    # Act
    result = get_user_id(mock_request)

    # Assert
    assert result == "ip:192.168.1.1"


def test_get_endpoint_key_with_route() -> None:
    """Test getting endpoint key when route is available."""
    # Arrange
    mock_request = MagicMock()
    mock_request.url.path = "/api/concepts/generate"

    # Act
    result = get_endpoint_key(mock_request)

    # Assert
    assert result == "/concepts/generate"  # API prefix removed


def test_get_endpoint_key_without_route() -> None:
    """Test getting endpoint key when path doesn't have API prefix."""
    # Arrange
    mock_request = MagicMock()
    mock_request.url.path = "/concepts/generate"

    # Act
    result = get_endpoint_key(mock_request)

    # Assert
    assert result == "/concepts/generate"  # Path is unchanged


def test_combine_keys() -> None:
    """Test combining user ID and endpoint key."""
    # Arrange
    user_id = "user:user-123"
    endpoint_key = "endpoint:/api/concepts/generate"

    # Act
    result = combine_keys(user_id, endpoint_key)

    # Assert
    assert result == "user:user-123:endpoint:/api/concepts/generate"


def test_calculate_ttl_minute() -> None:
    """Test calculating TTL for 'minute' period."""
    assert calculate_ttl("minute") == 60


def test_calculate_ttl_hour() -> None:
    """Test calculating TTL for 'hour' period."""
    assert calculate_ttl("hour") == 3600


def test_calculate_ttl_day() -> None:
    """Test calculating TTL for 'day' period."""
    assert calculate_ttl("day") == 86400


def test_calculate_ttl_month() -> None:
    """Test calculating TTL for 'month' period."""
    assert calculate_ttl("month") == 2592000  # 30 days


def test_calculate_ttl_default() -> None:
    """Test calculating TTL for an unknown period."""
    assert calculate_ttl("unknown") == 2592000  # Default to month


def test_generate_rate_limit_keys_regular_endpoint() -> None:
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


def test_generate_rate_limit_keys_svg_endpoint() -> None:
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


def test_generate_rate_limit_keys_convert_endpoint() -> None:
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
