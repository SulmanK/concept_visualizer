"""
SVG conversion utilities.

This module provides utility functions for SVG conversion operations.
"""

import base64
import logging
from io import BytesIO
from PIL import Image
from app.core.limiter import get_redis_client

# Configure logging
logger = logging.getLogger(__name__)


def create_simple_svg_from_image(image: Image.Image, output_path: str) -> None:
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


def increment_svg_rate_limit(limiter, user_id: str, endpoint: str, period: str = "hour") -> bool:
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
        redis_client = get_redis_client()
        
        if not redis_client:
            logger.warning("Cannot increment SVG rate limit: Redis not available")
            return True  # Return success anyway to allow the operation to continue
        
        # Use key formats matching what's being checked in health/limits.py
        # IMPORTANT: We must only include SVG-specific keys to avoid affecting other quotas
        keys = [
            # REMOVED: The generic key that was affecting other endpoints
            # f"{user_id}:{period}", 
            
            # SVG-specific keys only
            f"svg:{user_id}:{period}",
            
            # Make the standard format keys specific to SVG
            f"svg:POST:{endpoint}:{user_id}:{period}", 
            f"svg:{endpoint}:{user_id}:{period}"
        ]
        
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