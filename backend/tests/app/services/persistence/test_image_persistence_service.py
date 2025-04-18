"""
Tests for ImagePersistenceService.

This module tests the ImagePersistenceService class which is responsible for
storing and retrieving images from Supabase storage.
"""

import io
from unittest.mock import AsyncMock, MagicMock, patch, call
import pytest
from typing import Dict, Any, Tuple, Optional
from datetime import datetime
from io import BytesIO
from PIL import Image

from fastapi import UploadFile

from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.core.exceptions import ImageNotFoundError, ImageStorageError
from app.core.supabase.image_storage import ImageStorage


class TestImagePersistenceService:
    """Tests for the ImagePersistenceService class."""

    @pytest.fixture
    def mock_image_storage(self):
        """Create a mock ImageStorage."""
        storage = MagicMock(spec=ImageStorage)
        storage.upload_image = MagicMock()
        storage.download_image = MagicMock(return_value=b"test_image_data")
        storage.create_signed_url = MagicMock(return_value="https://example.com/signed-url")
        storage.remove_image = MagicMock(return_value=True)
        return storage

    @pytest.fixture
    def mock_client(self):
        """Create a mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def service(self, mock_client, mock_image_storage):
        """Create an ImagePersistenceService with mocks."""
        service = ImagePersistenceService(mock_client)
        service.storage = mock_image_storage
        # Set bucket names from settings
        service.concept_bucket = "concept-images"
        service.palette_bucket = "palette-images"
        return service

    @pytest.fixture
    def sample_image_bytes(self):
        """Create sample image bytes for testing."""
        # Create a small test image
        img = Image.new('RGB', (100, 100), color='red')
        img_io = BytesIO()
        img.save(img_io, format='PNG')
        return img_io.getvalue()

    @pytest.fixture
    def sample_upload_file(self):
        """Create a sample UploadFile for testing."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.file = BytesIO(b"test_upload_file_content")
        mock_file.filename = "test_image.jpg"
        return mock_file

    def test_store_image_bytes(self, service, mock_image_storage, sample_image_bytes):
        """Test storing image from bytes."""
        # Track the actual path that gets created by the method
        actual_path = None
        original_upload_image = mock_image_storage.upload_image
        
        def capture_path(**kwargs):
            nonlocal actual_path
            actual_path = kwargs.get('path')
            return original_upload_image(**kwargs)
            
        mock_image_storage.upload_image.side_effect = capture_path
        
        # Call the method
        with patch('app.services.persistence.image_persistence_service.uuid.uuid4', return_value="test-uuid"):
            with patch('app.services.persistence.image_persistence_service.datetime') as mock_datetime:
                # Mock datetime.now() to return a fixed time
                mock_now = MagicMock()
                mock_now.strftime.return_value = "20230101000000"
                mock_datetime.now.return_value = mock_now

                # Create a mock Image
                with patch('app.services.persistence.image_persistence_service.Image') as mock_image:
                    mock_img = MagicMock()
                    mock_img.format = "PNG"
                    mock_image.open.return_value = mock_img

                    # Call the service method
                    path, url = service.store_image(
                        image_data=sample_image_bytes,
                        user_id="user-123",
                        concept_id="concept-456",
                        metadata={"key": "value"}
                    )

        # Verify the upload_image was called with the correct path captured by our spy
        assert mock_image_storage.upload_image.called
        assert actual_path is not None
        
        # Verify the path contains the expected components
        assert "user-123" in actual_path
        assert "concept-456" in actual_path
        assert "20230101000000" in actual_path
        assert "test-uuid" in actual_path
        assert actual_path.endswith(".png")
        
        # Verify signed URL was requested
        mock_image_storage.create_signed_url.assert_called_once_with(
            path=actual_path,
            bucket_name="concept-images", 
            expiry_seconds=259200
        )

        # Verify the returned URL
        assert url == "https://example.com/signed-url"

    def test_store_image_bytes_no_concept_id(self, service, mock_image_storage, sample_image_bytes):
        """Test storing image from bytes without concept ID."""
        # Call the method with UUID and datetime mocks
        with patch('app.services.persistence.image_persistence_service.uuid.uuid4', return_value="test-uuid"):
            with patch('app.services.persistence.image_persistence_service.datetime') as mock_datetime:
                # Mock datetime.now() to return a fixed time
                mock_now = MagicMock()
                mock_now.strftime.return_value = "20230101000000"
                mock_datetime.now.return_value = mock_now

                # Create a mock Image
                with patch('app.services.persistence.image_persistence_service.Image') as mock_image:
                    mock_img = MagicMock()
                    mock_img.format = "PNG"
                    mock_image.open.return_value = mock_img

                    # Call the service method
                    path, url = service.store_image(
                        image_data=sample_image_bytes,
                        user_id="user-123"
                    )

        # Verify the path is constructed correctly without concept ID
        assert path == "user-123/20230101000000_test-uuid.png"

    def test_store_image_bytes_is_palette(self, service, mock_image_storage, sample_image_bytes):
        """Test storing image as palette."""
        # Call the method with UUID and datetime mocks
        with patch('app.services.persistence.image_persistence_service.uuid.uuid4', return_value="test-uuid"):
            with patch('app.services.persistence.image_persistence_service.datetime') as mock_datetime:
                # Mock datetime.now() to return a fixed time
                mock_now = MagicMock()
                mock_now.strftime.return_value = "20230101000000"
                mock_datetime.now.return_value = mock_now

                # Create a mock Image
                with patch('app.services.persistence.image_persistence_service.Image') as mock_image:
                    mock_img = MagicMock()
                    mock_img.format = "PNG"
                    mock_image.open.return_value = mock_img

                    # Call the service method with is_palette=True
                    path, url = service.store_image(
                        image_data=sample_image_bytes,
                        user_id="user-123",
                        is_palette=True
                    )

        # Verify storage methods were called with is_palette=True
        args, kwargs = mock_image_storage.upload_image.call_args
        assert kwargs["is_palette"] is True

    def test_store_image_bytesio(self, service, mock_image_storage):
        """Test storing image from BytesIO."""
        # Create a BytesIO object
        bytes_io = BytesIO(b"test_bytesio_content")

        # Mock the necessary objects
        with patch('app.services.persistence.image_persistence_service.uuid.uuid4', return_value="test-uuid"):
            with patch('app.services.persistence.image_persistence_service.datetime') as mock_datetime:
                mock_now = MagicMock()
                mock_now.strftime.return_value = "20230101000000"
                mock_datetime.now.return_value = mock_now

                # Create a mock Image
                with patch('app.services.persistence.image_persistence_service.Image') as mock_image:
                    mock_img = MagicMock()
                    mock_img.format = "JPEG"
                    mock_image.open.return_value = mock_img

                    # Call the service method
                    path, url = service.store_image(
                        image_data=bytes_io,
                        user_id="user-123"
                    )

        # Verify storage methods were called with correct content
        args, kwargs = mock_image_storage.upload_image.call_args
        assert kwargs["content_type"] == "image/jpeg"  # Should detect JPEG format

    def test_store_image_upload_file(self, service, mock_image_storage, sample_upload_file):
        """Test storing image from UploadFile."""
        # Mock the necessary objects
        with patch('app.services.persistence.image_persistence_service.uuid.uuid4', return_value="test-uuid"):
            with patch('app.services.persistence.image_persistence_service.datetime') as mock_datetime:
                mock_now = MagicMock()
                mock_now.strftime.return_value = "20230101000000"
                mock_datetime.now.return_value = mock_now

                # Create a mock Image
                with patch('app.services.persistence.image_persistence_service.Image') as mock_image:
                    mock_img = MagicMock()
                    mock_img.format = "JPEG"
                    mock_image.open.return_value = mock_img

                    # Call the service method
                    path, url = service.store_image(
                        image_data=sample_upload_file,
                        user_id="user-123"
                    )

        # Verify content type from filename extension
        args, kwargs = mock_image_storage.upload_image.call_args
        assert kwargs["content_type"] == "image/jpeg"

    def test_store_image_with_filename(self, service, mock_image_storage, sample_image_bytes):
        """Test storing image with provided filename."""
        # Call the method
        path, url = service.store_image(
            image_data=sample_image_bytes,
            user_id="user-123",
            file_name="custom_name.png"
        )

        # Verify the path uses the custom filename
        assert path == "user-123/custom_name.png"

    def test_store_image_error(self, service, mock_image_storage, sample_image_bytes):
        """Test error handling when storing image."""
        # Setup ImageStorage.upload_image to raise an exception
        mock_image_storage.upload_image.side_effect = Exception("Upload failed")

        # Call the method and expect ImageStorageError
        with pytest.raises(ImageStorageError) as excinfo:
            service.store_image(
                image_data=sample_image_bytes,
                user_id="user-123"
            )

        # Verify error message
        assert "Failed to store image" in str(excinfo.value)
        assert "Upload failed" in str(excinfo.value)

    def test_get_image_success(self, service, mock_image_storage):
        """Test successful image retrieval."""
        # Call the method
        image_data = service.get_image("user-123/image.png")

        # Verify storage method was called
        mock_image_storage.download_image.assert_called_once_with(
            path="user-123/image.png",
            bucket_name="concept-images"
        )

        # Verify result
        assert image_data == b"test_image_data"

    def test_get_image_palette(self, service, mock_image_storage):
        """Test retrieving a palette image."""
        # Call the method with is_palette=True
        image_data = service.get_image("user-123/palette.png", is_palette=True)

        # Verify correct bucket was used
        mock_image_storage.download_image.assert_called_once_with(
            path="user-123/palette.png",
            bucket_name="palette-images"
        )

    def test_get_image_not_found(self, service, mock_image_storage):
        """Test image retrieval when image is not found."""
        # Setup ImageStorage.download_image to raise an exception with "404" in the message
        mock_image_storage.download_image.side_effect = Exception("404 Not Found")

        # Call the method and expect ImageNotFoundError
        with pytest.raises(ImageNotFoundError) as excinfo:
            service.get_image("user-123/nonexistent.png")

        # Verify error message
        assert "Image not found" in str(excinfo.value)

    def test_get_image_other_error(self, service, mock_image_storage):
        """Test image retrieval with other errors."""
        # Setup ImageStorage.download_image to raise a generic exception
        mock_image_storage.download_image.side_effect = Exception("Some error")

        # Call the method and expect ImageStorageError
        with pytest.raises(ImageStorageError) as excinfo:
            service.get_image("user-123/image.png")

        # Verify error message
        assert "Failed to get image" in str(excinfo.value)

    def test_delete_image_success(self, service, mock_image_storage):
        """Test successful image deletion."""
        # Call the method
        result = service.delete_image("user-123/image.png")

        # Verify storage method was called
        mock_image_storage.remove_image.assert_called_once_with(
            path="user-123/image.png",
            bucket_name="concept-images"
        )

        # Verify result
        assert result is True

    def test_delete_image_palette(self, service, mock_image_storage):
        """Test deleting a palette image."""
        # Call the method with is_palette=True
        service.delete_image("user-123/palette.png", is_palette=True)

        # Verify correct bucket was used
        mock_image_storage.remove_image.assert_called_once_with(
            path="user-123/palette.png",
            bucket_name="palette-images"
        )

    def test_get_signed_url(self, service, mock_image_storage):
        """Test getting a signed URL for an image."""
        # Call the method
        url = service.get_signed_url("user-123/image.png")

        # Verify storage method was called
        mock_image_storage.create_signed_url.assert_called_once_with(
            path="user-123/image.png",
            bucket_name="concept-images",
            expiry_seconds=259200  # Default expiry
        )

        # Verify result
        assert url == "https://example.com/signed-url"

    def test_get_signed_url_palette(self, service, mock_image_storage):
        """Test getting a signed URL for a palette image."""
        # Call the method with is_palette=True
        url = service.get_signed_url("user-123/palette.png", is_palette=True)

        # Verify correct bucket was used
        mock_image_storage.create_signed_url.assert_called_once_with(
            path="user-123/palette.png",
            bucket_name="palette-images",
            expiry_seconds=259200
        )

    def test_get_signed_url_custom_expiry(self, service, mock_image_storage):
        """Test getting a signed URL with custom expiry."""
        # Call the method with custom expiry
        url = service.get_signed_url("user-123/image.png", expiry_seconds=3600)

        # Verify correct expiry was used
        mock_image_storage.create_signed_url.assert_called_once_with(
            path="user-123/image.png",
            bucket_name="concept-images",
            expiry_seconds=3600
        )

    def test_get_image_url_with_http(self, service, mock_image_storage):
        """Test get_image_url with existing URL."""
        # Call the method with a URL that already has http/https
        url = service.get_image_url("https://example.com/image.png")

        # Verify no storage methods were called
        mock_image_storage.create_signed_url.assert_not_called()

        # Verify the URL is returned unchanged
        assert url == "https://example.com/image.png"

    def test_get_image_url_with_path(self, service, mock_image_storage):
        """Test get_image_url with path."""
        # Call the method with a path
        url = service.get_image_url("user-123/image.png")

        # Verify signed URL was created
        mock_image_storage.create_signed_url.assert_called_once()

        # Verify the signed URL is returned
        assert url == "https://example.com/signed-url"

    @pytest.mark.asyncio
    async def test_get_image_async_with_http(self, service):
        """Test get_image_async with URL."""
        # Mock httpx.AsyncClient
        mock_response = MagicMock()
        mock_response.content = b"downloaded_image_data"
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        # Patch httpx.AsyncClient
        with patch('app.services.persistence.image_persistence_service.httpx.AsyncClient', return_value=mock_client):
            # Call the method with a URL
            result = await service.get_image_async("https://example.com/image.png")

        # Verify httpx.AsyncClient.get was called
        mock_client.get.assert_called_once_with("https://example.com/image.png")

        # Verify the result
        assert result == b"downloaded_image_data"

    @pytest.mark.asyncio
    async def test_get_image_async_with_path(self, service, mock_image_storage):
        """Test get_image_async with path."""
        # Call the method with a path
        result = await service.get_image_async("user-123/image.png")

        # Verify get_image was called
        assert result == b"test_image_data"

    @pytest.mark.asyncio
    async def test_get_image_async_http_error(self, service):
        """Test get_image_async with HTTP error."""
        # Mock httpx.AsyncClient with error response
        mock_response = MagicMock()
        mock_response.content = b"error"
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        # Patch httpx.AsyncClient
        with patch('app.services.persistence.image_persistence_service.httpx.AsyncClient', return_value=mock_client):
            # Call the method and expect ImageNotFoundError
            with pytest.raises(ImageNotFoundError) as excinfo:
                await service.get_image_async("https://example.com/nonexistent.png")

        # Verify error message
        assert "Could not download image" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_image_async_empty_content(self, service):
        """Test get_image_async with empty content."""
        # Mock httpx.AsyncClient with empty response
        mock_response = MagicMock()
        mock_response.content = b""
        mock_response.status_code = 200

        mock_client = AsyncMock()
        mock_client.get.return_value = mock_response

        # Patch httpx.AsyncClient
        with patch('app.services.persistence.image_persistence_service.httpx.AsyncClient', return_value=mock_client):
            # Call the method and expect ImageNotFoundError
            with pytest.raises(ImageNotFoundError) as excinfo:
                await service.get_image_async("https://example.com/empty.png")

        # Verify error message
        assert "Empty content returned" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_image_async_connection_error(self, service):
        """Test get_image_async with connection error."""
        # Mock httpx.AsyncClient to raise ConnectionError
        mock_client = AsyncMock()
        mock_client.get.side_effect = Exception("Connection error")

        # Patch httpx.AsyncClient
        with patch('app.services.persistence.image_persistence_service.httpx.AsyncClient', return_value=mock_client):
            # Call the method and expect ImageNotFoundError
            with pytest.raises(ImageNotFoundError) as excinfo:
                await service.get_image_async("https://example.com/image.png")

        # Verify error message
        assert "Could not download image" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_get_image_async_file_protocol(self, service, mock_image_storage):
        """Test get_image_async with file:// protocol."""
        # Call the method with file:// URL
        result = await service.get_image_async("file:///path/to/image.png")

        # Verify get_image was called for the path part
        assert result == b"test_image_data"

    def test_list_images(self, service, mock_image_storage):
        """Test listing images."""
        # Mock the storage list method
        mock_image_storage.list_images = MagicMock(return_value=[
            {"name": "image1.png", "metadata": {"key": "value"}},
            {"name": "image2.png", "metadata": {"key": "value"}}
        ])

        # Call the method
        result = service.list_images(concept_id="concept-123")

        # Verify storage method was called
        mock_image_storage.list_images.assert_called_once_with(
            path="concept-123",
            bucket_name="concept-images"
        )

        # Verify result
        assert len(result) == 2
        assert result[0]["name"] == "image1.png"

    def test_list_images_no_concept(self, service, mock_image_storage):
        """Test listing images without concept ID."""
        # Mock the storage list method
        mock_image_storage.list_images = MagicMock(return_value=[])

        # Call the method without concept_id
        service.list_images()

        # Verify storage method was called with None path
        mock_image_storage.list_images.assert_called_once_with(
            path=None,
            bucket_name="concept-images"
        )

    @pytest.mark.asyncio
    async def test_authenticate_url(self, service):
        """Test authenticate_url method."""
        # Mock the get_signed_url method
        with patch.object(service, 'get_signed_url', return_value="https://example.com/authenticated-url"):
            # Call the method
            result = await service.authenticate_url("user-123/image.png", "user-123")

            # Verify get_signed_url was called
            service.get_signed_url.assert_called_once_with(
                path="user-123/image.png",
                is_palette=False
            )

            # Verify result
            assert result == "https://example.com/authenticated-url"

    def test_get_image_with_token(self, service, mock_image_storage):
        """Test get_image_with_token method."""
        # Call the method
        result = service.get_image_with_token("user-123/image.png", "test-token")

        # Verify storage method was called
        mock_image_storage.download_image_with_token.assert_called_once_with(
            path="user-123/image.png",
            token="test-token",
            bucket_name="concept-images"
        )

    def test_get_image_by_path(self, service, mock_image_storage):
        """Test get_image_by_path method."""
        # Call the method
        result = service.get_image_by_path("user-123/image.png")

        # Verify storage method was called
        mock_image_storage.download_image.assert_called_once_with(
            path="user-123/image.png",
            bucket_name="concept-images"
        )

        # Verify result
        assert result == b"test_image_data" 