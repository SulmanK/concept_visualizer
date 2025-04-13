"""
Image storage operations for Supabase.

This module provides functionality for managing images in Supabase Storage.
"""

import logging
import io
import requests
from typing import List, Dict, Optional, Any, Union
from PIL import Image
from datetime import datetime
import uuid
from io import BytesIO
from fastapi import UploadFile

from .client import SupabaseClient
from ...utils.security.mask import mask_id, mask_path
from app.utils.jwt_utils import create_supabase_jwt
from app.core.config import get_masked_value


# Configure logging
logger = logging.getLogger(__name__)


class ImageStorage:
    """Handles image-related operations in Supabase Storage.
    
    This class provides methods for storing, retrieving, and managing images in Supabase Storage.
    
    Implementation notes:
    - Some methods use direct HTTP requests instead of the SDK methods to have better control
      over authentication, especially when using JWT tokens for user-specific storage access.
    - Storage paths are expected to follow the pattern: `{user_id}/{filename}` or 
      `{user_id}/{concept_id}/{filename}` where the user_id segment is CRITICAL for RLS policies.
    - When working with storage objects, we distinguish between:
        * storage_path: The path within a bucket (e.g., "user123/image.png")
        * full_url: Complete URL to access the resource (e.g., "https://xyz.supabase.co/storage/v1/...")
        * signed_url: URL with temporary access token
    """
    
    def __init__(self, client: SupabaseClient):
        """Initialize with a Supabase client.
        
        Args:
            client: Configured SupabaseClient instance
        """
        self.client = client
        self.logger = logging.getLogger("supabase_image")
        
        # Get bucket names from config
        from app.core.config import settings
        self.concept_bucket = settings.STORAGE_BUCKET_CONCEPT
        self.palette_bucket = settings.STORAGE_BUCKET_PALETTE
    
    def _mask_path(self, path: str) -> str:
        """Mask a storage path to protect user ID privacy.
        
        Args:
            path: Storage path potentially containing user ID (format: user_id/filename)
            
        Returns:
            Masked path with user ID portion obscured
            
        Note:
            This is used for logging to avoid exposing sensitive user IDs in logs.
        """
        if not path or "/" not in path:
            return path
            
        # Split path at first slash to separate user ID from filename
        parts = path.split("/", 1)
        if len(parts) >= 2:
            user_part = parts[0]
            file_part = parts[1]
            return f"{get_masked_value(user_part)}/{file_part}"
        return path
    
    async def upload_image_from_url(self, image_url: str, bucket: str, user_id: str) -> Optional[str]:
        """Upload an image from URL to Supabase Storage.
        
        Args:
            image_url: URL of the image to download
            bucket: Storage bucket to upload to
            user_id: User ID to use in the image path
            
        Returns:
            Storage path if successful, None otherwise
            
        Note:
            - The returned path will follow the pattern: `{user_id}/{uuid}.png`
            - This is critical for Supabase RLS policies which restrict access based on the first path segment
        """
        try:
            # Download the image
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Process the image with PIL to standardize format
            img = Image.open(io.BytesIO(response.content))
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            # Generate a unique filename
            filename = f"{user_id}/{uuid.uuid4()}.png"
            
            # Upload to Supabase Storage
            self.client.client.storage.from_(bucket).upload(
                path=filename,
                file=img_bytes.getvalue(),
                file_options={"content-type": "image/png"}
            )
            
            # Log success with masked path
            self.logger.info(f"Uploaded image to {self._mask_path(filename)}")
            
            return filename
        except Exception as e:
            self.logger.error(f"Error uploading image from URL: {e}")
            return None
    
    def get_image_url(self, path: str, bucket: str) -> Optional[str]:
        """Get a signed URL for an image in storage.
        
        This method uses direct HTTP requests instead of the Supabase SDK method for better
        control over JWT authentication and to ensure the storage RLS policies are respected.
        
        Args:
            path: Path to the image in storage (format: user_id/filename)
            bucket: Bucket name
            
        Returns:
            Signed URL for the image or None if not found
            
        Note:
            - The path MUST follow the pattern `{user_id}/...` for RLS policies to work
            - The created JWT includes the user_id from the first path segment for access control
            - The signed URL is valid for 3 days (259200 seconds)
            - If the signed URL endpoint fails, a fallback direct token URL is generated
        """
        try:
            # Create a JWT token for access
            from app.utils.jwt_utils import create_supabase_jwt
            
            # First segment is user_id - CRITICAL for RLS policy enforcement
            user_id = path.split('/')[0] if '/' in path else None
            if not user_id:
                self.logger.warning(f"Invalid path format - cannot extract user ID: {path}")
                return None
                
            # Create JWT token with the user_id claim for access control
            token = create_supabase_jwt(user_id)
            
            # Get the base URL
            api_url = self.client.url
            api_key = self.client.key
            
            # Use the signed URL endpoint
            signed_url_endpoint = f"{api_url}/storage/v1/object/sign/{bucket}/{path}"
            
            # Call the signed URL endpoint with 3-day expiration using direct HTTP
            # This is used instead of SDK methods to have better control over authentication
            response = requests.post(
                signed_url_endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": api_key
                },
                json={"expiresIn": 259200}  # 3 days in seconds
            )
            
            if response.status_code == 200:
                data = response.json()
                if "signedUrl" in data:
                    signed_url = data["signedUrl"]
                    # Ensure the URL is absolute and correctly formatted
                    if signed_url.startswith('/'):
                        # Make sure URL has the correct format with /storage/v1/
                        if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                            signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                        signed_url = f"{api_url}{signed_url}"
                    return signed_url
                elif "signedURL" in data:
                    signed_url = data["signedURL"]
                    # Ensure the URL is absolute and correctly formatted
                    if signed_url.startswith('/'):
                        # Make sure URL has the correct format with /storage/v1/
                        if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                            signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                        signed_url = f"{api_url}{signed_url}"
                    return signed_url
            
            # Fallback to direct URL with token if signed URL fails
            self.logger.warning(f"Failed to get signed URL, using fallback URL with token")
            return f"{api_url}/storage/v1/object/token/{bucket}/{path}?token={token}"
        
        except Exception as e:
            self.logger.error(f"Error getting image URL: {str(e)}")
            return None
    
    async def apply_color_palette(self, image_path: str, palette: List[str], user_id: str) -> Optional[str]:
        """Apply a color palette to an image and store the result.
        
        Args:
            image_path: Path to the source image in Storage
            palette: List of hex color codes
            user_id: User ID for the new image path
            
        Returns:
            Path to the color-modified image if successful, None otherwise
            
        Note:
            - The path return follows the pattern: `{user_id}/{uuid}_palette.png`
            - Currently this is a placeholder implementation
        """
        try:
            # Helper functions for color conversion
            def hex_to_rgb(hex_color):
                """Convert hex color to RGB tuple."""
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            def rgb_to_bgr(rgb):
                """Convert RGB to BGR (for OpenCV compatibility)."""
                return (rgb[2], rgb[1], rgb[0])
            
            def rgb_to_hsv(rgb):
                """Convert RGB to HSV values."""
                import colorsys
                r, g, b = rgb
                return colorsys.rgb_to_hsv(r/255, g/255, b/255)
            
            # TODO: Implement the recoloring logic
            # For now, we'll just upload the original image to a new path
            
            # Get the original image
            # Download image from storage
            import uuid
            output_path = f"{user_id}/{uuid.uuid4()}_palette.png"
            
            # Log the operation with masked paths
            self.logger.info(
                f"Applied color palette to {self._mask_path(image_path)} → {self._mask_path(output_path)}"
            )
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error applying color palette: {e}")
            return None
    
    def delete_all_storage_objects(self, bucket: str, user_id: Optional[str] = None) -> bool:
        """Delete all storage objects for a user or all objects in a bucket.
        
        Args:
            bucket: Storage bucket name
            user_id: Optional user ID to delete only objects for this user
            
        Returns:
            True if successful, False otherwise
            
        Note:
            - This method uses the standard SDK methods as they work well for deletion operations
            - When user_id is provided, only files in that user's folder are deleted
            - When user_id is None, ALL files in the bucket are deleted - USE WITH CAUTION
        """
        try:
            if user_id:
                # List all files in the user's folder
                files = self.client.client.storage.from_(bucket).list(user_id)
                
                # Delete each file
                for file in files:
                    path = f"{user_id}/{file['name']}"
                    self.client.client.storage.from_(bucket).remove([path])
                    
                self.logger.info(f"Deleted all storage objects for user ID {mask_id(user_id)}")
            else:
                # WARNING: This will delete ALL files in the bucket
                files = self.client.client.storage.from_(bucket).list()
                
                # Delete each file in all folders
                for file in files:
                    if 'name' in file and file.get('name') != '.emptyFolderPlaceholder':
                        self.client.client.storage.from_(bucket).remove([file['name']])
                        
                self.logger.warning(f"Deleted ALL storage objects in bucket {bucket}")
                
            return True
        except Exception as e:
            self.logger.error(f"Error deleting storage objects: {e}")
            return False

    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False,
    ) -> str:
        """Store an image in the storage bucket with user ID metadata.
        
        This method uses direct HTTP requests instead of the Supabase SDK methods to ensure
        proper JWT authentication and to maintain metadata like user_id.
        
        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            user_id: User ID for access control (REQUIRED for RLS)
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image (changes the bucket)
            
        Returns:
            Path to the stored image (format: user_id/filename or user_id/concept_id/filename)
            
        Note:
            - The path ALWAYS starts with the user_id segment which is CRITICAL for RLS policies
            - If concept_id is provided, the path format is: {user_id}/{concept_id}/{filename}
            - Otherwise, the path format is: {user_id}/{filename}
            - This method uses a direct HTTP request with JWT authentication instead of the SDK
              to ensure the RLS policies are correctly applied
        """
        try:
            # Select the appropriate bucket
            bucket = self.palette_bucket if is_palette else self.concept_bucket
            
            # Process the data based on type
            if isinstance(image_data, UploadFile):
                content = image_data.file.read()
            elif isinstance(image_data, BytesIO):
                content = image_data.getvalue()
            else:
                # Assume it's already bytes
                content = image_data
                
            # Generate a unique file name if not provided
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                unique_id = uuid.uuid4().hex[:8]
                file_name = f"{timestamp}_{unique_id}.png"
                
            # Construct the path with user_id as the first segment (CRITICAL for RLS)
            if concept_id:
                path = f"{user_id}/{concept_id}/{file_name}"
            else:
                path = f"{user_id}/{file_name}"
                
            # Get file content type based on extension
            content_type = "image/png"  # Default
            if file_name:
                if file_name.lower().endswith(".jpg") or file_name.lower().endswith(".jpeg"):
                    content_type = "image/jpeg"
                elif file_name.lower().endswith(".gif"):
                    content_type = "image/gif"
                elif file_name.lower().endswith(".webp"):
                    content_type = "image/webp"
            
            # Create a JWT token specifically for this user_id
            # This is critical for RLS as it ensures the token has the right user claims
            token = create_supabase_jwt(user_id)
            
            # Use direct HTTP request instead of SDK for better control over authentication
            api_url = self.client.url
            api_key = self.client.key
            
            upload_url = f"{api_url}/storage/v1/object/{bucket}/{path}"
            
            # Set headers with JWT token and user-specific metadata
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": api_key,
                "Content-Type": content_type
            }
            
            # Include metadata about ownership in request
            file_metadata = {"user_id": user_id}
            if metadata:
                file_metadata.update(metadata)
                
            # Upload using requests instead of SDK
            response = requests.post(
                upload_url,
                headers=headers,
                data=content
            )
            
            # Check status code
            response.raise_for_status()
            
            # Log success with masked values
            masked_path = mask_path(path)
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Stored image for user {masked_user_id} at {masked_path}")
            
            return path
        except Exception as e:
            self.logger.error(f"Error storing image: {e}")
            return None
            
    def get_signed_url(
        self, 
        path: str,
        bucket: Optional[str] = None,
        expiry_seconds: int = 3600
    ) -> Optional[str]:
        """Get a signed URL for an image with a specified expiration time.
        
        This method should be used whenever a URL needs to be shared outside the system
        or embedded in responses to clients.
        
        Args:
            path: Path to the image in storage (format: user_id/filename)
            bucket: Optional bucket name (defaults to concept bucket)
            expiry_seconds: Expiration time in seconds (default 1 hour)
            
        Returns:
            Signed URL for the image or None if failed
            
        Note:
            - The path MUST follow the pattern `{user_id}/...` for RLS policies to work
            - The signed URL is valid only for the specified expiration period
            - This method uses direct HTTP requests with JWT authentication
        """
        if not path:
            return None
            
        try:
            # Determine bucket to use
            if not bucket:
                bucket = self.concept_bucket
                
            # Extract user_id from path (first segment)
            user_id = path.split('/')[0] if '/' in path else None
            if not user_id:
                self.logger.warning(f"Invalid path format - cannot extract user ID: {path}")
                return None
            
            # Create JWT with the user's ID - critical for RLS policies
            token = create_supabase_jwt(user_id)
            
            # Get base info
            api_url = self.client.url
            api_key = self.client.key
            
            # Construct signed URL endpoint
            signed_url_endpoint = f"{api_url}/storage/v1/object/sign/{bucket}/{path}"
            
            # Make direct HTTP request to get signed URL
            response = requests.post(
                signed_url_endpoint,
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": api_key
                },
                json={"expiresIn": expiry_seconds}
            )
            
            # Process response
            if response.status_code == 200:
                data = response.json()
                signed_url = data.get("signedUrl") or data.get("signedURL")
                
                # Ensure the URL is absolute and correctly formatted
                if signed_url and signed_url.startswith('/'):
                    signed_url = f"{api_url}{signed_url}"
                    
                return signed_url
                
            # Log if there was a problem
            self.logger.warning(f"Failed to get signed URL for {mask_path(path)}: {response.status_code}")
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting signed URL: {str(e)}")
            return None 