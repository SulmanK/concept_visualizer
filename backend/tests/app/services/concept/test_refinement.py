"""Tests for the ConceptRefiner class.

This module tests the ConceptRefiner class which is responsible for
refining existing visual concepts.
"""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.exceptions import ConceptError, JigsawStackError
from app.services.concept.refinement import ConceptRefiner
from app.services.jigsawstack.client import JigsawStackClient


class TestConceptRefiner:
    """Tests for the ConceptRefiner class."""

    @pytest.fixture
    def mock_client(self) -> AsyncMock:
        """Create a mock JigsawStackClient."""
        client = AsyncMock(spec=JigsawStackClient)
        # Mock refine_image to return a URL
        client.refine_image = AsyncMock(return_value="https://example.com/refined.png")
        # Mock generate_multiple_palettes to return a list of palettes
        client.generate_multiple_palettes = AsyncMock(
            return_value=[
                {
                    "name": "Vibrant Blue",
                    "colors": [
                        "#FF5733",
                        "#33FF57",
                        "#3357FF",
                        "#F3FF33",
                        "#FF33F3",
                    ],
                    "description": "A vibrant blue palette",
                },
            ]
        )
        return client

    @pytest.fixture
    def refiner(self, mock_client: AsyncMock) -> ConceptRefiner:
        """Create a ConceptRefiner with a mock client."""
        return ConceptRefiner(mock_client)

    @pytest.mark.asyncio
    async def test_refine_success(self, refiner: ConceptRefiner, mock_client: AsyncMock) -> None:
        """Test successful refinement of a concept."""
        # Set up test inputs
        original_image_url = "https://example.com/original.png"
        logo_description = "A modern tech logo with abstract shapes"
        theme_description = "Modern, sleek, blue theme"
        refinement_prompt = "Make it more abstract and use brighter colors"
        preserve_aspects = ["color scheme", "basic shape"]

        # Mock UUID for deterministic testing
        with patch("uuid.uuid4", return_value=uuid.UUID("12345678-1234-5678-1234-567812345678")):
            # Create a fixed datetime string for testing
            fixed_dt_str = "2023-01-01T12:00:00"

            # Mock datetime.datetime properly
            with patch("datetime.datetime") as mock_dt:
                # Set up the utcnow mock to return a mock datetime object
                mock_datetime = MagicMock()
                mock_datetime.isoformat.return_value = fixed_dt_str
                mock_dt.utcnow.return_value = mock_datetime

                # Call the method
                result = await refiner.refine(
                    original_image_url=original_image_url,
                    logo_description=logo_description,
                    theme_description=theme_description,
                    refinement_prompt=refinement_prompt,
                    preserve_aspects=preserve_aspects,
                )

        # Verify correct calls were made to refine_image
        mock_client.refine_image.assert_called_once()
        call_args = mock_client.refine_image.call_args[1]

        # Verify the prompt contains all the necessary information
        assert "Refine this logo design" in call_args["prompt"]
        assert logo_description in call_args["prompt"]
        assert theme_description in call_args["prompt"]
        assert refinement_prompt in call_args["prompt"]
        assert "Preserve the following aspects" in call_args["prompt"]
        assert "color scheme, basic shape" in call_args["prompt"]

        # Verify other parameters - updated to match implementation
        assert call_args["image_url"] == original_image_url
        assert call_args["strength"] == 0.7

        # Verify call to generate_multiple_palettes instead of generate_color_palette
        mock_client.generate_multiple_palettes.assert_called_once_with(logo_description=logo_description, theme_description=theme_description, num_palettes=1)

        # Verify result is a dictionary with the expected fields
        assert isinstance(result, dict)
        assert result["prompt_id"] == "12345678-1234-5678-1234-567812345678"
        assert result["logo_description"] == logo_description
        assert result["theme_description"] == theme_description
        assert result["image_url"] == "https://example.com/refined.png"
        assert result["created_at"] == fixed_dt_str
        assert result["refinement_prompt"] == refinement_prompt
        assert result["original_image_url"] == "https://example.com/original.png"

        # Verify colors from palette
        assert "colors" in result
        assert isinstance(result["colors"], list)
        assert result["colors"][0] == "#FF5733"

    @pytest.mark.asyncio
    async def test_refine_with_minimal_inputs(self, refiner: ConceptRefiner, mock_client: AsyncMock) -> None:
        """Test refinement with only the required parameters."""
        # Set up test inputs with minimal requirements
        original_image_url = "https://example.com/original.png"
        refinement_prompt = "Make it more abstract"

        # Create a fixed datetime string for testing
        fixed_dt_str = "2023-01-01T12:00:00"

        # Mock datetime.datetime properly with autospec
        with patch("datetime.datetime") as mock_dt:
            # Set up the utcnow mock to return a mock datetime object
            mock_datetime = MagicMock()
            mock_datetime.isoformat.return_value = fixed_dt_str
            mock_dt.utcnow.return_value = mock_datetime

            # Call the method with minimal inputs
            result = await refiner.refine(
                original_image_url=original_image_url,
                logo_description=None,
                theme_description=None,
                refinement_prompt=refinement_prompt,
                preserve_aspects=[],
            )

        # Verify the prompt contains default descriptions
        call_args = mock_client.refine_image.call_args[1]
        assert "the existing logo" in call_args["prompt"]
        assert "the existing theme" in call_args["prompt"]
        assert refinement_prompt in call_args["prompt"]

        # Verify no preservation text was included
        assert "Preserve the following aspects" not in call_args["prompt"]

        # Verify result contains correct values - updated to match dict return type
        assert result["logo_description"] == "the existing logo"
        assert result["theme_description"] == "the existing theme"
        assert result["refinement_prompt"] == refinement_prompt
        assert result["original_image_url"] == "https://example.com/original.png"
        assert result["image_url"] == "https://example.com/refined.png"
        assert result["created_at"] == fixed_dt_str
        # We don't check preserve_aspects as it's not part of the GenerationResponse model

    @pytest.mark.asyncio
    async def test_refine_jigsawstack_error(self, refiner: ConceptRefiner, mock_client: AsyncMock) -> None:
        """Test refinement with JigsawStackError."""
        # Set up API client to raise a JigsawStackError
        mock_client.refine_image.side_effect = JigsawStackError("API Error")

        # Call the method and check that it raises the original JigsawStackError
        with pytest.raises(JigsawStackError):
            await refiner.refine(
                original_image_url="https://example.com/original.png",
                logo_description="A logo",
                theme_description="A theme",
                refinement_prompt="Improve it",
                preserve_aspects=[],
            )

    @pytest.mark.asyncio
    async def test_refine_generic_error(self, refiner: ConceptRefiner, mock_client: AsyncMock) -> None:
        """Test refinement with a generic error."""
        # Set up API client to raise a generic exception
        mock_client.refine_image.side_effect = Exception("Some generic error")

        # Call the method and check that it wraps the error in a ConceptError
        with pytest.raises(ConceptError) as excinfo:
            await refiner.refine(
                original_image_url="https://example.com/original.png",
                logo_description="A logo",
                theme_description="A theme",
                refinement_prompt="Improve it",
                preserve_aspects=[],
            )

        # Verify error details
        assert "Failed to refine concept" in str(excinfo.value)
        assert "Some generic error" in str(excinfo.value)
