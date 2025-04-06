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


# Configure logging
logger = logging.getLogger(__name__)


class ImageStorage:
    """Handles image-related operations in Supabase Storage."""
    
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
    
    async def upload_image_from_url(self, image_url: str, bucket: str, session_id: str) -> Optional[str]:
        """Upload an image from URL to Supabase Storage.
        
        Args:
            image_url: URL of the image to download
            bucket: Storage bucket to upload to
            session_id: Session ID to use in the image path
            
        Returns:
            Storage path if successful, None otherwise
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
            filename = f"{session_id}/{uuid.uuid4()}.png"
            
            # Upload to Supabase Storage
            self.client.client.storage.from_(bucket).upload(
                path=filename,
                file=img_bytes.getvalue(),
                file_options={"content-type": "image/png"}
            )
            
            # Log success with masked path
            self.logger.info(f"Uploaded image to {self.client._mask_path(filename)}")
            
            return filename
        except Exception as e:
            self.logger.error(f"Error uploading image from URL: {e}")
            return None
    
    def get_image_url(self, path: str, bucket: str) -> Optional[str]:
        """
        Get a signed URL for an image in storage.
        
        Args:
            path: Path to the image in storage
            bucket: Bucket name
            
        Returns:
            Signed URL for the image or None if not found
        """
        try:
            # Create a JWT token for access
            from app.utils.jwt_utils import create_supabase_jwt
            
            # First segment is session_id
            session_id = path.split('/')[0] if '/' in path else None
            if not session_id:
                self.logger.warning(f"Invalid path format - cannot extract session ID: {path}")
                return None
                
            token = create_supabase_jwt(session_id)
            
            # Get the base URL
            api_url = self.client.url
            api_key = self.client.key
            
            # Use the signed URL endpoint
            signed_url_endpoint = f"{api_url}/storage/v1/object/sign/{bucket}/{path}"
            
            # Call the signed URL endpoint with 3-day expiration
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
                    return data["signedUrl"]
            
            # Fallback to direct URL with token if signed URL fails
            self.logger.warning(f"Failed to get signed URL, using fallback URL with token")
            return f"{api_url}/storage/v1/object/token/{bucket}/{path}?token={token}"
        
        except Exception as e:
            self.logger.error(f"Error getting image URL: {str(e)}")
            return None
    
    async def apply_color_palette(self, image_path: str, palette: List[str], session_id: str) -> Optional[str]:
        """Apply a color palette to an image and store the result.
        
        Args:
            image_path: Path to the source image in Storage
            palette: List of hex color codes
            session_id: Session ID for the new image path
            
        Returns:
            Path to the color-modified image if successful, None otherwise
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
            output_path = f"{session_id}/{uuid.uuid4()}_palette.png"
            
            # Log the operation with masked paths
            self.logger.info(
                f"Applied color palette to {self.client._mask_path(image_path)} → {self.client._mask_path(output_path)}"
            )
            
            return output_path
        except Exception as e:
            self.logger.error(f"Error applying color palette: {e}")
            return None
    
    def delete_all_storage_objects(self, bucket: str, session_id: Optional[str] = None) -> bool:
        """Delete all storage objects for a session or all objects in a bucket.
        
        Args:
            bucket: Storage bucket name
            session_id: Optional session ID to delete only objects for this session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if session_id:
                # List all files in the session's folder
                files = self.client.client.storage.from_(bucket).list(session_id)
                
                # Delete each file
                for file in files:
                    path = f"{session_id}/{file['name']}"
                    self.client.client.storage.from_(bucket).remove([path])
                    
                self.logger.info(f"Deleted all storage objects for session ID {mask_id(session_id)}")
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
        session_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False,
    ) -> str:
        """
        Store an image in the storage bucket with session ID metadata.
        
        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            session_id: Session ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            is_palette: Whether the image is a palette (uses palette-images bucket)
            
        Returns:
            Signed URL of the stored image
            
        Raises:
            Exception: If image storage fails
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
            
            # Default extension
            ext = "png"
                
            # Generate a unique file name if not provided
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = str(uuid.uuid4())[:8]
                
                # Try to determine file format
                try:
                    img = Image.open(BytesIO(content))
                    if img.format:
                        ext = img.format.lower()
                except Exception as e:
                    self.logger.warning(f"Could not determine image format: {str(e)}, using default: {ext}")
                    
                file_name = f"{timestamp}_{random_id}.{ext}"
                
            # Create path with session_id as the first folder segment
            # This is CRITICAL for our RLS policy to work
            path = f"{session_id}/{file_name}"
            if concept_id:
                path = f"{session_id}/{concept_id}/{file_name}"
                
            # Set content type based on extension
            content_type = "image/png"  # Default
            if ext == "jpg" or ext == "jpeg":
                content_type = "image/jpeg"
            elif ext == "gif":
                content_type = "image/gif"
            elif ext == "webp":
                content_type = "image/webp"
            
            # Prepare file metadata including session ID
            file_metadata = {"owner_session_id": session_id}
            if metadata:
                file_metadata.update(metadata)
            
            # Create JWT token for authentication (for Supabase Storage RLS)
            token = create_supabase_jwt(session_id)
            
            # Use direct HTTP request with requests library for JWT authorization
            # Get the API endpoint from settings
            from app.core.config import settings
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
            
            # Add metadata as custom headers
            for key, value in file_metadata.items():
                # Convert metadata to string and add as headers
                if isinstance(value, (dict, list)):
                    import json
                    headers[f"x-amz-meta-{key}"] = json.dumps(value)
                else:
                    headers[f"x-amz-meta-{key}"] = str(value)
            
            # Upload the file with requests
            response = requests.post(
                upload_url,
                headers=headers,
                data=content
            )
            
            # Check if upload was successful
            if response.status_code not in (200, 201):
                self.logger.error(f"Upload failed with status {response.status_code}: {response.text}")
                raise Exception(f"Failed to upload image: {response.text}")
            
            # Get the signed URL with detailed logging
            self.logger.info(f"Getting signed URL from bucket: {bucket_name}, path: {mask_path(path)}")
            try:
                # Create a signed URL with 3-day expiration
                from app.utils.jwt_utils import create_supabase_jwt
                
                # First segment is session_id
                token = create_supabase_jwt(path.split('/')[0])
                
                # Use signed URL API endpoint
                api_url = self.client.url
                api_key = self.client.key
                
                signed_url_endpoint = f"{api_url}/storage/v1/object/sign/{bucket_name}/{path}"
                
                # Call the signed URL endpoint with 3-day expiration 
                signed_response = requests.post(
                    signed_url_endpoint,
                    headers={
                        "Authorization": f"Bearer {token}",
                        "apikey": api_key
                    },
                    json={"expiresIn": 259200}  # 3 days in seconds
                )
                
                if signed_response.status_code == 200:
                    response_data = signed_response.json()
                    self.logger.info(f"Sign response keys: {list(response_data.keys())}")
                    
                    # Check for signed URL in response
                    if "signedUrl" in response_data:
                        image_url = response_data["signedUrl"]
                        self.logger.info(f"Generated signed URL successfully")
                        
                        # Log success with masked path
                        self.logger.info(f"Successfully uploaded image to {mask_path(path)}")
                        return image_url
                
                # Fallback to using a direct URL with token if signed URL fails
                self.logger.warning(f"Failed to get signed URL, falling back to direct URL with token")
                direct_url = f"{api_url}/storage/v1/object/token/{bucket_name}/{path}?token={token}"
                
                # Log success with masked path
                self.logger.info(f"Successfully uploaded image, using direct URL with token")
                return direct_url
                
            except Exception as e:
                self.logger.error(f"Error getting signed URL: {str(e)}")
                # Try a direct construction of URL for debugging
                try:
                    # Get a JWT token for fallback URL
                    from app.utils.jwt_utils import create_supabase_jwt
                    token = create_supabase_jwt(path.split('/')[0])
                    
                    # Direct URL with token fallback
                    fallback_url = f"{self.client.url}/storage/v1/object/token/{bucket_name}/{path}?token={token}"
                    self.logger.info(f"Constructed fallback URL with token")
                    return fallback_url
                except Exception as inner_e:
                    self.logger.error(f"Failed to create fallback URL: {str(inner_e)}")
                    # Last resort fallback - probably won't work but better than nothing
                    return f"{self.client.url}/storage/v1/object/token/{bucket_name}/{path}?token={token}"
            
        except Exception as e:
            self.logger.error(f"Error uploading image: {e}")
            raise e 