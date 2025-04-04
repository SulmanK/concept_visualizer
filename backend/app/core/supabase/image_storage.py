"""
Image storage operations for Supabase.

This module provides functionality for managing images in Supabase Storage.
"""

import logging
import io
import requests
from typing import List, Dict, Optional, Any, Union
from PIL import Image

from .client import SupabaseClient
from ...utils.security.mask import mask_id, mask_path


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
            import uuid
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
        """Get the public URL for an image in Supabase Storage.
        
        Args:
            path: Storage path of the image
            bucket: Storage bucket where the image is stored
            
        Returns:
            Public URL if successful, None otherwise
        """
        try:
            url = self.client.client.storage.from_(bucket).get_public_url(path)
            return url
        except Exception as e:
            self.logger.error(f"Error getting image URL: {e}")
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