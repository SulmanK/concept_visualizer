"""
Export routes for the API.

This module provides routes for exporting images in different formats.
"""

import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Optional

from app.models.export.request import ExportRequest
from app.services.export import ExportService, get_export_service
from app.api.dependencies import get_current_user
from app.utils.api_limits.endpoints import apply_rate_limit

# Configure logging
logger = logging.getLogger(__name__)

# Create the router
router = APIRouter()


@router.post("/process")
async def process_export(
    request_data: ExportRequest,
    req: Request,
    current_user: Dict = Depends(get_current_user),
    export_service: ExportService = Depends(get_export_service),
):
    """
    Process an image export request.
    
    Args:
        request_data: Export request data
        req: FastAPI request object for rate limiting
        current_user: Current authenticated user
        export_service: Service for handling exports
        
    Returns:
        A streaming response with the exported file
    """
    try:
        # Apply unified rate limiting for all export formats
        if hasattr(req.app.state, 'limiter'):
            await apply_rate_limit(
                req=req,
                endpoint="/export/process",
                rate_limit="50/hour",
                period="hour"
            )
        
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