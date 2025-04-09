"""
Export service for converting and exporting images.

This module provides services for exporting images in different formats.
"""

import logging
import os
import tempfile
import base64
from io import BytesIO
from typing import Dict, Literal, Optional, Tuple, Any, BinaryIO
from fastapi import Depends, HTTPException
from PIL import Image

import vtracer
from app.core.supabase import SupabaseClient, get_supabase_client
from app.core.supabase.image_storage import ImageStorage
from app.services.interfaces import ImageServiceInterface
from app.services.image import get_image_service
from app.services.storage import get_concept_storage_service
from app.utils.security.mask import mask_id, mask_path

# Configure logging
logger = logging.getLogger(__name__)


class ExportError(Exception):
    """Exception raised for image export errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ExportService:
    """Service for exporting images in different formats."""
    
    def __init__(
        self, 
        supabase_client: SupabaseClient = Depends(get_supabase_client),
        image_service: ImageServiceInterface = Depends(get_image_service),
    ):
        """Initialize export service with required dependencies.
        
        Args:
            supabase_client: Client for Supabase operations
            image_service: Service for image operations
        """
        self.supabase_client = supabase_client
        self.image_storage = ImageStorage(supabase_client)
        self.image_service = image_service
        self.logger = logging.getLogger("export_service")
    
    async def process_export(
        self,
        image_identifier: str,
        target_format: Literal["png", "jpg", "svg"],
        target_size: Literal["small", "medium", "large", "original"],
        user_id: str,
        svg_params: Optional[Dict] = None,
        storage_bucket: str = "concept-images",
    ) -> Tuple[bytes, str, str]:
        """
        Process the image export request.
        
        Args:
            image_identifier: Storage path identifier for the image
            target_format: Target format for export (png, jpg, svg)
            target_size: Target size for export (small, medium, large, original)
            user_id: Current user ID
            svg_params: Optional parameters for SVG conversion
            storage_bucket: Storage bucket where the image is stored
            
        Returns:
            Tuple containing:
                - Processed image bytes
                - Filename for the exported file
                - Content type for the exported file
            
        Raises:
            ExportError: If the export processing fails
            HTTPException: If there are permission issues or other errors
        """
        try:
            # Verify user has access to this image (must be owner)
            masked_image_id = mask_path(image_identifier)
            masked_user_id = mask_id(user_id)
            self.logger.info(
                f"Processing export for image: {masked_image_id}, "
                f"format: {target_format}, size: {target_size}, "
                f"user: {masked_user_id}, bucket: {storage_bucket}"
            )
            
            # Ensure the image belongs to the authenticated user
            if not image_identifier.startswith(f"{user_id}/"):
                self.logger.warning(
                    f"User {masked_user_id} attempted to access unauthorized image: {masked_image_id}"
                )
                raise HTTPException(status_code=403, detail="Access denied to this image")
            
            # Fetch the image from storage
            image_bytes = await self._fetch_image(image_identifier, storage_bucket)
            
            # Process the image based on requested format and size
            if target_format == "svg":
                # Process for SVG conversion
                processed_bytes, filename, content_type = await self._convert_to_svg(
                    image_bytes, image_identifier, svg_params
                )
            else:
                # Process for PNG/JPG
                processed_bytes, filename, content_type = await self._process_raster_image(
                    image_bytes, image_identifier, target_format, target_size
                )
            
            self.logger.info(
                f"Export processed successfully: {mask_path(filename)}, "
                f"size: {len(processed_bytes)}, type: {content_type}"
            )
            
            return processed_bytes, filename, content_type
        except HTTPException:
            # Re-raise HTTP exceptions directly
            raise
        except Exception as e:
            self.logger.error(f"Error processing export: {str(e)}")
            raise ExportError(f"Error processing export: {str(e)}")
    
    async def _fetch_image(self, image_identifier: str, storage_bucket: str = "concept-images") -> bytes:
        """
        Fetch image bytes from storage.
        
        Args:
            image_identifier: Storage path identifier for the image
            storage_bucket: Storage bucket where the image is stored
            
        Returns:
            Image bytes
            
        Raises:
            ExportError: If fetching the image fails
        """
        try:
            # Use the specified storage bucket
            self.logger.info(f"Fetching image from bucket: {storage_bucket}, path: {mask_path(image_identifier)}")
            
            # Use the Supabase service role client for elevated permissions
            service_client = self.supabase_client.get_service_role_client()
            
            # Get the image data with service role for elevated permissions
            response = service_client.storage.from_(storage_bucket).download(image_identifier)
            
            if not response:
                self.logger.error(f"Failed to fetch image {mask_path(image_identifier)} from bucket {storage_bucket}")
                raise ExportError(f"Failed to fetch image: {os.path.basename(image_identifier)}")
            
            return response
        except Exception as e:
            self.logger.error(f"Error fetching image {mask_path(image_identifier)}: {str(e)}")
            raise ExportError(f"Error fetching image: {str(e)}")
    
    async def _process_raster_image(
        self,
        image_bytes: bytes,
        image_identifier: str,
        target_format: Literal["png", "jpg"],
        target_size: Literal["small", "medium", "large", "original"],
    ) -> Tuple[bytes, str, str]:
        """
        Process a raster image (resize and convert format).
        
        Args:
            image_bytes: Original image bytes
            image_identifier: Original image identifier
            target_format: Target format (png, jpg)
            target_size: Target size (small, medium, large, original)
            
        Returns:
            Tuple containing:
                - Processed image bytes
                - Filename for the exported file
                - Content type for the exported file
        """
        try:
            # Open the image with PIL
            image = Image.open(BytesIO(image_bytes))
            
            # Resize if requested
            if target_size != "original":
                image = self._resize_image(image, target_size)
            
            # Convert format if needed
            output_format = target_format.upper()
            if output_format == "JPG":
                output_format = "JPEG"  # PIL uses JPEG, not JPG
            
            # Save to BytesIO
            output = BytesIO()
            
            # Save with appropriate quality/compression settings
            if output_format == "JPEG":
                image = image.convert("RGB")  # Ensure RGB mode for JPEG
                image.save(output, format=output_format, quality=90)
            else:
                image.save(output, format=output_format)
                
            output.seek(0)
            processed_bytes = output.getvalue()
            
            # Generate appropriate filename
            base_name = os.path.basename(image_identifier)
            name_without_ext = os.path.splitext(base_name)[0]
            new_filename = f"{name_without_ext}.{target_format.lower()}"
            
            # Set content type
            content_type = f"image/{target_format.lower()}"
            if target_format.lower() == "jpg":
                content_type = "image/jpeg"
                
            return processed_bytes, new_filename, content_type
        except Exception as e:
            self.logger.error(f"Error processing raster image: {str(e)}")
            raise ExportError(f"Error processing image: {str(e)}")
    
    def _resize_image(self, image: Image.Image, target_size: str) -> Image.Image:
        """
        Resize an image based on the target size.
        
        Args:
            image: PIL Image to resize
            target_size: Target size (small, medium, large)
            
        Returns:
            Resized PIL Image
        """
        original_width, original_height = image.size
        
        # Define size mapping (max dimensions for each size)
        size_mapping = {
            "small": 500,
            "medium": 1000,
            "large": 2000
        }
        
        max_dimension = size_mapping.get(target_size)
        if not max_dimension:
            return image  # Return original if size not recognized
        
        # Calculate new dimensions preserving aspect ratio
        if original_width > original_height:
            new_width = min(original_width, max_dimension)
            new_height = int(original_height * (new_width / original_width))
        else:
            new_height = min(original_height, max_dimension)
            new_width = int(original_width * (new_height / original_height))
        
        # Only resize if the image is larger than the target
        if original_width > new_width or original_height > new_height:
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return image
    
    async def _convert_to_svg(
        self,
        image_bytes: bytes,
        image_identifier: str,
        svg_params: Optional[Dict] = None,
    ) -> Tuple[bytes, str, str]:
        """
        Convert a raster image to SVG format.
        
        Args:
            image_bytes: Original image bytes
            image_identifier: Original image identifier
            svg_params: Optional parameters for SVG conversion
            
        Returns:
            Tuple containing:
                - SVG bytes
                - Filename for the exported file
                - Content type for the exported file
        """
        try:
            # Create temporary files for input and output
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_in_file, \
                 tempfile.NamedTemporaryFile(delete=False, suffix=".svg") as temp_out_file:
                
                temp_in_path = temp_in_file.name
                temp_out_path = temp_out_file.name
                
                # Close files so they can be used by other processes
                temp_in_file.close()
                temp_out_file.close()
                
                try:
                    # Process the image with PIL to ensure the format is correct
                    image = Image.open(BytesIO(image_bytes))
                    
                    # Apply default max size limit for SVG conversion
                    max_size = svg_params.get("max_size", 1024) if svg_params else 1024
                    
                    # Resize if needed
                    if max_size and (image.width > max_size or image.height > max_size):
                        # Preserve aspect ratio
                        if image.width > image.height:
                            new_width = max_size
                            new_height = int(image.height * (max_size / image.width))
                        else:
                            new_height = max_size
                            new_width = int(image.width * (max_size / image.height))
                        
                        image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    
                    # Save to temporary input file
                    image.save(temp_in_path, format="PNG")
                    
                    # Get SVG parameters
                    color_mode = "color"
                    if svg_params and "color_mode" in svg_params:
                        color_mode = svg_params["color_mode"]
                    
                    # Process the image using the vtracer Python API
                    self.logger.info(
                        f"Converting image to SVG: {os.path.basename(temp_in_path)} -> "
                        f"{os.path.basename(temp_out_path)}"
                    )
                    
                    try:
                        # Read the input image
                        with open(temp_in_path, 'rb') as f:
                            input_bytes = f.read()
                        
                        # Use vtracer for the conversion
                        svg_content = vtracer.convert_raw_image_to_svg(
                            input_bytes,
                            img_format="png",
                            colormode=color_mode
                        )
                        
                        # Check if conversion was successful
                        if not svg_content or not (
                            svg_content.strip().startswith("<?xml") or 
                            svg_content.strip().startswith("<svg")
                        ):
                            # Fallback: Create a simple SVG by embedding the image
                            self._create_simple_svg_from_image(image, temp_out_path)
                            with open(temp_out_path, "r") as svg_file:
                                svg_content = svg_file.read()
                    except Exception as e:
                        self.logger.warning(f"SVG conversion failed: {str(e)}, using fallback")
                        # Fallback: Create a simple SVG by embedding the image
                        self._create_simple_svg_from_image(image, temp_out_path)
                        with open(temp_out_path, "r") as svg_file:
                            svg_content = svg_file.read()
                    
                    # Generate appropriate filename
                    base_name = os.path.basename(image_identifier)
                    name_without_ext = os.path.splitext(base_name)[0]
                    new_filename = f"{name_without_ext}.svg"
                    
                    # Return SVG content as bytes
                    svg_bytes = svg_content.encode('utf-8')
                    
                    return svg_bytes, new_filename, "image/svg+xml"
                finally:
                    # Clean up temporary files
                    if os.path.exists(temp_in_path):
                        os.unlink(temp_in_path)
                    if os.path.exists(temp_out_path):
                        os.unlink(temp_out_path)
        except Exception as e:
            self.logger.error(f"Error converting to SVG: {str(e)}")
            raise ExportError(f"Error converting to SVG: {str(e)}")
    
    def _create_simple_svg_from_image(self, image: Image.Image, output_path: str) -> None:
        """
        Create a simple SVG by embedding the raster image.
        
        Args:
            image: PIL Image object
            output_path: Path to save the SVG file
        """
        # Convert image to PNG
        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        base64_img = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
        
        # Get image dimensions
        width, height = image.size
        
        # Create SVG with embedded image
        svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" 
            xmlns="http://www.w3.org/2000/svg" 
            xmlns:xlink="http://www.w3.org/1999/xlink">
            <image width="{width}" height="{height}" xlink:href="data:image/png;base64,{base64_img}"/>
        </svg>
        """
        
        # Write to file
        with open(output_path, 'w') as f:
            f.write(svg_content)


async def get_export_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
    image_service: ImageServiceInterface = Depends(get_image_service),
) -> ExportService:
    """
    Get an instance of the export service.
    
    Args:
        supabase_client: Client for Supabase operations
        image_service: Service for image operations
        
    Returns:
        An initialized export service
    """
    return ExportService(supabase_client, image_service) 