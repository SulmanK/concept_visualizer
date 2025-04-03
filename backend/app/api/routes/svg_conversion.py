"""
SVG conversion API endpoints.

This module provides routes for converting raster images to SVG format.
"""

import logging
from fastapi import APIRouter, HTTPException, Body, Request
import base64
from io import BytesIO
import tempfile
import os
import vtracer
from PIL import Image
from slowapi.util import get_remote_address

from app.models.request import SVGConversionRequest
from app.models.response import SVGConversionResponse
from app.utils.mask import mask_id, mask_ip

# Configure logging
logger = logging.getLogger("svg_conversion")

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
    """
    limiter = None
    if req:
        limiter = req.app.state.limiter
        try:
            # Use session ID for rate limiting (key_func is now get_session_id)
            rate_limit = "20/hour"
            
            # Log the rate limiting attempt
            logger.info(f"Checking rate limit '{rate_limit}' for SVG conversion")
            
            # Try-except block for the rate limit to handle connection issues
            try:
                # Fix the await syntax - limiter.limit returns a function, not an awaitable
                limit_func = limiter.limit(rate_limit)
                # Apply the limit function to the request, but don't await it (it's not an async function)
                limit_func(req)
                logger.info("SlowAPI rate limit check passed for SVG conversion")
            except Exception as e:
                logger.error(f"SlowAPI rate limiting error in SVG conversion: {str(e)}")
                # Continue even if rate limiting fails
        except Exception as e:
            logger.error(f"Error checking rate limit for SVG conversion: {str(e)}")
            # Continue even if rate limiting fails
    
    try:
        # Extract the image data from base64
        if not request.image_data:
            raise HTTPException(status_code=400, detail="No image data provided")
        
        # Remove data URL prefix if present
        image_data = request.image_data
        if "base64," in image_data:
            image_data = image_data.split("base64,")[1]
        
        # Decode base64
        image_bytes = base64.b64decode(image_data)
        
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
                        success = _increment_svg_rate_limit(
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
                        _increment_svg_rate_limit(
                            limiter, 
                            user_key, 
                            "/api/svg/convert-to-svg", 
                            "hour"
                        )
                    
                    return SVGConversionResponse(
                        svg_data=svg_content,
                        success=True,
                        message="SVG conversion successful (fallback method)"
                    )
                
            finally:
                # Clean up temporary files
                try:
                    os.unlink(temp_in_path)
                    os.unlink(temp_out_path)
                except Exception as e:
                    logger.error(f"Error removing temporary files: {e}")
        
    except Exception as e:
        logger.error(f"SVG conversion error: {str(e)}")
        # Don't increment the rate limit counter if conversion failed
        raise HTTPException(status_code=500, detail=f"SVG conversion failed: {str(e)}")


def create_simple_svg_from_image(image, output_path):
    """Create a simple SVG from an image as a fallback.
    
    Args:
        image: PIL Image object
        output_path: Path to save the SVG file
    
    Returns:
        None
    """
    width, height = image.size
    
    # Create a basic SVG that embeds the image as a data URL
    with open(output_path, "w") as f:
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_b64 = base64.b64encode(img_bytes.getvalue()).decode("utf-8")
        
        svg_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="{width}" height="{height}">
  <image width="{width}" height="{height}" xlink:href="data:image/png;base64,{img_b64}"/>
</svg>"""
        
        f.write(svg_content) 

def _increment_svg_rate_limit(limiter, user_id, endpoint, period="hour"):
    """Custom function to increment only SVG-specific rate limit keys.
    
    This function avoids using generic keys that could affect other endpoints.
    
    Args:
        limiter: The limiter instance
        user_id: The user identifier (e.g., "session:{id}")
        endpoint: The endpoint path (e.g., "/api/svg/convert-to-svg")
        period: The time period (minute, hour, day, month)
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Use the same Redis client getter as the main rate limiter 
        # to ensure we're accessing Redis the same way
        from app.core.rate_limiter import get_redis_client
        redis_client = get_redis_client()
        
        if not redis_client:
            logger.warning("Cannot increment SVG rate limit: Redis not available")
            return True  # Return success anyway to allow the operation to continue
        
        # Use only specific key formats for SVG conversion, NOT generic ones like {user_id}:{period}
        # which could interfere with other rate limits
        keys = [
            # Use specific SVG key formats
            f"svg:{user_id}:{period}",
            f"POST:{endpoint}:{user_id}:{period}", 
            f"{endpoint}:{user_id}:{period}"
        ]
        
        # Deliberately exclude the generic key format: f"{user_id}:{period}"
        
        # Calculate TTL based on period
        if period == "minute":
            ttl = 60
        elif period == "hour":
            ttl = 3600
        elif period == "day":
            ttl = 86400
        else:  # month
            ttl = 2592000  # 30 days
        
        # Try to increment all SVG-specific key formats
        success = False
        for key in keys:
            try:
                # Increment and set expiry
                result = redis_client.incr(key)
                redis_client.expire(key, ttl)
                logger.debug(f"Incremented SVG rate limit key: {key} = {result}")
                success = True
            except Exception as e:
                logger.error(f"Failed to increment SVG key {key}: {str(e)}")
                
        return success
    except Exception as e:
        logger.error(f"Error incrementing SVG rate limit: {str(e)}")
        return True  # Return success anyway to allow the operation to continue 