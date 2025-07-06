"""Tests for the ConceptGenerator class.

This module tests the ConceptGenerator class which is responsible for
generating visual concepts using the JigsawStack API.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ConceptError, JigsawStackError
from app.models.concept.response import ColorPalette, GenerationResponse
from app.services.concept.generation import ConceptGenerator
from app.services.jigsawstack.client import JigsawStackClient


class TestConceptGenerator:
    """Tests for the ConceptGenerator class."""

    @pytest.fixture
    def mock_client(self) -> AsyncMock:
        """Create a mock JigsawStackClient."""
        client = AsyncMock(spec=JigsawStackClient)
        # Mock generate_image to return a URL in a dictionary (matching implementation)
        client.generate_image = AsyncMock(return_value={"url": "https://example.com/image.png", "id": "image123"})
        # Mock generate_multiple_palettes to return a list of palettes
        client.generate_multiple_palettes = AsyncMock(
            return_value=[
                {
                    "name": "Vibrant Blue",
                    "colors": ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"],
                    "description": "A vibrant blue palette",
                },
                {
                    "name": "Forest Green",
                    "colors": ["#228B22", "#32CD32", "#90EE90", "#98FB98", "#ADFF2F"],
                    "description": "A forest green palette",
                },
            ]
        )
        # Mock generate_image_with_palette to return binary image data
        client.generate_image_with_palette = AsyncMock(return_value=b"image_data")
        return client

    @pytest.fixture
    def generator(self, mock_client: AsyncMock) -> ConceptGenerator:
        """Create a ConceptGenerator with a mock client."""
        return ConceptGenerator(mock_client)

    @pytest.mark.asyncio
    async def test_generate_success(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test successful generation of a concept."""
        # Set up test inputs
        logo_description = "A modern tech logo with abstract shapes"
        theme_description = "Modern, sleek, blue theme"

        # Mock UUID for deterministic testing
        with patch("uuid.uuid4", return_value=uuid.UUID("12345678-1234-5678-1234-567812345678")):
            # Create a fixed datetime for testing
            fixed_dt_str = "2023-01-01T12:00:00"

            # Create a proper datetime mock that will work with isoformat
            mock_datetime = MagicMock()
            mock_datetime.isoformat.return_value = fixed_dt_str

            # Patch datetime.utcnow to return our mock
            with patch("datetime.datetime", autospec=True) as mock_dt_class:
                mock_dt_class.utcnow.return_value = mock_datetime

                # Call the method
                result = await generator.generate(logo_description, theme_description)

        # Verify correct calls were made
        mock_client.generate_image.assert_called_once_with(prompt=logo_description, width=256, height=256, model="stable-diffusion-xl")

        # Updated to match implementation - now using generate_multiple_palettes
        mock_client.generate_multiple_palettes.assert_called_once_with(logo_description=logo_description, theme_description=theme_description, num_palettes=1)

        # Verify result is correctly structured
        assert isinstance(result, GenerationResponse)
        assert result.prompt_id == "12345678-1234-5678-1234-567812345678"
        assert result.logo_description == logo_description
        assert result.theme_description == theme_description
        assert str(result.image_url) == "https://example.com/image.png"
        assert result.created_at == fixed_dt_str

        # Verify color palette - using colors from the mock generate_multiple_palettes response
        assert isinstance(result.color_palette, ColorPalette)
        assert result.color_palette.primary == "#FF5733"
        assert result.color_palette.secondary == "#33FF57"
        assert result.color_palette.accent == "#3357FF"
        assert result.color_palette.background == "#F3FF33"
        assert result.color_palette.text == "#FF33F3"
        assert result.color_palette.additional_colors == []

    @pytest.mark.asyncio
    async def test_generate_jigsawstack_error(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test generate with JigsawStackError."""
        # Set up API client to raise a JigsawStackError
        mock_client.generate_image.side_effect = JigsawStackError("API Error")

        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await generator.generate("A logo", "A theme")

    @pytest.mark.asyncio
    async def test_generate_generic_error(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test generate with a generic error."""
        # Set up API client to raise a generic exception
        mock_client.generate_image.side_effect = Exception("Some generic error")

        # Call the method and check that it wraps the error in a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate("A logo", "A theme")

        # Verify error details
        assert "Failed to generate concept" in str(excinfo.value)
        assert "Some generic error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_with_palettes_success(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test successful generation of a concept with multiple palettes."""
        # Set up test inputs
        logo_description = "A modern tech logo with abstract shapes"
        theme_description = "Modern, sleek, blue theme"
        num_palettes = 2

        # Call the method
        palettes, variation_images = await generator.generate_with_palettes(logo_description, theme_description, num_palettes)

        # Verify correct calls were made
        mock_client.generate_multiple_palettes.assert_called_once_with(
            logo_description=logo_description,
            theme_description=theme_description,
            num_palettes=num_palettes,
        )

        # Should be called twice, once for each palette
        assert mock_client.generate_image_with_palette.call_count == 2

        # First call should use the first palette
        mock_client.generate_image_with_palette.assert_any_call(
            logo_prompt=logo_description,
            palette=["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"],
            palette_name="Vibrant Blue",
        )

        # Second call should use the second palette
        mock_client.generate_image_with_palette.assert_any_call(
            logo_prompt=logo_description,
            palette=["#228B22", "#32CD32", "#90EE90", "#98FB98", "#ADFF2F"],
            palette_name="Forest Green",
        )

        # Verify result structure
        assert len(palettes) == 2
        assert len(variation_images) == 2

        # Check first palette details
        assert palettes[0]["name"] == "Vibrant Blue"
        assert palettes[0]["colors"] == ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"]
        assert palettes[0]["description"] == "A vibrant blue palette"

        # Check first variation image
        assert variation_images[0]["name"] == "Vibrant Blue"
        assert variation_images[0]["colors"] == ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"]
        assert variation_images[0]["description"] == "A vibrant blue palette"
        assert variation_images[0]["image_data"] == b"image_data"

    @pytest.mark.asyncio
    async def test_generate_with_palettes_partial_failure(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test generation with palettes when some palette generations fail."""
        # Make the second image generation fail
        mock_client.generate_image_with_palette.side_effect = [b"image_data", Exception("Failed for test")]

        # Call the method
        palettes, variation_images = await generator.generate_with_palettes("A logo", "A theme", 2)

        # Should still have both palettes
        assert len(palettes) == 2
        # But only one successful image generation
        assert len(variation_images) == 1

        # The successful image should be the first palette's image
        assert variation_images[0]["name"] == "Vibrant Blue"

    @pytest.mark.asyncio
    async def test_generate_with_palettes_complete_failure(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test generation with palettes when all generations fail."""
        # Make all image generations fail
        mock_client.generate_image_with_palette.side_effect = Exception("Failed for test")

        # Call the method and check that it raises an error when all images fail
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate_with_palettes("A logo", "A theme", 2)

        # Check the error message
        assert "Failed to generate any images" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_with_palettes_jigsawstack_error(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test generate_with_palettes with JigsawStackError."""
        # Set up API client to raise a JigsawStackError
        mock_client.generate_multiple_palettes.side_effect = JigsawStackError("API Error")

        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await generator.generate_with_palettes("A logo", "A theme")

    @pytest.mark.asyncio
    async def test_generate_with_palettes_generic_error(self, generator: ConceptGenerator, mock_client: AsyncMock) -> None:
        """Test generate_with_palettes with a generic error."""
        # Set up API client to raise a generic exception
        mock_client.generate_multiple_palettes.side_effect = Exception("Some generic error")

        # Call the method and check that it wraps the error in a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate_with_palettes("A logo", "A theme")

        # Verify error details
        assert "Failed to generate concept with palettes" in str(excinfo.value)
