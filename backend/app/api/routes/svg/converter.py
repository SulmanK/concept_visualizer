"""
SVG conversion endpoints.

This module provides endpoints for converting raster images to SVG format.
"""

import logging
import os
import tempfile
import base64
import traceback
from io import BytesIO
from fastapi import APIRouter, Body, Request, HTTPException
from PIL import Image
from slowapi.util import get_remote_address
import vtracer
import io
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.responses import StreamingResponse, JSONResponse

from app.models.request import SVGConversionRequest
from app.models.response import SVGConversionResponse
from app.services.concept import get_concept_service
from app.services.image import get_image_service
from app.services.storage import get_concept_storage_service
from app.services.interfaces import (
    ImageServiceInterface,
    StorageServiceInterface
)
from app.api.dependencies import CommonDependencies
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError
from app.utils.security.mask import mask_id, mask_ip
from app.api.routes.svg.utils import create_simple_svg_from_image, increment_svg_rate_limit
from app.core.limiter import get_redis_client
from app.utils.api_limits import apply_multiple_rate_limits
from app.utils.api_limits.endpoints import apply_rate_limit
from app.utils.api_limits.decorators import store_rate_limit_info

# Configure logging
logger = logging.getLogger("svg_converter_api")

# Create router
router = APIRouter()


@router.post("/convert-to-svg", response_model=SVGConversionResponse)
async def convert_to_svg(
    request: SVGConversionRequest = Body(...),
    req: Request = None
):
    """Convert a raster image to SVG using vtracer.
    
    Args:
        request: The request containing the image data and conversion options
        req: The FastAPI request object for rate limiting
        
    Returns:
        SVGConversionResponse containing the SVG data
        
    Raises:
        ValidationError: If the request is invalid
        ServiceUnavailableError: If the service fails to convert the image
    """
    try:
        # Apply rate limiting using the centralized function
        if req and hasattr(req.app.state, 'limiter'):
            # Use only the svg_conversion rate limit for this endpoint
            # SVG conversion doesn't need to check/increment other rate limits
            await apply_rate_limit(
                req=req,
                endpoint="/svg/convert-to-svg",
                rate_limit="20/hour",
                period="hour"
            )
            
            # Now manually store the rate limit info after the counter has been incremented
            try:
                user_id = None
                if hasattr(req, "state") and hasattr(req.state, "user") and req.state.user:
                    user_id = req.state.user.get("id")
                
                if user_id:
                    from app.core.limiter import check_rate_limit
                    limit_status = check_rate_limit(
                        user_id=f"user:{user_id}", 
                        endpoint="/svg/convert-to-svg",
                        limit="20/hour",
                        check_only=True  # Just check current status after increment
                    )
                    
                    # Store in request.state for the middleware to use
                    req.state.limiter_info = {
                        "limit": limit_status.get("limit", 0),
                        "remaining": limit_status.get("remaining", 0),
                        "reset": limit_status.get("reset_at", 0)
                    }
                    
                    logger.debug(
                        f"Stored rate limit info for /svg/convert-to-svg after increment: "
                        f"remaining={limit_status.get('remaining', 0)}"
                    )
            except Exception as e:
                logger.error(f"Error storing post-increment rate limit info: {str(e)}")
        
        # Validate the request
        # Extract the image data from base64
        if not request.image_data:
            raise ValidationError(
                detail="No image data provided",
                field_errors={"image_data": ["Field is required"]}
            )
        
        # Remove data URL prefix if present
        image_data = request.image_data
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        
        try:
            # Decode base64
            image_bytes = base64.b64decode(image_data)
        except Exception as e:
            raise ValidationError(
                detail=f"Invalid base64 image data: {str(e)}",
                field_errors={"image_data": ["Invalid base64 format"]}
            )
        
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
                try:
                    image = Image.open(BytesIO(image_bytes))
                except Exception as e:
                    raise ValidationError(
                        detail=f"Invalid image format: {str(e)}",
                        field_errors={"image_data": ["Invalid image format"]}
                    )
                
                # Resize if needed
                if request.max_size and (image.width > request.max_size or image.height > request.max_size):
                    # Preserve aspect ratio
                    if image.width > image.height:
                        new_width = request.max_size
                        new_height = int(image.height * (request.max_size / image.width))
                    else:
                        new_height = request.max_size
                        new_width = int(image.width * (request.max_size / image.height))
                    
                    image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Save to temporary input file
                image.save(temp_in_path, format="PNG")
                
                try:
                    # Process the image using the vtracer Python API
                    logger.info(f"Converting image to SVG with vtracer: {os.path.basename(temp_in_path)} -> {os.path.basename(temp_out_path)}")
                    
                    # Set color mode parameter
                    color_mode = "binary"
                    if request.color_mode == "color":
                        color_mode = "color"
                    elif request.color_mode == "grayscale":
                        color_mode = "color"  # vtracer doesn't have grayscale mode, fallback to color
                    
                    # Use a simplified approach first - try with minimal parameters
                    with open(temp_in_path, 'rb') as f:
                        input_bytes = f.read()
                    
                    # Try with minimal parameters first for better compatibility
                    try:
                        svg_content = vtracer.convert_raw_image_to_svg(
                            input_bytes,
                            img_format="png",
                            colormode=color_mode
                        )
                    except Exception as e:
                        logger.info(f"Simple conversion failed: {e}, falling back to embedding image")
                        # If simple conversion fails, use the fallback
                        create_simple_svg_from_image(image, temp_out_path)
                        with open(temp_out_path, "r") as svg_file:
                            svg_content = svg_file.read()
                    
                    logger.info("Conversion completed successfully")
                    
                    # Ensure SVG content is valid
                    if not svg_content.strip().startswith("<?xml") and not svg_content.strip().startswith("<svg"):
                        logger.info("Generated SVG content may be invalid, using fallback")
                        create_simple_svg_from_image(image, temp_out_path)
                        with open(temp_out_path, "r") as svg_file:
                            svg_content = svg_file.read()
                    
                    # Write SVG to temp file for debugging
                    with open(temp_out_path, "w") as f:
                        f.write(svg_content)
                    
                    return SVGConversionResponse(
                        svg_data=svg_content,
                        success=True,
                        message="SVG conversion successful"
                    )
                    
                except Exception as e:
                    logger.error(f"Error during vtracer conversion: {e}")
                    # Fall back to a simpler conversion
                    create_simple_svg_from_image(image, temp_out_path)
                    with open(temp_out_path, "r") as svg_file:
                        svg_content = svg_file.read()
                    
                    return SVGConversionResponse(
                        svg_data=svg_content,
                        success=True,
                        message="SVG conversion successful (using fallback method)"
                    )
                
            finally:
                # Clean up temp files
                try:
                    os.unlink(temp_in_path)
                except Exception:
                    pass
                    
                try:
                    os.unlink(temp_out_path)
                except Exception:
                    pass
                    
    except ValidationError:
        # Re-raise validation errors directly
        raise
    except HTTPException:
        # Re-raise HTTP exceptions (like our 429 error from apply_rate_limit)
        raise
    except Exception as e:
        logger.error(f"Error converting image to SVG: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"SVG conversion failed: {str(e)}")


# Alias route for backward compatibility
# router.post("/convert", response_model=SVGConversionResponse)(convert_to_svg)
# Add the decorator to the alias as well
# converter_with_info = store_rate_limit_info("/svg/convert", "20/hour")(convert_to_svg)
router.post("/convert", response_model=SVGConversionResponse)(convert_to_svg) 