"""
Tests for HTTP utility functions.
"""

import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx
from app.utils.http_utils import download_image


@pytest.mark.asyncio
class TestHttpUtils:
    """Tests for HTTP utility functions."""

    @patch("app.utils.http_utils.httpx.AsyncClient")
    async def test_download_image_success(self, mock_client_class):
        """Test successful image download."""
        # Set up mock
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.content = b"image_data"
        mock_client.get.return_value = mock_response

        # Execute
        result = await download_image("https://example.com/image.jpg")

        # Assert
        mock_client.get.assert_called_once_with("https://example.com/image.jpg")
        assert result == b"image_data"

    @patch("app.utils.http_utils.httpx.AsyncClient")
    async def test_download_image_http_error(self, mock_client_class):
        """Test image download with HTTP error."""
        # Set up mock
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        
        # Create a real HTTPStatusError
        request = httpx.Request("GET", "https://example.com/not-found.jpg")
        response = httpx.Response(404, request=request)
        http_error = httpx.HTTPStatusError("404 Not Found", request=request, response=response)
        
        # Make get() raise the exception directly
        mock_client.get.side_effect = http_error

        # Execute and assert
        with pytest.raises(httpx.HTTPStatusError):
            await download_image("https://example.com/not-found.jpg")

    @patch("app.utils.http_utils.httpx.AsyncClient")
    async def test_download_image_empty_content(self, mock_client_class):
        """Test image download with empty content."""
        # Set up mock
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_response = AsyncMock()
        mock_response.content = b""  # Empty content
        mock_client.get.return_value = mock_response

        # Execute and assert
        with pytest.raises(ValueError, match="Downloaded image is empty"):
            await download_image("https://example.com/empty.jpg")

    @patch("app.utils.http_utils.httpx.AsyncClient")
    async def test_download_image_connection_error(self, mock_client_class):
        """Test image download with connection error."""
        # Set up mock
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.get.side_effect = httpx.ConnectError("Connection failed")

        # Execute and assert
        with pytest.raises(httpx.ConnectError):
            await download_image("https://example.com/image.jpg") 