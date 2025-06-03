"""Tests for ImageStorage in the Supabase module."""

import io
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from fastapi import UploadFile

from app.core.config import settings
from app.core.supabase.image_storage import ImageStorage


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock the Supabase client."""
    client = MagicMock()
    client.client = MagicMock()
    client.url = "https://example.supabase.co"
    client.key = "fake-api-key"
    return client


@pytest.fixture
def image_storage(mock_client: MagicMock) -> ImageStorage:
    """Create an ImageStorage instance with mocked client."""
    with patch("app.core.supabase.image_storage.get_masked_value"):
        with patch("app.core.config.settings") as mock_settings:
            mock_settings.STORAGE_BUCKET_CONCEPT = "concepts"
            mock_settings.STORAGE_BUCKET_PALETTE = "palettes"
            return ImageStorage(mock_client)


@pytest.fixture
def mock_settings() -> Generator[MagicMock, None, None]:
    """Mock the app settings."""
    with patch("app.core.config.settings") as mock:
        mock.SUPABASE_URL = "https://example.supabase.co"
        mock.SUPABASE_SERVICE_ROLE = "fake-service-role-key"
        mock.STORAGE_BUCKET_CONCEPT = "concepts"
        mock.STORAGE_BUCKET_PALETTE = "palettes"
        yield mock


class TestUploadImageFromUrl:
    """Tests for the upload_image_from_url method."""

    @pytest.mark.asyncio
    async def test_upload_image_from_url_success(self, image_storage: ImageStorage, mock_client: MagicMock) -> None:
        """Test successful upload of image from URL."""
        # Arrange
        image_url = "https://example.com/image.png"
        bucket = "concepts"
        user_id = "user-123"

        # Mock the requests.get call
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.content = b"fake-image-data"
            mock_get.return_value = mock_response

            # Mock PIL.Image.open
            with patch("app.core.supabase.image_storage.Image.open") as mock_open_image:
                mock_img = MagicMock()
                mock_img.save.side_effect = lambda buf, format: None
                mock_open_image.return_value = mock_img

                # Mock uuid generation
                with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
                    mock_uuid.return_value = "generated-uuid"

                    # Mock the upload method
                    with patch.object(image_storage, "upload_image", return_value=True):
                        # Act
                        result = await image_storage.upload_image_from_url(image_url, bucket, user_id)

                        # Assert
                        assert result == f"{user_id}/generated-uuid.png"
                        mock_get.assert_called_once_with(image_url, timeout=10)
                        mock_client.client.storage.from_.assert_called_once_with(bucket)
                        mock_client.client.storage.from_.return_value.upload.assert_called_once()
                        # Check the upload path
                        upload_path = mock_client.client.storage.from_.return_value.upload.call_args[1]["path"]
                        assert upload_path == f"{user_id}/generated-uuid.png"
                        # Check content-type
                        file_options = mock_client.client.storage.from_.return_value.upload.call_args[1]["file_options"]
                        assert file_options["content-type"] == "image/png"

    @pytest.mark.asyncio
    async def test_upload_image_from_url_request_error(self, image_storage: ImageStorage) -> None:
        """Test handling of request error in upload_image_from_url."""
        # Arrange
        image_url = "https://example.com/image.png"
        bucket = "concepts"
        user_id = "user-123"

        # Mock the requests.get call to raise an exception
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Request failed")

            # Act
            result = await image_storage.upload_image_from_url(image_url, bucket, user_id)

            # Assert
            assert result is None
            mock_get.assert_called_once_with(image_url, timeout=10)


class TestGetImageUrl:
    """Tests for the get_image_url method."""

    def test_get_image_url_success(self, image_storage: ImageStorage) -> None:
        """Test successful generation of signed URL."""
        # Arrange
        path = "user-123/image.png"
        bucket = "concepts"
        expected_url = "https://example.com/signed-url"

        # Mock the create_signed_url method
        with patch.object(
            image_storage,
            "create_signed_url",
            return_value=expected_url,
        ) as mock_get_signed:
            # Act
            result = image_storage.get_image_url(path, bucket)

            # Assert
            assert result == expected_url
            mock_get_signed.assert_called_once_with(path=path, bucket_name=bucket, expires_in=settings.SIGNED_URL_EXPIRY_SECONDS)

    def test_get_image_url_empty_path(self, image_storage: ImageStorage) -> None:
        """Test get_image_url with empty path."""
        # Arrange
        path = ""
        bucket = "concepts"

        # Act
        result = image_storage.get_image_url(path, bucket)

        # Assert
        assert result is None


class TestApplyColorPalette:
    """Tests for the apply_color_palette method."""

    @pytest.mark.asyncio
    async def test_apply_color_palette_success(self, image_storage: ImageStorage) -> None:
        """Test successful color palette application."""
        # Arrange
        image_path = "user-123/image.png"
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        user_id = "user-123"

        # Mock uuid generation
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value = "palette-uuid"

            # Act
            result = await image_storage.apply_color_palette(image_path, palette, user_id)

            # Assert
            assert result == f"{user_id}/palette-uuid_palette.png"

    @pytest.mark.asyncio
    async def test_apply_color_palette_error(self, image_storage: ImageStorage) -> None:
        """Test error handling in apply_color_palette."""
        # Arrange
        image_path = "user-123/image.png"
        palette = ["#FF0000", "#00FF00", "#0000FF"]
        user_id = "user-123"

        # Mock uuid generation to raise exception
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.side_effect = Exception("UUID generation failed")

            # Act
            result = await image_storage.apply_color_palette(image_path, palette, user_id)

            # Assert
            assert result is None


class TestDeleteAllStorageObjects:
    """Tests for the delete_all_storage_objects method."""

    def test_delete_all_storage_objects_for_user(self, image_storage: ImageStorage, mock_client: MagicMock) -> None:
        """Test deleting all storage objects for a specific user."""
        # Arrange
        user_id = "user-123"
        bucket = "concepts"  # Testing with a single bucket is sufficient

        # Setup mock responses with files that will be returned from the list operation
        files_to_delete = [
            {"name": "file1.png"},
            {"name": "file2.png"},
        ]

        # Mock the implementation's behavior - it uses files with a dict structure that has 'name' key
        bucket_storage_mock = MagicMock()
        bucket_storage_mock.list.return_value = files_to_delete
        bucket_storage_mock.remove.return_value = None

        # Set up nested mocks to match how the implementation accesses the client
        storage_mock = mock_client.client.storage
        storage_mock.from_.return_value = bucket_storage_mock

        # Act
        result = image_storage.delete_all_storage_objects(bucket, user_id)

        # Assert
        assert result is True
        storage_mock.from_.assert_called_with(bucket)
        bucket_storage_mock.list.assert_called_once_with(f"{user_id}")
        assert bucket_storage_mock.remove.call_count == 2
        bucket_storage_mock.remove.assert_any_call([f"{user_id}/file1.png"])
        bucket_storage_mock.remove.assert_any_call([f"{user_id}/file2.png"])

    def test_delete_all_storage_objects_all_users(self, image_storage: ImageStorage, mock_client: MagicMock) -> None:
        """Test deleting all storage objects (all users)."""
        # Arrange
        bucket = "concepts"  # Testing with a single bucket is sufficient

        # Setup mock responses with files that will be returned from the list operation
        files_to_delete = [
            {"name": "user-1/file1.png"},
            {"name": "user-2/file2.png"},
            {"name": ".emptyFolderPlaceholder"},  # This should be skipped
        ]

        # Mock the implementation's behavior
        bucket_storage_mock = MagicMock()
        bucket_storage_mock.list.return_value = files_to_delete
        bucket_storage_mock.remove.return_value = None

        # Set up nested mocks to match how the implementation accesses the client
        storage_mock = mock_client.client.storage
        storage_mock.from_.return_value = bucket_storage_mock

        # Act
        result = image_storage.delete_all_storage_objects(bucket)  # Note: no user_id means delete all

        # Assert
        assert result is True
        storage_mock.from_.assert_called_with(bucket)
        bucket_storage_mock.list.assert_called_once_with()
        assert bucket_storage_mock.remove.call_count == 2  # Should skip the placeholder file
        bucket_storage_mock.remove.assert_any_call(["user-1/file1.png"])
        bucket_storage_mock.remove.assert_any_call(["user-2/file2.png"])

    def test_delete_all_storage_objects_error(self, image_storage: ImageStorage, mock_client: MagicMock) -> None:
        """Test error handling during storage object deletion."""
        # Arrange
        user_id = "user-123"

        # Configure storage mock to raise an exception
        storage_mock = mock_client.client.storage
        storage_mock.from_.return_value.list.side_effect = Exception("Storage error")

        # Act
        result = image_storage.delete_all_storage_objects(user_id)

        # Assert
        assert result is False
        storage_mock.from_.return_value.list.assert_called_once()


class TestStoreImage:
    """Tests for the store_image method."""

    def test_store_image_bytes_success(self, image_storage: ImageStorage) -> None:
        """Test storing an image from bytes."""
        # Arrange
        image_data = b"fake-image-data"
        user_id = "user-123"

        # Mock the necessary parts
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "image-uuid"  # use .hex property to match implementation

            # Mock datetime for predictable filename
            with patch("app.core.supabase.image_storage.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20220101000000"

                # Mock the JWT token creation and requests for direct HTTP
                with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
                    mock_jwt.return_value = "fake-jwt-token"

                    # Mock the requests post call
                    with patch("requests.post") as mock_post:
                        mock_response = MagicMock()
                        mock_response.raise_for_status = MagicMock()
                        mock_post.return_value = mock_response

                        # Act
                        result = image_storage.store_image(image_data, user_id, is_palette=False)

                        # Assert
                        # The implementation uses only the first 8 chars of the UUID
                        expected_path = f"{user_id}/20220101000000_image-uu.png"
                        assert result == expected_path
                        # Verify that request was made with correct data
                        mock_post.assert_called_once()
                        mock_jwt.assert_called_once_with(user_id)

    def test_store_image_bytesio_success(self, image_storage: ImageStorage) -> None:
        """Test storing an image from BytesIO."""
        # Arrange
        image_data = io.BytesIO(b"fake-image-data")
        user_id = "user-123"

        # Mock the necessary parts
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "image-uuid"  # use .hex property to match implementation

            # Mock datetime for predictable filename
            with patch("app.core.supabase.image_storage.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20220101000000"

                # Mock the JWT token creation and requests for direct HTTP
                with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
                    mock_jwt.return_value = "fake-jwt-token"

                    # Mock the requests post call
                    with patch("requests.post") as mock_post:
                        mock_response = MagicMock()
                        mock_response.raise_for_status = MagicMock()
                        mock_post.return_value = mock_response

                        # Act
                        result = image_storage.store_image(image_data, user_id, is_palette=False)

                        # Assert
                        # The implementation uses only the first 8 chars of the UUID
                        expected_path = f"{user_id}/20220101000000_image-uu.png"
                        assert result == expected_path
                        # Verify that request was made with correct data
                        mock_post.assert_called_once()

    def test_store_image_uploadfile_success(self, image_storage: ImageStorage) -> None:
        """Test store_image with UploadFile."""
        # Arrange
        mock_uploadfile = MagicMock(spec=UploadFile)
        mock_uploadfile.content_type = "image/png"
        mock_uploadfile.filename = "test.png"
        # Important: need to set file attribute with read method
        mock_file = MagicMock()
        mock_file.read.return_value = b"fake-image-data"
        mock_uploadfile.file = mock_file

        user_id = "user-123"

        # Mock the necessary parts
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "image-uuid"  # use .hex property to match implementation

            # Mock datetime for predictable filename
            with patch("app.core.supabase.image_storage.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20220101000000"

                # Mock the JWT token creation and requests for direct HTTP
                with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
                    mock_jwt.return_value = "fake-jwt-token"

                    # Mock the requests post call
                    with patch("requests.post") as mock_post:
                        mock_response = MagicMock()
                        mock_response.raise_for_status = MagicMock()
                        mock_post.return_value = mock_response

                        # Act
                        result = image_storage.store_image(mock_uploadfile, user_id, is_palette=False)

                        # Assert
                        # The implementation uses only the first 8 chars of the UUID
                        expected_path = f"{user_id}/20220101000000_image-uu.png"
                        assert result == expected_path
                        # Verify file was read
                        mock_file.read.assert_called_once()
                        # Verify request was made
                        mock_post.assert_called_once()

    def test_store_image_palette_bucket(self, image_storage: ImageStorage) -> None:
        """Test storing an image in the palette bucket."""
        # Arrange
        image_data = b"fake-image-data"
        user_id = "user-123"

        # Mock the necessary parts
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.return_value.hex = "palette-uuid"  # use .hex property to match implementation

            # Mock datetime for predictable filename
            with patch("app.core.supabase.image_storage.datetime") as mock_datetime:
                mock_datetime.now.return_value.strftime.return_value = "20220101000000"

                # Mock the JWT token creation and requests for direct HTTP
                with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
                    mock_jwt.return_value = "fake-jwt-token"

                    # Mock the requests post call
                    with patch("requests.post") as mock_post:
                        mock_response = MagicMock()
                        mock_response.raise_for_status = MagicMock()
                        mock_post.return_value = mock_response

                        # Act
                        result = image_storage.store_image(image_data, user_id, is_palette=True)

                        # Assert
                        # The implementation uses only the first 8 chars of the UUID
                        expected_path = f"{user_id}/20220101000000_palette-.png"
                        assert result == expected_path
                        # Verify that request was made with correct data
                        mock_post.assert_called_once()
                        # Should use palettes bucket
                        assert "palettes" in mock_post.call_args[0][0]

    def test_store_image_error(self, image_storage: ImageStorage) -> None:
        """Test error handling in store_image."""
        # Arrange
        image_data = b"fake-image-data"
        user_id = "user-123"

        # Mock uuid to raise an exception
        with patch("app.core.supabase.image_storage.uuid.uuid4") as mock_uuid:
            mock_uuid.side_effect = Exception("UUID generation error")

            # Act
            result = image_storage.store_image(image_data, user_id)

            # Assert
            assert result is None


class TestGetSignedUrl:
    """Tests for the get_signed_url method."""

    def test_get_signed_url_success(self, image_storage: ImageStorage) -> None:
        """Test successful generation of signed URL."""
        # Arrange
        path = "user-123/image.png"
        bucket = "concepts"
        expected_url = "https://example.com/signed-url"
        expiry_seconds = 3600

        # Mock the create_signed_url method
        with patch.object(
            image_storage,
            "create_signed_url",
            return_value=expected_url,
        ) as mock_get_signed:
            # Act
            result = image_storage.get_signed_url(path, bucket=bucket, expiry_seconds=expiry_seconds)

            # Assert
            assert result == expected_url
            mock_get_signed.assert_called_once_with(path=path, bucket_name=bucket, expires_in=expiry_seconds)

    def test_get_signed_url_default_bucket(self, image_storage: ImageStorage) -> None:
        """Test get_signed_url with default bucket."""
        # Arrange
        path = "user-123/image.png"
        expected_url = "https://example.com/signed-url"
        # No bucket provided, should use default

        # Mock the create_signed_url method
        with patch.object(
            image_storage,
            "create_signed_url",
            return_value=expected_url,
        ) as mock_create_signed:
            # Act
            result = image_storage.get_signed_url(path)

            # Assert
            assert result == expected_url
            # Should use the default bucket (concepts)
            mock_create_signed.assert_called_once_with(path=path, bucket_name="concepts", expires_in=settings.SIGNED_URL_EXPIRY_SECONDS)

    def test_get_signed_url_error(self, image_storage: ImageStorage) -> None:
        """Test error handling in get_signed_url."""
        # Arrange
        path = "user-123/image.png"
        bucket = "concepts"

        # Mock create_signed_url to raise an exception
        with patch.object(image_storage, "create_signed_url", side_effect=Exception("Signing error")) as mock_create_signed:
            # Act
            result = image_storage.get_signed_url(path, bucket=bucket)

            # Assert
            assert result is None
            mock_create_signed.assert_called_once_with(path=path, bucket_name=bucket, expires_in=settings.SIGNED_URL_EXPIRY_SECONDS)


class TestUploadImage:
    """Tests for the upload_image method."""

    @pytest.mark.asyncio
    async def test_upload_image_success(self, image_storage: ImageStorage, mock_settings: MagicMock) -> None:
        """Test successful image upload."""
        # Arrange
        file_data = b"fake-image-data"
        path = "user-123/image.png"
        user_id = "user-123"
        content_type = "image/png"

        # Mock the JWT token creation and httpx client
        with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
            mock_jwt.return_value = "fake-jwt-token"

            # Mock the httpx client
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.raise_for_status = MagicMock()

                # Setup the context manager returned by httpx.AsyncClient()
                mock_async_client = MagicMock()
                mock_async_client.__aenter__.return_value.post.return_value = mock_response
                mock_client.return_value = mock_async_client

                # Act
                result = await image_storage.upload_image(file_data, path, content_type, user_id, is_palette=False)

                # Assert
                assert result is True
                mock_jwt.assert_called_once_with(user_id)
                # Verify httpx client was called
                mock_async_client.__aenter__.return_value.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_upload_image_palette_bucket(self, image_storage: ImageStorage, mock_settings: MagicMock) -> None:
        """Test upload to palette bucket."""
        # Arrange
        file_data = b"fake-image-data"
        path = "user-123/palette.png"
        user_id = "user-123"
        content_type = "image/png"

        # Mock the JWT token creation and httpx client
        with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
            mock_jwt.return_value = "fake-jwt-token"

            # Mock the httpx client
            with patch("httpx.AsyncClient") as mock_client:
                mock_response = MagicMock()
                mock_response.raise_for_status = MagicMock()

                # Setup the context manager returned by httpx.AsyncClient()
                mock_async_client = MagicMock()
                mock_async_client.__aenter__.return_value.post.return_value = mock_response
                mock_client.return_value = mock_async_client

                # Act
                result = await image_storage.upload_image(file_data, path, content_type, user_id, is_palette=True)

                # Assert
                assert result is True
                mock_jwt.assert_called_once_with(user_id)
                # Verify httpx client was called
                mock_async_client.__aenter__.return_value.post.assert_called_once()
                # Verify palette bucket was used
                api_url = mock_async_client.__aenter__.return_value.post.call_args[0][0]
                assert "palettes" in api_url

    @pytest.mark.asyncio
    async def test_upload_image_error(self, image_storage: ImageStorage) -> None:
        """Test error handling in upload_image."""
        # Arrange
        file_data = b"fake-image-data"
        path = "user-123/image.png"
        user_id = "user-123"
        content_type = "image/png"

        # Mock the JWT token creation and httpx client to raise an exception
        with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
            mock_jwt.return_value = "fake-jwt-token"

            # Mock the httpx client to raise an exception
            with patch("httpx.AsyncClient") as mock_client:
                mock_async_client = MagicMock()
                mock_async_client.__aenter__.return_value.post.side_effect = Exception("Storage error")
                mock_client.return_value = mock_async_client

                # Act and Assert
                with pytest.raises(Exception) as exc_info:
                    await image_storage.upload_image(file_data, path, content_type, user_id)
                assert "Storage error" in str(exc_info.value)


class TestDownloadImage:
    """Tests for the download_image method."""

    def test_download_image_success(self, image_storage: ImageStorage, mock_settings: MagicMock) -> None:
        """Test successful image download."""
        # Arrange
        path = "user-123/image.png"
        bucket = "concepts"
        expected_content = b"fake-image-data"

        # Mock the client's storage
        storage_mock = image_storage.client.client.storage
        storage_mock.from_.return_value.download.return_value = expected_content

        # Act
        content = image_storage.download_image(path, bucket)

        # Assert
        assert content == expected_content
        # Check storage client was called correctly
        storage_mock.from_.assert_called_once_with(bucket)
        storage_mock.from_.return_value.download.assert_called_once_with(path)

    def test_download_image_not_found(self, image_storage: ImageStorage) -> None:
        """Test download_image with non-existent image."""
        # Arrange
        path = "user-123/nonexistent.png"
        bucket = "concepts"

        # Mock the storage client to raise a 404 exception
        class NotFoundError(Exception):
            """Custom exception with status_code attribute."""

            status_code = 404

        not_found_error = NotFoundError("Not Found")

        # First mock standard client to fail
        standard_storage_mock = image_storage.client.client.storage
        standard_storage_mock.from_.return_value.download.side_effect = not_found_error

        # Then mock service role client
        service_client_mock = MagicMock()
        service_download_mock = MagicMock()
        service_download_mock.side_effect = not_found_error
        service_client_mock.storage.from_.return_value.download = service_download_mock
        with patch.object(image_storage.client, "get_service_role_client", return_value=service_client_mock):
            # Act and Assert
            with pytest.raises(Exception) as exc_info:
                image_storage.download_image(path, bucket)
            # Check that we get the expected error
            assert "Not Found" in str(exc_info.value)

    def test_download_image_server_error(self, image_storage: ImageStorage) -> None:
        """Test handling of server errors in download_image."""
        # Arrange
        path = "user-123/image.png"
        bucket = "concepts"

        # Mock the storage client to raise a 500 exception
        class ServerError(Exception):
            """Custom exception with status_code attribute."""

            status_code = 500

        server_error = ServerError("Server Error")

        # First mock standard client to fail
        standard_storage_mock = image_storage.client.client.storage
        standard_storage_mock.from_.return_value.download.side_effect = server_error

        # Then mock service role client
        service_client_mock = MagicMock()
        service_download_mock = MagicMock()
        service_download_mock.side_effect = server_error
        service_client_mock.storage.from_.return_value.download = service_download_mock
        with patch.object(image_storage.client, "get_service_role_client", return_value=service_client_mock):
            # Act and Assert
            with pytest.raises(Exception) as exc_info:
                image_storage.download_image(path, bucket)
            # Check that we get the expected error
            assert "Server Error" in str(exc_info.value)


class TestCreateSignedUrl:
    """Tests for the create_signed_url method."""

    def test_create_signed_url_success(self, image_storage: ImageStorage, mock_settings: MagicMock) -> None:
        """Test successful creation of signed URL."""
        # Arrange
        path = "user-123/image.png"
        bucket_name = "concepts"
        expiry_seconds = 3600
        expected_url = "https://example.com/signed-url"

        # Mock the JWT token creation
        with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
            mock_jwt.return_value = "fake-jwt-token"

            # Mock the response from the storage API
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"signedURL": expected_url}

            # Mock the requests module
            with patch("requests.post") as mock_post:
                mock_post.return_value = mock_response

                # Act
                result = image_storage.create_signed_url(path, bucket_name, expiry_seconds)

                # Assert
                assert result == expected_url
                # Verify the URL was constructed correctly
                expected_base_url = f"{mock_settings.SUPABASE_URL}/storage/v1/object/sign/{bucket_name}/{path}"
                mock_post.assert_called_once()
                call_args = mock_post.call_args
                assert call_args[0][0] == expected_base_url

    def test_create_signed_url_error(self, image_storage: ImageStorage) -> None:
        """Test error handling in create_signed_url."""
        # Arrange
        path = "user-123/image.png"
        bucket_name = "concepts"
        expiry_seconds = 3600

        # Mock the JWT token creation
        with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
            mock_jwt.return_value = "fake-jwt-token"

            # Mock the requests module to raise an exception
            with patch("requests.post") as mock_post:
                mock_post.side_effect = Exception("API error")

                # Act
                result = image_storage.create_signed_url(path, bucket_name, expiry_seconds)

                # Assert
                assert result is None

    def test_create_signed_url_malformed_response(self, image_storage: ImageStorage) -> None:
        """Test handling of malformed response in create_signed_url."""
        # Arrange
        path = "user-123/image.png"
        bucket_name = "concepts"
        expiry_seconds = 3600

        # Mock the JWT token creation
        with patch("app.core.supabase.image_storage.create_supabase_jwt") as mock_jwt:
            mock_jwt.return_value = "fake-jwt-token"

            # Mock the response to be malformed
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"unexpected": "data"}  # Missing signedURL

            # Mock the requests module
            with patch("requests.post") as mock_post:
                mock_post.return_value = mock_response

                # Act
                result = image_storage.create_signed_url(path, bucket_name, expiry_seconds)

                # Assert
                assert result is None
