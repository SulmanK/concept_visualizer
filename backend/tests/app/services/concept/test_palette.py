"""Tests for the PaletteGenerator class.

This module tests the PaletteGenerator class which is responsible for
generating color palettes.
"""

from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ConceptError, JigsawStackError
from app.services.concept.palette import PaletteGenerator
from app.services.jigsawstack.client import JigsawStackClient


class TestPaletteGenerator:
    """Tests for the PaletteGenerator class."""

    @pytest.fixture
    def mock_client(self) -> AsyncMock:
        """Create a mock JigsawStackClient."""
        client = AsyncMock(spec=JigsawStackClient)

        # Mock generate_multiple_palettes to return a list of palettes
        client.generate_multiple_palettes = AsyncMock(
            return_value=[
                {
                    "name": "Vibrant Blue",
                    "colors": ["#0047AB", "#6495ED", "#00BFFF", "#87CEEB", "#B0E0E6"],
                    "description": "A vibrant blue palette",
                },
                {
                    "name": "Forest Green",
                    "colors": ["#228B22", "#32CD32", "#90EE90", "#98FB98", "#ADFF2F"],
                    "description": "A forest green palette",
                },
                {
                    "name": "Sunset Orange",
                    "colors": ["#FF4500", "#FF6347", "#FF7F50", "#FFA07A", "#FFDAB9"],
                    "description": "A warm sunset palette",
                },
            ]
        )

        # Mock generate_color_palette to return a list of color hex codes
        client.generate_color_palette = AsyncMock(
            return_value=[
                "#FF5733",
                "#33FF57",
                "#3357FF",
                "#F3FF33",
                "#FF33F3",
                "#33FFF3",
                "#FF3333",
                "#33FF33",
            ]
        )

        return client

    @pytest.fixture
    def generator(self, mock_client: AsyncMock) -> PaletteGenerator:
        """Create a PaletteGenerator with a mock client."""
        return PaletteGenerator(mock_client)

    @pytest.mark.asyncio
    async def test_generate_palettes_success(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test successful generation of multiple color palettes."""
        # Set up test inputs
        theme_description = "Modern, sleek, blue theme"
        logo_description = "A modern tech logo with abstract shapes"
        num_palettes = 3

        # Call the method
        result = await generator.generate_palettes(
            theme_description=theme_description,
            logo_description=logo_description,
            num_palettes=num_palettes,
        )

        # Verify correct call was made to generate_multiple_palettes
        mock_client.generate_multiple_palettes.assert_called_once_with(
            logo_description=logo_description,
            theme_description=theme_description,
            num_palettes=num_palettes,
        )

        # Verify the result
        assert len(result) == 3
        assert isinstance(result, list)
        assert isinstance(result[0], dict)

        # Check the structure of the first palette
        assert "name" in result[0]
        assert "colors" in result[0]
        assert "description" in result[0]
        assert isinstance(result[0]["colors"], list)
        assert result[0]["name"] == "Vibrant Blue"
        assert result[0]["colors"] == [
            "#0047AB",
            "#6495ED",
            "#00BFFF",
            "#87CEEB",
            "#B0E0E6",
        ]
        assert result[0]["description"] == "A vibrant blue palette"

    @pytest.mark.asyncio
    async def test_generate_palettes_without_logo_description(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test generating palettes without providing a logo description."""
        # Set up test inputs
        theme_description = "Modern, sleek, blue theme"
        num_palettes = 3

        # Call the method without logo_description
        result = await generator.generate_palettes(theme_description=theme_description, num_palettes=num_palettes)

        # Verify correct call was made to generate_multiple_palettes with empty logo_description
        mock_client.generate_multiple_palettes.assert_called_once_with(
            logo_description="",
            theme_description=theme_description,
            num_palettes=num_palettes,
        )

        # Verify the result is still as expected
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_generate_palettes_jigsawstack_error(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test generate_palettes with JigsawStackError."""
        # Set up API client to raise a JigsawStackError
        mock_client.generate_multiple_palettes.side_effect = JigsawStackError("API Error")

        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await generator.generate_palettes(theme_description="A theme", logo_description="A logo")

    @pytest.mark.asyncio
    async def test_generate_palettes_generic_error(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test generate_palettes with a generic error."""
        # Set up API client to raise a generic exception
        mock_client.generate_multiple_palettes.side_effect = Exception("Some generic error")

        # Call the method and check that it wraps the error in a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate_palettes(theme_description="A theme", logo_description="A logo")

        # Verify error details
        assert "Failed to generate palettes" in str(excinfo.value)
        assert "Some generic error" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_single_palette_success(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test successful generation of a single color palette."""
        # Set up test inputs
        theme_description = "Modern, sleek, blue theme"
        num_colors = 8

        # Call the method
        result = await generator.generate_single_palette(theme_description=theme_description, num_colors=num_colors)

        # Update the test to match the implementation: generate_single_palette uses generate_multiple_palettes
        # instead of generate_color_palette
        mock_client.generate_multiple_palettes.assert_called_once_with(logo_description="", theme_description=theme_description, num_palettes=1)

        # Verify the result
        assert len(result) == 8  # The palette implementation pads to the requested number of colors
        assert isinstance(result, list)
        assert isinstance(result[0], str)
        # The first colors should be from the mock response's first palette
        assert result[0] == "#0047AB"

    @pytest.mark.asyncio
    async def test_generate_single_palette_jigsawstack_error(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test generate_single_palette with JigsawStackError."""
        # Set up API client to raise a JigsawStackError
        mock_client.generate_multiple_palettes.side_effect = JigsawStackError("API Error")

        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await generator.generate_single_palette(theme_description="A theme")

    @pytest.mark.asyncio
    async def test_generate_single_palette_generic_error(self, generator: PaletteGenerator, mock_client: AsyncMock) -> None:
        """Test generate_single_palette with a generic error."""
        # Set up API client to raise a generic exception
        mock_client.generate_multiple_palettes.side_effect = Exception("Some generic error")

        # Call the method and check that it wraps the error in a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate_single_palette(theme_description="A theme")

        # Verify error details
        assert "Failed to generate palette" in str(excinfo.value)
        assert "Some generic error" in str(excinfo.value)
