"""
Tests for concept response models.
"""

import pytest
from pydantic import ValidationError
from app.models.concept.response import (
    ColorPalette,
    PaletteVariation,
    GenerationResponse,
    RefinementResponse,
    ConceptSummary,
    ConceptDetail
)


class TestColorPalette:
    """Tests for the ColorPalette model."""

    def test_valid_palette(self):
        """Test creating a valid ColorPalette."""
        palette = ColorPalette(
            primary="#FF0000",
            secondary="#00FF00",
            accent="#0000FF",
            background="#FFFFFF",
            text="#000000",
            additional_colors=["#CCCCCC", "#333333"]
        )
        assert palette.primary == "#FF0000"
        assert palette.secondary == "#00FF00"
        assert palette.accent == "#0000FF"
        assert palette.background == "#FFFFFF"
        assert palette.text == "#000000"
        assert palette.additional_colors == ["#CCCCCC", "#333333"]

    def test_minimal_palette(self):
        """Test creating a minimal ColorPalette."""
        palette = ColorPalette(
            primary="#FF0000",
            secondary="#00FF00",
            accent="#0000FF",
            background="#FFFFFF",
            text="#000000"
        )
        assert palette.primary == "#FF0000"
        assert palette.secondary == "#00FF00"
        assert palette.accent == "#0000FF"
        assert palette.background == "#FFFFFF"
        assert palette.text == "#000000"
        assert palette.additional_colors == []


class TestPaletteVariation:
    """Tests for the PaletteVariation model."""

    def test_valid_variation(self):
        """Test creating a valid PaletteVariation."""
        variation = PaletteVariation(
            palette_name="Vibrant Blue",
            colors=["#0000FF", "#00FFFF", "#000088"],
            description="A vibrant blue color scheme",
            image_url="https://example.com/image.png"
        )
        assert variation.name == "Vibrant Blue"
        assert variation.colors == ["#0000FF", "#00FFFF", "#000088"]
        assert variation.description == "A vibrant blue color scheme"
        assert str(variation.image_url) == "https://example.com/image.png"

    def test_minimal_variation(self):
        """Test creating a minimal PaletteVariation."""
        variation = PaletteVariation(
            palette_name="Simple",
            colors=["#000000", "#FFFFFF"],
            image_url="https://example.com/image.png"
        )
        assert variation.name == "Simple"
        assert variation.colors == ["#000000", "#FFFFFF"]
        assert variation.description is None
        assert str(variation.image_url) == "https://example.com/image.png"


class TestGenerationResponse:
    """Tests for the GenerationResponse model."""

    def test_valid_response(self):
        """Test creating a valid GenerationResponse."""
        response = GenerationResponse(
            prompt_id="gen-123",
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            created_at="2023-01-01T12:00:00Z",
            image_url="https://example.com/image.png",
            color_palette=ColorPalette(
                primary="#0000FF",
                secondary="#00FF00",
                accent="#FF0000",
                background="#FFFFFF",
                text="#000000"
            ),
            variations=[
                PaletteVariation(
                    palette_name="Blue",
                    colors=["#0000FF", "#00FFFF"],
                    image_url="https://example.com/var1.png"
                ),
                PaletteVariation(
                    palette_name="Green",
                    colors=["#00FF00", "#88FF88"],
                    image_url="https://example.com/var2.png"
                )
            ]
        )
        assert response.prompt_id == "gen-123"
        assert response.logo_description == "A modern tech logo"
        assert response.theme_description == "Blue professional theme"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert str(response.image_url) == "https://example.com/image.png"
        assert response.color_palette.primary == "#0000FF"
        assert len(response.variations) == 2
        assert response.variations[0].name == "Blue"
        assert response.variations[1].name == "Green"

    def test_minimal_response(self):
        """Test creating a minimal GenerationResponse."""
        response = GenerationResponse(
            prompt_id="gen-123",
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            created_at="2023-01-01T12:00:00Z",
            image_url="https://example.com/image.png"
        )
        assert response.prompt_id == "gen-123"
        assert response.logo_description == "A modern tech logo"
        assert response.theme_description == "Blue professional theme"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert str(response.image_url) == "https://example.com/image.png"
        assert response.color_palette is None
        assert response.variations == []


class TestRefinementResponse:
    """Tests for the RefinementResponse model."""

    def test_valid_refinement(self):
        """Test creating a valid RefinementResponse."""
        response = RefinementResponse(
            prompt_id="ref-123",
            logo_description="An improved tech logo",
            theme_description="Blue professional theme",
            created_at="2023-01-01T12:00:00Z",
            image_url="https://example.com/refined.png",
            original_image_url="https://example.com/original.png",
            refinement_prompt="Make it more minimalist",
            original_concept_id="concept-123"
        )
        assert response.prompt_id == "ref-123"
        assert response.logo_description == "An improved tech logo"
        assert response.theme_description == "Blue professional theme"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert str(response.image_url) == "https://example.com/refined.png"
        assert str(response.original_image_url) == "https://example.com/original.png"
        assert response.refinement_prompt == "Make it more minimalist"
        assert response.original_concept_id == "concept-123"


class TestConceptSummary:
    """Tests for the ConceptSummary model."""

    def test_valid_summary(self):
        """Test creating a valid ConceptSummary."""
        summary = ConceptSummary(
            id="concept-123",
            created_at="2023-01-01T12:00:00Z",
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            image_url="https://example.com/image.png",
            has_variations=True,
            variations_count=3,
            is_refinement=False
        )
        assert summary.id == "concept-123"
        assert summary.created_at == "2023-01-01T12:00:00Z"
        assert summary.logo_description == "A modern tech logo"
        assert summary.theme_description == "Blue professional theme"
        assert str(summary.image_url) == "https://example.com/image.png"
        assert summary.has_variations is True
        assert summary.variations_count == 3
        assert summary.is_refinement is False
        assert summary.original_concept_id is None

    def test_refinement_summary(self):
        """Test creating a ConceptSummary for a refinement."""
        summary = ConceptSummary(
            id="concept-456",
            created_at="2023-01-02T12:00:00Z",
            logo_description="An improved tech logo",
            theme_description="Blue professional theme",
            image_url="https://example.com/refined.png",
            has_variations=False,
            variations_count=0,
            is_refinement=True,
            original_concept_id="concept-123"
        )
        assert summary.id == "concept-456"
        assert summary.is_refinement is True
        assert summary.original_concept_id == "concept-123"


class TestConceptDetail:
    """Tests for the ConceptDetail model."""

    def test_valid_detail(self):
        """Test creating a valid ConceptDetail."""
        detail = ConceptDetail(
            id="concept-123",
            created_at="2023-01-01T12:00:00Z",
            logo_description="A modern tech logo",
            theme_description="Blue professional theme",
            image_url="https://example.com/image.png",
            has_variations=True,
            variations_count=2,
            is_refinement=False,
            variations=[
                PaletteVariation(
                    palette_name="Blue",
                    colors=["#0000FF", "#00FFFF"],
                    image_url="https://example.com/var1.png"
                ),
                PaletteVariation(
                    palette_name="Green",
                    colors=["#00FF00", "#88FF88"],
                    image_url="https://example.com/var2.png"
                )
            ]
        )
        assert detail.id == "concept-123"
        assert detail.created_at == "2023-01-01T12:00:00Z"
        assert detail.logo_description == "A modern tech logo"
        assert detail.theme_description == "Blue professional theme"
        assert str(detail.image_url) == "https://example.com/image.png"
        assert detail.has_variations is True
        assert detail.variations_count == 2
        assert len(detail.variations) == 2
        assert detail.variations[0].name == "Blue"
        assert detail.variations[1].name == "Green"
        assert detail.is_refinement is False
        assert detail.refinement_prompt is None
        assert detail.original_image_url is None

    def test_refinement_detail(self):
        """Test creating a ConceptDetail for a refinement."""
        detail = ConceptDetail(
            id="concept-456",
            created_at="2023-01-02T12:00:00Z",
            logo_description="An improved tech logo",
            theme_description="Blue professional theme",
            image_url="https://example.com/refined.png",
            has_variations=False,
            variations_count=0,
            is_refinement=True,
            original_concept_id="concept-123",
            refinement_prompt="Make it more minimalist",
            original_image_url="https://example.com/original.png"
        )
        assert detail.id == "concept-456"
        assert detail.is_refinement is True
        assert detail.original_concept_id == "concept-123"
        assert detail.refinement_prompt == "Make it more minimalist"
        assert str(detail.original_image_url) == "https://example.com/original.png" 