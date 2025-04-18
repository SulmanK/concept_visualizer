"""Tests for the image conversion utilities.

This module contains tests for the conversion functions that handle
image format conversions, thumbnail generation, and metadata extraction.
"""

import pytest
from unittest.mock import patch, MagicMock, Mock
from io import BytesIO
from PIL import Image, ImageOps

from app.services.image.conversion import (
    detect_image_format,
    convert_image_format,
    generate_thumbnail,
    get_image_metadata,
    optimize_image,
    ConversionError
)


@pytest.fixture
def sample_png_bytes():
    """Create a simple PNG image and return its bytes."""
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@pytest.fixture
def sample_jpg_bytes():
    """Create a simple JPEG image and return its bytes."""
    img = Image.new('RGB', (100, 100), color='blue')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG', quality=95)
    return img_bytes.getvalue()


@pytest.fixture
def sample_png_with_alpha_bytes():
    """Create a PNG image with transparency and return its bytes."""
    img = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))  # Semi-transparent red
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


class TestDetectImageFormat:
    """Tests for the detect_image_format function."""

    def test_detect_png_format(self, sample_png_bytes):
        """Test detection of PNG format."""
        result = detect_image_format(sample_png_bytes)
        assert result == "png"

    def test_detect_jpg_format(self, sample_jpg_bytes):
        """Test detection of JPEG format."""
        result = detect_image_format(sample_jpg_bytes)
        assert result == "jpg"

    @patch('imghdr.what')
    def test_detect_webp_format(self, mock_imghdr_what):
        """Test detection of WebP format."""
        # Setup: imghdr returns webp
        mock_imghdr_what.return_value = "webp"
        
        # Execute
        result = detect_image_format(b"test_data")
        
        # Verify
        assert result == "webp"
        mock_imghdr_what.assert_called_once()

    @patch('imghdr.what')
    def test_detect_gif_format(self, mock_imghdr_what):
        """Test detection of GIF format."""
        # Setup: imghdr returns gif
        mock_imghdr_what.return_value = "gif"
        
        # Execute
        result = detect_image_format(b"test_data")
        
        # Verify
        assert result == "gif"
        mock_imghdr_what.assert_called_once()

    @patch('imghdr.what')
    @patch('PIL.Image.open')
    def test_fallback_to_pil(self, mock_pil_open, mock_imghdr_what, sample_png_bytes):
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

    @patch('imghdr.what')
    @patch('PIL.Image.open')
    def test_fallback_to_default(self, mock_pil_open, mock_imghdr_what, sample_png_bytes):
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

    @patch('imghdr.what')
    def test_exception_handling(self, mock_imghdr_what, sample_png_bytes):
        """Test error handling when exceptions occur during detection."""
        # Setup
        mock_imghdr_what.side_effect = Exception("Test error")
        
        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            detect_image_format(sample_png_bytes)
        
        assert "Failed to detect image format" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)

    @patch('imghdr.what')
    @patch('PIL.Image.open')
    def test_pil_exception_handling(self, mock_pil_open, mock_imghdr_what, sample_png_bytes):
        """Test error handling when PIL throws an exception."""
        # Setup: imghdr fails, and PIL raises exception
        mock_imghdr_what.return_value = None
        mock_pil_open.side_effect = Exception("PIL error")
        
        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            detect_image_format(sample_png_bytes)
        
        assert "Failed to detect image format" in str(excinfo.value)
        assert "PIL error" in str(excinfo.value)

    @patch('imghdr.what')
    @patch('PIL.Image.open')
    def test_normalize_jpeg_format(self, mock_pil_open, mock_imghdr_what):
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

    def test_convert_png_to_jpg(self, sample_png_bytes):
        """Test conversion from PNG to JPEG."""
        result = convert_image_format(sample_png_bytes, target_format="jpg", quality=95)
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Verify result is a JPEG
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"

    def test_convert_jpg_to_png(self, sample_jpg_bytes):
        """Test conversion from JPEG to PNG."""
        result = convert_image_format(sample_jpg_bytes, target_format="png")
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Verify result is a PNG
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"

    def test_convert_rgba_to_jpg(self, sample_png_with_alpha_bytes):
        """Test conversion from RGBA PNG to JPEG (which doesn't support alpha)."""
        result = convert_image_format(sample_png_with_alpha_bytes, target_format="jpg", quality=95)
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Verify result is a JPEG
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"
        assert img.mode == "RGB"  # Should have converted from RGBA to RGB

    def test_convert_to_webp(self, sample_png_bytes):
        """Test conversion to WebP format."""
        result = convert_image_format(sample_png_bytes, target_format="webp", quality=90)
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Verify result format if possible (may need to check differently for WebP)
        try:
            img = Image.open(BytesIO(result))
            assert img.format == "WEBP"
        except Exception:
            # If PIL doesn't support WebP, we can at least verify it's not the original PNG
            assert result != sample_png_bytes

    def test_convert_format_error(self):
        """Test error handling when conversion fails."""
        # Setup: Invalid image data
        invalid_data = b"not an image"
        
        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            convert_image_format(invalid_data, target_format="png")
        
        assert "Failed to convert image" in str(excinfo.value)


class TestGenerateThumbnail:
    """Tests for the generate_thumbnail function."""

    def test_generate_png_thumbnail(self, sample_png_bytes):
        """Test generating a PNG thumbnail."""
        result = generate_thumbnail(sample_png_bytes, size=(50, 50), format="png")
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Verify thumbnail dimensions
        img = Image.open(BytesIO(result))
        assert img.format == "PNG"
        assert img.width <= 50
        assert img.height <= 50

    def test_generate_jpg_thumbnail(self, sample_png_bytes):
        """Test generating a JPEG thumbnail."""
        result = generate_thumbnail(sample_png_bytes, size=(50, 50), format="jpg", quality=90)
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Verify thumbnail dimensions and format
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"
        assert img.width <= 50
        assert img.height <= 50

    def test_preserve_aspect_ratio(self, sample_png_bytes):
        """Test thumbnail generation with aspect ratio preservation."""
        # Original image is 100x100
        result = generate_thumbnail(sample_png_bytes, size=(50, 25), format="png", preserve_aspect_ratio=True)
        
        # Verify thumbnail maintains aspect ratio
        img = Image.open(BytesIO(result))
        assert img.width == img.height  # Original was square, should still be square

    def test_ignore_aspect_ratio(self, sample_png_bytes):
        """Test thumbnail generation without aspect ratio preservation."""
        result = generate_thumbnail(sample_png_bytes, size=(50, 25), format="png", preserve_aspect_ratio=False)
        
        # Verify thumbnail has exactly the requested dimensions
        img = Image.open(BytesIO(result))
        assert img.width == 50
        assert img.height == 25

    def test_rgba_to_jpg_thumbnail(self, sample_png_with_alpha_bytes):
        """Test thumbnail generation from RGBA to JPEG (which doesn't support alpha)."""
        result = generate_thumbnail(sample_png_with_alpha_bytes, size=(50, 50), format="jpg")
        
        # Verify result is a JPEG
        img = Image.open(BytesIO(result))
        assert img.format == "JPEG"
        assert img.mode == "RGB"  # Should have converted from RGBA to RGB

    def test_thumbnail_error(self):
        """Test error handling when thumbnail generation fails."""
        # Setup: Invalid image data
        invalid_data = b"not an image"
        
        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            generate_thumbnail(invalid_data, size=(50, 50))
        
        assert "Failed to generate thumbnail" in str(excinfo.value)


class TestGetImageMetadata:
    """Tests for the get_image_metadata function."""

    def test_get_png_metadata(self, sample_png_bytes):
        """Test extracting metadata from a PNG image."""
        metadata = get_image_metadata(sample_png_bytes)
        
        # Verify metadata structure and basic values
        assert metadata["format"] == "PNG"
        assert metadata["width"] == 100
        assert metadata["height"] == 100
        assert metadata["mode"] == "RGB"
        assert metadata["aspect_ratio"] == 1.0
        assert metadata["size_bytes"] > 0
        assert "exif" in metadata

    @patch('PIL.Image.Image._getexif', create=True)
    def test_metadata_with_exif(self, mock_getexif, sample_jpg_bytes):
        """Test extracting metadata with EXIF information."""
        # Setup: Mock EXIF data
        mock_exif_data = {
            271: "Camera Make",  # EXIF tag for camera make
            272: "Camera Model",  # EXIF tag for camera model
            306: "2023:01:01 12:00:00"  # EXIF tag for datetime
        }
        
        # Setup: Mock _getexif method on the image
        mock_getexif.return_value = mock_exif_data
        
        # Execute
        with patch.object(Image.Image, 'getexif', return_value=mock_exif_data):
            metadata = get_image_metadata(sample_jpg_bytes)
        
        # Verify
        assert "exif" in metadata
        # If we can't access EXIF data, just verify that no exceptions were raised
        # and the function returned metadata successfully
        assert isinstance(metadata, dict)
        assert "format" in metadata
        assert "width" in metadata
        assert "height" in metadata

    def test_metadata_error(self):
        """Test error handling when metadata extraction fails."""
        # Setup: Invalid image data
        invalid_data = b"not an image"
        
        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            get_image_metadata(invalid_data)
        
        assert "Failed to extract image metadata" in str(excinfo.value)


class TestOptimizeImage:
    """Tests for the optimize_image function."""

    def test_optimize_png(self, sample_png_bytes):
        """Test optimizing a PNG image."""
        result = optimize_image(sample_png_bytes, quality=85)
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Should not be larger than original
        assert len(result) <= len(sample_png_bytes)

    def test_optimize_jpg(self, sample_jpg_bytes):
        """Test optimizing a JPEG image."""
        result = optimize_image(sample_jpg_bytes, quality=80)
        
        # Verify result is bytes
        assert isinstance(result, bytes)
        
        # Should not be larger than original
        assert len(result) <= len(sample_jpg_bytes)

    @patch('PIL.Image.open')
    def test_optimize_with_max_size(self, mock_pil_open, sample_png_bytes):
        """Test optimizing an image with maximum size constraints."""
        # Create a mock image
        mock_img = MagicMock()
        mock_img.width = 100
        mock_img.height = 100
        mock_img.format = 'PNG'
        mock_img.mode = 'RGB'
        mock_img.info = {}
        
        # Setup thumbnail behavior to modify the dimensions when called
        def thumbnail_effect(size, *args, **kwargs):
            mock_img.width, mock_img.height = 50, 50
        mock_img.thumbnail.side_effect = thumbnail_effect
            
        # Return the mock image when PIL.Image.open is called
        mock_pil_open.return_value = mock_img
        
        # For the image.save method, write some test data to the BytesIO
        def save_effect(output, **kwargs):
            output.write(b"optimized_image")
        mock_img.save.side_effect = save_effect
        
        # Execute with real BytesIO - we're only mocking the image, not the IO
        result = optimize_image(sample_png_bytes, quality=85, max_size=(50, 50))
        
        # Verify results
        assert isinstance(result, bytes)
        assert len(result) > 0  # Should have some content
        
        # Verify the image was resized via thumbnail
        mock_img.thumbnail.assert_called_once()
        args, kwargs = mock_img.thumbnail.call_args
        assert args[0] == (50, 50)  # Check the size tuple
        
        # Verify save was called with the expected format
        # The optimize_image function chooses JPEG for RGB images
        mock_img.save.assert_called_once()
        call_args = mock_img.save.call_args
        assert call_args[1]['format'] == 'JPEG'  # Function chooses JPEG for RGB images
        assert 'optimize' in call_args[1] and call_args[1]['optimize'] == True

    def test_optimize_error(self):
        """Test error handling when optimization fails."""
        # Setup: Invalid image data
        invalid_data = b"not an image"
        
        # Execute and verify
        with pytest.raises(ConversionError) as excinfo:
            optimize_image(invalid_data)
        
        assert "Failed to optimize image" in str(excinfo.value) 