"""
Tests for authentication utility functions.
"""

import pytest
from unittest.mock import MagicMock, patch
from fastapi import Request
from fastapi.security import HTTPAuthorizationCredentials

from app.utils.auth.user import get_current_user_id, get_current_user_auth, get_current_user


class TestGetCurrentUserId:
    """Tests for the get_current_user_id function."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request object."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.headers = {}
        request.scope = {}
        return request

    def test_get_current_user_id_from_state(self, mock_request):
        """Test extracting user ID from request state."""
        # Setup
        mock_request.state.user = {"id": "user-123", "email": "user@example.com"}
        
        # Execute
        user_id = get_current_user_id(mock_request)
        
        # Assert
        assert user_id == "user-123"

    def test_get_current_user_id_state_empty_user(self, mock_request):
        """Test with empty user in state."""
        # Setup
        mock_request.state.user = {}
        
        # Execute
        user_id = get_current_user_id(mock_request)
        
        # Assert
        assert user_id is None

    @patch("app.utils.auth.user.decode_token")
    def test_get_current_user_id_from_header(self, mock_decode_token, mock_request):
        """Test extracting user ID from Authorization header."""
        # Setup
        mock_request.state.user = None  # No user in state
        mock_request.headers = {"Authorization": "Bearer fake-token"}
        mock_decode_token.return_value = {"sub": "user-456", "exp": 1635283200}
        
        # Execute
        user_id = get_current_user_id(mock_request)
        
        # Assert
        mock_decode_token.assert_called_once_with("fake-token")
        assert user_id == "user-456"

    @patch("app.utils.auth.user.decode_token")
    def test_get_current_user_id_invalid_token(self, mock_decode_token, mock_request):
        """Test with invalid token in header."""
        # Setup
        mock_request.state.user = None
        mock_request.headers = {"Authorization": "Bearer invalid-token"}
        mock_decode_token.side_effect = Exception("Invalid token")
        
        # Execute
        user_id = get_current_user_id(mock_request)
        
        # Assert
        assert user_id is None

    def test_get_current_user_id_from_session(self, mock_request):
        """Test extracting user ID from session."""
        # Setup
        mock_request.state.user = None
        mock_request.headers = {}
        mock_request.scope = {"session": {}}
        mock_request.session = {"user": {"id": "user-789"}}
        
        # Execute
        user_id = get_current_user_id(mock_request)
        
        # Assert
        assert user_id == "user-789"

    def test_get_current_user_id_no_user(self, mock_request):
        """Test when no user information is available."""
        # Setup
        mock_request.state.user = None
        mock_request.headers = {}
        mock_request.scope = {}
        
        # Execute
        user_id = get_current_user_id(mock_request)
        
        # Assert
        assert user_id is None


class TestGetCurrentUserAuth:
    """Tests for the get_current_user_auth function."""

    @patch("app.utils.auth.user.decode_token")
    def test_get_current_user_auth_valid(self, mock_decode_token):
        """Test with valid credentials."""
        # Setup
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="fake-token")
        mock_decode_token.return_value = {"sub": "user-123", "exp": 1635283200}
        
        # Execute
        user_id = get_current_user_auth(credentials)
        
        # Assert
        mock_decode_token.assert_called_once_with("fake-token")
        assert user_id == "user-123"

    def test_get_current_user_auth_no_credentials(self):
        """Test with no credentials."""
        # Execute
        user_id = get_current_user_auth(None)
        
        # Assert
        assert user_id is None

    @patch("app.utils.auth.user.decode_token")
    def test_get_current_user_auth_invalid_token(self, mock_decode_token):
        """Test with invalid token."""
        # Setup
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="invalid-token")
        mock_decode_token.side_effect = Exception("Invalid token")
        
        # Execute
        user_id = get_current_user_auth(credentials)
        
        # Assert
        assert user_id is None

    @patch("app.utils.auth.user.decode_token")
    def test_get_current_user_auth_missing_sub(self, mock_decode_token):
        """Test with token missing sub claim."""
        # Setup
        credentials = HTTPAuthorizationCredentials(scheme="Bearer", credentials="incomplete-token")
        mock_decode_token.return_value = {"exp": 1635283200}  # No sub claim
        
        # Execute
        user_id = get_current_user_auth(credentials)
        
        # Assert
        assert user_id is None


class TestGetCurrentUser:
    """Tests for the get_current_user function."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request object."""
        request = MagicMock(spec=Request)
        return request

    @patch("app.utils.auth.user.get_current_user_id")
    def test_get_current_user_with_id(self, mock_get_current_user_id, mock_request):
        """Test getting user info with valid user ID."""
        # Setup
        mock_get_current_user_id.return_value = "user-123"
        
        # Execute
        user_info = get_current_user(mock_request)
        
        # Assert
        mock_get_current_user_id.assert_called_once_with(mock_request)
        assert user_info == {"id": "user-123"}

    @patch("app.utils.auth.user.get_current_user_id")
    def test_get_current_user_no_id(self, mock_get_current_user_id, mock_request):
        """Test getting user info with no user ID."""
        # Setup
        mock_get_current_user_id.return_value = None
        
        # Execute
        user_info = get_current_user(mock_request)
        
        # Assert
        mock_get_current_user_id.assert_called_once_with(mock_request)
        assert user_info == {} 