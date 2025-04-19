"""
Tests for concept request models.
"""

import pytest
from pydantic import ValidationError
from app.models.concept.request import PromptRequest, RefinementRequest


class TestPromptRequest:
    """Tests for the PromptRequest model."""

    def test_valid_request(self):
        """Test creating a valid PromptRequest."""
        request = PromptRequest(
            logo_description="A modern tech logo with abstract shapes",
            theme_description="Blue and green color scheme with a professional look"
        )
        assert request.logo_description == "A modern tech logo with abstract shapes"
        assert request.theme_description == "Blue and green color scheme with a professional look"

    def test_short_logo_description(self):
        """Test validation of short logo description."""
        with pytest.raises(ValidationError) as exc_info:
            PromptRequest(
                logo_description="Hi",  # Too short
                theme_description="Blue and green color scheme with a professional look"
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_short" for e in errors)

    def test_short_theme_description(self):
        """Test validation of short theme description."""
        with pytest.raises(ValidationError) as exc_info:
            PromptRequest(
                logo_description="A modern tech logo with abstract shapes",
                theme_description="Hi"  # Too short
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_short" for e in errors)

    def test_long_logo_description(self):
        """Test validation of long logo description."""
        with pytest.raises(ValidationError) as exc_info:
            PromptRequest(
                logo_description="A" * 501,  # Too long
                theme_description="Blue and green color scheme with a professional look"
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_long" for e in errors)

    def test_long_theme_description(self):
        """Test validation of long theme description."""
        with pytest.raises(ValidationError) as exc_info:
            PromptRequest(
                logo_description="A modern tech logo with abstract shapes",
                theme_description="A" * 501  # Too long
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_long" for e in errors)


class TestRefinementRequest:
    """Tests for the RefinementRequest model."""

    def test_valid_request(self):
        """Test creating a valid RefinementRequest."""
        request = RefinementRequest(
            original_image_url="https://example.com/image.png",
            logo_description="A modern tech logo with abstract shapes",
            theme_description="Blue and green color scheme with a professional look",
            refinement_prompt="Make the logo more minimalist",
            preserve_aspects=["colors", "layout"]
        )
        assert str(request.original_image_url) == "https://example.com/image.png"
        assert request.logo_description == "A modern tech logo with abstract shapes"
        assert request.theme_description == "Blue and green color scheme with a professional look"
        assert request.refinement_prompt == "Make the logo more minimalist"
        assert request.preserve_aspects == ["colors", "layout"]

    def test_minimal_valid_request(self):
        """Test creating a minimal valid RefinementRequest."""
        request = RefinementRequest(
            original_image_url="https://example.com/image.png",
            refinement_prompt="Make the logo more minimalist"
        )
        assert str(request.original_image_url) == "https://example.com/image.png"
        assert request.refinement_prompt == "Make the logo more minimalist"
        assert request.logo_description is None
        assert request.theme_description is None
        assert request.preserve_aspects == []

    def test_invalid_url(self):
        """Test validation of invalid URL."""
        with pytest.raises(ValidationError) as exc_info:
            RefinementRequest(
                original_image_url="not-a-url",
                refinement_prompt="Make the logo more minimalist"
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "url_parsing" for e in errors)

    def test_short_refinement_prompt(self):
        """Test validation of short refinement prompt."""
        with pytest.raises(ValidationError) as exc_info:
            RefinementRequest(
                original_image_url="https://example.com/image.png",
                refinement_prompt="Hi"  # Too short
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "string_too_short" for e in errors)

    def test_invalid_preserve_aspects(self):
        """Test validation of invalid preserve_aspects."""
        with pytest.raises(ValidationError) as exc_info:
            RefinementRequest(
                original_image_url="https://example.com/image.png",
                refinement_prompt="Make the logo more minimalist",
                preserve_aspects=["colors", "invalid_aspect"]
            )
        errors = exc_info.value.errors()
        assert "Invalid aspect: invalid_aspect" in str(exc_info.value) 