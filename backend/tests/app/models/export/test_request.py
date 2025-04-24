"""Tests for export request models."""

import pytest
from pydantic import ValidationError

from app.models.export.request import ExportRequest


class TestExportRequest:
    """Tests for the ExportRequest model."""

    def test_valid_png_export(self) -> None:
        """Test creating a valid PNG export request."""
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="medium",
            storage_bucket="concept-images",
            svg_params=None,
        )
        assert request.image_identifier == "user-123/concepts/logo.png"
        assert request.target_format == "png"
        assert request.target_size == "medium"
        assert request.svg_params is None
        assert request.storage_bucket == "concept-images"

    def test_valid_svg_export(self) -> None:
        """Test creating a valid SVG export request with SVG params."""
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="svg",
            target_size="original",
            svg_params={
                "colorQuantization": True,
                "colorCount": 16,
                "filterSpeckles": True,
                "posterization": 3,
            },
            storage_bucket="concept-images",
        )
        assert request.image_identifier == "user-123/concepts/logo.png"
        assert request.target_format == "svg"
        assert request.target_size == "original"
        assert request.svg_params is not None
        assert request.svg_params["colorQuantization"] is True
        assert request.svg_params["colorCount"] == 16
        assert request.storage_bucket == "concept-images"

    def test_minimal_export(self) -> None:
        """Test creating a minimal export request."""
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="jpg",
            target_size="original",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.image_identifier == "user-123/concepts/logo.png"
        assert request.target_format == "jpg"
        assert request.target_size == "original"  # Default
        assert request.svg_params is None
        assert request.storage_bucket == "concept-images"  # Default

    def test_image_identifier_validation(self) -> None:
        """Test image_identifier validation logic."""
        # Test that a valid storage path works
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="original",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.image_identifier == "user-123/concepts/logo.png"

    def test_storage_bucket_validation(self) -> None:
        """Test storage_bucket validation logic."""
        # Test with valid storage bucket
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="original",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.storage_bucket == "concept-images"

        # Test with another valid bucket
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="original",
            svg_params=None,
            storage_bucket="palette-images",
        )
        assert request.storage_bucket == "palette-images"

    def test_invalid_target_format(self) -> None:
        """Test validation rejects invalid target format."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="user-123/concepts/logo.png",
                target_format="gif",  # type: ignore # Not supported
                target_size="original",
                svg_params=None,
                storage_bucket="concept-images",
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "literal_error" for e in errors)

    def test_invalid_target_size(self) -> None:
        """Test validation rejects invalid target size."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="user-123/concepts/logo.png",
                target_format="png",
                target_size="huge",  # type: ignore # Not supported
                svg_params=None,
                storage_bucket="concept-images",
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "literal_error" for e in errors)

    def test_target_size_validation(self) -> None:
        """Test that valid target sizes are accepted."""
        # Test with small size
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="small",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.target_size == "small"

        # Test with medium size
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="medium",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.target_size == "medium"

        # Test with large size
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="large",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.target_size == "large"

        # Test with original size
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="original",
            svg_params=None,
            storage_bucket="concept-images",
        )
        assert request.target_size == "original"
