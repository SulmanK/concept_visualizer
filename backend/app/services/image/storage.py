"""
Image storage service.

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
from app.utils.security import mask_id, mask_path

logger = logging.getLogger(__name__)

class ImageStorageService:
    """Service for storing and retrieving images from Supabase storage."""

    def __init__(self, supabase_client: Client):
        """
        Initialize the image storage service.
        
        Args:
            supabase_client: Supabase client instance
        """
        self.supabase = supabase_client
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
                    
                    # Get signed URL instead of public URL
                    url = self.get_signed_url(full_path, is_palette)
                    
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

    def get_signed_url(self, path: str, is_palette: bool = False, expiry_seconds: int = 259200) -> str:
        """
        Get a signed URL for an image with 3-day expiration by default.
        
        Args:
            path: Path to the image in storage
            is_palette: Whether the image is a palette (uses palette-images bucket)
            expiry_seconds: Expiration time in seconds (default: 3 days / 259200 seconds)
            
        Returns:
            Signed URL of the image with temporary access
        """
        # Select the appropriate bucket
        bucket_name = self.palette_bucket if is_palette else self.concept_bucket
        
        # ENHANCED LOGGING: Debug actual bucket configuration values
        self.logger.info("-------- DEBUG URL GENERATION --------")
        self.logger.info(f"BUCKET CONFIG: concept_bucket={self.concept_bucket}, palette_bucket={self.palette_bucket}")
        self.logger.info(f"BUCKET SELECTION: is_palette={is_palette}, using bucket_name={bucket_name}")
        
        # Normalize path - ensure it doesn't start with a slash
        if path.startswith('/'):
            path = path[1:]
        
        self.logger.info(f"PATH: {mask_path(path)}")
        
        # Extract user_id from the path (first segment)
        user_id = path.split('/')[0] if '/' in path else path
        self.logger.info(f"Extracted user_id from path: {mask_id(user_id)}")
        
        # Log some useful information
        self.logger.info(f"Getting signed URL for path={mask_path(path)}, bucket={bucket_name}, is_palette={is_palette}, expiry={expiry_seconds}s")
        
        try:
            # Try using the service role key if available - this has highest priority for private buckets
            try:
                from app.core.config import settings
                service_role_key = settings.SUPABASE_SERVICE_ROLE
                if service_role_key:
                    self.logger.info("Attempting to use service role key for signed URL")
                    import requests
                    
                    # Construct the signed URL endpoint
                    api_url = settings.SUPABASE_URL
                    signed_url_endpoint = f"{api_url}/storage/v1/object/sign/{bucket_name}/{path}"
                    
                    # Use service role key for authorization
                    response = requests.post(
                        signed_url_endpoint,
                        headers={
                            "Authorization": f"Bearer {service_role_key}",
                            "apikey": service_role_key
                        },
                        json={"expiresIn": expiry_seconds}
                    )
                    
                    self.logger.info(f"Service role key signed URL response: Status {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        if "signedURL" in result:
                            signed_url = result["signedURL"]
                            # Ensure the URL is absolute and correctly formatted
                            if signed_url.startswith('/'):
                                # Make sure URL has the correct format with /storage/v1/
                                if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                                    signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                                signed_url = f"{settings.SUPABASE_URL}{signed_url}"
                                self.logger.info(f"Converted to absolute URL: {mask_path(signed_url)}")
                            self.logger.info("Generated signed URL with service role key")
                            return signed_url
                        elif "signedUrl" in result:
                            signed_url = result["signedUrl"]
                            # Ensure the URL is absolute and correctly formatted
                            if signed_url.startswith('/'):
                                # Make sure URL has the correct format with /storage/v1/
                                if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                                    signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                                signed_url = f"{settings.SUPABASE_URL}{signed_url}"
                                self.logger.info(f"Converted to absolute URL: {mask_path(signed_url)}")
                            self.logger.info("Generated signed URL with service role key")
                            return signed_url
                    else:
                        self.logger.warning(f"Service role key request failed: {response.status_code}, {response.text}")
            except Exception as role_key_error:
                self.logger.warning(f"Service role key approach failed: {str(role_key_error)}")
            
            # Fall back to using Supabase's SDK to create a signed URL
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                response = self.supabase.client.storage.from_(bucket_name).create_signed_url(
                    path=path,
                    expires_in=expiry_seconds
                )
            else:
                # Legacy client compatibility
                response = self.supabase.storage.from_(bucket_name).create_signed_url(
                    path=path,
                    expires_in=expiry_seconds
                )
            
            self.logger.info(f"SDK create_signed_url response: {response}")
            
            # Check for signedUrl (lowercase u) or signedURL (uppercase URL)
            if response and isinstance(response, dict):
                # Extract data field if it exists (newer SDK versions)
                data = response.get('data', response)
                
                # Check if we got data
                if not data:
                    self.logger.warning(f"No data in signed URL response: {response}")
                    
                if isinstance(data, dict):
                    # Try each known field name for the signed URL
                    signed_url = data.get('signedUrl') or data.get('signedURL')
                    
                    if signed_url:
                        self.logger.info(f"Generated signed URL: {mask_path(signed_url)}")
                        
                        # Ensure the URL is absolute and correctly formatted
                        if signed_url.startswith('/'):
                            from app.core.config import settings
                            # Make sure URL has the correct format with /storage/v1/
                            if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                                signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                            signed_url = f"{settings.SUPABASE_URL}{signed_url}"
                            self.logger.info(f"Converted to absolute URL: {mask_path(signed_url)}")
                            
                        return signed_url
            
            self.logger.warning(f"Failed to generate signed URL with SDK: {response}")
            
            # Fallback to manual REST API approach
            from app.utils.jwt_utils import create_supabase_jwt
            from app.core.config import settings
            
            # Generate a JWT token with the user_id
            jwt_token = create_supabase_jwt(user_id, expiry_seconds)
            
            # Build signed URL with the JWT token
            api_url = settings.SUPABASE_URL
            api_key = settings.SUPABASE_KEY
            
            # Construct the signed URL endpoint
            signed_url_endpoint = f"{api_url}/storage/v1/object/sign/{bucket_name}/{path}"
            
            # Use requests to call the sign endpoint with our JWT
            import requests
            response = requests.post(
                signed_url_endpoint,
                headers={
                    "Authorization": f"Bearer {jwt_token}",
                    "apikey": api_key
                },
                json={"expiresIn": expiry_seconds}
            )
            
            if response.status_code == 200:
                result = response.json()
                if "signedURL" in result:
                    signed_url = result["signedURL"]
                    # Ensure the URL is absolute and correctly formatted
                    if signed_url.startswith('/'):
                        # Make sure URL has the correct format with /storage/v1/
                        if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                            signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                        signed_url = f"{api_url}{signed_url}"
                    self.logger.info(f"Manual signed URL created: {mask_path(signed_url)}")
                    return signed_url
                elif "signedUrl" in result:
                    signed_url = result["signedUrl"]
                    # Ensure the URL is absolute and correctly formatted
                    if signed_url.startswith('/'):
                        # Make sure URL has the correct format with /storage/v1/
                        if '/storage/v1/' not in signed_url and '/object/sign/' in signed_url:
                            signed_url = signed_url.replace('/object/sign/', '/storage/v1/object/sign/')
                        signed_url = f"{api_url}{signed_url}"
                    self.logger.info(f"Manual signed URL created: {mask_path(signed_url)}")
                    return signed_url
            else:
                self.logger.warning(f"Manual JWT approach failed: Status {response.status_code}, {response.text}")
            
            # If that also failed, create a download URL that will direct through our REST API
            # This will still require authentication but may be more reliable
            fallback_url = f"{api_url}/storage/v1/object/download/{bucket_name}/{path}?token={jwt_token}"
            self.logger.warning(f"Using download URL fallback: {mask_path(fallback_url)}")
            return fallback_url
            
        except Exception as e:
            self.logger.error(f"Error generating signed URL: {str(e)}")
            
            # Last resort fallback
            try:
                # Try to generate an authenticated URL using a different approach
                from app.utils.jwt_utils import create_supabase_jwt
                from app.core.config import settings
                
                jwt_token = create_supabase_jwt(user_id, expiry_seconds)
                
                # For private buckets, the authenticated endpoint is more reliable than public
                fallback_url = f"{settings.SUPABASE_URL}/storage/v1/object/authenticated/{bucket_name}/{path}?token={jwt_token}"
                self.logger.warning(f"Using fallback URL: {mask_path(fallback_url)}")
                return fallback_url
            except Exception as inner_e:
                self.logger.error(f"Even fallback method failed: {str(inner_e)}")
                # Do not return a public URL for a private bucket as it won't work
                return f"{settings.SUPABASE_URL}/storage/v1/object/authenticated/{bucket_name}/{path}"

    async def authenticate_url(self, path: str, user_id: str, is_palette: bool = False) -> str:
        """
        Get a signed URL for authenticated access.
        
        Args:
            path: Path to the image in storage
            user_id: User ID for authentication
            is_palette: Whether the image is a palette
            
        Returns:
            Signed URL with temporary access
        """
        # Use our get_signed_url method which returns signed URLs
        return self.get_signed_url(path, is_palette)

    def get_image_with_token(
        self,
        path: str,
        token: str,
        is_palette: bool = False
    ) -> bytes:
        """
        Get image data using a JWT token for authentication.
        
        Args:
            path: Path to the image in storage
            token: JWT token for authentication
            is_palette: Whether this is a palette image
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageNotFoundError: If image doesn't exist
            ImageStorageError: On other errors
        """
        try:
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Set Authorization header with the JWT token
            headers = {
                "Authorization": f"Bearer {token}"
            }
            
            # Fetch image using the token
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                response = self.supabase.client.storage.from_(bucket_name).download(
                    path=path,
                    headers=headers
                )
            else:
                response = self.supabase.storage.from_(bucket_name).download(
                    path=path,
                    headers=headers
                )
                
            return response
            
        except Exception as e:
            error_msg = f"Failed to get image {path}: {str(e)}"
            self.logger.error(error_msg)
            
            if "404" in str(e) or "not found" in str(e).lower():
                raise ImageNotFoundError(f"Image not found: {path}")
                
            # Access denied errors
            if "403" in str(e) or "forbidden" in str(e).lower() or "access denied" in str(e).lower():
                self.logger.warning(f"Access denied to image {path}, possibly due to JWT validation failure")
                raise ImageStorageError(f"Access denied to image: {path}")
                
            raise ImageStorageError(error_msg)

    def get_image_by_path(self, path: str, is_palette: bool = False) -> bytes:
        """
        Retrieve an image from storage using the exact path we know exists.
        This method is for internal use after storing an image when we know
        the path is valid and want to avoid using a signed URL that may have 
        cache or CDN issues.
        
        Args:
            path: Path of the image in storage (e.g. user_id/concept_id/filename)
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
            
            self.logger.info(f"Directly accessing image with path: {mask_path(path)} in bucket: {bucket_name}")
            
            # For Supabase, use the low-level REST API to get the file
            # This bypasses any caching issues with signed URLs
            api_url = settings.SUPABASE_URL
            api_key = settings.SUPABASE_KEY  # Use the regular key instead of service key
            
            # Create a JWT token for access (we need this for bucket access)
            user_id = path.split('/')[0]  # First segment is user_id
            from app.utils.jwt_utils import create_supabase_jwt
            token = create_supabase_jwt(user_id)
            
            # First try the standard object download path (using JWT for RLS)
            download_url = f"{api_url}/storage/v1/object/{bucket_name}/{path}"
            
            # Set headers with JWT token for RLS
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": api_key
            }
            
            # Get the file using JWT token for RLS authentication
            response = requests.get(
                download_url,
                headers=headers
            )
            
            # Check if successful
            if response.status_code == 200:
                return response.content
            
            # If standard access fails, try using the direct Supabase client download
            # This works through our regular SDK methods
            try:
                if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                    response = self.supabase.client.storage.from_(bucket_name).download(path)
                else:
                    response = self.supabase.storage.from_(bucket_name).download(path)
                return response
            except Exception as e:
                # If that also fails, log the error and continue to raise the original error
                self.logger.warning(f"Failed to get image through SDK: {str(e)}")
            
            # Handle errors from original REST API call
            error_msg = f"Failed to get image {path} (status: {response.status_code}): {response.text}"
            self.logger.error(error_msg)
            
            if response.status_code == 404:
                raise ImageNotFoundError(f"Image not found: {path}")
            
            raise ImageStorageError(error_msg)
            
        except (ImageNotFoundError, ImageStorageError):
            # Re-raise specific errors
            raise
        except Exception as e:
            error_msg = f"Failed to get image {path}: {str(e)}"
            self.logger.error(error_msg)
            
            if "404" in str(e) or "not found" in str(e).lower():
                raise ImageNotFoundError(f"Image not found: {path}")
                
            raise ImageStorageError(error_msg) 