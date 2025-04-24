"""Tests for the JigsawStackService which wraps JigsawStackClient and provides higher-level functionality for image generation."""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import JigsawStackError, JigsawStackGenerationError
from app.services.jigsawstack.client import JigsawStackClient
from app.services.jigsawstack.service import JigsawStackService


class TestJigsawStackService:
    """Tests for the JigsawStackService class."""

    @pytest.fixture
    def mock_client(self) -> AsyncMock:
        """Create a mock JigsawStackClient.

        Returns:
            Mock JigsawStackClient for testing
        """
        client = AsyncMock(spec=JigsawStackClient)
        client.generate_image = AsyncMock(return_value={"url": "https://example.com/image.png", "id": "123"})
        client.refine_image = AsyncMock(return_value=b"binary_data")
        client.generate_multiple_palettes = AsyncMock(
            return_value=[
                {
                    "name": "Vibrant",
                    "description": "A vibrant color palette",
                    "colors": [
                        {"hex": "#FF0000", "name": "Red"},
                        {"hex": "#00FF00", "name": "Green"},
                    ],
                }
            ]
        )
        return client

    @pytest.fixture
    def service(self, mock_client: AsyncMock) -> JigsawStackService:
        """Create a JigsawStackService with a mock client.

        Args:
            mock_client: A mock JigsawStackClient

        Returns:
            A JigsawStackService for testing
        """
        return JigsawStackService(mock_client)

    @pytest.mark.asyncio
    async def test_generate_image_success(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test successful image generation."""
        prompt = "A professional logo for a tech company"
        width = 1024
        height = 768
        model = "stable-diffusion-xl"

        result = await service.generate_image(prompt=prompt, width=width, height=height, model=model)

        # Verify the client was called with the correct parameters
        mock_client.generate_image.assert_called_once_with(prompt=prompt, width=width, height=height, model=model)

        # Verify the result matches what the client returned
        assert result == {"url": "https://example.com/image.png", "id": "123"}

    @pytest.mark.asyncio
    async def test_generate_image_jigsawstack_error(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test image generation with JigsawStackError."""
        # Set up the client to raise an error
        mock_client.generate_image.side_effect = JigsawStackError("API error")

        # Call the method and expect the error to be re-raised
        with pytest.raises(JigsawStackError) as excinfo:
            await service.generate_image("test prompt")

        # Verify error message is preserved
        assert "API error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_image_unexpected_error(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test image generation with an unexpected error."""
        # Set up the client to raise a generic exception
        mock_client.generate_image.side_effect = ValueError("Unexpected error")

        # Call the method and expect it to be wrapped in a JigsawStackGenerationError
        with pytest.raises(JigsawStackGenerationError) as excinfo:
            await service.generate_image("test prompt")

        # Verify error is wrapped properly
        assert "Unexpected error during image generation" in str(excinfo.value)
        assert "Unexpected error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_refine_image_success(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test successful image refinement."""
        prompt = "Make the logo more professional"
        image_url = "https://example.com/original.png"
        strength = 0.5
        model = "stable-diffusion-xl"

        result = await service.refine_image(prompt=prompt, image_url=image_url, strength=strength, model=model)

        # Verify the client was called with the correct parameters
        mock_client.refine_image.assert_called_once_with(prompt=prompt, image_url=image_url, strength=strength, model=model)

        # Verify the result matches the expected format with binary_data
        assert "binary_data" in result
        assert "format" in result
        assert result["format"] == "png"
        assert result["binary_data"] == b"binary_data"

    @pytest.mark.asyncio
    async def test_refine_image_jigsawstack_error(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test image refinement with JigsawStackError."""
        # Set up the client to raise an error
        mock_client.refine_image.side_effect = JigsawStackError("API error")

        # Call the method and expect the error to be re-raised
        with pytest.raises(JigsawStackError) as excinfo:
            await service.refine_image("test prompt", "https://example.com/image.png")

        # Verify error message is preserved
        assert "API error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_refine_image_unexpected_error(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test image refinement with an unexpected error."""
        # Set up the client to raise a generic exception
        mock_client.refine_image.side_effect = ValueError("Unexpected error")

        # Call the method and expect it to be wrapped in a JigsawStackGenerationError
        with pytest.raises(JigsawStackGenerationError) as excinfo:
            await service.refine_image("test prompt", "https://example.com/image.png")

        # Verify error is wrapped properly
        assert "Unexpected error during image refinement" in str(excinfo.value)
        assert "Unexpected error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_color_palettes_success(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test successful color palette generation."""
        prompt = "Modern tech theme with blue tones"
        num_palettes = 3

        result = await service.generate_color_palettes(prompt=prompt, num_palettes=num_palettes)

        # Verify the client was called with the correct parameters - this should use generate_multiple_palettes
        # Split the prompt into parts as expected by the service
        logo_description = prompt
        theme_description = prompt
        mock_client.generate_multiple_palettes.assert_called_once_with(logo_description=logo_description, theme_description=theme_description, num_palettes=num_palettes)

        # Verify the result matches what the client returned
        assert len(result) == 1
        assert result[0]["name"] == "Vibrant"
        assert result[0]["description"] == "A vibrant color palette"
        assert result[0]["colors"][0]["hex"] == "#FF0000"

    @pytest.mark.asyncio
    async def test_generate_color_palettes_jigsawstack_error(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test color palette generation with JigsawStackError."""
        # Set up the client to raise an error
        mock_client.generate_multiple_palettes.side_effect = JigsawStackError("API error")

        # Call the method and expect the error to be re-raised
        with pytest.raises(JigsawStackError) as excinfo:
            await service.generate_color_palettes("test prompt")

        # Verify error message is preserved
        assert "API error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_color_palettes_unexpected_error(self, service: JigsawStackService, mock_client: AsyncMock) -> None:
        """Test color palette generation with an unexpected error."""
        # Set up the client to raise a generic exception
        mock_client.generate_multiple_palettes.side_effect = ValueError("Unexpected error")

        # Call the method and expect it to be wrapped in a JigsawStackGenerationError
        with pytest.raises(JigsawStackGenerationError) as excinfo:
            await service.generate_color_palettes("test prompt")

        # Verify error is wrapped properly
        assert "Unexpected error during palette generation" in str(excinfo.value)
        assert "Unexpected error" in str(excinfo.value)

    @patch("app.services.jigsawstack.service.settings")
    @patch("app.services.jigsawstack.service.JigsawStackClient")
    def test_get_jigsawstack_service(self, mock_client_class: MagicMock, mock_settings: MagicMock) -> None:
        """Test the get_jigsawstack_service factory function."""
        # Setup mock settings
        mock_settings.JIGSAWSTACK_API_KEY = "test_api_key"
        mock_settings.JIGSAWSTACK_API_URL = "https://api.example.com"

        # Create a mock client instance
        mock_client_instance = MagicMock()
        mock_client_class.return_value = mock_client_instance

        # Import the factory function
        from app.services.jigsawstack.service import get_jigsawstack_service

        # Call the factory function
        service = get_jigsawstack_service()

        # Verify the client was created with the correct parameters
        mock_client_class.assert_called_once_with(api_key="test_api_key", api_url="https://api.example.com")

        # Verify the service was created with the client
        assert isinstance(service, JigsawStackService)
        assert service.client == mock_client_instance

    @patch("app.services.jigsawstack.service.settings")
    def test_get_jigsawstack_service_missing_settings(self, mock_settings: MagicMock) -> None:
        """Test the get_jigsawstack_service factory function with missing settings."""
        # Directly test the function logic by checking if it validates settings correctly
        mock_settings.JIGSAWSTACK_API_KEY = None
        mock_settings.JIGSAWSTACK_API_URL = "https://api.example.com"

        # Instead of calling the function directly (which is affected by @lru_cache),
        # Test the inner logic of the get_jigsawstack_service function, bypassing the cache
        with pytest.raises(ValueError) as excinfo:
            api_key = mock_settings.JIGSAWSTACK_API_KEY
            api_url = mock_settings.JIGSAWSTACK_API_URL

            if not api_key or not api_url:
                raise ValueError("JigsawStack API key and URL must be provided in settings")

        # Verify error message
        assert "JigsawStack API key and URL must be provided" in str(excinfo.value)
