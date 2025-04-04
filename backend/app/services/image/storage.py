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
        self.bucket_name = "images"
        self._ensure_bucket_exists()
        self.logger = logging.getLogger(__name__)

    def _ensure_bucket_exists(self) -> None:
        """
        Ensure that the images bucket exists.
        Creates it if it doesn't exist.
        """
        try:
            buckets = self.supabase.storage.list_buckets()
            bucket_names = [bucket["name"] for bucket in buckets]
            
            if self.bucket_name not in bucket_names:
                self.logger.info(f"Creating storage bucket: {self.bucket_name}")
                self.supabase.storage.create_bucket(self.bucket_name, public=True)
                
        except Exception as e:
            self.logger.warning(f"Failed to check/create bucket {self.bucket_name}: {str(e)}")
            # Continue anyway, as bucket might already exist
    
    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Store an image in the storage bucket.
        
        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            
        Returns:
            Public URL of the stored image
            
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
                
            # Generate a unique file name if not provided
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = str(uuid.uuid4())[:8]
                
                # Try to determine file format from content
                try:
                    img = Image.open(BytesIO(content))
                    ext = img.format.lower() if img.format else "png"
                except:
                    ext = "png"  # Default extension
                    
                file_name = f"{timestamp}_{random_id}.{ext}"
                
            # Create subfolder path based on concept_id if provided
            path = f"{concept_id}/{file_name}" if concept_id else file_name
                
            # Upload to storage
            self.supabase.storage.from_(self.bucket_name).upload(
                path=path,
                file=content,
                file_options={"content-type": f"image/{ext}"}
            )
            
            # Get the public URL
            image_url = self.supabase.storage.from_(self.bucket_name).get_public_url(path)
            
            # Store metadata if provided
            if metadata and concept_id:
                self._store_image_metadata(path, concept_id, metadata)
                
            return image_url
            
        except Exception as e:
            error_msg = f"Failed to store image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_image(self, image_path: str) -> bytes:
        """
        Retrieve an image from storage.
        
        Args:
            image_path: Path of the image in storage
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        try:
            response = self.supabase.storage.from_(self.bucket_name).download(image_path)
            return response
            
        except Exception as e:
            error_msg = f"Failed to get image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            
            if "404" in str(e) or "not found" in str(e).lower():
                raise ImageNotFoundError(f"Image not found: {image_path}")
                
            raise ImageStorageError(error_msg)
    
    def _store_image_metadata(self, image_path: str, concept_id: str, metadata: Dict[str, Any]) -> None:
        """
        Store metadata about an image in the database.
        
        Args:
            image_path: Path of the image in storage
            concept_id: Concept ID associated with the image
            metadata: Metadata to store
        """
        try:
            # Store in a database table for image metadata
            data = {
                "path": image_path,
                "concept_id": concept_id,
                "metadata": metadata,
                "created_at": datetime.now().isoformat()
            }
            
            self.supabase.table("image_metadata").insert(data).execute()
            
        except Exception as e:
            # Log but don't fail the overall operation
            self.logger.warning(f"Failed to store image metadata: {str(e)}")
            
    def delete_image(self, image_path: str) -> bool:
        """
        Delete an image from storage.
        
        Args:
            image_path: Path of the image in storage
            
        Returns:
            True if deletion was successful
            
        Raises:
            ImageStorageError: If image deletion fails
        """
        try:
            self.supabase.storage.from_(self.bucket_name).remove([image_path])
            
            # Also delete metadata if it exists
            try:
                self.supabase.table("image_metadata").delete().eq("path", image_path).execute()
            except Exception as e:
                self.logger.warning(f"Failed to delete image metadata: {str(e)}")
                
            return True
            
        except Exception as e:
            if "404" in str(e) or "not found" in str(e).lower():
                self.logger.warning(f"Image not found during deletion: {image_path}")
                return False
                
            error_msg = f"Failed to delete image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
            
    def list_images(self, concept_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List images in storage, optionally filtered by concept ID.
        
        Args:
            concept_id: Optional concept ID to filter by
            
        Returns:
            List of image information dictionaries
            
        Raises:
            ImageStorageError: If listing images fails
        """
        try:
            # List files in the bucket, potentially in a subfolder
            path = f"{concept_id}" if concept_id else ""
            response = self.supabase.storage.from_(self.bucket_name).list(path)
            
            # Transform the response into a more usable format
            images = []
            for item in response:
                if "name" in item and not item.get("id", "").endswith("/"):  # Skip folders
                    full_path = f"{path}/{item['name']}" if path else item["name"]
                    url = self.supabase.storage.from_(self.bucket_name).get_public_url(full_path)
                    
                    images.append({
                        "path": full_path,
                        "name": item["name"],
                        "url": url,
                        "size": item.get("metadata", {}).get("size", 0),
                        "created_at": item.get("created_at", ""),
                        "concept_id": concept_id
                    })
            
            return images
            
        except Exception as e:
            error_msg = f"Failed to list images: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg) 