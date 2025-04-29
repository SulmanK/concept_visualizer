"""Tests for the Supabase client implementation."""

from typing import Generator
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
        # Use a valid JWT format for the API key (valid format is required by Supabase client)
        mock.SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c"
        mock.SUPABASE_SERVICE_ROLE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzZXJ2aWNlIiwibmFtZSI6IlNlcnZpY2UgUm9sZSIsImlhdCI6MTUxNjIzOTAyMn0.fEImTrVZkFLWNirzBdKGfDjVjzKER2I3xrEHAHYhY84"
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
    # Create a minimal client that doesn't connect to Supabase
    with patch("app.core.supabase.client.create_client"):
        auth_client = SupabaseAuthClient()

        # We need to directly test the function since we're not going to mock verify_token
        # itself in this test, but test its behavior with an empty token

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.verify_token("")

        assert "No token provided" in str(excinfo.value)


def test_verify_token_expired() -> None:
    """Test verification with an expired token."""
    # Set up
    with patch("app.core.supabase.client.create_client"), patch("app.core.supabase.client.jwt.decode") as mock_decode:
        # Configure JWT decode to raise ExpiredSignatureError
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token has expired")

        auth_client = SupabaseAuthClient()

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.verify_token("fake-expired-token")

        assert "Token expired" in str(excinfo.value)
        mock_decode.assert_called_once()


def test_verify_token_invalid() -> None:
    """Test verification with an invalid token."""
    # Set up
    with patch("app.core.supabase.client.create_client"), patch("app.core.supabase.client.jwt.decode") as mock_decode:
        # Configure JWT decode to raise InvalidTokenError
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token format")

        auth_client = SupabaseAuthClient()

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.verify_token("fake-invalid-token")

        assert "Invalid token" in str(excinfo.value)
        mock_decode.assert_called_once()


def test_get_user_from_request_bearer_token_success() -> None:
    """Test getting user from request with Bearer token."""
    # Set up
    with patch("app.core.supabase.client.create_client"), patch.object(SupabaseAuthClient, "verify_token") as mock_verify, patch("app.core.supabase.client.mask_id", return_value="masked-user-id"):
        auth_client = SupabaseAuthClient()
        # Add logger manually since we're bypassing initialization
        auth_client.logger = MagicMock()

        # Mock the token verification
        payload = {
            "sub": "user-123",
            "email": "user@example.com",
            "role": "authenticated",
        }
        mock_verify.return_value = payload

        # Create a mock request
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer fake-token-123"}

        # Act
        user = auth_client.get_user_from_request(mock_request)

        # Assert
        assert user is not None
        assert user["id"] == "user-123"
        assert user["email"] == "user@example.com"
        assert user["role"] == "authenticated"
        assert user["token"] == "fake-token-123"  # Original token should be included
        mock_verify.assert_called_once_with("fake-token-123")
        auth_client.logger.debug.assert_called_once()  # Logger should be called


def test_get_user_from_request_no_auth_header() -> None:
    """Test getting user from request with no Authorization header."""
    # Set up
    with patch("app.core.supabase.client.create_client"):
        auth_client = SupabaseAuthClient()

        # Create a mock request with no Authorization header
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.cookies = {}  # No cookies either

        # Since this method returns None by default, we can simply assert that
        # Act
        result = auth_client.get_user_from_request(mock_request)

        # Assert
        assert result is None


def test_get_user_from_request_verification_error() -> None:
    """Test getting user from request when token verification fails."""
    # Set up
    with patch("app.core.supabase.client.create_client"), patch.object(SupabaseAuthClient, "verify_token") as mock_verify:
        auth_client = SupabaseAuthClient()
        # Add logger manually since we're bypassing initialization
        auth_client.logger = MagicMock()

        # Configure verify_token mock to raise an error
        auth_error = AuthenticationError(message="Token verification failed")
        mock_verify.side_effect = auth_error

        # Create a mock request with Authorization header
        mock_request = MagicMock()
        mock_request.headers = {"Authorization": "Bearer invalid-token"}
        mock_request.cookies = {}

        # Act & Assert
        with pytest.raises(AuthenticationError) as excinfo:
            auth_client.get_user_from_request(mock_request)

        assert "Token verification failed" in str(excinfo.value)
        mock_verify.assert_called_once_with("invalid-token")


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
