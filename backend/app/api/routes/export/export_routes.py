"""Export endpoints for converting and downloading images in different formats.

This module provides routes for exporting images in various formats and sizes.
"""

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse

from app.models.export.request import ExportRequest
from app.services.export import get_export_service
from app.services.export.interface import ExportServiceInterface
from app.services.persistence import get_image_persistence_service
from app.services.persistence.interface import ImagePersistenceServiceInterface
from app.utils.auth.user import get_current_user
from app.utils.security.mask import mask_path

# Configure logger
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()


@router.post("/process")
async def export_action(
    request_data: ExportRequest,
    req: Request,
    current_user: Dict[str, Any] = Depends(get_current_user),
    export_service: ExportServiceInterface = Depends(get_export_service),
    image_persistence_service: ImagePersistenceServiceInterface = Depends(get_image_persistence_service),
) -> StreamingResponse:
    """Process an export request and return the file.

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

        # Get image identifier from request
        image_identifier = request_data.image_identifier
        masked_image_id = mask_path(image_identifier)

        # Determine the storage bucket based on request and path pattern
        storage_bucket = request_data.storage_bucket
        is_palette = storage_bucket == "palette-images" or "palette" in image_identifier.lower()

        # Log detailed information about the request
        logger.info(
            "Processing export request for image: {}, "
            "in bucket: {}, is_palette: {}, "
            "format: {}, size: {}".format(masked_image_id, storage_bucket, is_palette, request_data.target_format, request_data.target_size)
        )

        # Fetch the image data using the ImagePersistenceService - just to validate it exists
        try:
            # Attempt to get the image - this will use service role access if needed
            # We're explicitly passing the detected bucket type
            if is_palette:
                logger.debug("Validating image exists in palette bucket")
                image_path_with_hint = f"palette_{image_identifier}" if "palette" not in image_identifier else image_identifier
                await image_persistence_service.get_image(image_path_with_hint)
            else:
                logger.debug("Validating image exists in concept bucket")
                await image_persistence_service.get_image(image_identifier)
        except Exception as e:
            logger.error(f"Failed to fetch image {masked_image_id}: {str(e)}")

            # Try the opposite bucket as a fallback
            try:
                if is_palette:
                    logger.warning(f"Image not found in palette bucket, trying concept bucket: {str(e)}")
                    await image_persistence_service.get_image(image_identifier)
                    is_palette = False  # Update our detection
                else:
                    logger.warning(f"Image not found in concept bucket, trying palette bucket: {str(e)}")
                    image_path_with_hint = f"palette_{image_identifier}"
                    await image_persistence_service.get_image(image_path_with_hint)
                    is_palette = True  # Update our detection

                logger.info(f"Found image in the {'palette' if is_palette else 'concept'} bucket instead")
            except Exception as inner_e:
                logger.error(f"Image not found in either bucket: {str(e)}, {str(inner_e)}")
                raise HTTPException(status_code=404, detail=f"Image not found: {image_identifier}")

        # Process the export request with the ExportService
        # Use ExportService's export_image method from the interface
        size: Optional[Dict[str, int]] = {"width": 512, "height": 512}  # Default size

        # Map target_size to actual dimensions if needed
        if request_data.target_size == "small":
            size = {"width": 500, "height": 500}
        elif request_data.target_size == "medium":
            size = {"width": 1000, "height": 1000}
        elif request_data.target_size == "large":
            size = {"width": 2000, "height": 2000}
        elif request_data.target_size == "original":
            size = None

        # Use the export_image method from the interface
        # Note: We're letting the export service handle bucket detection now
        # but we've done our best to validate the image exists first
        export_result = await export_service.export_image(
            image_path=image_identifier,
            format=request_data.target_format,
            size=size,
            quality=90 if request_data.target_format == "jpg" else None,
            user_id=user_id,
        )

        # Return a streaming response with the file
        headers = {"Content-Disposition": f'attachment; filename="{export_result.get("filename", "export."+request_data.target_format)}"'}

        logger.info(f"Successfully processed export request for {masked_image_id}, returning {export_result.get('size', 0)} bytes")
        return StreamingResponse(
            iter([export_result.get("data", b"")]),
            media_type=export_result.get("content_type", f"image/{request_data.target_format}"),
            headers=headers,
        )
    except HTTPException:
        # Re-raise HTTP exceptions directly
        raise
    except Exception as e:
        logger.error(f"Export processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Export processing failed: {str(e)}")
