"""
Image persistence service.

This module provides functionality for storing and retrieving images
from Supabase storage.
"""

import logging
import uuid
import requests
from typing import Optional, Dict, Any, Union, List, Tuple
from io import BytesIO
from datetime import datetime

from fastapi import UploadFile
from supabase import Client, create_client
from PIL import Image

from app.core.exceptions import ImageNotFoundError, ImageStorageError
from app.core.config import settings
from app.utils.jwt_utils import create_supabase_jwt, create_supabase_jwt_for_storage
from app.utils.security.mask import mask_id, mask_path

logger = logging.getLogger(__name__)

class ImagePersistenceService:
    """Service for storing and retrieving images from Supabase storage."""

    def __init__(self, client: Client):
        """
        Initialize the image persistence service.
        
        Args:
            client: Supabase client instance
        """
        self.supabase = client
        # Get bucket names from config instead of hardcoding
        self.concept_bucket = settings.STORAGE_BUCKET_CONCEPT
        self.palette_bucket = settings.STORAGE_BUCKET_PALETTE
        self.logger = logging.getLogger(__name__)
    
    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> Tuple[str, str]:
        """
        Store an image in the storage bucket with user ID metadata.
        
        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            user_id: User ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            is_palette: Whether the image is a palette (uses palette-images bucket)
            
        Returns:
            Tuple[str, str]: (image_path, image_url)
            
        Raises:
            ImageStorageError: If image storage fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
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
            content_type = "image/png"  # Default content type
            if ext == "jpg" or ext == "jpeg":
                content_type = "image/jpeg"
            elif ext == "gif":
                content_type = "image/gif"
            elif ext == "webp":
                content_type = "image/webp"
            
            # Create JWT token for authentication (for Supabase Storage RLS)
            token = create_supabase_jwt(user_id)
            
            # Prepare file metadata including user ID
            file_metadata = {"owner_user_id": user_id}
            if metadata:
                file_metadata.update(metadata)
                
            # Use direct HTTP request with requests library for JWT authorization
            # Get the API endpoint directly from settings instead of client objects
            api_url = settings.SUPABASE_URL
            api_key = settings.SUPABASE_KEY
                
            # Construct the storage upload URL
            upload_url = f"{api_url}/storage/v1/object/{bucket_name}/{path}"
            
            # Set headers with JWT token and other required headers
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": api_key,
                "Content-Type": content_type,
                "x-upsert": "true"  # Update if exists
            }
            
            # Upload the file with requests
            response = requests.post(
                upload_url,
                headers=headers,
                data=content
            )
            
            # Check if upload was successful
            if response.status_code not in (200, 201):
                self.logger.error(f"Upload failed with status {response.status_code}: {response.text}")
                raise ImageStorageError(f"Failed to upload image: {response.text}")
                
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

    def get_image(self, image_path: str, is_palette: bool = False) -> bytes:
        """
        Retrieve an image from storage.
        
        Args:
            image_path: Path of the image in storage
            is_palette: Whether the image is a palette (uses palette-images bucket)
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Try storage access through client attribute first, then fall back to direct access
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                response = self.supabase.client.storage.from_(bucket_name).download(image_path)
            else:
                response = self.supabase.storage.from_(bucket_name).download(image_path)
                
            return response
            
        except Exception as e:
            error_msg = f"Failed to get image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            
            if "404" in str(e) or "not found" in str(e).lower():
                raise ImageNotFoundError(f"Image not found: {image_path}")
                
            raise ImageStorageError(error_msg)
    
    def _store_image_metadata(self, image_path: str, concept_id: str, bucket_name: str, metadata: Dict[str, Any]) -> None:
        """
        Store metadata about an image in the database.
        
        Args:
            image_path: Path of the image in storage
            concept_id: Concept ID associated with the image
            bucket_name: Name of the bucket containing the image
            metadata: Metadata to store
        """
        try:
            # We don't have an image_metadata table, so just log that we would store metadata
            # Instead of trying to use self.supabase.table() which doesn't exist
            self.logger.info(f"Metadata for image {image_path} in bucket {bucket_name} would be stored: {metadata}")
            
            # If concept_id looks like a UUID, we could try to update the concepts table
            # but this is safer for now to avoid further errors
            
        except Exception as e:
            # Log but don't fail the overall operation
            self.logger.warning(f"Failed to store image metadata: {str(e)}")
            
    def delete_image(self, image_path: str, is_palette: bool = False) -> bool:
        """
        Delete an image from storage.
        
        Args:
            image_path: Path of the image in storage
            is_palette: Whether the image is a palette (uses palette-images bucket)
            
        Returns:
            True if deletion was successful
            
        Raises:
            ImageStorageError: If image deletion fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Try storage access through client attribute first, then fall back to direct access
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                self.supabase.client.storage.from_(bucket_name).remove([image_path])
            else:
                self.supabase.storage.from_(bucket_name).remove([image_path])
            
            return True
            
        except Exception as e:
            error_msg = f"Failed to delete image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
    
    def list_images(self, concept_id: Optional[str] = None, is_palette: bool = False) -> List[Dict[str, Any]]:
        """
        List images in storage.
        
        Args:
            concept_id: Optional concept ID to filter images by
            is_palette: Whether to list palette images
            
        Returns:
            List of image metadata dictionaries
            
        Raises:
            ImageStorageError: If listing fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # TODO: Implement filtering by concept_id using list_paths with prefix filtering
            # We don't have a direct way to filter by concept_id in the storage API
            
            # Try storage access through client attribute first, then fall back to direct access
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                files = self.supabase.client.storage.from_(bucket_name).list()
            else:
                files = self.supabase.storage.from_(bucket_name).list()
            
            # Filter by concept_id if provided
            # This is a naive implementation; in a real system we would use a more efficient query
            if concept_id:
                filtered_files = []
                for file in files:
                    # Check if the path contains the concept_id
                    # Format is typically: {user_id}/{concept_id}/{file_name}
                    path_segments = file.get("name", "").split("/")
                    if len(path_segments) >= 2 and path_segments[1] == concept_id:
                        filtered_files.append(file)
                return filtered_files
            
            return files
            
        except Exception as e:
            error_msg = f"Failed to list images: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_signed_url(self, path: str, is_palette: bool = False, expiry_seconds: int = 259200) -> str:
        """
        Get a signed URL for an image.
        
        Args:
            path: Path of the image in storage
            is_palette: Whether the image is a palette
            expiry_seconds: URL expiration time in seconds (default: 3 days)
            
        Returns:
            Signed URL for the image
            
        Raises:
            ImageStorageError: If URL generation fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket

            # Generate signed URL with expiration
            # Construct URL parts ourselves for more reliability
            base_url = settings.SUPABASE_URL
            storage_path = f"/storage/v1/object/sign/{bucket_name}/{path}"
            expiry = int(datetime.now().timestamp()) + expiry_seconds
            
            # Create a special storage JWT that includes the signature parameters
            # Include the bucket name in the path for the JWT
            token = create_supabase_jwt_for_storage(path=f"{bucket_name}/{path}", expiry_timestamp=expiry)
            
            # Add query parameters for expiry
            query_params = f"?token={token}&expiry={expiry}"
            
            # Construct the final URL
            signed_url = f"{base_url}{storage_path}{query_params}"
            
            return signed_url
        
        except Exception as e:
            error_msg = f"Failed to generate signed URL for {path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
            
    # Additional methods for the service would be placed here
    
    async def authenticate_url(self, path: str, user_id: str, is_palette: bool = False) -> str:
        """
        Authenticate an image URL for a specific user.
        
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
        
    def get_image_with_token(
        self,
        path: str,
        token: str,
        is_palette: bool = False
    ) -> bytes:
        """
        Get an image using a secure token.
        
        Args:
            path: Path of the image in storage
            token: Authentication token
            is_palette: Whether the image is a palette
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        try:
            # Verify the token is valid for this path
            # This is a placeholder for a real token verification system
            # In a production system, you'd verify the JWT signature and claims
            
            # For now, we'll just pass through to get_image
            return self.get_image(path, is_palette=is_palette)
            
        except ImageNotFoundError:
            # Re-raise not found error
            raise
        except Exception as e:
            error_msg = f"Failed to get image with token: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
            
    def get_image_by_path(self, path: str, is_palette: bool = False) -> bytes:
        """
        Get an image by its storage path.
        
        Args:
            path: Path of the image in storage
            is_palette: Whether the image is a palette
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        return self.get_image(path, is_palette=is_palette) 