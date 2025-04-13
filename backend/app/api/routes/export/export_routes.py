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
from app.core.supabase import get_supabase_client
from app.services.image import get_image_service

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
        
    Returns:
        A streaming response with the exported file
    """
    try:
        # Get user ID from authenticated user
        user_id = current_user.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Process the export request
        processed_bytes, filename, content_type = await export_service.process_export(
            image_identifier=request_data.image_identifier,
            target_format=request_data.target_format,
            target_size=request_data.target_size,
            user_id=user_id,
            svg_params=request_data.svg_params,
            storage_bucket=request_data.storage_bucket,
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