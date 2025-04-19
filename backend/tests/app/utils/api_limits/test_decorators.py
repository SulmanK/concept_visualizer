"""
Tests for API rate limit decorators.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import Request

from app.utils.api_limits.decorators import store_rate_limit_info


class TestStoreRateLimitInfo:
    """Tests for the store_rate_limit_info decorator."""

    @pytest.fixture
    def mock_request(self):
        """Create a mock Request object."""
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        return request

    @pytest.fixture
    def mock_handler(self):
        """Create a mock request handler function."""
        return AsyncMock()

    @patch("app.utils.api_limits.decorators.get_user_id")
    @patch("app.utils.api_limits.decorators.check_rate_limit")
    async def test_store_rate_limit_info_with_request_arg(
        self, mock_check_rate_limit, mock_get_user_id, mock_request, mock_handler
    ):
        """Test decorator when Request is passed as positional argument."""
        # Setup
        endpoint_path = "/api/concepts/generate"
        limit_string = "10/minute"
        mock_get_user_id.return_value = "user-123"
        mock_check_rate_limit.return_value = {
            "limit": 10,
            "remaining": 8,
            "reset_at": 1635283200,
        }
        decorated_handler = store_rate_limit_info(endpoint_path, limit_string)(mock_handler)

        # Execute
        await decorated_handler(mock_request, "arg1", arg2="value2")

        # Assert
        mock_get_user_id.assert_called_once_with(mock_request)
        mock_check_rate_limit.assert_called_once_with(
            user_id="user-123",
            endpoint=endpoint_path,
            limit=limit_string,
            check_only=True
        )
        assert mock_request.state.limiter_info == {
            "limit": 10,
            "remaining": 8,
            "reset": 1635283200
        }
        mock_handler.assert_called_once_with(mock_request, "arg1", arg2="value2")

    @patch("app.utils.api_limits.decorators.get_user_id")
    @patch("app.utils.api_limits.decorators.check_rate_limit")
    async def test_store_rate_limit_info_with_request_kwarg(
        self, mock_check_rate_limit, mock_get_user_id, mock_request, mock_handler
    ):
        """Test decorator when Request is passed as keyword argument."""
        # Setup
        endpoint_path = "/api/concepts/generate"
        limit_string = "10/minute"
        mock_get_user_id.return_value = "user-123"
        mock_check_rate_limit.return_value = {
            "limit": 10,
            "remaining": 8,
            "reset_at": 1635283200,
        }
        decorated_handler = store_rate_limit_info(endpoint_path, limit_string)(mock_handler)

        # Execute
        await decorated_handler("arg1", request=mock_request, arg2="value2")

        # Assert
        mock_get_user_id.assert_called_once_with(mock_request)
        mock_check_rate_limit.assert_called_once_with(
            user_id="user-123",
            endpoint=endpoint_path,
            limit=limit_string,
            check_only=True
        )
        assert mock_request.state.limiter_info == {
            "limit": 10,
            "remaining": 8,
            "reset": 1635283200
        }
        mock_handler.assert_called_once_with("arg1", request=mock_request, arg2="value2")

    @patch("app.utils.api_limits.decorators.get_user_id")
    async def test_store_rate_limit_info_no_user_id(
        self, mock_get_user_id, mock_request, mock_handler
    ):
        """Test decorator when no user ID is found."""
        # Setup
        endpoint_path = "/api/concepts/generate"
        limit_string = "10/minute"
        mock_get_user_id.return_value = None
        decorated_handler = store_rate_limit_info(endpoint_path, limit_string)(mock_handler)

        # Execute
        await decorated_handler(mock_request)

        # Assert
        mock_get_user_id.assert_called_once_with(mock_request)
        mock_handler.assert_called_once_with(mock_request)
        # No limiter_info should be set
        assert not hasattr(mock_request.state, "limiter_info")

    @patch("app.utils.api_limits.decorators.get_user_id")
    @patch("app.utils.api_limits.decorators.check_rate_limit")
    async def test_store_rate_limit_info_exception(
        self, mock_check_rate_limit, mock_get_user_id, mock_request, mock_handler
    ):
        """Test decorator when check_rate_limit raises an exception."""
        # Setup
        endpoint_path = "/api/concepts/generate"
        limit_string = "10/minute"
        mock_get_user_id.return_value = "user-123"
        mock_check_rate_limit.side_effect = Exception("Rate limit error")
        decorated_handler = store_rate_limit_info(endpoint_path, limit_string)(mock_handler)

        # Execute
        await decorated_handler(mock_request)

        # Assert
        mock_get_user_id.assert_called_once_with(mock_request)
        mock_check_rate_limit.assert_called_once_with(
            user_id="user-123",
            endpoint=endpoint_path,
            limit=limit_string,
            check_only=True
        )
        # Handler should still be called even if rate limit check fails
        mock_handler.assert_called_once_with(mock_request)
        # No limiter_info should be set
        assert not hasattr(mock_request.state, "limiter_info")

    async def test_store_rate_limit_info_no_request(self, mock_handler):
        """Test decorator when no Request object is found in args or kwargs."""
        # Setup
        endpoint_path = "/api/concepts/generate"
        limit_string = "10/minute"
        decorated_handler = store_rate_limit_info(endpoint_path, limit_string)(mock_handler)

        # Execute
        await decorated_handler("arg1", arg2="value2")

        # Assert - handler should still be called
        mock_handler.assert_called_once_with("arg1", arg2="value2") 