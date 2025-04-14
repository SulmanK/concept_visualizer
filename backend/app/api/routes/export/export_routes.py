"""
Export endpoints for converting and downloading images in different formats.

This module provides routes for exporting images in various formats and sizes.
"""

import logging
from typing import Dict

from fastapi import APIRouter, Depends, Request, HTTPException
from fastapi.responses import StreamingResponse

from app.models.export.request import ExportRequest
from app.utils.auth.user import get_current_user
from app.services.export import get_export_service
from app.services.persistence import get_image_persistence_service
from app.services.persistence.interface import ImagePersistenceServiceInterface
from app.utils.security.mask import mask_path

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/process")
async def export_action(
    request_data: ExportRequest,
    req: Request,
    current_user: Dict = Depends(get_current_user),
    export_service = Depends(get_export_service),
    image_persistence_service: ImagePersistenceServiceInterface = Depends(get_image_persistence_service),
):
    """
    Process an export request and return the file.
    
    This endpoint handles converting images to different formats (PNG, JPEG, SVG)
    and resizing them according to the requested parameters.
    
    Args:
        request_data: Export request parameters
        req: FastAPI request object
        current_user: Current authenticated user
        export_service: Service for handling exports
        image_persistence_service: Service for image storage operations
        
    Returns:
        A streaming response with the exported file
    """
    try:
        # Get user ID from authenticated user
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Verify user has access to this image (must be owner)
        image_identifier = request_data.image_identifier
        masked_image_id = mask_path(image_identifier)
        
        # Ensure the image belongs to the authenticated user
        if not image_identifier.startswith(f"{user_id}/"):
            logger.warning(
                f"User attempted to access unauthorized image: {masked_image_id}"
            )
            raise HTTPException(status_code=403, detail="Access denied to this image")
            
        # Determine if it's a palette image based on the bucket
        is_palette = request_data.storage_bucket == "palette-images"
        
        # Fetch the image data using the ImagePersistenceService
        logger.info(f"Fetching image from bucket: {request_data.storage_bucket}, path: {masked_image_id}")
        try:
            image_data = await image_persistence_service.get_image_async(
                image_identifier, 
                is_palette=is_palette
            )
        except Exception as e:
            logger.error(f"Failed to fetch image {masked_image_id}: {str(e)}")
            raise HTTPException(status_code=404, detail=f"Image not found: {image_identifier}")
        
        # Process the export request with the refactored ExportService
        processed_bytes, filename, content_type = await export_service.process_export(
            image_data=image_data,
            original_filename=image_identifier,
            target_format=request_data.target_format,
            target_size=request_data.target_size,
            svg_params=request_data.svg_params,
        )
        
        # Return a streaming response with the file
        headers = {
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
        
        return StreamingResponse(
            iter([processed_bytes]),
            media_type=content_type,
            headers=headers
        )
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        logger.error(f"Export processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export processing failed: {str(e)}") 