"""Tests for API rate limit endpoint utilities."""

from unittest.mock import MagicMock, patch

import pytest
from fastapi import HTTPException, Request

from app.utils.api_limits.endpoints import apply_multiple_rate_limits, apply_rate_limit


class TestApplyRateLimit:
    """Tests for the apply_rate_limit function."""

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock Request object.

        Returns:
            MagicMock: A mocked FastAPI Request object
        """
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        return request

    @patch("app.utils.api_limits.endpoints.settings")
    async def test_apply_rate_limit_disabled(self, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test when rate limiting is disabled."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = False

        # Execute
        result = await apply_rate_limit(mock_request, "test_endpoint", "10/minute")

        # Assert
        assert result == {"enabled": False}

    @patch("app.utils.api_limits.endpoints.settings")
    async def test_apply_rate_limit_no_limiter(self, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test when limiter is not available."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state = MagicMock(spec={})  # No limiter attribute

        # Execute
        result = await apply_rate_limit(mock_request, "test_endpoint", "10/minute")

        # Assert
        assert result == {"enabled": False}

    @patch("app.utils.api_limits.endpoints.settings")
    @patch("app.utils.api_limits.endpoints.get_remote_address")
    async def test_apply_rate_limit_with_user_id(self, mock_get_remote_address: MagicMock, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test with authenticated user ID."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state.limiter = MagicMock()
        mock_request.app.state.limiter.check_request = MagicMock(return_value=False)  # Not rate limited
        mock_request.state.user = {"id": "user-123"}
        mock_request.state.limiter_info = {
            "limit": 10,
            "remaining": 9,
            "reset": 1635283200,
        }
        mock_request.response = MagicMock()

        # Execute
        result = await apply_rate_limit(mock_request, "test_endpoint", "10/minute")

        # Assert
        mock_request.app.state.limiter.check_request.assert_called_once_with(mock_request, "10/minute")
        assert result == {"enabled": True, "limited": False}

        # Check headers
        assert mock_request.response.headers["X-RateLimit-Limit"] == "10"
        assert mock_request.response.headers["X-RateLimit-Remaining"] == "9"
        assert mock_request.response.headers["X-RateLimit-Reset"] == "1635283200"

        # Verify get_remote_address was not called (using user ID instead)
        mock_get_remote_address.assert_not_called()

    @patch("app.utils.api_limits.endpoints.settings")
    @patch("app.utils.api_limits.endpoints.get_remote_address")
    async def test_apply_rate_limit_with_ip(self, mock_get_remote_address: MagicMock, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test with IP address (no authenticated user)."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state.limiter = MagicMock()
        mock_request.app.state.limiter.check_request = MagicMock(return_value=False)  # Not rate limited
        mock_request.state.user = None  # No authenticated user
        mock_get_remote_address.return_value = "127.0.0.1"

        # Execute
        result = await apply_rate_limit(mock_request, "test_endpoint", "10/minute")

        # Assert
        mock_request.app.state.limiter.check_request.assert_called_once_with(mock_request, "10/minute")
        mock_get_remote_address.assert_called_once_with(mock_request)
        assert result == {"enabled": True, "limited": False}

    @patch("app.utils.api_limits.endpoints.settings")
    @patch("app.utils.api_limits.endpoints.get_remote_address")
    async def test_apply_rate_limit_exceeded(self, mock_get_remote_address: MagicMock, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test when rate limit is exceeded."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state.limiter = MagicMock()
        mock_request.app.state.limiter.check_request = MagicMock(return_value=True)  # Rate limited
        mock_request.state.user = {"id": "user-123"}
        mock_request.state.limiter_info = {"reset": 1635283200}

        # Execute and Assert
        with pytest.raises(HTTPException) as exc_info:
            await apply_rate_limit(mock_request, "test_endpoint", "10/minute")

        assert exc_info.value.status_code == 429
        assert "Rate limit exceeded" in exc_info.value.detail
        assert exc_info.value.headers == {"Retry-After": "1635283200"}

    @patch("app.utils.api_limits.endpoints.settings")
    @patch("app.utils.api_limits.endpoints.check_rate_limit")
    async def test_apply_rate_limit_using_fallback(self, mock_check_rate_limit: MagicMock, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test using the fallback check_rate_limit method."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        limiter = MagicMock()  # No check_request method
        mock_request.app.state.limiter = limiter
        mock_request.state.user = {"id": "user-123"}
        mock_check_rate_limit.return_value = {"exceeded": False}

        # Execute
        result = await apply_rate_limit(mock_request, "test_endpoint", "10/minute")

        # Assert
        mock_check_rate_limit.assert_called_once()
        assert result == {"enabled": True, "limited": False}


class TestApplyMultipleRateLimits:
    """Tests for the apply_multiple_rate_limits function."""

    @pytest.fixture
    def mock_request(self) -> MagicMock:
        """Create a mock Request object.

        Returns:
            MagicMock: A mocked FastAPI Request object
        """
        request = MagicMock(spec=Request)
        request.state = MagicMock()
        request.app = MagicMock()
        request.app.state = MagicMock()
        return request

    @patch("app.utils.api_limits.endpoints.settings")
    async def test_apply_multiple_rate_limits_disabled(self, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test when rate limiting is disabled."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = False
        rate_limits = [
            {"endpoint": "test_endpoint1", "rate_limit": "10/minute"},
            {"endpoint": "test_endpoint2", "rate_limit": "100/day"},
        ]

        # Execute
        result = await apply_multiple_rate_limits(mock_request, rate_limits)

        # Assert
        assert result == {"enabled": False}

    @patch("app.utils.api_limits.endpoints.settings")
    async def test_apply_multiple_rate_limits_no_limiter(self, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test when limiter is not available."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state = MagicMock(spec={})  # No limiter attribute
        rate_limits = [
            {"endpoint": "test_endpoint1", "rate_limit": "10/minute"},
            {"endpoint": "test_endpoint2", "rate_limit": "100/day"},
        ]

        # Execute
        result = await apply_multiple_rate_limits(mock_request, rate_limits)

        # Assert
        assert result == {"enabled": False}

    @patch("app.utils.api_limits.endpoints.settings")
    @patch("app.utils.api_limits.endpoints.check_rate_limit")
    @patch("app.utils.api_limits.endpoints.get_remote_address")
    async def test_apply_multiple_rate_limits_success(
        self,
        mock_get_remote_address: MagicMock,
        mock_check_rate_limit: MagicMock,
        mock_settings: MagicMock,
        mock_request: MagicMock,
    ) -> None:
        """Test successful application of multiple rate limits."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state.limiter = MagicMock()
        mock_request.state.user = {"id": "user-123"}

        # Configure check_rate_limit to return non-exceeded for all limits
        mock_check_rate_limit.return_value = {
            "exceeded": False,
            "limit": 10,
            "remaining": 9,
            "reset_at": 1635283200,
        }

        rate_limits = [
            {"endpoint": "test_endpoint1", "rate_limit": "10/minute"},
            {"endpoint": "test_endpoint2", "rate_limit": "100/day", "period": "day"},
        ]

        # Execute
        result = await apply_multiple_rate_limits(mock_request, rate_limits)

        # Assert
        assert mock_check_rate_limit.call_count == 2
        assert "test_endpoint1" in result
        assert "test_endpoint2" in result
        assert result["test_endpoint1"]["limited"] is False
        assert result["test_endpoint2"]["limited"] is False

    @patch("app.utils.api_limits.endpoints.settings")
    @patch("app.utils.api_limits.endpoints.check_rate_limit")
    @patch("app.utils.api_limits.endpoints.get_remote_address")
    async def test_apply_multiple_rate_limits_exceeded(
        self,
        mock_get_remote_address: MagicMock,
        mock_check_rate_limit: MagicMock,
        mock_settings: MagicMock,
        mock_request: MagicMock,
    ) -> None:
        """Test when one of the rate limits is exceeded."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        mock_request.app.state.limiter = MagicMock()
        mock_request.state.user = {"id": "user-123"}

        # Configure check_rate_limit to return exceeded for the second limit
        mock_check_rate_limit.side_effect = [
            {
                "exceeded": False,
                "limit": 10,
                "remaining": 9,
                "reset_at": 1635283200,
            },  # First limit OK
            {
                "exceeded": True,
                "limit": 100,
                "remaining": 0,
                "reset_at": 1635369600,
            },  # Second limit exceeded
        ]

        rate_limits = [
            {"endpoint": "test_endpoint1", "rate_limit": "10/minute"},
            {"endpoint": "test_endpoint2", "rate_limit": "100/day"},
        ]

        # Execute and Assert
        with pytest.raises(HTTPException) as exc_info:
            await apply_multiple_rate_limits(mock_request, rate_limits)

        assert exc_info.value.status_code == 429
        assert "test_endpoint2" in exc_info.value.detail
        assert "100/day" in exc_info.value.detail
        assert exc_info.value.headers == {"Retry-After": "1635369600"}

    @patch("app.utils.api_limits.endpoints.settings")
    async def test_apply_multiple_rate_limits_missing_fields(self, mock_settings: MagicMock, mock_request: MagicMock) -> None:
        """Test handling of rate limit items with missing fields."""
        # Setup
        mock_settings.RATE_LIMITING_ENABLED = True
        rate_limits = [
            {"endpoint": "test_endpoint1"},  # Missing rate_limit
            {"rate_limit": "100/day"},  # Missing endpoint
        ]

        # Execute
        result = await apply_multiple_rate_limits(mock_request, rate_limits)

        # Assert
        assert result == {"enabled": True, "limited": False, "rate_limits": []}

    @patch("app.utils.api_limits.endpoints.apply_rate_limit")
    async def test_apply_multiple_rate_limits_with_period(self, mock_apply_rate_limit: MagicMock, mock_request: MagicMock) -> None:
        """Test applying multiple rate limits with a period override."""
        # Setup
        mock_apply_rate_limit.side_effect = [
            {"enabled": True, "limited": False},
            {"enabled": True, "limited": False},
        ]
        rate_limits = [
            {"endpoint": "test_endpoint1", "rate_limit": "10", "period": "minute"},
            {"endpoint": "test_endpoint2", "rate_limit": "100", "period": "day"},
        ]

        # Execute
        result = await apply_multiple_rate_limits(mock_request, rate_limits)

        # Assert
        assert result == {
            "enabled": True,
            "limited": False,
            "rate_limits": [
                {"enabled": True, "limited": False},
                {"enabled": True, "limited": False},
            ],
        }
        assert mock_apply_rate_limit.call_count == 2
        mock_apply_rate_limit.assert_any_call(mock_request, "test_endpoint1", "10", "minute")
        mock_apply_rate_limit.assert_any_call(mock_request, "test_endpoint2", "100", "day")

    async def test_apply_multiple_rate_limits_empty_list(self, mock_request: MagicMock) -> None:
        """Test applying an empty list of rate limits."""
        # Setup
        rate_limits = []  # type: list[dict]

        # Execute
        result = await apply_multiple_rate_limits(mock_request, rate_limits)

        # Assert
        assert result is not None
        assert result["enabled"] is True
        assert result["limited"] is False
        assert result["rate_limits"] == []
