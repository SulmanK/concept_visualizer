"""
Tests for export request models.
"""

import pytest
from pydantic import ValidationError
from app.models.export.request import ExportRequest


class TestExportRequest:
    """Tests for the ExportRequest model."""

    def test_valid_png_export(self):
        """Test creating a valid PNG export request."""
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="png",
            target_size="medium",
            storage_bucket="concept-images"
        )
        assert request.image_identifier == "user-123/concepts/logo.png"
        assert request.target_format == "png"
        assert request.target_size == "medium"
        assert request.svg_params is None
        assert request.storage_bucket == "concept-images"

    def test_valid_svg_export(self):
        """Test creating a valid SVG export request with SVG params."""
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="svg",
            target_size="original",
            svg_params={
                "colorQuantization": True,
                "colorCount": 16,
                "filterSpeckles": True,
                "posterization": 3
            },
            storage_bucket="concept-images"
        )
        assert request.image_identifier == "user-123/concepts/logo.png"
        assert request.target_format == "svg"
        assert request.target_size == "original"
        assert request.svg_params["colorQuantization"] is True
        assert request.svg_params["colorCount"] == 16
        assert request.storage_bucket == "concept-images"

    def test_minimal_export(self):
        """Test creating a minimal export request."""
        request = ExportRequest(
            image_identifier="user-123/concepts/logo.png",
            target_format="jpg"
        )
        assert request.image_identifier == "user-123/concepts/logo.png"
        assert request.target_format == "jpg"
        assert request.target_size == "original"  # Default
        assert request.svg_params is None
        assert request.storage_bucket == "concept-images"  # Default

    def test_invalid_image_identifier_url(self):
        """Test validation rejects URL as image identifier."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="https://example.com/image.png",
                target_format="png"
            )
        errors = exc_info.value.errors()
        assert any("image_identifier must be a storage path, not a URL" in e["msg"] for e in errors)

    def test_invalid_image_identifier_absolute_path(self):
        """Test validation rejects absolute path as image identifier."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="/user-123/concepts/logo.png",
                target_format="png"
            )
        errors = exc_info.value.errors()
        assert any("image_identifier must be a storage path, not a URL" in e["msg"] for e in errors)

    def test_invalid_target_format(self):
        """Test validation rejects invalid target format."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="user-123/concepts/logo.png",
                target_format="gif"  # Not supported
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "literal_error" for e in errors)

    def test_invalid_target_size(self):
        """Test validation rejects invalid target size."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="user-123/concepts/logo.png",
                target_format="png",
                target_size="huge"  # Not supported
            )
        errors = exc_info.value.errors()
        assert any(e["type"] == "literal_error" for e in errors)

    def test_invalid_storage_bucket(self):
        """Test validation rejects invalid storage bucket."""
        with pytest.raises(ValidationError) as exc_info:
            ExportRequest(
                image_identifier="user-123/concepts/logo.png",
                target_format="png",
                storage_bucket="invalid-bucket"
            )
        errors = exc_info.value.errors()
        assert any("storage_bucket must be one of" in e["msg"] for e in errors) 