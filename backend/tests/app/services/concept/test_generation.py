"""
Tests for the ConceptGenerator class.

This module tests the ConceptGenerator class which is responsible for
generating visual concepts using the JigsawStack API.
"""

import datetime
import uuid
from unittest.mock import AsyncMock, patch, MagicMock
import pytest
from typing import Dict, List, Any, Tuple

from app.core.exceptions import ConceptError, JigsawStackError
from app.models.concept.response import GenerationResponse, ColorPalette
from app.services.concept.generation import ConceptGenerator
from app.services.jigsawstack.client import JigsawStackClient


class TestConceptGenerator:
    """Tests for the ConceptGenerator class."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock JigsawStackClient."""
        client = AsyncMock(spec=JigsawStackClient)
        # Mock generate_image to return a URL
        client.generate_image = AsyncMock(return_value="https://example.com/image.png")
        # Mock generate_color_palette to return a list of colors
        client.generate_color_palette = AsyncMock(return_value=[
            "#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3",
            "#33FFF3", "#FF3333", "#33FF33"
        ])
        # Mock generate_multiple_palettes to return a list of palettes
        client.generate_multiple_palettes = AsyncMock(return_value=[
            {
                "name": "Vibrant Blue",
                "colors": ["#0047AB", "#6495ED", "#00BFFF", "#87CEEB", "#B0E0E6"],
                "description": "A vibrant blue palette"
            },
            {
                "name": "Forest Green",
                "colors": ["#228B22", "#32CD32", "#90EE90", "#98FB98", "#ADFF2F"],
                "description": "A forest green palette"
            }
        ])
        # Mock generate_image_with_palette to return binary image data
        client.generate_image_with_palette = AsyncMock(return_value=b'image_data')
        return client

    @pytest.fixture
    def generator(self, mock_client):
        """Create a ConceptGenerator with a mock client."""
        return ConceptGenerator(mock_client)

    @pytest.mark.asyncio
    async def test_generate_success(self, generator, mock_client):
        """Test successful generation of a concept."""
        # Set up test inputs
        logo_description = "A modern tech logo with abstract shapes"
        theme_description = "Modern, sleek, blue theme"
        
        # Mock UUID for deterministic testing
        with patch('uuid.uuid4', return_value=uuid.UUID('12345678-1234-5678-1234-567812345678')):
            # Create a fixed datetime for testing
            fixed_dt_str = "2023-01-01T12:00:00"
            
            # Create a proper datetime mock that will work with isoformat
            mock_datetime = MagicMock()
            mock_datetime.isoformat.return_value = fixed_dt_str
            
            # Patch datetime.utcnow to return our mock
            with patch('datetime.datetime', autospec=True) as mock_dt_class:
                mock_dt_class.utcnow.return_value = mock_datetime
                
                # Call the method
                result = await generator.generate(logo_description, theme_description)
        
        # Verify correct calls were made
        mock_client.generate_image.assert_called_once_with(
            prompt=logo_description,
            width=512,
            height=512,
            model="stable-diffusion-xl"
        )
        
        mock_client.generate_color_palette.assert_called_once_with(
            prompt=theme_description,
            num_colors=8
        )
        
        # Verify result is correctly structured
        assert isinstance(result, GenerationResponse)
        assert result.prompt_id == "12345678-1234-5678-1234-567812345678"
        assert result.logo_description == logo_description
        assert result.theme_description == theme_description
        assert str(result.image_url) == "https://example.com/image.png"
        assert result.created_at == fixed_dt_str
        
        # Verify color palette
        assert isinstance(result.color_palette, ColorPalette)
        assert result.color_palette.primary == "#FF5733"
        assert result.color_palette.secondary == "#33FF57"
        assert result.color_palette.accent == "#3357FF"
        assert result.color_palette.background == "#F3FF33"
        assert result.color_palette.text == "#FF33F3"
        assert result.color_palette.additional_colors == ["#33FFF3", "#FF3333", "#33FF33"]

    @pytest.mark.asyncio
    async def test_generate_jigsawstack_error(self, generator, mock_client):
        """Test generate with JigsawStackError."""
        # Set up API client to raise a JigsawStackError
        mock_client.generate_image.side_effect = JigsawStackError("API Error")
        
        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await generator.generate("A logo", "A theme")

    @pytest.mark.asyncio
    async def test_generate_generic_error(self, generator, mock_client):
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
    async def test_generate_with_palettes_success(self, generator, mock_client):
        """Test successful generation of a concept with multiple palettes."""
        # Set up test inputs
        logo_description = "A modern tech logo with abstract shapes"
        theme_description = "Modern, sleek, blue theme"
        num_palettes = 2
        
        # Call the method
        palettes, variation_images = await generator.generate_with_palettes(
            logo_description, theme_description, num_palettes
        )
        
        # Verify correct calls were made
        mock_client.generate_multiple_palettes.assert_called_once_with(
            logo_description=logo_description,
            theme_description=theme_description,
            num_palettes=num_palettes
        )
        
        # Should be called twice, once for each palette
        assert mock_client.generate_image_with_palette.call_count == 2
        
        # First call should use the first palette
        mock_client.generate_image_with_palette.assert_any_call(
            logo_prompt=logo_description,
            palette=["#0047AB", "#6495ED", "#00BFFF", "#87CEEB", "#B0E0E6"],
            palette_name="Vibrant Blue"
        )
        
        # Second call should use the second palette
        mock_client.generate_image_with_palette.assert_any_call(
            logo_prompt=logo_description,
            palette=["#228B22", "#32CD32", "#90EE90", "#98FB98", "#ADFF2F"],
            palette_name="Forest Green"
        )
        
        # Verify result structure
        assert len(palettes) == 2
        assert len(variation_images) == 2
        
        # Check first palette details
        assert palettes[0]["name"] == "Vibrant Blue"
        assert palettes[0]["colors"] == ["#0047AB", "#6495ED", "#00BFFF", "#87CEEB", "#B0E0E6"]
        assert palettes[0]["description"] == "A vibrant blue palette"
        
        # Check first variation image
        assert variation_images[0]["name"] == "Vibrant Blue"
        assert variation_images[0]["colors"] == ["#0047AB", "#6495ED", "#00BFFF", "#87CEEB", "#B0E0E6"]
        assert variation_images[0]["description"] == "A vibrant blue palette"
        assert variation_images[0]["image_data"] == b'image_data'

    @pytest.mark.asyncio
    async def test_generate_with_palettes_partial_failure(self, generator, mock_client):
        """Test generation with palettes where some image generations fail."""
        # Second call to generate_image_with_palette will fail
        mock_client.generate_image_with_palette.side_effect = [
            b'image_data',  # First call succeeds
            JigsawStackError("Failed to generate image")  # Second call fails
        ]
        
        # Call the method
        palettes, variation_images = await generator.generate_with_palettes(
            "A logo", "A theme", 2
        )
        
        # Verify we still get palettes
        assert len(palettes) == 2
        
        # But only one variation image
        assert len(variation_images) == 1
        assert variation_images[0]["name"] == "Vibrant Blue"

    @pytest.mark.asyncio
    async def test_generate_with_palettes_complete_failure(self, generator, mock_client):
        """Test generation with palettes where all image generations fail."""
        # All calls to generate_image_with_palette will fail
        mock_client.generate_image_with_palette.side_effect = JigsawStackError("Failed to generate image")
        
        # Call the method and expect a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate_with_palettes("A logo", "A theme", 2)
        
        # Verify error details
        assert "Failed to generate any images" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_generate_with_palettes_jigsawstack_error(self, generator, mock_client):
        """Test generate_with_palettes with JigsawStackError in the palette generation."""
        # Set up API client to raise a JigsawStackError
        mock_client.generate_multiple_palettes.side_effect = JigsawStackError("API Error")
        
        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await generator.generate_with_palettes("A logo", "A theme")

    @pytest.mark.asyncio
    async def test_generate_with_palettes_generic_error(self, generator, mock_client):
        """Test generate_with_palettes with a generic error in the palette generation."""
        # Set up API client to raise a generic exception
        mock_client.generate_multiple_palettes.side_effect = Exception("Some generic error")
        
        # Call the method and check that it wraps the error in a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await generator.generate_with_palettes("A logo", "A theme")
        
        # Verify error details
        assert "Failed to generate concept with palettes" in str(excinfo.value)
        assert "Some generic error" in str(excinfo.value) 