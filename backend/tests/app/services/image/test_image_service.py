"""Tests for the ImageService class.

This module tests the ImageService class which is responsible for
image processing and persistence operations.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.image.service import ImageError, ImageService


class TestImageService:
    """Tests for the ImageService class."""

    @pytest.fixture
    def mock_persistence_service(self) -> MagicMock:
        """Create a mock ImagePersistenceService."""
        mock = MagicMock()
        # Use AsyncMock for async methods
        mock.store_image = AsyncMock(return_value=("path/to/image.png", "https://example.com/image.png"))
        mock.get_image_async = AsyncMock(return_value=b"image_data_from_persistence")
        mock.get_image = AsyncMock(return_value=b"image_data_from_storage")
        return mock

    @pytest.fixture
    def mock_processing_service(self) -> AsyncMock:
        """Create a mock ImageProcessingService."""
        mock = AsyncMock()
        mock.process_image = AsyncMock(return_value=b"processed_image_data")
        mock.convert_to_format = MagicMock(return_value=b"converted_image_data")
        mock.generate_thumbnail = MagicMock(return_value=b"thumbnail_data")
        mock.extract_color_palette = AsyncMock(return_value=["#FFFFFF", "#000000", "#FF0000"])
        return mock

    @pytest.fixture
    def image_service(self, mock_persistence_service: MagicMock, mock_processing_service: AsyncMock) -> ImageService:
        """Create an ImageService with mocked dependencies."""
        service = ImageService(
            persistence_service=mock_persistence_service,
            processing_service=mock_processing_service,
        )

        # Initialize cache properties
        service._image_cache = {}
        service._cache_size_limit = 100

        return service

    @pytest.mark.asyncio
    async def test_process_image(self, image_service: ImageService, mock_processing_service: AsyncMock) -> None:
        """Test that process_image delegates to the processing service."""
        # Test data
        image_data = b"test_image_data"
        operations = [{"type": "resize", "width": 100, "height": 100}]

        # Call the method
        result = await image_service.process_image(image_data, operations)

        # Verify the processing service was called with correct arguments
        mock_processing_service.process_image.assert_called_once_with(image_data, operations)

        # Verify the result
        assert result == b"processed_image_data"

    def test_store_image(self, image_service: ImageService, mock_persistence_service: MagicMock) -> None:
        """Test that store_image delegates to the persistence service."""
        # Test data
        image_data = b"test_image_data"
        user_id = "user123"
        concept_id = "concept456"
        file_name = "test_image.png"
        metadata = {"test_key": "test_value"}
        is_palette = False

        # Call the method
        result = image_service.store_image(
            image_data=image_data,
            user_id=user_id,
            concept_id=concept_id,
            file_name=file_name,
            metadata=metadata,
            is_palette=is_palette,
        )

        # Verify the persistence service was called with correct arguments
        # The store_image method runs the persistence.store_image async method in an event loop
        assert mock_persistence_service.store_image.called
        call_args = mock_persistence_service.store_image.call_args[1]
        assert call_args["image_data"] == image_data
        assert call_args["user_id"] == user_id
        assert call_args["concept_id"] == concept_id
        assert call_args["file_name"] == file_name
        assert call_args["metadata"] == metadata
        assert call_args["is_palette"] == is_palette

        # Verify the result
        assert result == ("path/to/image.png", "https://example.com/image.png")

    def test_convert_to_format(self, image_service: ImageService, mock_processing_service: AsyncMock) -> None:
        """Test that convert_to_format delegates to the processing service."""
        # Test data
        image_data = b"test_image_data"
        target_format = "jpg"
        quality = 90

        # Call the method
        result = image_service.convert_to_format(image_data=image_data, target_format=target_format, quality=quality)

        # Verify the processing service was called with correct arguments
        mock_processing_service.convert_to_format.assert_called_once_with(image_data=image_data, target_format=target_format, quality=quality)

        # Verify the result
        assert result == b"converted_image_data"

    def test_generate_thumbnail(self, image_service: ImageService, mock_processing_service: AsyncMock) -> None:
        """Test that generate_thumbnail delegates to the processing service."""
        # Test data
        image_data = b"test_image_data"
        width = 100
        height = 100
        preserve_aspect_ratio = True
        format = "png"

        # Call the method
        result = image_service.generate_thumbnail(
            image_data=image_data,
            width=width,
            height=height,
            preserve_aspect_ratio=preserve_aspect_ratio,
            format=format,
        )

        # Verify the processing service was called with correct arguments
        mock_processing_service.generate_thumbnail.assert_called_once_with(
            image_data=image_data,
            width=width,
            height=height,
            format=format,
            preserve_aspect_ratio=preserve_aspect_ratio,
        )

        # Verify the result
        assert result == b"thumbnail_data"

    @pytest.mark.asyncio
    async def test_extract_color_palette(self, image_service: ImageService, mock_processing_service: AsyncMock) -> None:
        """Test that extract_color_palette delegates to the processing service."""
        # Test data
        image_data = b"test_image_data"
        num_colors = 3

        # Call the method
        result = await image_service.extract_color_palette(image_data=image_data, num_colors=num_colors)

        # Verify the processing service was called with correct arguments
        mock_processing_service.extract_color_palette.assert_called_once_with(image_data, num_colors)

        # Verify the result
        assert result == ["#FFFFFF", "#000000", "#FF0000"]

    @pytest.mark.asyncio
    async def test_create_palette_variations(self, image_service: ImageService, mock_processing_service: AsyncMock, mock_persistence_service: MagicMock) -> None:
        """Test create_palette_variations method with semaphore optimization."""
        # Test data
        base_image_data = b"test_image_data"
        palettes = [
            {
                "name": "Palette 1",
                "colors": ["#FFFFFF", "#000000", "#FF0000"],
                "description": "Test palette 1",
            },
            {
                "name": "Palette 2",
                "colors": ["#00FF00", "#0000FF", "#FFFF00"],
                "description": "Test palette 2",
            },
            {
                "name": "Palette with Error",
                "colors": [],  # Empty palette should be skipped
                "description": "Test palette with error",
            },
        ]
        user_id = "user123"
        blend_strength = 0.75

        # Setup mock persistence to return successful results for two palettes
        mock_persistence_service.store_image.side_effect = [
            ("path/to/palette1.png", "https://example.com/palette1.png"),
            ("path/to/palette2.png", "https://example.com/palette2.png"),
        ]

        # Mock PIL Image and the semaphore optimization components
        with patch("PIL.Image.open") as mock_pil_open, patch("app.core.config.settings") as mock_settings, patch("asyncio.Semaphore") as mock_semaphore_class, patch("asyncio.gather") as mock_gather:
            # Configure the mock settings
            mock_settings.PALETTE_PROCESSING_CONCURRENCY_LIMIT = 4
            mock_settings.PALETTE_PROCESSING_TIMEOUT_SECONDS = 120

            # Configure the mocked image
            mock_img = MagicMock()
            mock_img.mode = "RGB"
            mock_buffer = MagicMock()
            mock_buffer.getvalue.return_value = b"test_image_data"  # Match the expected input for the test
            mock_img.save.side_effect = lambda buffer, format: None
            mock_pil_open.return_value = mock_img

            # Mock the semaphore
            mock_semaphore = MagicMock()
            mock_semaphore_class.return_value = mock_semaphore

            # Mock asyncio.gather to return a coroutine that resolves to successful results for valid palettes
            async def mock_gather_coroutine(*tasks, return_exceptions=True):
                # Only return results for palettes with colors (skip empty palette)
                return [
                    {
                        "name": "Palette 1",
                        "colors": ["#FFFFFF", "#000000", "#FF0000"],
                        "description": "Test palette 1",
                        "image_path": "path/to/palette1.png",
                        "image_url": "https://example.com/palette1.png",
                    },
                    {
                        "name": "Palette 2",
                        "colors": ["#00FF00", "#0000FF", "#FFFF00"],
                        "description": "Test palette 2",
                        "image_path": "path/to/palette2.png",
                        "image_url": "https://example.com/palette2.png",
                    },
                    None,  # Empty palette result
                ]

            mock_gather.side_effect = mock_gather_coroutine

            # Mock BytesIO
            with patch("app.services.image.service.BytesIO") as mock_bytesio:
                mock_bytesio.return_value = mock_buffer

                # Call the method
                result = await image_service.create_palette_variations(
                    base_image_data=base_image_data,
                    palettes=palettes,
                    user_id=user_id,
                    blend_strength=blend_strength,
                )

        # Verify the result contains two processed palettes
        assert len(result) == 2

        # Verify semaphore was created with correct concurrency limit
        mock_semaphore_class.assert_called_once_with(3)  # min(4, 3) since we have 3 total palettes

        # Verify asyncio.gather was called for concurrent processing
        mock_gather.assert_called_once()

        # Verify the result contains the expected palette data
        palette_names = [palette["name"] for palette in result]
        assert "Palette 1" in palette_names
        assert "Palette 2" in palette_names
        assert "Palette with Error" not in palette_names  # Should have been skipped

        # Verify each result contains the expected fields
        for palette in result:
            assert "name" in palette
            assert "colors" in palette
            assert "description" in palette
            assert "image_path" in palette
            assert "image_url" in palette

    @pytest.mark.asyncio
    async def test_create_palette_variations_with_exceptions(self, image_service: ImageService, mock_processing_service: AsyncMock, mock_persistence_service: MagicMock) -> None:
        """Test create_palette_variations method with exceptions in processing."""
        # Test data
        base_image_data = b"test_image_data"
        palettes = [
            {
                "name": "Success Palette",
                "colors": ["#FFFFFF", "#000000", "#FF0000"],
                "description": "This palette should process successfully",
            },
            {
                "name": "Error Palette",
                "colors": ["#00FF00", "#0000FF"],
                "description": "This palette should fail during processing",
            },
        ]
        user_id = "user123"
        blend_strength = 0.75

        # Setup the processing service to succeed for first palette but fail for second
        mock_processing_service.process_image.side_effect = [
            b"processed_image_data",  # Success for first palette
            Exception("Processing error"),  # Failure for second palette
        ]

        # Setup mock persistence to return successful results for the first palette
        mock_persistence_service.store_image.return_value = ("path/to/palette.png", "https://example.com/palette.png")

        # Mock PIL Image and the semaphore optimization components
        with patch("PIL.Image.open") as mock_pil_open, patch("app.core.config.settings") as mock_settings, patch("asyncio.Semaphore") as mock_semaphore_class, patch("asyncio.gather") as mock_gather:
            # Configure the mock settings
            mock_settings.PALETTE_PROCESSING_CONCURRENCY_LIMIT = 4
            mock_settings.PALETTE_PROCESSING_TIMEOUT_SECONDS = 120

            # Configure the mocked image
            mock_img = MagicMock()
            mock_img.mode = "RGB"
            mock_buffer = MagicMock()
            mock_buffer.getvalue.return_value = b"test_image_data"
            mock_img.save.side_effect = lambda buffer, format: None
            mock_pil_open.return_value = mock_img

            # Mock the semaphore
            mock_semaphore = MagicMock()
            mock_semaphore_class.return_value = mock_semaphore

            # Mock asyncio.gather to return a coroutine with one success and one exception
            async def mock_gather_coroutine(*tasks, return_exceptions=True):
                return [
                    {
                        "name": "Success Palette",
                        "colors": ["#FFFFFF", "#000000", "#FF0000"],
                        "description": "This palette should process successfully",
                        "image_path": "path/to/palette.png",
                        "image_url": "https://example.com/palette.png",
                    },
                    Exception("Processing error"),  # Exception for second palette
                ]

            mock_gather.side_effect = mock_gather_coroutine

            # Mock BytesIO
            with patch("app.services.image.service.BytesIO") as mock_bytesio:
                mock_bytesio.return_value = mock_buffer

                # Call the method
                result = await image_service.create_palette_variations(
                    base_image_data=base_image_data,
                    palettes=palettes,
                    user_id=user_id,
                    blend_strength=blend_strength,
                )

        # Verify we received only the successful palette
        assert len(result) == 1
        assert result[0]["name"] == "Success Palette"

        # Verify semaphore was created with correct concurrency limit
        mock_semaphore_class.assert_called_once_with(2)  # min(4, 2) since we have 2 total palettes

        # Verify asyncio.gather was called for concurrent processing
        mock_gather.assert_called_once()

    @pytest.mark.asyncio
    async def test_apply_palette_to_image(self, image_service: ImageService, mock_processing_service: AsyncMock) -> None:
        """Test apply_palette_to_image method."""
        # Test data
        image_data = b"test_image_data"
        palette_colors = ["#FFFFFF", "#000000", "#FF0000"]
        blend_strength = 0.5

        # Mock PIL Image
        with patch("PIL.Image.open") as mock_pil_open:
            # Configure the mocked image
            mock_img = MagicMock()
            mock_img.mode = "RGB"
            mock_buffer = MagicMock()
            mock_buffer.getvalue.return_value = b"test_image_data"  # Match the expected input
            mock_img.save.side_effect = lambda buffer, format: None
            mock_pil_open.return_value = mock_img

            # Mock BytesIO
            with patch("app.services.image.service.BytesIO") as mock_bytesio:
                mock_bytesio.return_value = mock_buffer

                # Call the method
                result = await image_service.apply_palette_to_image(
                    image_data=image_data,
                    palette_colors=palette_colors,
                    blend_strength=blend_strength,
                )

        # Verify the processing service was called with correct operations for applying palettes
        mock_processing_service.process_image.assert_called_once_with(
            b"test_image_data",
            operations=[
                {
                    "type": "apply_palette",
                    "palette": ["#FFFFFF", "#000000", "#FF0000"],
                    "blend_strength": 0.5,
                }
            ],
        )

        # Verify the result
        assert result == b"processed_image_data"

    @pytest.mark.asyncio
    async def test_get_image_async_url(self, image_service: ImageService, mock_persistence_service: MagicMock) -> None:
        """Test get_image_async with a URL path."""
        # Test data
        image_url = "https://example.com/image.png"

        # Clear the cache to ensure we hit the correct path
        image_service._image_cache = {}

        # Mock httpx client response for URL downloads
        mock_response = MagicMock()
        mock_response.content = b"image_data_from_url"
        mock_response.raise_for_status = MagicMock()

        # Mock the httpx.AsyncClient context manager behavior
        mock_client = MagicMock()
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client.get = AsyncMock(return_value=mock_response)

        # Use a context manager to patch httpx.AsyncClient
        with patch("httpx.AsyncClient", return_value=mock_client):
            # Call the method
            result = await image_service.get_image_async(image_url)

        # Verify the mock client was used for the URL
        mock_client.get.assert_called_once_with(image_url)

        # Verify the response was checked for errors
        mock_response.raise_for_status.assert_called_once()

        # Verify the result
        assert result == b"image_data_from_url"

        # Test caching - the image should now be in the cache
        assert image_url in image_service._image_cache
        assert image_service._image_cache[image_url] == b"image_data_from_url"

    @pytest.mark.asyncio
    async def test_get_image_async_path(self, image_service: ImageService, mock_persistence_service: MagicMock) -> None:
        """Test get_image_async with a file path."""
        # Test data
        image_path = "user123/concept456/image.png"
        image_data = b"image_data_from_storage"

        # Clear the cache to ensure we hit the persistence service
        image_service._image_cache = {}

        # Setup mock persistence service to properly handle async calls
        mock_persistence_service.get_image = AsyncMock(return_value=image_data)

        # Call the method
        result = await image_service.get_image_async(image_path)

        # Verify the persistence service was called with correct arguments
        mock_persistence_service.get_image.assert_called_once_with(image_path)

        # Verify the result
        assert result == image_data

        # Test caching - the image should now be in the cache with the proper key
        cache_key = f"storage:{image_path}:False"
        assert cache_key in image_service._image_cache
        assert image_service._image_cache[cache_key] == image_data

    @pytest.mark.asyncio
    async def test_process_image_error(self, image_service: ImageService, mock_processing_service: AsyncMock) -> None:
        """Test error handling in process_image."""
        # Test data
        image_data = b"test_image_data"
        operations = [{"type": "resize", "width": 100, "height": 100}]

        # Make the processing service raise an exception
        mock_processing_service.process_image.side_effect = Exception("Processing error")

        # Call the method and expect an ImageError
        with pytest.raises(ImageError) as excinfo:
            await image_service.process_image(image_data, operations)

        # Verify the error message
        assert "Error processing image: Processing error" in str(excinfo.value)
