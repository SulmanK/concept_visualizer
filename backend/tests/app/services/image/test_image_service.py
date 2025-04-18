"""
Tests for the ImageService class.

This module tests the ImageService class which is responsible for
image processing and persistence operations.
"""

import json
from io import BytesIO
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from typing import Dict, List, Any

from app.services.image.service import ImageService, ImageError


class TestImageService:
    """Tests for the ImageService class."""

    @pytest.fixture
    def mock_persistence_service(self):
        """Create a mock ImagePersistenceService."""
        mock = MagicMock()
        mock.store_image = MagicMock(return_value=("path/to/image.png", "https://example.com/image.png"))
        mock.get_image_async = AsyncMock(return_value=b'image_data_from_persistence')
        return mock

    @pytest.fixture
    def mock_processing_service(self):
        """Create a mock ImageProcessingService."""
        mock = AsyncMock()
        mock.process_image = AsyncMock(return_value=b'processed_image_data')
        mock.convert_to_format = MagicMock(return_value=b'converted_image_data')
        mock.generate_thumbnail = MagicMock(return_value=b'thumbnail_data')
        mock.extract_color_palette = AsyncMock(return_value=['#FFFFFF', '#000000', '#FF0000'])
        return mock

    @pytest.fixture
    def image_service(self, mock_persistence_service, mock_processing_service):
        """Create an ImageService with mocked dependencies."""
        service = ImageService(
            persistence_service=mock_persistence_service,
            processing_service=mock_processing_service
        )
        
        # Initialize cache properties
        service._image_cache = {}
        service._cache_size_limit = 100
        
        return service

    @pytest.mark.asyncio
    async def test_process_image(self, image_service, mock_processing_service):
        """Test that process_image delegates to the processing service."""
        # Test data
        image_data = b'test_image_data'
        operations = [{'type': 'resize', 'width': 100, 'height': 100}]
        
        # Call the method
        result = await image_service.process_image(image_data, operations)
        
        # Verify the processing service was called with correct arguments
        mock_processing_service.process_image.assert_called_once_with(image_data, operations)
        
        # Verify the result
        assert result == b'processed_image_data'

    def test_store_image(self, image_service, mock_persistence_service):
        """Test that store_image delegates to the persistence service."""
        # Test data
        image_data = b'test_image_data'
        user_id = 'user123'
        concept_id = 'concept456'
        file_name = 'test_image.png'
        metadata = {'test_key': 'test_value'}
        is_palette = False
        
        # Call the method
        result = image_service.store_image(
            image_data=image_data,
            user_id=user_id,
            concept_id=concept_id,
            file_name=file_name,
            metadata=metadata,
            is_palette=is_palette
        )
        
        # Verify the persistence service was called with correct arguments
        mock_persistence_service.store_image.assert_called_once_with(
            image_data=image_data,
            user_id=user_id,
            concept_id=concept_id,
            file_name=file_name,
            metadata=metadata,
            is_palette=is_palette
        )
        
        # Verify the result
        assert result == ("path/to/image.png", "https://example.com/image.png")

    def test_convert_to_format(self, image_service, mock_processing_service):
        """Test that convert_to_format delegates to the processing service."""
        # Test data
        image_data = b'test_image_data'
        target_format = 'jpg'
        quality = 90
        
        # Call the method
        result = image_service.convert_to_format(
            image_data=image_data,
            target_format=target_format,
            quality=quality
        )
        
        # Verify the processing service was called with correct arguments
        mock_processing_service.convert_to_format.assert_called_once_with(
            image_data=image_data,
            target_format=target_format,
            quality=quality
        )
        
        # Verify the result
        assert result == b'converted_image_data'

    def test_generate_thumbnail(self, image_service, mock_processing_service):
        """Test that generate_thumbnail delegates to the processing service."""
        # Test data
        image_data = b'test_image_data'
        width = 100
        height = 100
        preserve_aspect_ratio = True
        format = 'png'
        
        # Call the method
        result = image_service.generate_thumbnail(
            image_data=image_data,
            width=width,
            height=height,
            preserve_aspect_ratio=preserve_aspect_ratio,
            format=format
        )
        
        # Verify the processing service was called with correct arguments
        mock_processing_service.generate_thumbnail.assert_called_once_with(
            image_data=image_data,
            width=width,
            height=height,
            format=format,
            preserve_aspect_ratio=preserve_aspect_ratio
        )
        
        # Verify the result
        assert result == b'thumbnail_data'

    @pytest.mark.asyncio
    async def test_extract_color_palette(self, image_service, mock_processing_service):
        """Test that extract_color_palette delegates to the processing service."""
        # Test data
        image_data = b'test_image_data'
        num_colors = 3
        
        # Call the method
        result = await image_service.extract_color_palette(
            image_data=image_data,
            num_colors=num_colors
        )
        
        # Verify the processing service was called with correct arguments
        mock_processing_service.extract_color_palette.assert_called_once_with(
            image_data, num_colors
        )
        
        # Verify the result
        assert result == ['#FFFFFF', '#000000', '#FF0000']

    @pytest.mark.asyncio
    async def test_create_palette_variations(self, image_service, mock_processing_service, mock_persistence_service):
        """Test create_palette_variations method."""
        # Test data
        base_image_data = b'test_image_data'
        palettes = [
            {
                'name': 'Palette 1',
                'colors': ['#FFFFFF', '#000000', '#FF0000'],
                'description': 'Test palette 1'
            },
            {
                'name': 'Palette 2',
                'colors': ['#00FF00', '#0000FF', '#FFFF00'],
                'description': 'Test palette 2'
            }
        ]
        user_id = 'user123'
        blend_strength = 0.75
        
        # Mock PIL Image
        with patch('PIL.Image.open') as mock_pil_open:
            # Configure the mocked image
            mock_img = MagicMock()
            mock_img.mode = 'RGB'
            mock_buffer = MagicMock()
            mock_buffer.getvalue.return_value = b'validated_image_data'
            mock_img.save.side_effect = lambda buffer, format: None
            mock_pil_open.return_value = mock_img
            
            # Mock BytesIO
            with patch('app.services.image.service.BytesIO') as mock_bytesio:
                mock_bytesio.return_value = mock_buffer
                
                # Call the method
                result = await image_service.create_palette_variations(
                    base_image_data=base_image_data,
                    palettes=palettes,
                    user_id=user_id,
                    blend_strength=blend_strength
                )
        
        # Verify the processing service was called twice (once for each palette)
        assert mock_processing_service.process_image.call_count == 2
        
        # Verify the processing service was called with correct operations for applying palettes
        mock_processing_service.process_image.assert_any_call(
            b'validated_image_data',
            operations=[{
                'type': 'apply_palette',
                'palette': ['#FFFFFF', '#000000', '#FF0000'],
                'blend_strength': 0.75
            }]
        )
        mock_processing_service.process_image.assert_any_call(
            b'validated_image_data',
            operations=[{
                'type': 'apply_palette',
                'palette': ['#00FF00', '#0000FF', '#FFFF00'],
                'blend_strength': 0.75
            }]
        )
        
        # Verify the persistence service was called twice
        assert mock_persistence_service.store_image.call_count == 2
        
        # Verify the metadata passed to store_image
        for call_args in mock_persistence_service.store_image.call_args_list:
            kwargs = call_args[1]
            assert kwargs['user_id'] == user_id
            assert kwargs['is_palette'] is True
            assert 'metadata' in kwargs
            
            # One of the two palette names should be in the metadata
            palette_name = kwargs['metadata']['palette_name']
            assert palette_name in ['Palette 1', 'Palette 2']
            
            # The colors should be JSON-encoded
            if palette_name == 'Palette 1':
                assert json.loads(kwargs['metadata']['colors']) == ['#FFFFFF', '#000000', '#FF0000']
            else:
                assert json.loads(kwargs['metadata']['colors']) == ['#00FF00', '#0000FF', '#FFFF00']
        
        # Verify the result structure
        assert len(result) == 2
        
        # Each result should have the correct fields
        for item in result:
            assert 'name' in item
            assert 'colors' in item
            assert 'description' in item
            assert 'image_path' in item
            assert 'image_url' in item
            
            # The name should be one of the original palette names
            assert item['name'] in ['Palette 1', 'Palette 2']
            
            # The image URL should be the mocked URL
            assert item['image_url'] == 'https://example.com/image.png'

    @pytest.mark.asyncio
    async def test_apply_palette_to_image(self, image_service, mock_processing_service):
        """Test that apply_palette_to_image delegates to the processing service."""
        # Test data
        image_data = b'test_image_data'
        palette_colors = ['#FFFFFF', '#000000', '#FF0000']
        blend_strength = 0.8
        
        # Call the method
        result = await image_service.apply_palette_to_image(
            image_data=image_data,
            palette_colors=palette_colors,
            blend_strength=blend_strength
        )
        
        # Verify the processing service was called with correct arguments
        mock_processing_service.process_image.assert_called_once_with(
            image_data,
            operations=[{
                'type': 'apply_palette',
                'palette': palette_colors,
                'blend_strength': blend_strength
            }]
        )
        
        # Verify the result
        assert result == b'processed_image_data'

    @pytest.mark.asyncio
    async def test_get_image_async_url(self, image_service, mock_persistence_service):
        """Test get_image_async with a URL, including caching behavior."""
        # Test data
        image_url = 'https://example.com/image.png'
        
        # Mock httpx.AsyncClient
        with patch('httpx.AsyncClient') as mock_client_class:
            # Configure the mock response
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.content = b'image_data_from_url'
            mock_client.get.return_value = mock_response
            
            # First call should fetch from URL
            result1 = await image_service.get_image_async(image_url)
            
            # Verify httpx.AsyncClient.get was called with the URL
            mock_client.get.assert_called_once_with(image_url)
            
            # Verify the result is the content from the response
            assert result1 == b'image_data_from_url'
            
            # Second call should use cache, reset mock to verify no new call is made
            mock_client.reset_mock()
            
            # Make second call to same URL
            result2 = await image_service.get_image_async(image_url)
            
            # Verify client was not called again (cache hit)
            mock_client.get.assert_not_called()
            
            # Verify the result is the same
            assert result2 == b'image_data_from_url'

    @pytest.mark.asyncio
    async def test_get_image_async_path(self, image_service, mock_persistence_service):
        """Test get_image_async with a path (not URL), including caching behavior."""
        # Test data
        image_path = 'path/to/image.png'
        
        # First call should use persistence service
        result1 = await image_service.get_image_async(image_path)
        
        # Verify the persistence service was called with the path
        mock_persistence_service.get_image_async.assert_called_once_with(image_path)
        
        # Verify the result is from the persistence service
        assert result1 == b'image_data_from_persistence'
        
        # Reset mock to verify no new call is made for second request
        mock_persistence_service.get_image_async.reset_mock()
        
        # Second call should use cache
        result2 = await image_service.get_image_async(image_path)
        
        # Verify persistence service was not called again (cache hit)
        mock_persistence_service.get_image_async.assert_not_called()
        
        # Verify the result is the same
        assert result2 == b'image_data_from_persistence'

    @pytest.mark.asyncio
    async def test_process_image_error(self, image_service, mock_processing_service):
        """Test that process_image properly handles errors."""
        # Make the processing service raise an exception
        mock_processing_service.process_image.side_effect = Exception('Processing error')
        
        # Call the method and expect an ImageError
        with pytest.raises(ImageError) as excinfo:
            await image_service.process_image(b'test_image_data', [{'type': 'resize'}])
        
        # Verify the error message
        assert 'Error processing image: Processing error' in str(excinfo.value) 