"""
Tests for the ImageService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import io
from datetime import datetime

from app.services.image.service import ImageService
from app.services.image.storage import ImageStorageService
from app.services.interfaces import ImageServiceInterface


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    client = MagicMock()
    return client


@pytest.fixture
def mock_jigsawstack_client():
    """Create a mock JigsawStack client for testing."""
    client = MagicMock()
    client.generate_image = AsyncMock()
    return client


@pytest.fixture
def mock_storage_service():
    """Create a mock storage service for testing."""
    service = MagicMock(spec=ImageStorageService)
    service.store_image = MagicMock()
    return service


@pytest.fixture
def image_service(mock_jigsawstack_client, mock_supabase_client, mock_storage_service):
    """Create an ImageService instance with mock dependencies."""
    return ImageService(
        jigsawstack_client=mock_jigsawstack_client,
        supabase_client=mock_supabase_client,
        storage_service=mock_storage_service
    )


@pytest.mark.asyncio
async def test_generate_and_store_image(image_service, mock_jigsawstack_client, mock_storage_service):
    """Test generating and storing an image."""
    # Setup mock responses
    mock_jigsawstack_client.generate_image.return_value = {
        "url": "https://example.com/test-image.png",
        "id": "test-generation-id"
    }
    
    mock_storage_service.store_image.return_value = "https://storage.example.com/images/test-image.png"
    
    # Mock httpx.AsyncClient for downloading the image
    with patch("httpx.AsyncClient") as mock_client:
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.content = b"test-image-data"
        
        # Make the async context manager return a client that returns our mock response
        mock_client_instance = MagicMock()
        mock_client_instance.get.return_value = mock_response
        mock_client().__aenter__.return_value = mock_client_instance
        
        # Call the method
        result = await image_service.generate_and_store_image(
            prompt="test prompt",
            concept_id="test-concept-id",
            width=512,
            height=512
        )
        
        # Verify
        assert result["url"] == "https://example.com/test-image.png"
        assert result["stored_url"] == "https://storage.example.com/images/test-image.png"
        mock_jigsawstack_client.generate_image.assert_called_once_with(
            prompt="test prompt",
            width=512,
            height=512
        )
        mock_storage_service.store_image.assert_called_once()
        # Check that the correct metadata was passed
        metadata_arg = mock_storage_service.store_image.call_args[1]["metadata"]
        assert metadata_arg["prompt"] == "test prompt"
        assert metadata_arg["generation_service"] == "jigsawstack"


@pytest.mark.asyncio
async def test_process_image_resize(image_service):
    """Test processing an image with resize operation."""
    # Create a test image
    test_image_data = b"test-image-data"
    
    # Mock the generate_thumbnail function
    with patch("app.services.image.service.generate_thumbnail") as mock_thumbnail:
        mock_thumbnail.return_value = b"resized-image-data"
        
        # Call the method
        operations = [{"type": "resize", "width": 200, "height": 200}]
        result = await image_service.process_image(test_image_data, operations)
        
        # Verify
        assert result == b"resized-image-data"
        mock_thumbnail.assert_called_once_with(
            test_image_data,
            size=(200, 200),
            preserve_aspect_ratio=True
        )


@pytest.mark.asyncio
async def test_process_image_convert(image_service):
    """Test processing an image with format conversion."""
    # Create a test image
    test_image_data = b"test-image-data"
    
    # Mock the convert_image_format function
    with patch("app.services.image.service.convert_image_format") as mock_convert:
        mock_convert.return_value = b"converted-image-data"
        
        # Call the method
        operations = [{"type": "convert", "format": "jpg", "quality": 90}]
        result = await image_service.process_image(test_image_data, operations)
        
        # Verify
        assert result == b"converted-image-data"
        mock_convert.assert_called_once_with(
            test_image_data,
            target_format="jpg",
            quality=90
        )


@pytest.mark.asyncio
async def test_process_image_optimize(image_service):
    """Test processing an image with optimization."""
    # Create a test image
    test_image_data = b"test-image-data"
    
    # Mock the optimize_image function
    with patch("app.services.image.service.optimize_image") as mock_optimize:
        mock_optimize.return_value = b"optimized-image-data"
        
        # Call the method
        operations = [{"type": "optimize", "quality": 85, "max_width": 1000, "max_height": 1000}]
        result = await image_service.process_image(test_image_data, operations)
        
        # Verify
        assert result == b"optimized-image-data"
        mock_optimize.assert_called_once_with(
            test_image_data,
            quality=85,
            max_size=(1000, 1000)
        ) 