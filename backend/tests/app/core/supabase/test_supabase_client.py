"""Tests for the Supabase client implementation."""

from typing import Any, Dict, Generator
from unittest.mock import MagicMock, patch

import jwt
import pytest

from app.core.exceptions import AuthenticationError, DatabaseError
from app.core.supabase.client import SupabaseAuthClient, SupabaseClient, get_supabase_auth_client, get_supabase_client


@pytest.fixture
def mock_create_client() -> Generator[MagicMock, None, None]:
    """Mock the Supabase create_client function."""
    with patch("app.core.supabase.client.create_client") as mock:
        mock.return_value = MagicMock()
        yield mock


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    """Mock the app settings."""
    with patch("app.core.supabase.client.settings") as mock:
        mock.SUPABASE_URL = "https://example.supabase.co"
        mock.SUPABASE_KEY = "fake-api-key"
        mock.SUPABASE_SERVICE_ROLE = "fake-service-role-key"
        mock.SUPABASE_JWT_SECRET = "fake-jwt-secret"
        yield mock


def test_supabase_client_init_success(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test successful SupabaseClient initialization."""
    # Act
    client = SupabaseClient()

    # Assert
    mock_create_client.assert_called_once_with(mock_settings.SUPABASE_URL, mock_settings.SUPABASE_KEY)
    assert client.url == mock_settings.SUPABASE_URL
    assert client.key == mock_settings.SUPABASE_KEY
    assert client.client == mock_create_client.return_value


def test_supabase_client_init_with_session_id(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test SupabaseClient initialization with a session ID."""
    # Arrange
    session_id = "test-session-123"

    # Act
    client = SupabaseClient(session_id=session_id)

    # Assert
    assert client.session_id == session_id


def test_supabase_client_init_with_custom_url_and_key(mock_create_client: MagicMock) -> None:
    """Test SupabaseClient initialization with custom URL and key."""
    # Arrange
    custom_url = "https://custom.supabase.co"
    custom_key = "custom-api-key"

    # Act
    client = SupabaseClient(url=custom_url, key=custom_key)

    # Assert
    mock_create_client.assert_called_once_with(custom_url, custom_key)
    assert client.url == custom_url
    assert client.key == custom_key


def test_supabase_client_init_failure(mock_create_client: MagicMock) -> None:
    """Test SupabaseClient initialization failure."""
    # Arrange
    mock_create_client.side_effect = Exception("Connection failed")

    # Act & Assert
    with pytest.raises(DatabaseError) as excinfo:
        SupabaseClient()

    assert "Failed to initialize Supabase client" in str(excinfo.value)


def test_get_service_role_client_success(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test successful service role client creation."""
    # Arrange
    client = SupabaseClient()

    # Act
    service_client = client.get_service_role_client()

    # Assert
    mock_create_client.assert_called_with(mock_settings.SUPABASE_URL, mock_settings.SUPABASE_SERVICE_ROLE)
    assert service_client == mock_create_client.return_value


def test_get_service_role_client_missing_key(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test service role client creation when the service role key is missing."""
    # Arrange
    client = SupabaseClient()
    mock_settings.SUPABASE_SERVICE_ROLE = ""  # Empty service role key

    # Act & Assert
    with pytest.raises(DatabaseError) as excinfo:
        client.get_service_role_client()

    assert "Service role key not configured" in str(excinfo.value)


def test_get_service_role_client_failure(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test service role client creation failure."""
    # Arrange
    client = SupabaseClient()
    mock_create_client.side_effect = Exception("Creation failed")

    # Act & Assert
    with pytest.raises(DatabaseError) as excinfo:
        client.get_service_role_client()

    assert "Failed to initialize service role client" in str(excinfo.value)


def test_supabase_auth_client_init_success(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test successful SupabaseAuthClient initialization."""
    # Act
    auth_client = SupabaseAuthClient()

    # Assert
    mock_create_client.assert_called_once_with(mock_settings.SUPABASE_URL, mock_settings.SUPABASE_KEY)
    assert auth_client.url == mock_settings.SUPABASE_URL
    assert auth_client.key == mock_settings.SUPABASE_KEY
    assert auth_client.jwt_secret == mock_settings.SUPABASE_JWT_SECRET
    assert auth_client.client == mock_create_client.return_value


def test_supabase_auth_client_init_failure(mock_create_client: MagicMock) -> None:
    """Test SupabaseAuthClient initialization failure."""
    # Arrange
    mock_create_client.side_effect = Exception("Connection failed")

    # Act & Assert
    with pytest.raises(AuthenticationError) as excinfo:
        SupabaseAuthClient()

    assert "Failed to initialize Supabase auth client" in str(excinfo.value)


def test_verify_token_success(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test successful token verification."""
    # Arrange
    auth_client = SupabaseAuthClient()
    token = "fake-jwt-token"
    payload = {
        "sub": "user-123",
        "email": "user@example.com",
        "exp": 1735689600,
    }  # Some time in the future

    # Mock JWT decode
    with patch("app.core.supabase.client.jwt.decode") as mock_decode:
        mock_decode.return_value = payload

        # Act
        result = auth_client.verify_token(token)

        # Assert
        mock_decode.assert_called_once_with(
            token,
            mock_settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            options={
                "verify_signature": True,
                "verify_aud": False,
                "verify_exp": True,
                "require": ["exp", "sub"],
            },
        )
        assert result == payload


def test_verify_token_empty_token() -> None:
    """Test verification with an empty token."""
    # Arrange
    auth_client = SupabaseAuthClient()

    # Act & Assert
    with pytest.raises(AuthenticationError) as excinfo:
        auth_client.verify_token("")

    assert "No token provided" in str(excinfo.value)


def test_verify_token_expired() -> None:
    """Test verification with an expired token."""
    # Arrange
    auth_client = SupabaseAuthClient()
    token = "fake-expired-token"

    # Mock JWT decode to raise expired token error
    with patch("app.core.supabase.client.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.verify_token(token)

        # Check that the error message matches the actual implementation
        # The implementation returns "Token expired" not the original JWT error
        assert "Token expired" in str(excinfo.value)


def test_verify_token_invalid() -> None:
    """Test verification with an invalid token."""
    # Arrange
    auth_client = SupabaseAuthClient()
    token = "fake-invalid-token"

    # Mock JWT decode to raise invalid token error
    with patch("app.core.supabase.client.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token")

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.verify_token(token)

        assert "Invalid token" in str(excinfo.value)


def test_get_user_from_request_bearer_token_success() -> None:
    """Test getting user from request with Bearer token."""
    # Arrange
    auth_client = SupabaseAuthClient()
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer fake-token"}

    user_payload: Dict[str, Any] = {
        "sub": "user-123",
        "email": "user@example.com",
        "user_metadata": {
            "name": "Test User",
            "picture": "https://example.com/avatar.jpg",
        },
        "app_metadata": {
            "role": "user",
        },
        "exp": 1735689600,
    }

    # Mock verify_token
    with patch.object(auth_client, "verify_token") as mock_verify:
        mock_verify.return_value = user_payload

        # Act
        user = auth_client.get_user_from_request(mock_request)

        # Assert
        mock_verify.assert_called_once_with("fake-token")
        # Ensure user payload is not None before accessing properties
        assert user is not None
        assert user["id"] == "user-123"
        assert user["email"] == "user@example.com"
        # The implementation doesn't map user_metadata.name to user["name"]
        # It keeps the nested structure as in user["user_metadata"]["name"]
        assert user["user_metadata"]["name"] == "Test User"
        assert user["user_metadata"]["picture"] == "https://example.com/avatar.jpg"
        # The implementation uses "authenticated" as the default role if not in payload
        assert user["role"] == "authenticated"
        assert user["token"] == "fake-token"


def test_get_user_from_request_no_auth_header() -> None:
    """Test getting user from request with no Authorization header."""
    # Arrange
    auth_client = SupabaseAuthClient()
    mock_request = MagicMock()
    mock_request.headers = {}  # No Authorization header

    # Act
    user = auth_client.get_user_from_request(mock_request)

    # Assert
    assert user is None


def test_get_user_from_request_verification_error() -> None:
    """Test getting user from request when token verification fails."""
    # Arrange
    auth_client = SupabaseAuthClient()
    mock_request = MagicMock()
    mock_request.headers = {"Authorization": "Bearer fake-token"}

    # Mock verify_token to raise an error
    with patch.object(auth_client, "verify_token") as mock_verify:
        mock_verify.side_effect = AuthenticationError("Invalid token")

        # Act
        # The actual implementation re-raises the exception, not returns None
        # So we need to catch the exception
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.get_user_from_request(mock_request)

        # Assert
        mock_verify.assert_called_once_with("fake-token")
        assert "Invalid token" in str(excinfo.value)


def test_get_supabase_client(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test get_supabase_client function."""
    # Act
    client = get_supabase_client()

    # Assert
    mock_create_client.assert_called_once_with(mock_settings.SUPABASE_URL, mock_settings.SUPABASE_KEY)
    assert isinstance(client, SupabaseClient)


def test_get_supabase_client_with_session_id(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test get_supabase_client function with session_id."""
    # Arrange
    session_id = "test-session-456"

    # Act
    client = get_supabase_client(session_id=session_id)

    # Assert
    assert isinstance(client, SupabaseClient)
    assert client.session_id == session_id


def test_get_supabase_auth_client(mock_create_client: MagicMock, mock_settings: MagicMock) -> None:
    """Test get_supabase_auth_client function."""
    # Act
    auth_client = get_supabase_auth_client()

    # Assert
    mock_create_client.assert_called_once_with(mock_settings.SUPABASE_URL, mock_settings.SUPABASE_KEY)
    assert isinstance(auth_client, SupabaseAuthClient)
