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
from fastapi import APIRouter, Body, Request
from PIL import Image
from slowapi.util import get_remote_address
import vtracer

from app.models.request import SVGConversionRequest
from app.models.response import SVGConversionResponse
from app.services.session_service import SessionService, get_session_service
from app.services.concept_service import ConceptService, get_concept_service
from app.services.image_service import ImageService, get_image_service
from app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service
from app.utils.security.mask import mask_id, mask_ip
from app.api.routes.svg.utils import create_simple_svg_from_image, increment_svg_rate_limit
from app.core.limiter import get_redis_client

# Import error handling
from app.api.errors import ValidationError, ServiceUnavailableError

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
        # Handle rate limiting manually instead of using the decorator
        if req and hasattr(req.app.state, 'limiter'):
            limiter = req.app.state.limiter
            try:
                # Use session ID for rate limiting (key_func is now get_session_id)
                rate_limit = "20/hour"
                
                # Log the rate limiting attempt
                logger.info(f"Checking rate limit '{rate_limit}' for SVG conversion")
                
                # Manual rate limit check using keys directly
                user_id = req.cookies.get("concept_session", get_remote_address(req))
                masked_user_id = mask_id(user_id) if "concept_session" in req.cookies else mask_ip(user_id)
                user_key = f"session:{user_id}" if "concept_session" in req.cookies else f"ip:{user_id}"
                
                # Use the custom increment function to check the current rate limit
                # And we'll increment it later only if the conversion is successful
                redis_client = get_redis_client()
                if redis_client:
                    # Check the count but don't increment yet
                    for key in [f"svg:{user_key}:hour", f"POST:/api/svg/convert-to-svg:{user_key}:hour"]:
                        try:
                            count = redis_client.get(key)
                            if count and int(count) >= 20:  # 20/hour limit
                                logger.warning(f"Rate limit exceeded for {masked_user_id}: {int(count)}/20 requests")
                                raise ServiceUnavailableError(
                                    detail="Rate limit exceeded for SVG conversion. Please try again later."
                                )
                        except ValueError:
                            # If the count can't be parsed, continue
                            pass
                        except Exception as e:
                            if not isinstance(e, ServiceUnavailableError):
                                logger.error(f"Error checking rate limit: {str(e)}")
                
            except Exception as e:
                if isinstance(e, ServiceUnavailableError):
                    raise
                logger.error(f"Error in rate limit check for SVG conversion: {str(e)}")
                # Continue even if rate limiting fails
        
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
                    
                    # Only increment rate limit counter AFTER successful conversion
                    if req and limiter and hasattr(limiter, 'increment_rate_limit'):
                        # The user ID will be extracted from cookies in the key_func
                        user_id = req.cookies.get("concept_session", get_remote_address(req))
                        masked_user_id = mask_id(user_id) if "concept_session" in req.cookies else mask_ip(user_id)
                        user_key = f"session:{user_id}" if "concept_session" in req.cookies else f"ip:{user_id}"
                        
                        logger.info(f"Incrementing rate limit for user: {masked_user_id} after successful conversion")
                        
                        # Use a custom function to increment only SVG-specific keys
                        success = increment_svg_rate_limit(
                            limiter, 
                            user_key, 
                            "/api/svg/convert-to-svg", 
                            "hour"
                        )
                        
                        if success:
                            logger.info("Rate limit counter incremented successfully in Redis for SVG conversion")
                        else:
                            logger.warning("Failed to increment rate limit counter in Redis for SVG conversion")
                    
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
                    
                    # Even with fallback, we had a successful conversion, so increment the counter
                    if req and limiter and hasattr(limiter, 'increment_rate_limit'):
                        user_id = req.cookies.get("concept_session", get_remote_address(req))
                        masked_user_id = mask_id(user_id) if "concept_session" in req.cookies else mask_ip(user_id)
                        user_key = f"session:{user_id}" if "concept_session" in req.cookies else f"ip:{user_id}"
                        
                        logger.info(f"Incrementing rate limit for user: {masked_user_id} after fallback conversion")
                        increment_svg_rate_limit(
                            limiter, 
                            user_key, 
                            "/api/svg/convert-to-svg", 
                            "hour"
                        )
                    
                    return SVGConversionResponse(
                        svg_data=svg_content,
                        success=True,
                        message="SVG conversion successful (using fallback method)"
                    )
                
            finally:
                # Clean up temp files
                try:
                    os.unlink(temp_in_path)
                except:
                    pass
                    
                try:
                    os.unlink(temp_out_path)
                except:
                    pass
                    
    except ValidationError:
        # Re-raise validation errors directly
        raise
    except Exception as e:
        logger.error(f"Error converting image to SVG: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"SVG conversion failed: {str(e)}")


# Alias route for backward compatibility
router.post("/convert", response_model=SVGConversionResponse)(convert_to_svg) 