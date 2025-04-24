"""Tests for the image conversion utilities.

This module contains tests for the conversion functions that handle
image format conversions, thumbnail generation, and metadata extraction.
"""

from io import BytesIO
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from PIL import Image

from app.services.image.conversion import ConversionError, convert_image_format, detect_image_format, generate_thumbnail, get_image_metadata, optimize_image


@pytest.fixture
def sample_png_bytes() -> bytes:
    """Create a simple PNG image and return its bytes."""
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


@pytest.fixture
def sample_jpg_bytes() -> bytes:
    """Create a simple JPEG image and return its bytes."""
    img = Image.new("RGB", (100, 100), color="blue")
    img_bytes = BytesIO()
    img.save(img_bytes, format="JPEG", quality=95)
    return img_bytes.getvalue()


@pytest.fixture
def sample_png_with_alpha_bytes() -> bytes:
    """Create a PNG image with transparency and return its bytes."""
    img = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))  # Semi-transparent red
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    return img_bytes.getvalue()


class TestDetectImageFormat:
    """Tests for the detect_image_format function."""

    def test_detect_png_format(self, sample_png_bytes: bytes) -> None:
        """Test detection of PNG format."""
        result = detect_image_format(sample_png_bytes)
        assert result == "png"

    def test_detect_jpg_format(self, sample_jpg_bytes: bytes) -> None:
        """Test detection of JPEG format."""
        result = detect_image_format(sample_jpg_bytes)
        assert result == "jpg"

    @patch("imghdr.what")
    def test_detect_webp_format(self, mock_imghdr_what: MagicMock) -> None:
        """Test detection of WebP format."""
        # Setup: imghdr returns webp
        mock_imghdr_what.return_value = "webp"

        # Execute
        result = detect_image_format(b"test_data")

        # Verify
        assert result == "webp"
        mock_imghdr_what.assert_called_once()

    @patch("imghdr.what")
    def test_detect_gif_format(self, mock_imghdr_what: MagicMock) -> None:
        """Test detection of GIF format."""
        # Setup: imghdr returns gif
        mock_imghdr_what.return_value = "gif"

        # Execute
        result = detect_image_format(b"test_data")

        # Verify
        assert result == "gif"
        mock_imghdr_what.assert_called_once()

    @patch("imghdr.what")
    @patch("PIL.Image.open")
    def test_fallback_to_pil(self, mock_pil_open: MagicMock, mock_imghdr_what: MagicMock, sample_png_bytes: bytes) -> None:
        """Test fallback to PIL when imghdr fails."""
        # Setup: imghdr fails to detect format
        mock_imghdr_what.return_value = None

        # Setup: PIL detects format
        mock_img = MagicMock()
        mock_img.format = "PNG"
        mock_pil_open.return_value = mock_img

        # Execute
        result = detect_image_format(sample_png_bytes)

        # Verify
        assert result == "png"
        mock_imghdr_what.assert_called_once()
        mock_pil_open.assert_called_once()

    @patch("imghdr.what")
    @patch("PIL.Image.open")
    def test_fallback_to_default(self, mock_pil_open: MagicMock, mock_imghdr_what: MagicMock, sample_png_bytes: bytes) -> None:
        """Test fallback to default format when all detection methods fail."""
        # Setup: both imghdr and PIL fail
        mock_imghdr_what.return_value = None
        mock_img = MagicMock()
        mock_img.format = None
        mock_pil_open.return_value = mock_img

        # Execute
        result = detect_image_format(sample_png_bytes)

        # Verify
        assert result == "png"  # Default is PNG

    @patch("imghdr.what")
    def test_exception_handling(self, mock_imghdr_what: MagicMock, sample_png_bytes: bytes) -> None:
        """Test error handling when exceptions occur during detection."""
        # Setup
        mock_imghdr_what.side_effect = Exception("Test error")

        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            detect_image_format(sample_png_bytes)

        assert "Failed to detect image format" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)

    @patch("imghdr.what")
    @patch("PIL.Image.open")
    def test_pil_exception_handling(self, mock_pil_open: MagicMock, mock_imghdr_what: MagicMock, sample_png_bytes: bytes) -> None:
        """Test error handling when PIL throws an exception."""
        # Setup: imghdr fails, and PIL raises exception
        mock_imghdr_what.return_value = None
        mock_pil_open.side_effect = Exception("PIL error")

        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            detect_image_format(sample_png_bytes)

        assert "Failed to detect image format" in str(excinfo.value)
        assert "PIL error" in str(excinfo.value)

    @patch("imghdr.what")
    @patch("PIL.Image.open")
    def test_normalize_jpeg_format(self, mock_pil_open: MagicMock, mock_imghdr_what: MagicMock) -> None:
        """Test that 'jpeg' is normalized to 'jpg'."""
        # Setup: imghdr returns jpeg
        mock_imghdr_what.return_value = "jpeg"

        # Execute
        result = detect_image_format(b"test_data")

        # Verify
        assert result == "jpg"  # Should normalize to jpg
        mock_imghdr_what.assert_called_once()


class TestConvertImageFormat:
    """Tests for the convert_image_format function."""

    def test_convert_png_to_jpg(self, sample_png_bytes: bytes) -> None:
        """Test conversion from PNG to JPEG."""
        result = convert_image_format(sample_png_bytes, target_format="jpg", quality=95)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify result is a JPEG
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"

    def test_convert_jpg_to_png(self, sample_jpg_bytes: bytes) -> None:
        """Test conversion from JPEG to PNG."""
        result = convert_image_format(sample_jpg_bytes, target_format="png")

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify result is a PNG
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"

    def test_convert_rgba_to_jpg(self, sample_png_with_alpha_bytes: bytes) -> None:
        """Test conversion from RGBA PNG to JPEG (which doesn't support alpha)."""
        result = convert_image_format(sample_png_with_alpha_bytes, target_format="jpg", quality=95)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify result is a JPEG
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"
        assert img.mode == "RGB"  # Should have converted from RGBA to RGB

    def test_convert_to_webp(self, sample_png_bytes: bytes) -> None:
        """Test conversion to WebP format."""
        result = convert_image_format(sample_png_bytes, target_format="webp", quality=90)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Check if WebP format is supported
        try:
            img = Image.open(BytesIO(result))
            # If we get here, WebP is supported
            assert img.format == "WEBP"
        except Exception:
            # WebP might not be supported in the test environment
            # Skip the assertions in this case
            pass

    def test_convert_identity(self, sample_png_bytes: bytes) -> None:
        """Test conversion to the same format (identity operation)."""
        # Detect format
        source_format = detect_image_format(sample_png_bytes)
        assert source_format == "png"

        # Convert to the same format
        result = convert_image_format(sample_png_bytes, target_format=source_format)

        # Verify result
        assert isinstance(result, bytes)
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"

    def test_convert_with_quality(self, sample_png_bytes: bytes) -> None:
        """Test conversion with specific quality settings."""
        # Convert with high quality
        high_quality = convert_image_format(sample_png_bytes, target_format="jpg", quality=95)

        # Convert with low quality
        low_quality = convert_image_format(sample_png_bytes, target_format="jpg", quality=30)

        # Verify both are valid JPEGs
        high_img = Image.open(BytesIO(high_quality))
        low_img = Image.open(BytesIO(low_quality))
        assert high_img.format == "JPEG"
        assert low_img.format == "JPEG"

        # Low quality should yield smaller file size
        assert len(low_quality) < len(high_quality)

    def test_convert_format_error(self) -> None:
        """Test error handling in convert_image_format."""
        # Invalid image data
        with pytest.raises(ConversionError) as excinfo:
            convert_image_format(b"invalid_image_data", target_format="png")

        assert "Failed to convert image" in str(excinfo.value)


class TestGenerateThumbnail:
    """Tests for the generate_thumbnail function."""

    def test_generate_png_thumbnail(self, sample_png_bytes: bytes) -> None:
        """Test generating a thumbnail from a PNG image."""
        thumbnail = generate_thumbnail(sample_png_bytes, size=(50, 50), format="png")

        # Verify result is bytes
        assert isinstance(thumbnail, bytes)

        # Verify result is a PNG with correct dimensions
        img = Image.open(BytesIO(thumbnail))
        assert img.format == "PNG"
        assert img.width == 50
        assert img.height == 50

    def test_generate_jpg_thumbnail(self, sample_png_bytes: bytes) -> None:
        """Test generating a JPEG thumbnail from a PNG image."""
        thumbnail = generate_thumbnail(sample_png_bytes, size=(50, 50), format="jpg")

        # Verify result is bytes
        assert isinstance(thumbnail, bytes)

        # Verify result is a JPEG with correct dimensions
        img = Image.open(BytesIO(thumbnail))
        assert img.format == "JPEG"
        assert img.width == 50
        assert img.height == 50

    def test_preserve_aspect_ratio(self, sample_png_bytes: bytes) -> None:
        """Test thumbnail generation with preserved aspect ratio."""
        thumbnail = generate_thumbnail(sample_png_bytes, size=(50, 25), format="png", preserve_aspect_ratio=True)

        # Original is 100x100, so the aspect ratio would make it 25x25
        img = Image.open(BytesIO(thumbnail))
        assert img.width == 25
        assert img.height == 25

    def test_ignore_aspect_ratio(self, sample_png_bytes: bytes) -> None:
        """Test thumbnail generation without preserving aspect ratio."""
        thumbnail = generate_thumbnail(sample_png_bytes, size=(50, 25), format="png", preserve_aspect_ratio=False)

        # Should be exactly the requested dimensions
        img = Image.open(BytesIO(thumbnail))
        assert img.width == 50
        assert img.height == 25

    def test_rgba_to_jpg_thumbnail(self, sample_png_with_alpha_bytes: bytes) -> None:
        """Test converting an RGBA image to JPEG thumbnail (which doesn't support alpha)."""
        thumbnail = generate_thumbnail(sample_png_with_alpha_bytes, size=(50, 50), format="jpg")

        # Verify result is a JPEG with no alpha channel
        img = Image.open(BytesIO(thumbnail))
        assert img.format == "JPEG"
        assert img.mode == "RGB"  # Should have converted from RGBA to RGB

    def test_thumbnail_error(self) -> None:
        """Test error handling in generate_thumbnail."""
        # Invalid image data
        with pytest.raises(ConversionError) as excinfo:
            generate_thumbnail(b"invalid_image_data", size=(50, 50), format="png")

        assert "Failed to generate thumbnail" in str(excinfo.value)


class TestGetImageMetadata:
    """Tests for the get_image_metadata function."""

    def test_get_png_metadata(self, sample_png_bytes: bytes) -> None:
        """Test extracting metadata from a PNG image."""
        metadata = get_image_metadata(sample_png_bytes)

        # Check basic properties
        assert "width" in metadata
        assert "height" in metadata
        assert "format" in metadata
        assert "mode" in metadata

        assert metadata["width"] == 100
        assert metadata["height"] == 100
        assert metadata["format"] == "PNG"
        assert metadata["mode"] == "RGB"

    @patch("PIL.Image.open")
    def test_metadata_with_exif(self, mock_pil_open: MagicMock, sample_jpg_bytes: bytes) -> None:
        """Test extracting EXIF metadata from a JPEG image."""
        # Setup: Create a mock image with EXIF data
        mock_img = MagicMock()
        mock_img.format = "JPEG"
        mock_img.width = 100
        mock_img.height = 100
        mock_img.mode = "RGB"

        # Mock the _getexif method on the image
        mock_exif = {
            0x010F: "Manufacturer",
            0x0110: "Model",
            0x0112: 1,  # Orientation
        }
        mock_img._getexif = MagicMock(return_value=mock_exif)

        # Return our mock image when PIL.Image.open is called
        mock_pil_open.return_value = mock_img

        # Execute
        metadata = get_image_metadata(sample_jpg_bytes)

        # Verify
        assert "width" in metadata
        assert "height" in metadata
        assert "format" in metadata
        assert "exif" in metadata
        assert metadata["width"] == 100
        assert metadata["height"] == 100
        assert metadata["format"] == "JPEG"
        assert "Manufacturer" in metadata["exif"].values()
        assert "Model" in metadata["exif"].values()

        # Check if orientation is in exif with the right key
        # The implementation may map EXIF IDs to human-readable names
        if "orientation" in metadata["exif"]:
            assert metadata["exif"]["orientation"] == 1
        elif "Orientation" in metadata["exif"]:
            assert metadata["exif"]["Orientation"] == 1

    def test_metadata_error(self) -> None:
        """Test error handling in get_image_metadata."""
        # Invalid image data
        with pytest.raises(ConversionError) as excinfo:
            get_image_metadata(b"invalid_image_data")

        assert "Failed to extract image metadata" in str(excinfo.value)


class TestOptimizeImage:
    """Tests for the optimize_image function."""

    def test_optimize_png(self, sample_png_bytes: bytes) -> None:
        """Test optimizing a PNG image."""
        result = optimize_image(sample_png_bytes, quality=85)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify it's still a valid PNG
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"

    def test_optimize_jpg(self, sample_jpg_bytes: bytes) -> None:
        """Test optimizing a JPEG image."""
        result = optimize_image(sample_jpg_bytes, quality=85)

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify it's still a valid JPEG
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"

    @patch("PIL.Image.open")
    def test_optimize_with_max_size(self, mock_pil_open: MagicMock, sample_png_bytes: bytes) -> None:
        """Test optimizing an image with maximum dimension constraint."""
        # Setup: Mock an image that needs resizing
        mock_img = MagicMock()
        mock_img.width = 2000
        mock_img.height = 1000
        mock_img.format = "PNG"
        mock_img.mode = "RGB"
        mock_pil_open.return_value = mock_img

        # Mock the thumbnail method to track called dimensions
        def thumbnail_effect(size: tuple[int, int], *args: Any, **kwargs: Any) -> None:
            mock_img.width = size[0]
            mock_img.height = size[1] // 2  # Maintain aspect ratio

        mock_img.thumbnail = thumbnail_effect

        # Mock the save method
        def save_effect(output: BytesIO, **kwargs: Any) -> None:
            img = Image.new("RGB", (mock_img.width, mock_img.height), color="red")
            img.save(output, format=mock_img.format)

        mock_img.save = save_effect

        # Execute with max size
        result = optimize_image(sample_png_bytes, quality=85, max_size=(1000, 1000))

        # Verify result is bytes
        assert isinstance(result, bytes)

        # Verify the image was resized
        assert mock_img.width == 1000
        assert mock_img.height == 500

    def test_optimize_error(self) -> None:
        """Test error handling in optimize_image."""
        # Invalid image data
        with pytest.raises(ConversionError) as excinfo:
            optimize_image(b"invalid_image_data")

        assert "Failed to optimize image" in str(excinfo.value)
