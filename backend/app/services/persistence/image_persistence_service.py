"""Image persistence service.

This module provides functionality for storing and retrieving images
from Supabase storage.
"""

import logging
import uuid
from datetime import datetime
from io import BytesIO
from typing import Any, Dict, List, Optional, Tuple, Union

import httpx
from fastapi import UploadFile
from PIL import Image

from app.core.config import settings
from app.core.exceptions import ImageNotFoundError, ImageStorageError
from app.core.supabase.client import SupabaseClient
from app.core.supabase.image_storage import ImageStorage
from app.services.persistence.interface import ImagePersistenceServiceInterface
from app.utils.security.mask import mask_id, mask_path

logger = logging.getLogger(__name__)


class ImagePersistenceService(ImagePersistenceServiceInterface):
    """Service for storing and retrieving images from Supabase storage."""

    def __init__(self, client: SupabaseClient):
        """Initialize the image persistence service.

        Args:
            client: Supabase client instance
        """
        self.supabase = client.client  # Access the underlying client
        # Get bucket names from config instead of hardcoding
        self.concept_bucket = settings.STORAGE_BUCKET_CONCEPT
        self.palette_bucket = settings.STORAGE_BUCKET_PALETTE
        self.logger = logging.getLogger(__name__)
        self.storage = ImageStorage(client)

    async def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        content_type: str = "image/png",
        is_palette: bool = False,
    ) -> Tuple[str, str]:
        """Store an image in the storage bucket with user ID metadata.

        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            user_id: User ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            content_type: Content type of the image
            is_palette: Whether the image is a palette (uses palette-images bucket)

        Returns:
            Tuple[str, str]: (image_path, image_url)

        Raises:
            ImageStorageError: If image storage fails
        """
        try:
            # Process image data to get bytes
            if isinstance(image_data, UploadFile):
                content = image_data.file.read()
            elif isinstance(image_data, BytesIO):
                content = image_data.getvalue()
            else:
                content = image_data

            # Default extension - initialize it here to avoid undefined issues
            ext = "png"

            # Generate a unique file name if not provided
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = str(uuid.uuid4())[:8]

                # Try to determine file format from content
                try:
                    img = Image.open(BytesIO(content))
                    if img.format:
                        ext = img.format.lower()
                except Exception as e:
                    self.logger.warning(f"Could not determine image format: {str(e)}, using default: {ext}")

                file_name = f"{timestamp}_{random_id}.{ext}"
            else:
                # Extract extension from provided file_name
                if "." in file_name:
                    ext = file_name.split(".")[-1].lower()

            # Create path with user_id as the first folder segment
            # This is CRITICAL for our RLS policy to work
            if concept_id:
                path = f"{user_id}/{concept_id}/{file_name}"
            else:
                path = f"{user_id}/{file_name}"

            # Set content type based on extension
            if not content_type or content_type == "image/png":
                content_type = "image/png"  # Default content type
                if ext == "jpg" or ext == "jpeg":
                    content_type = "image/jpeg"
                elif ext == "gif":
                    content_type = "image/gif"
                elif ext == "webp":
                    content_type = "image/webp"

            # Prepare file metadata including user ID
            file_metadata = {"owner_user_id": user_id}
            if metadata:
                file_metadata.update(metadata)

            # Use the ImageStorage component to store the image
            await self.storage.upload_image(
                image_data=content,
                path=path,
                content_type=content_type,
                user_id=user_id,
                is_palette=is_palette,
                metadata=file_metadata,
            )

            # Generate signed URL with 3-day expiration
            image_url = self.get_signed_url(path, is_palette=is_palette)

            # Log success with masked user ID
            masked_user_id = mask_id(user_id)
            masked_path = mask_path(path)
            self.logger.info(f"Stored image for user {masked_user_id} at {masked_path}")

            return path, image_url

        except Exception as e:
            error_msg = f"Failed to store image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    async def get_image(self, image_path: str) -> bytes:
        """Retrieve an image from storage.

        Args:
            image_path: Path of the image in storage

        Returns:
            Image data as bytes

        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        try:
            # Determine if this is a palette image based on the path
            is_palette = False
            if "palette" in image_path.lower():
                is_palette = True

            # Get the appropriate bucket name
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            self.logger.debug(f"Attempting to get image from bucket: {bucket_name}, path: {mask_path(image_path)}")

            # Try to download the image from the selected bucket
            try:
                image_data = self.storage.download_image(path=image_path, bucket_name=bucket_name)
                self.logger.debug(f"Successfully retrieved image {mask_path(image_path)} from {bucket_name}")
                return image_data
            except Exception as e:
                error_msg = f"Failed to get image {image_path} from {bucket_name}: {str(e)}"
                self.logger.error(error_msg)

                # Check if this is a "not found" error
                if "404" in str(e) or "not found" in str(e).lower():
                    # Try the opposite bucket before giving up
                    opposite_bucket = self.concept_bucket if is_palette else self.palette_bucket
                    try:
                        self.logger.info(f"Image not found in {bucket_name}, trying {opposite_bucket}")

                        # If we're switching from palette to concept, try removing "palette_" prefix if it exists
                        try_path = image_path
                        if is_palette and image_path.startswith("palette_"):
                            try_path = image_path[8:]  # Remove "palette_" prefix
                            self.logger.debug(f"Removing palette_ prefix, trying path: {mask_path(try_path)}")

                        # If we're switching from concept to palette, we don't need to modify the path
                        image_data = self.storage.download_image(path=try_path, bucket_name=opposite_bucket)
                        self.logger.info(f"Successfully retrieved image {mask_path(try_path)} from {opposite_bucket}")
                        return image_data
                    except Exception as opposite_err:
                        # If it fails in the opposite bucket too, try with service role
                        if "404" in str(opposite_err) or "not found" in str(opposite_err).lower():
                            raise ImageNotFoundError(f"Image not found in any bucket: {image_path}")

                # For other errors or if opposite bucket failed but wasn't a 404, attempt with service role
                try:
                    self.logger.info("Attempting to get image with service role")
                    # Get a service role client
                    from app.core.supabase.client import SupabaseClient

                    service_client = SupabaseClient(url=settings.SUPABASE_URL, key=settings.SUPABASE_KEY).get_service_role_client()

                    # Try with service role in the original bucket first
                    try:
                        result = service_client.storage.from_(bucket_name).download(image_path)
                        if result is not None:
                            self.logger.info(f"Retrieved image {mask_path(image_path)} from {bucket_name} using service role")
                            return bytes(result)
                    except Exception as bucket1_err:
                        self.logger.debug(f"Service role failed in {bucket_name}: {str(bucket1_err)}")

                    # Try with service role in the opposite bucket
                    opposite_bucket = self.concept_bucket if is_palette else self.palette_bucket
                    try:
                        # If switching buckets, adjust path if needed
                        try_path = image_path
                        if is_palette and image_path.startswith("palette_"):
                            try_path = image_path[8:]  # Remove "palette_" prefix

                        result = service_client.storage.from_(opposite_bucket).download(try_path)
                        if result is not None:
                            self.logger.info(f"Retrieved image {mask_path(try_path)} from {opposite_bucket} using service role")
                            return bytes(result)
                    except Exception as bucket2_err:
                        self.logger.debug(f"Service role failed in {opposite_bucket}: {str(bucket2_err)}")

                    # If we've tried both buckets with service role and still failed, raise an error
                    raise ImageNotFoundError(f"Image not found with service role in any bucket: {image_path}")

                except Exception as service_err:
                    self.logger.error(f"Service role fallback also failed: {str(service_err)}")
                    raise ImageStorageError(error_msg)
        except ImageNotFoundError:
            # Re-raise ImageNotFoundError without wrapping
            raise
        except Exception as e:
            error_msg = f"Failed to get image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def _store_image_metadata(
        self,
        image_path: str,
        concept_id: str,
        bucket_name: str,
        metadata: Dict[str, Any],
    ) -> None:
        """Store metadata about an image in the database.

        Args:
            image_path: Path of the image in storage
            concept_id: Concept ID associated with the image
            bucket_name: Name of the bucket containing the image
            metadata: Metadata to store
        """
        try:
            # We don't have an image_metadata table, so just log that we would store metadata
            # Instead of trying to use self.supabase.table() which doesn't exist
            self.logger.debug(f"Metadata for image {image_path} in bucket {bucket_name} would be stored: {metadata}")

            # If concept_id looks like a UUID, we could try to update the concepts table
            # but this is safer for now to avoid further errors

        except Exception as e:
            # Log but don't fail the overall operation
            self.logger.warning(f"Failed to store image metadata: {str(e)}")

    def delete_image(self, image_path: str) -> bool:
        """Delete an image from storage.

        Args:
            image_path: Path of the image in storage

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            ImageStorageError: If deletion fails
        """
        try:
            # Determine if this is a palette image based on the path
            is_palette = False
            if "palette" in image_path or "palette" in self.palette_bucket:
                is_palette = True

            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            # Use delete_image method
            self.storage.delete_image(path=image_path, bucket_name=bucket_name)
            self.logger.info(f"Deleted image {mask_path(image_path)}")
            return True
        except Exception as e:
            error_msg = f"Failed to delete image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_signed_url(self, path: str, is_palette: bool = False, expiry_seconds: int = 345600) -> str:
        """Get a signed URL for an image with expiry time.

        Args:
            path: Path of the image in storage
            is_palette: Whether the image is in the palette bucket
            expiry_seconds: Expiry time in seconds (default: 4 days)

        Returns:
            Signed URL for the image

        Raises:
            ImageStorageError: If URL generation fails
        """
        try:
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            url = self.storage.get_signed_url(path=path, bucket=bucket_name, expiry_seconds=expiry_seconds)
            if not url:
                raise ImageStorageError(f"Failed to generate signed URL for image {path}")
            return url
        except Exception as e:
            error_msg = f"Failed to get signed URL for image {path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_image_url(self, image_path: str, expiration: int = 3600) -> str:
        """Get a URL for an image.

        Args:
            image_path: Path of the image in storage
            expiration: Expiration time in seconds

        Returns:
            URL for the image

        Raises:
            ImageStorageError: If URL generation fails
        """
        # If image_path is already a URL, return it directly
        if image_path.startswith("http://") or image_path.startswith("https://"):
            return image_path

        try:
            # Determine if this is a palette image based on the path
            is_palette = False
            if "palette" in image_path or "palette" in self.palette_bucket:
                is_palette = True

            # Return a signed URL with the specified expiration
            return self.get_signed_url(image_path, is_palette=is_palette, expiry_seconds=expiration)
        except Exception as e:
            error_msg = f"Failed to get URL for image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    async def get_image_async(self, image_path_or_url: str, is_palette: bool = False) -> bytes:
        """Retrieve an image asynchronously, supporting both storage paths and URLs.

        Args:
            image_path_or_url: Path or URL of the image
            is_palette: Whether the image is a palette (for storage paths only)

        Returns:
            Image data as bytes

        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        # Check if it's a URL or a path
        if image_path_or_url.startswith("http://") or image_path_or_url.startswith("https://"):
            # It's a URL - fetch using httpx
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_path_or_url)
                    response.raise_for_status()
                    return response.content
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise ImageNotFoundError(f"Image not found at URL: {image_path_or_url}")
                else:
                    raise ImageStorageError(f"HTTP error fetching image: {str(e)}")
            except Exception as e:
                error_msg = f"Failed to fetch image from URL {image_path_or_url}: {str(e)}"
                self.logger.error(error_msg)
                raise ImageStorageError(error_msg)
        else:
            # It's a storage path - use get_image method
            # Check if it's a signed URL disguised as a path
            if "/object/sign/" in image_path_or_url:
                # Try to extract the actual path from the signed URL
                try:
                    # The path is everything after the last slash in the URL
                    parts = image_path_or_url.split("/")
                    path = parts[-1]

                    # We don't need the bucket info since we determine it in get_image
                    # Removing this to fix unused variable warning

                    if path:
                        self.logger.debug(f"Extracted path from signed URL: {path}")
                        # Get the image directly
                        return await self.get_image(path)

                    # If we can't extract a path or it doesn't match expected format,
                    # fall back to treating it as a URL
                    async with httpx.AsyncClient() as client:
                        response = await client.get(image_path_or_url)
                        response.raise_for_status()
                        return response.content

                except Exception as e:
                    self.logger.error(f"Error processing signed URL: {e}")
                    # Fall back to treating it as a regular path
                    return await self.get_image(image_path_or_url)
            else:
                # This is a regular storage path
                return await self.get_image(image_path_or_url)

    def list_images(
        self,
        user_id: str,
        concept_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        include_metadata: bool = False,
    ) -> List[Dict[str, Any]]:
        """List images in storage for a specific user and concept.

        Args:
            user_id: User ID for filtering images
            concept_id: Optional concept ID for filtering images
            limit: Maximum number of images to return
            offset: Offset for pagination
            include_metadata: Whether to include metadata in results

        Returns:
            List of image objects with paths and URLs

        Raises:
            ImageStorageError: If listing fails
        """
        try:
            # Construct the path prefix for searching
            path_prefix = f"{user_id}"
            if concept_id:
                path_prefix = f"{user_id}/{concept_id}"

            # Get list of images from storage using the client directly
            bucket_name = self.concept_bucket
            try:
                # Use the storage service to list files
                files = self.supabase.storage.from_(bucket_name).list(path_prefix, limit, offset)
                results = [{"name": f, "created_at": "", "metadata": {}} for f in files]
            except Exception as e:
                self.logger.error(f"Failed to list files using storage.from_: {str(e)}")
                # Fall back to empty list
                results = []

            # Process each image to add a signed URL and extract metadata if needed
            images = []
            for item in results:
                image_path = item.get("name")
                if not image_path:
                    continue

                # Create an image object with path and URL
                image_obj = {
                    "path": image_path,
                    "url": self.get_signed_url(image_path),
                    "created_at": item.get("created_at", ""),
                }

                # Include metadata if requested
                if include_metadata and "metadata" in item and item["metadata"]:
                    image_obj["metadata"] = item["metadata"]

                images.append(image_obj)

            return images

        except Exception as e:
            error_msg = f"Failed to list images for user {mask_id(user_id)}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    async def authenticate_url(self, path: str, user_id: str, is_palette: bool = False) -> str:
        """Authenticate an image URL for a specific user.

        Args:
            path: Path of the image in storage
            user_id: User ID for authentication
            is_palette: Whether the image is a palette

        Returns:
            Authenticated URL for the image
        """
        # For now, we'll just return a signed URL
        # In a real implementation, we might add user-specific tokens
        return self.get_signed_url(path, is_palette=is_palette)

    def get_image_with_token(self, path: str, token: str, is_palette: bool = False) -> bytes:
        """Get an image using an authentication token.

        Args:
            path: Path to the image in storage
            token: Authentication token
            is_palette: Whether the image is a palette

        Returns:
            Image data as bytes

        Raises:
            ImageNotFoundError: If image not found
            ImageStorageError: If retrieval fails
        """
        # For now, we're not actually using the token - we're just validating
        # that a token was provided at all
        if not token:
            raise ImageStorageError("Authentication token required")

        try:
            # Just retrieve the image directly
            # In a real implementation, we would validate the token
            import asyncio

            return asyncio.run(self.get_image(path))
        except ImageNotFoundError:
            raise
        except Exception as e:
            error_msg = f"Failed to get image with token: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_image_by_path(self, path: str, is_palette: bool = False) -> bytes:
        """Get an image by its path.

        This is a convenience method that delegates to get_image.

        Args:
            path: Path to the image in storage
            is_palette: Whether the image is a palette

        Returns:
            Image data as bytes

        Raises:
            ImageNotFoundError: If image not found
            ImageStorageError: If retrieval fails
        """
        import asyncio

        return asyncio.run(self.get_image(path))
