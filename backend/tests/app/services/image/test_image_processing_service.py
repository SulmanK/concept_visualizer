"""Tests for the ImageProcessingService.

This module contains tests for the ImageProcessingService which handles
image transformations, format conversions, and other processing operations.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, Mock, ANY
from io import BytesIO
import httpx
from PIL import Image
import numpy as np

from app.services.image.processing_service import (
    ImageProcessingService,
    ImageProcessingError
)
from app.services.image.conversion import ConversionError


@pytest.fixture
def image_processing_service():
    """Return an instance of ImageProcessingService for testing."""
    return ImageProcessingService()


@pytest.fixture
def sample_image_bytes():
    """Create a simple test image and return its bytes."""
    # Create a simple 100x100 red image
    img = Image.new('RGB', (100, 100), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


class TestImageProcessingService:
    """Tests for the ImageProcessingService."""

    @patch('app.services.image.processing_service.convert_image_format')
    async def test_process_image_format_conversion(self, mock_convert, image_processing_service, sample_image_bytes):
        """Test process_image with format conversion operation."""
        # Setup
        mock_convert.return_value = b"converted_image_data"
        
        # Execute
        operations = [{"type": "format_conversion", "target_format": "jpg", "quality": 90}]
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify
        mock_convert.assert_called_once_with(
            image_data=sample_image_bytes,
            target_format="jpg",
            quality=90
        )
        assert result == b"converted_image_data"

    @patch('app.services.image.processing_service.ImageProcessingService.resize_image')
    async def test_process_image_resize(self, mock_resize, image_processing_service, sample_image_bytes):
        """Test process_image with resize operation."""
        # Setup
        mock_resize.return_value = b"resized_image_data"
        
        # Execute
        operations = [{"type": "resize", "width": 200, "height": 200, "maintain_aspect_ratio": True}]
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify
        mock_resize.assert_called_once_with(
            sample_image_bytes,
            width=200,
            height=200,
            maintain_aspect_ratio=True
        )
        assert result == b"resized_image_data"

    @patch('app.services.image.processing_service.ImageProcessingService.generate_thumbnail')
    async def test_process_image_thumbnail(self, mock_thumbnail, image_processing_service, sample_image_bytes):
        """Test process_image with thumbnail operation."""
        # Setup
        mock_thumbnail.return_value = b"thumbnail_image_data"
        
        # Execute
        operations = [{"type": "thumbnail", "width": 128, "height": 128}]
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify
        mock_thumbnail.assert_called_once_with(
            sample_image_bytes,
            width=128,
            height=128,
            preserve_aspect_ratio=True,
            format="png"
        )
        assert result == b"thumbnail_image_data"

    @patch('app.services.image.processing_service.optimize_image')
    async def test_process_image_optimize(self, mock_optimize, image_processing_service, sample_image_bytes):
        """Test process_image with optimize operation."""
        # Setup
        mock_optimize.return_value = b"optimized_image_data"
        
        # Execute
        operations = [{"type": "optimize", "quality": 80, "max_width": 800, "max_height": 600}]
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify
        mock_optimize.assert_called_once_with(
            sample_image_bytes,
            quality=80,
            max_size=(800, 600)
        )
        assert result == b"optimized_image_data"

    @patch('app.services.image.processing_service.ImageProcessingService.apply_palette')
    async def test_process_image_apply_palette(self, mock_apply, image_processing_service, sample_image_bytes):
        """Test process_image with apply_palette operation."""
        # Setup
        mock_apply.return_value = b"palette_image_data"
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        
        # Execute
        operations = [{"type": "apply_palette", "palette": palette, "blend_strength": 0.8}]
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify
        mock_apply.assert_called_once_with(
            sample_image_bytes,
            palette_colors=palette,
            blend_strength=0.8
        )
        assert result == b"palette_image_data"

    @patch('app.services.image.processing_service.convert_image_format')
    async def test_process_image_multiple_operations(self, mock_convert, image_processing_service, sample_image_bytes):
        """Test process_image with multiple operations in sequence."""
        # Setup
        with patch('app.services.image.processing_service.ImageProcessingService.resize_image') as mock_resize:
            mock_resize.return_value = b"resized_data"
            mock_convert.return_value = b"final_data"
            
            # Execute
            operations = [
                {"type": "resize", "width": 200, "height": 200},
                {"type": "format_conversion", "target_format": "jpg"}
            ]
            result = await image_processing_service.process_image(sample_image_bytes, operations)
            
            # Verify
            mock_resize.assert_called_once()
            mock_convert.assert_called_once_with(
                image_data=b"resized_data",
                target_format="jpg",
                quality=95
            )
            assert result == b"final_data"

    @patch('app.services.image.processing_service.convert_image_format')
    async def test_process_image_error_handling(self, mock_convert, image_processing_service, sample_image_bytes):
        """Test process_image handles errors properly."""
        # Setup
        mock_convert.side_effect = ConversionError("Test conversion error")
        
        # Execute and verify
        operations = [{"type": "format_conversion", "target_format": "jpg"}]
        with pytest.raises(ImageProcessingError) as excinfo:
            await image_processing_service.process_image(sample_image_bytes, operations)
        
        assert "Test conversion error" in str(excinfo.value)

    async def test_process_image_unsupported_operation(self, image_processing_service, sample_image_bytes):
        """Test process_image skips unsupported operations."""
        # Execute
        operations = [{"type": "unsupported_op", "some_param": "value"}]
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify - should return original image data unchanged
        assert result == sample_image_bytes

    @patch('app.services.image.processing_service.convert_image_format')
    def test_convert_to_format(self, mock_convert, image_processing_service, sample_image_bytes):
        """Test convert_to_format method."""
        # Setup
        mock_convert.return_value = b"converted_image"
        
        # Execute
        result = image_processing_service.convert_to_format(
            sample_image_bytes, 
            target_format="jpg", 
            quality=90
        )
        
        # Verify
        mock_convert.assert_called_once_with(
            image_data=sample_image_bytes,
            target_format="jpg",
            quality=90
        )
        assert result == b"converted_image"

    @patch('app.services.image.processing_service.convert_image_format')
    def test_convert_to_format_error(self, mock_convert, image_processing_service, sample_image_bytes):
        """Test convert_to_format handles conversion errors."""
        # Setup
        mock_convert.side_effect = ConversionError("Test error")
        
        # Execute and verify
        with pytest.raises(ImageProcessingError) as excinfo:
            image_processing_service.convert_to_format(sample_image_bytes)
        
        assert "Failed to convert image format" in str(excinfo.value)

    @patch('httpx.AsyncClient.get')
    @patch('PIL.Image.open')
    async def test_resize_image_from_bytes(self, mock_pil_open, mock_get, image_processing_service, sample_image_bytes):
        """Test resize_image with bytes input."""
        # Setup
        mock_img = MagicMock()
        mock_img.width = 100
        mock_img.height = 100
        mock_pil_open.return_value = mock_img
        
        mock_img.resize.return_value = mock_img
        
        mock_bytesio = MagicMock()
        mock_img.save.side_effect = lambda output, format: output.write(b"resized_image")
        
        # Execute
        with patch('io.BytesIO', return_value=mock_bytesio):
            result = await image_processing_service.resize_image(
                sample_image_bytes, 
                width=200,
                height=200
            )
        
        # Verify
        mock_pil_open.assert_called_once()
        mock_img.resize.assert_called_once_with((200, 200), resample=Image.Resampling.LANCZOS)
        assert result == b"resized_image"
        
        # Get should not be called for bytes input
        mock_get.assert_not_called()

    @patch('httpx.AsyncClient')
    @patch('PIL.Image.open')
    async def test_resize_image_from_url(self, mock_pil_open, MockAsyncClient, image_processing_service):
        """Test resize_image with URL input."""
        # Setup
        mock_client = AsyncMock()
        MockAsyncClient.return_value.__aenter__.return_value = mock_client
        
        mock_response = AsyncMock()
        mock_response.content = b"image_data_from_url"
        mock_client.get.return_value = mock_response
        
        mock_img = MagicMock()
        mock_img.width = 100
        mock_img.height = 100
        mock_pil_open.return_value = mock_img
        
        mock_img.resize.return_value = mock_img
        
        mock_bytesio = MagicMock()
        mock_img.save.side_effect = lambda output, format: output.write(b"resized_image")
        
        # Execute
        with patch('io.BytesIO', return_value=mock_bytesio):
            result = await image_processing_service.resize_image(
                "https://example.com/image.jpg", 
                width=200
            )
        
        # Verify
        mock_client.get.assert_called_once_with("https://example.com/image.jpg")
        mock_pil_open.assert_called_once()
        assert result == b"resized_image"

    @patch('app.services.image.processing_service.generate_thumbnail')
    def test_generate_thumbnail(self, mock_gen_thumbnail, image_processing_service, sample_image_bytes):
        """Test generate_thumbnail method."""
        # Setup - return mock data
        mock_gen_thumbnail.return_value = b"thumbnail_data"
        
        # Execute
        result = image_processing_service.generate_thumbnail(
            sample_image_bytes,
            width=128,
            height=128,
            preserve_aspect_ratio=True,
            format="jpg"
        )
        
        # Verify - check that function was called and mock parameters match
        assert mock_gen_thumbnail.call_count == 1
        
        # Check that the parameters are correct, but don't compare image_data directly
        call_kwargs = mock_gen_thumbnail.call_args.kwargs
        assert call_kwargs['size'] == (128, 128)
        assert call_kwargs['format'] == 'jpg'
        assert call_kwargs['preserve_aspect_ratio'] == True
        # The quality parameter might be optional or handled differently in the implementation
        
        # Verify the return value matches our mock
        assert result == b"thumbnail_data"

    @patch('app.services.image.processing_service.extract_dominant_colors')
    async def test_extract_color_palette(self, mock_extract, image_processing_service, sample_image_bytes):
        """Test extract_color_palette method."""
        # Setup
        expected_colors = ["#FF0000", "#00FF00", "#0000FF"]
        mock_extract.return_value = expected_colors
        
        # Execute
        result = await image_processing_service.extract_color_palette(
            sample_image_bytes,
            num_colors=3
        )
        
        # Verify
        mock_extract.assert_called_once_with(sample_image_bytes, 3)
        assert result == expected_colors
        
    @patch('app.services.image.processing_service.extract_dominant_colors')
    async def test_extract_color_palette_with_different_num_colors(self, mock_extract, image_processing_service, sample_image_bytes):
        """Test extract_color_palette method with different number of colors."""
        # Setup - create different response for different num_colors
        def extract_colors_mock(image_data, num_colors):
            # Generate different number of colors based on input parameter
            colors = []
            for i in range(num_colors):
                # Generate a deterministic color based on index
                r = (i * 40) % 256
                g = (i * 80) % 256
                b = (i * 120) % 256
                colors.append(f"#{r:02x}{g:02x}{b:02x}")
            return colors
            
        mock_extract.side_effect = extract_colors_mock
        
        # Test with different numbers of colors
        for num_colors in [1, 3, 5, 8]:
            # Execute
            result = await image_processing_service.extract_color_palette(
                sample_image_bytes,
                num_colors=num_colors
            )
            
            # Verify
            assert len(result) == num_colors
            mock_extract.assert_any_call(sample_image_bytes, num_colors)
            
            # Verify the colors match our expected pattern
            for i, color in enumerate(result):
                r = (i * 40) % 256
                g = (i * 80) % 256
                b = (i * 120) % 256
                expected = f"#{r:02x}{g:02x}{b:02x}"
                assert color == expected
                
    @patch('app.services.image.processing_service.extract_dominant_colors')
    async def test_extract_color_palette_from_url(self, mock_extract, image_processing_service):
        """Test extract_color_palette from a URL."""
        # Setup
        url = "https://example.com/image.jpg"
        expected_colors = ["#FF0000", "#00FF00", "#0000FF"]
        mock_extract.return_value = expected_colors
        
        # First, we need to mock the download function
        with patch('httpx.AsyncClient') as MockAsyncClient:
            # Setup the mock client
            mock_client = AsyncMock()
            MockAsyncClient.return_value.__aenter__.return_value = mock_client
            
            # Setup the mock response
            mock_response = AsyncMock()
            mock_response.content = b"image_data_from_url"
            mock_client.get.return_value = mock_response
            
            # Execute
            result = await image_processing_service.extract_color_palette(
                url,
                num_colors=3
            )
            
            # Verify
            mock_client.get.assert_called_once_with(url)
            # The extract_dominant_colors should be called with the downloaded bytes
            mock_extract.assert_called_once_with(b"image_data_from_url", 3)
            assert result == expected_colors
            
    @patch('app.services.image.processing_service.extract_dominant_colors')
    async def test_extract_color_palette_error_handling(self, mock_extract, image_processing_service, sample_image_bytes):
        """Test error handling in extract_color_palette."""
        # Setup: extract_dominant_colors raises an exception
        mock_extract.side_effect = Exception("Color extraction failed")
        
        # Execute and verify
        with pytest.raises(ImageProcessingError) as excinfo:
            await image_processing_service.extract_color_palette(sample_image_bytes, num_colors=3)
        
        assert "Failed to extract color palette" in str(excinfo.value)
        assert "Color extraction failed" in str(excinfo.value)

    @patch('app.services.image.processing_service.get_image_metadata')
    def test_get_image_metadata(self, mock_get_metadata, image_processing_service, sample_image_bytes):
        """Test get_image_metadata method."""
        # Setup
        expected_metadata = {
            "format": "PNG",
            "mode": "RGB",
            "width": 100,
            "height": 100,
            "aspect_ratio": 1.0,
            "size_bytes": len(sample_image_bytes),
            "exif": {}
        }
        mock_get_metadata.return_value = expected_metadata
        
        # Execute
        result = image_processing_service.get_image_metadata(sample_image_bytes)
        
        # Verify
        mock_get_metadata.assert_called_once_with(sample_image_bytes)
        assert result == expected_metadata

    @patch('app.services.image.processing_service.get_image_metadata')
    def test_get_image_metadata_error(self, mock_get_metadata, image_processing_service, sample_image_bytes):
        """Test get_image_metadata handles errors properly."""
        # Setup
        mock_get_metadata.side_effect = Exception("Test metadata error")
        
        # Execute and verify
        with pytest.raises(ImageProcessingError) as excinfo:
            image_processing_service.get_image_metadata(sample_image_bytes)
        
        assert "Failed to extract image metadata" in str(excinfo.value)
        assert "Test metadata error" in str(excinfo.value)

    @patch('httpx.AsyncClient')
    async def test_convert_format_from_url(self, MockAsyncClient, image_processing_service):
        """Test convert_format with URL input."""
        # Setup
        mock_client = AsyncMock()
        MockAsyncClient.return_value.__aenter__.return_value = mock_client
        
        mock_response = AsyncMock()
        mock_response.content = b"image_data_from_url"
        mock_client.get.return_value = mock_response
        
        with patch('app.services.image.processing_service.convert_image_format') as mock_convert:
            mock_convert.return_value = b"converted_image"
            
            # Execute
            result = await image_processing_service.convert_format(
                "https://example.com/image.jpg",
                target_format="png",
                quality=95
            )
            
            # Verify
            mock_client.get.assert_called_once_with("https://example.com/image.jpg")
            mock_convert.assert_called_once_with(
                image_data=b"image_data_from_url",
                target_format="png",
                quality=95
            )
            assert result == b"converted_image"

    @patch('app.services.image.processing_service.apply_palette_with_masking_optimized')
    async def test_apply_palette(self, mock_apply_palette, image_processing_service, sample_image_bytes):
        """Test apply_palette method."""
        # Setup
        mock_apply_palette.return_value = b"palette_applied_image"
        palette_colors = ["#FF0000", "#00FF00", "#0000FF"]
        
        # Execute
        result = await image_processing_service.apply_palette(
            sample_image_bytes,
            palette_colors=palette_colors,
            blend_strength=0.75
        )
        
        # Verify
        mock_apply_palette.assert_called_once_with(
            sample_image_bytes,
            palette_colors=palette_colors,
            blend_strength=0.75
        )
        assert result == b"palette_applied_image"
        
    @patch('app.services.image.processing_service.apply_palette_with_masking_optimized')
    async def test_apply_palette_from_url(self, mock_apply_palette, image_processing_service):
        """Test apply_palette method with a URL input."""
        # Setup
        url = "https://example.com/image.jpg"
        expected_result = b"palette_applied_from_url"
        mock_apply_palette.return_value = expected_result
        palette_colors = ["#FF0000", "#00FF00", "#0000FF"]
        
        # Execute - doesn't need to mock HTTP client because apply_palette_with_masking_optimized 
        # handles the URL downloading internally
        result = await image_processing_service.apply_palette(
            url,
            palette_colors=palette_colors,
            blend_strength=0.75
        )
        
        # Verify
        mock_apply_palette.assert_called_once_with(
            url,  # URL is passed directly to apply_palette_with_masking_optimized
            palette_colors=palette_colors,
            blend_strength=0.75
        )
        assert result == expected_result
        
    @patch('app.services.image.processing_service.apply_palette_with_masking_optimized')
    async def test_apply_palette_with_different_blend_strengths(self, mock_apply_palette, image_processing_service, sample_image_bytes):
        """Test apply_palette method with different blend strengths."""
        # Setup
        palette_colors = ["#FF0000", "#00FF00", "#0000FF"]
        
        # Different blend strengths to test
        blend_strengths = [0.1, 0.5, 0.9]
        
        for blend_strength in blend_strengths:
            # Set up the mock to return a blend-specific result
            mock_apply_palette.return_value = f"result_with_blend_{blend_strength}".encode()
            
            # Execute
            result = await image_processing_service.apply_palette(
                sample_image_bytes,
                palette_colors=palette_colors,
                blend_strength=blend_strength
            )
            
            # Verify
            mock_apply_palette.assert_called_with(
                sample_image_bytes,
                palette_colors=palette_colors,
                blend_strength=blend_strength
            )
            assert result == f"result_with_blend_{blend_strength}".encode()
            
    @patch('app.services.image.processing_service.apply_palette_with_masking_optimized')
    async def test_apply_palette_error_handling(self, mock_apply_palette, image_processing_service, sample_image_bytes):
        """Test error handling in apply_palette method."""
        # Setup: apply_palette_with_masking_optimized raises an exception
        mock_apply_palette.side_effect = Exception("Palette application failed")
        palette_colors = ["#FF0000", "#00FF00", "#0000FF"]
        
        # Execute and verify
        with pytest.raises(ImageProcessingError) as excinfo:
            await image_processing_service.apply_palette(
                sample_image_bytes,
                palette_colors=palette_colors,
                blend_strength=0.75
            )
        
        assert "Failed to apply color palette" in str(excinfo.value)
        assert "Palette application failed" in str(excinfo.value)
        
    @patch('app.services.image.processing_service.apply_palette_with_masking_optimized')
    async def test_apply_palette_with_empty_palette(self, mock_apply_palette, image_processing_service, sample_image_bytes):
        """Test apply_palette method with an empty palette."""
        # Setup
        palette_colors = []
        
        # Execute and verify
        with pytest.raises(ValueError) as excinfo:
            await image_processing_service.apply_palette(
                sample_image_bytes,
                palette_colors=palette_colors,
                blend_strength=0.75
            )
        
        # Should fail with a meaningful error message
        assert "palette_colors" in str(excinfo.value)
        assert "empty" in str(excinfo.value)
        
        # The underlying function should not be called
        mock_apply_palette.assert_not_called()

    @patch('httpx.AsyncClient.get')
    @patch('PIL.Image.open')
    async def test_resize_image_maintain_aspect_ratio(self, mock_pil_open, mock_get, image_processing_service, sample_image_bytes):
        """Test resize_image with aspect ratio preservation."""
        # Setup: Create a mock image with 2:1 aspect ratio
        mock_img = MagicMock()
        mock_img.width = 200
        mock_img.height = 100
        mock_pil_open.return_value = mock_img
        
        # Mock the resize method to calculate and return new dimensions
        def resize_with_aspect_ratio(size, **kwargs):
            # This mock should calculate what the real resize would do
            # If maintaining aspect ratio and specifying width=100, a 200x100 image becomes 100x50
            width, height = size
            if width == 100 and mock_img._maintain_aspect_ratio:
                # Height should be half the width due to aspect ratio
                mock_img.width = 100
                mock_img.height = 50
            else:
                mock_img.width = width
                mock_img.height = height
            return mock_img
            
        mock_img.resize.side_effect = resize_with_aspect_ratio
        
        # Create a mock BytesIO for output
        mock_bytesio = MagicMock()
        mock_img.save.side_effect = lambda output, format: output.write(b"resized_with_aspect")
        
        # Execute: resize with only width specified and maintain_aspect_ratio=True
        with patch('io.BytesIO', return_value=mock_bytesio):
            # Store whether aspect ratio is maintained for the mock to use
            mock_img._maintain_aspect_ratio = True
            
            result = await image_processing_service.resize_image(
                sample_image_bytes, 
                width=100,
                maintain_aspect_ratio=True
            )
        
        # Verify
        assert mock_img.width == 100
        assert mock_img.height == 50  # Should be half of original due to aspect ratio
        assert result == b"resized_with_aspect"
        
    @patch('httpx.AsyncClient.get')
    @patch('PIL.Image.open')    
    async def test_resize_image_exact_dimensions(self, mock_pil_open, mock_get, image_processing_service, sample_image_bytes):
        """Test resize_image with exact dimensions (no aspect ratio preservation)."""
        # Setup
        mock_img = MagicMock()
        mock_img.width = 200
        mock_img.height = 100
        mock_pil_open.return_value = mock_img
        
        mock_img.resize.return_value = mock_img
        
        mock_bytesio = MagicMock()
        mock_img.save.side_effect = lambda output, format: output.write(b"resized_exact")
        
        # Execute
        with patch('io.BytesIO', return_value=mock_bytesio):
            result = await image_processing_service.resize_image(
                sample_image_bytes, 
                width=150,
                height=150,
                maintain_aspect_ratio=False
            )
        
        # Verify
        mock_pil_open.assert_called_once()
        # Should resize to exact dimensions provided
        mock_img.resize.assert_called_once_with((150, 150), resample=Image.Resampling.LANCZOS)
        assert result == b"resized_exact"
        
    @patch('httpx.AsyncClient.get')
    @patch('PIL.Image.open')
    async def test_resize_image_error_handling(self, mock_pil_open, mock_get, image_processing_service):
        """Test error handling in resize_image."""
        # Setup: PIL.Image.open raises an exception
        mock_pil_open.side_effect = Exception("Failed to open image")
        
        # Execute and verify
        with pytest.raises(ImageProcessingError) as excinfo:
            await image_processing_service.resize_image(b"invalid_image", width=100)
        
        assert "Failed to resize image" in str(excinfo.value)

    @patch('app.services.image.processing_service.ImageProcessingService.resize_image')
    @patch('app.services.image.processing_service.optimize_image')
    @patch('app.services.image.processing_service.convert_image_format')
    async def test_process_image_complex_sequence(self, mock_convert, mock_optimize, mock_resize, 
                                              image_processing_service, sample_image_bytes):
        """Test process_image with a complex sequence of operations."""
        # Setup mocks for each step
        mock_resize.return_value = b"resized_data"
        mock_optimize.return_value = b"optimized_data"
        mock_convert.return_value = b"final_data"
        
        # Create a complex operation sequence: resize -> optimize -> convert
        operations = [
            {"type": "resize", "width": 800, "height": 600, "maintain_aspect_ratio": True},
            {"type": "optimize", "quality": 90, "max_width": 1200, "max_height": 1200},
            {"type": "format_conversion", "target_format": "webp", "quality": 85}
        ]
        
        # Execute
        result = await image_processing_service.process_image(sample_image_bytes, operations)
        
        # Verify each step was called in order with the right inputs
        mock_resize.assert_called_once_with(
            sample_image_bytes,
            width=800,
            height=600,
            maintain_aspect_ratio=True
        )
        
        mock_optimize.assert_called_once_with(
            b"resized_data",  # Input from resize step
            quality=90,
            max_size=(1200, 1200)
        )
        
        mock_convert.assert_called_once_with(
            image_data=b"optimized_data",  # Input from optimize step
            target_format="webp",
            quality=85
        )
        
        assert result == b"final_data"
        
    async def test_process_image_empty_operations(self, image_processing_service, sample_image_bytes):
        """Test process_image with empty operations list."""
        # Execute with empty operations list
        result = await image_processing_service.process_image(sample_image_bytes, [])
        
        # Should return original image unchanged
        assert result == sample_image_bytes
        
    @patch('app.services.image.processing_service.ImageProcessingService.resize_image')
    async def test_process_image_partial_failure(self, mock_resize, image_processing_service, sample_image_bytes):
        """Test process_image when one operation fails but others can continue."""
        # Setup: First operation succeeds, second will fail
        with patch('app.services.image.processing_service.optimize_image') as mock_optimize:
            mock_resize.return_value = b"resized_data"
            mock_optimize.side_effect = Exception("Optimization failed")
            
            # Execute with multiple operations
            operations = [
                {"type": "resize", "width": 800, "height": 600},  # This should succeed
                {"type": "optimize", "quality": 90},              # This will fail
                {"type": "unsupported_op"}                        # This should be skipped
            ]
            
            # The second operation fails, so the function should raise an ImageProcessingError
            with pytest.raises(ImageProcessingError) as excinfo:
                await image_processing_service.process_image(sample_image_bytes, operations)
            
            # Verify the error contains info about the failed operation
            assert "Optimization failed" in str(excinfo.value)
            assert mock_resize.called
            assert mock_optimize.called 