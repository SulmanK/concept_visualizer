"""
Image storage service.

This module provides functionality for storing and retrieving images
from Supabase storage.
"""

import logging
import uuid
from typing import Optional, Dict, Any, Union, List
from io import BytesIO
from datetime import datetime

from fastapi import UploadFile
from supabase import Client, create_client
from PIL import Image

logger = logging.getLogger(__name__)

class ImageStorageError(Exception):
    """Base exception for image storage errors."""
    pass

class ImageNotFoundError(ImageStorageError):
    """Exception raised when an image is not found."""
    pass


class ImageStorageService:
    """Service for storing and retrieving images from Supabase storage."""

    def __init__(self, supabase_client: Client):
        """
        Initialize the image storage service.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.supabase = supabase_client
        # The buckets exist in Supabase and are public
        self.concept_bucket = "concept-images"
        self.palette_bucket = "palette-images"
        self.logger = logging.getLogger(__name__)
    
    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> str:
        """
        Store an image in the storage bucket.
        
        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            is_palette: Whether the image is a palette (uses palette-images bucket)
            
        Returns:
            Public URL of the stored image
            
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
                
            # Create subfolder path based on concept_id if provided
            path = f"{concept_id}/{file_name}" if concept_id else file_name
                
            # Upload to storage
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                # Set content type based on extension
                content_type = "image/png"  # Default content type
                if ext == "jpg" or ext == "jpeg":
                    content_type = "image/jpeg"
                elif ext == "gif":
                    content_type = "image/gif"
                elif ext == "webp":
                    content_type = "image/webp"
                
                # Set file options with correct content type
                file_options = {"content-type": content_type}
                
                self.supabase.client.storage.from_(bucket_name).upload(
                    path=path,
                    file=content,
                    file_options=file_options
                )
                
                # Get the public URL
                image_url = self.supabase.client.storage.from_(bucket_name).get_public_url(path)
            else:
                # Direct access if storage attribute exists on the client
                # Set content type based on extension
                content_type = "image/png"  # Default content type
                if ext == "jpg" or ext == "jpeg":
                    content_type = "image/jpeg"
                elif ext == "gif":
                    content_type = "image/gif"
                elif ext == "webp":
                    content_type = "image/webp"
                
                # Set file options with correct content type
                file_options = {"content-type": content_type}
                
                self.supabase.storage.from_(bucket_name).upload(
                    path=path,
                    file=content,
                    file_options=file_options
                )
                
                # Get the public URL
                image_url = self.supabase.storage.from_(bucket_name).get_public_url(path)
            
            # Store metadata if provided and we really need to store it
            # Currently we're not storing metadata so skip this to avoid errors
            # if metadata and concept_id:
            #     self._store_image_metadata(path, concept_id, bucket_name, metadata)
                
            return image_url
            
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
            
            # We don't have image_metadata table, so skip this
            # try:
            #     self.supabase.table("image_metadata").delete().eq("path", image_path).eq("bucket", bucket_name).execute()
            # except Exception as e:
            #     self.logger.warning(f"Failed to delete image metadata: {str(e)}")
                
            return True
            
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                self.logger.warning(f"Image not found during deletion: {image_path}")
                return False
                
            error_msg = f"Failed to delete image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
            
    def list_images(self, concept_id: Optional[str] = None, is_palette: bool = False) -> List[Dict[str, Any]]:
        """
        List images in storage, optionally filtered by concept ID.
        
        Args:
            concept_id: Optional concept ID to filter by
            is_palette: Whether to list palette images (uses palette-images bucket)
            
        Returns:
            List of image information dictionaries
            
        Raises:
            ImageStorageError: If listing images fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # List files in the bucket, potentially in a subfolder
            path = f"{concept_id}" if concept_id else ""
            
            # Try storage access through client attribute first, then fall back to direct access
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                response = self.supabase.client.storage.from_(bucket_name).list(path)
            else:
                response = self.supabase.storage.from_(bucket_name).list(path)
            
            # Transform the response into a more usable format
            images = []
            for item in response:
                if "name" in item and not item.get("id", "").endswith("/"):  # Skip folders
                    full_path = f"{path}/{item['name']}" if path else item["name"]
                    
                    # Get public URL based on the available access pattern
                    if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                        url = self.supabase.client.storage.from_(bucket_name).get_public_url(full_path)
                    else:
                        url = self.supabase.storage.from_(bucket_name).get_public_url(full_path)
                    
                    images.append({
                        "path": full_path,
                        "name": item["name"],
                        "url": url,
                        "size": item.get("metadata", {}).get("size", 0),
                        "created_at": item.get("created_at", ""),
                        "concept_id": concept_id,
                        "bucket": bucket_name
                    })
            
            return images
            
        except Exception as e:
            error_msg = f"Failed to list images: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_public_url(self, image_path: str, is_palette: bool = False) -> str:
        """
        Get the public URL for an image in storage.
        
        Args:
            image_path: Path to the image in storage
            is_palette: Whether this is a palette image (uses palette-images bucket)
            
        Returns:
            Public URL for the image
            
        Raises:
            ImageStorageError: If URL generation fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Get the public URL
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                return self.supabase.client.storage.from_(bucket_name).get_public_url(image_path)
            else:
                return self.supabase.storage.from_(bucket_name).get_public_url(image_path)
                
        except Exception as e:
            error_msg = f"Failed to get public URL for image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg) 