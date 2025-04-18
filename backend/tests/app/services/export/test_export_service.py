"""
Tests for the ExportService class.

This module tests the ExportService class which is responsible for
exporting images in different formats and sizes.
"""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch, mock_open, call
import pytest
from io import BytesIO
from PIL import Image

from app.services.export.service import ExportService, ExportError


class TestExportService:
    """Tests for the ExportService class."""

    @pytest.fixture
    def mock_image_service(self):
        """Create a mock ImageService."""
        mock = AsyncMock()
        mock.get_image_async = AsyncMock(return_value=b'image_data')
        return mock

    @pytest.fixture
    def mock_processing_service(self):
        """Create a mock ImageProcessingService."""
        mock = AsyncMock()
        mock.process_image = AsyncMock(return_value=b'processed_image_data')
        mock.convert_to_format = MagicMock(return_value=b'converted_image_data')
        return mock

    @pytest.fixture
    def export_service(self, mock_image_service, mock_processing_service):
        """Create an ExportService with mocked dependencies."""
        return ExportService(
            image_service=mock_image_service,
            processing_service=mock_processing_service
        )

    @pytest.mark.asyncio
    async def test_process_export_png(self, export_service, mock_processing_service):
        """Test exporting an image to PNG with a specific size."""
        # Test data
        image_data = b'test_image_data'
        original_filename = 'test_image.jpg'
        target_format = 'png'
        target_size = 'medium'  # 1000x1000 as defined in the service

        # Call the method
        result = await export_service.process_export(
            image_data=image_data,
            original_filename=original_filename,
            target_format=target_format,
            target_size=target_size,
            svg_params=None
        )

        # Check that the processing service was called with the correct operations
        mock_processing_service.process_image.assert_called_once()
        operations_arg = mock_processing_service.process_image.call_args[0][1]
        assert operations_arg[0]['type'] == 'resize'
        assert operations_arg[0]['width'] == 1000
        assert operations_arg[0]['height'] == 1000
        assert operations_arg[0]['preserve_aspect_ratio'] is True

        # Check that convert_to_format was called with the correct arguments
        mock_processing_service.convert_to_format.assert_called_once_with(
            b'processed_image_data',
            target_format='png',
            quality=95
        )

        # Verify the return values
        processed_bytes, filename, content_type = result
        assert processed_bytes == b'converted_image_data'
        assert filename == 'test_image.png'
        assert content_type == 'image/png'

    @pytest.mark.asyncio
    async def test_process_export_jpg(self, export_service, mock_processing_service):
        """Test exporting an image to JPG with a specific size."""
        # Test data
        image_data = b'test_image_data'
        original_filename = 'test_image.png'
        target_format = 'jpg'
        target_size = 'small'  # 500x500 as defined in the service

        # Call the method
        result = await export_service.process_export(
            image_data=image_data,
            original_filename=original_filename,
            target_format=target_format,
            target_size=target_size,
            svg_params=None
        )

        # Check that the processing service was called with the correct operations
        mock_processing_service.process_image.assert_called_once()
        operations_arg = mock_processing_service.process_image.call_args[0][1]
        assert operations_arg[0]['type'] == 'resize'
        assert operations_arg[0]['width'] == 500
        assert operations_arg[0]['height'] == 500

        # Check that convert_to_format was called with the correct arguments
        mock_processing_service.convert_to_format.assert_called_once_with(
            b'processed_image_data',
            target_format='jpeg',  # JPG is converted to JPEG internally
            quality=90
        )

        # Verify the return values
        processed_bytes, filename, content_type = result
        assert processed_bytes == b'converted_image_data'
        assert filename == 'test_image.jpg'
        assert content_type == 'image/jpeg'

    @pytest.mark.asyncio
    async def test_process_export_original_size(self, export_service, mock_processing_service):
        """Test exporting an image with original size."""
        # Test data
        image_data = b'test_image_data'
        original_filename = 'test_image.png'
        target_format = 'png'
        target_size = 'original'

        # Call the method
        result = await export_service.process_export(
            image_data=image_data,
            original_filename=original_filename,
            target_format=target_format,
            target_size=target_size,
            svg_params=None
        )

        # For original size, the image should not be processed with resize
        mock_processing_service.process_image.assert_not_called()

        # Only format conversion should be applied
        mock_processing_service.convert_to_format.assert_called_once_with(
            b'test_image_data',
            target_format='png',
            quality=95
        )

        # Verify the return values
        processed_bytes, filename, content_type = result
        assert processed_bytes == b'converted_image_data'
        assert filename == 'test_image.png'
        assert content_type == 'image/png'

    @pytest.mark.asyncio
    @patch('PIL.Image.open')
    @patch('tempfile.NamedTemporaryFile')
    @patch('os.unlink')
    async def test_process_export_svg(self, mock_unlink, mock_tempfile, mock_image_open, export_service):
        """Test exporting an image to SVG format."""
        # Test data
        image_data = b'test_image_data'
        original_filename = 'test_image.png'
        target_format = 'svg'
        target_size = 'original'
        svg_params = {'mode': 'color', 'max_colors': 16}

        # Setup mocks
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        # Mock the temp files
        input_temp = MagicMock()
        input_temp.name = '/tmp/input.png'
        output_temp = MagicMock()
        output_temp.name = '/tmp/output.svg'
        
        # Mock the context managers
        mock_tempfile.side_effect = [
            MagicMock(__enter__=MagicMock(return_value=input_temp)),
            MagicMock(__enter__=MagicMock(return_value=output_temp))
        ]
        
        # Mock the _convert_to_svg method
        with patch.object(export_service, '_convert_to_svg', AsyncMock()) as mock_convert_svg:
            # Set return value for _convert_to_svg
            svg_content = b'<svg>test svg content</svg>'
            mock_convert_svg.return_value = (svg_content, 'test_image.svg', 'image/svg+xml')
            
            # Call the method
            result = await export_service.process_export(
                image_data=image_data,
                original_filename=original_filename,
                target_format=target_format,
                target_size=target_size,
                svg_params=svg_params
            )
            
            # Verify _convert_to_svg was called
            mock_convert_svg.assert_called_once()
            # Check the arguments were correct
            args, kwargs = mock_convert_svg.call_args
            assert args[0] == image_data
            assert args[1] == original_filename
            assert args[2] == svg_params

        # Verify the return values
        processed_bytes, filename, content_type = result
        assert processed_bytes == svg_content
        assert filename == 'test_image.svg'
        assert content_type == 'image/svg+xml'

    @pytest.mark.asyncio
    async def test_process_export_error(self, export_service, mock_processing_service):
        """Test error handling in process_export."""
        # Test data
        image_data = b'test_image_data'
        original_filename = 'test_image.png'
        target_format = 'png'
        target_size = 'medium'

        # Make the processing service raise an exception
        mock_processing_service.process_image.side_effect = Exception("Processing error")

        # Call the method and expect an ExportError
        with pytest.raises(ExportError) as excinfo:
            await export_service.process_export(
                image_data=image_data,
                original_filename=original_filename,
                target_format=target_format,
                target_size=target_size,
                svg_params=None
            )

        # Verify the error message - using 'in' for partial matching
        assert "Processing error" in str(excinfo.value) 