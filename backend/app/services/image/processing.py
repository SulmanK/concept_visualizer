"""
Image processing utilities.

This module provides utilities for image color processing, including
dominant color extraction, color masking, and palette application.
"""

import logging
import numpy as np
import cv2
from io import BytesIO
from typing import List, Dict, Any, Tuple, Union
from PIL import Image

logger = logging.getLogger(__name__)


def download_image(image_url_or_data: Union[str, BytesIO, bytes]) -> np.ndarray:
    """
    Download or read an image and convert to OpenCV format.
    
    Args:
        image_url_or_data: URL of the image to download, BytesIO object, or raw bytes
        
    Returns:
        Image as a numpy array in BGR format (OpenCV default)
        
    Raises:
        Exception: If image download or conversion fails
    """
    try:
        # Handle bytes input
        if isinstance(image_url_or_data, bytes):
            logger.info(f"Processing binary image data: {len(image_url_or_data)} bytes")
            try:
                # Try to decode directly with OpenCV
                nparr = np.frombuffer(image_url_or_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if img is not None:
                    return img
            except Exception as e:
                logger.warning(f"Failed to decode with OpenCV: {str(e)}, trying PIL")
            
            # Fallback to PIL
            image = Image.open(BytesIO(image_url_or_data))
            image_rgb = np.array(image.convert("RGB"))
            return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Handle BytesIO input
        if isinstance(image_url_or_data, BytesIO):
            image = Image.open(image_url_or_data)
            image_rgb = np.array(image.convert("RGB"))
            return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Handle URL input
        if isinstance(image_url_or_data, str) and (image_url_or_data.startswith('http://') or image_url_or_data.startswith('https://')):
            import requests
            
            # Use a session that automatically handles redirects
            session = requests.Session()
            
            # Be more browser-like to avoid some access restrictions
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
            }
            
            # Try to download the image with a longer timeout
            response = session.get(image_url_or_data, headers=headers, timeout=30, allow_redirects=True)
            response.raise_for_status()
            
            # Log success
            logger.info(f"Successfully downloaded image: {len(response.content)} bytes")
            
            # Convert to numpy array via PIL
            image = Image.open(BytesIO(response.content))
            image_rgb = np.array(image.convert("RGB"))
            
            # Convert from RGB to BGR (OpenCV format)
            return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Handle local file paths (including those from file:// URLs)
        if isinstance(image_url_or_data, str):
            # If it starts with file://, remove that prefix
            if image_url_or_data.startswith('file://'):
                image_url_or_data = image_url_or_data[7:]
            
            # Open the local file
            with open(image_url_or_data, 'rb') as f:
                image_data = f.read()
                
            # Load as PIL image
            image = Image.open(BytesIO(image_data))
            image_rgb = np.array(image.convert("RGB"))
            
            # Convert from RGB to BGR (OpenCV format)
            return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
            
    except Exception as e:
        logger.error(f"Error downloading/reading image: {str(e)}")
        raise


def hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color code to BGR tuple (OpenCV format).
    
    Args:
        hex_color: Hexadecimal color code (e.g., '#FF5733')
        
    Returns:
        BGR tuple (Blue, Green, Red)
    """
    # Remove # if present
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]
    
    # Parse hex values
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)
    
    # Return in BGR order for OpenCV
    return (blue, green, red)


def bgr_to_hex(bgr: Tuple[int, int, int]) -> str:
    """
    Convert BGR tuple to hex color code.
    
    Args:
        bgr: BGR tuple (Blue, Green, Red)
        
    Returns:
        Hexadecimal color code (e.g., '#FF5733')
    """
    blue, green, red = bgr
    return f"#{red:02x}{green:02x}{blue:02x}"


def find_dominant_colors(image: np.ndarray, num_colors: int = 5) -> List[Tuple[Tuple[int, int, int], float]]:
    """
    Find dominant colors in an image.
    
    Args:
        image: Image as numpy array in BGR format
        num_colors: Number of dominant colors to find
        
    Returns:
        List of tuples containing ((B,G,R), percentage) for each dominant color
    """
    # Reshape the image to be a list of pixels
    pixels = image.reshape(-1, 3).astype(np.float32)
    
    # Define criteria and apply kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
    _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
    
    # Count labels to find percentages
    unique_labels, counts = np.unique(labels, return_counts=True)
    total_pixels = len(labels)
    
    # Create list of ((B,G,R), percentage) tuples
    colors = []
    for i in range(len(centers)):
        bgr = tuple(map(int, centers[i]))
        percentage = counts[i] / total_pixels
        colors.append((bgr, percentage))
    
    # Sort by percentage (most dominant first)
    colors.sort(key=lambda x: x[1], reverse=True)
    
    return colors[:num_colors]


async def extract_dominant_colors(image_data: bytes, num_colors: int = 8) -> List[str]:
    """
    Extract dominant colors from an image and return as hex codes.
    
    Args:
        image_data: Binary image data
        num_colors: Number of colors to extract
        
    Returns:
        List of color hex codes
    """
    # Load image into OpenCV format
    img = Image.open(BytesIO(image_data))
    img_rgb = np.array(img.convert("RGB"))
    img_bgr = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    
    # Find dominant colors
    dominant_colors = find_dominant_colors(img_bgr, num_colors)
    
    # Convert to hex strings
    hex_colors = [bgr_to_hex(color[0]) for color in dominant_colors]
    
    return hex_colors


def create_color_mask(image: np.ndarray, target_color: Tuple[int, int, int], threshold: int = 18) -> np.ndarray:
    """
    Create a binary mask for pixels close to the target color.
    
    Args:
        image: Image as numpy array in BGR format
        target_color: Target BGR color to mask
        threshold: Color distance threshold in each channel
        
    Returns:
        Binary mask as numpy array
    """
    # Convert to HSV for better color detection
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    target_hsv = cv2.cvtColor(np.uint8([[target_color]]), cv2.COLOR_BGR2HSV)[0][0]
    
    # Create range for target color
    # Explicitly convert to uint8 to avoid type mismatches and overflows
    h_thresh = min(threshold, 90)  # Limit hue threshold to avoid wrapping issues
    
    # Create bounds with proper types and clamping
    lower_bound = np.array([
        max(0, int(target_hsv[0]) - h_thresh),
        max(0, int(target_hsv[1]) - threshold),
        max(0, int(target_hsv[2]) - threshold)
    ], dtype=np.uint8)
    
    upper_bound = np.array([
        min(179, int(target_hsv[0]) + h_thresh),
        min(255, int(target_hsv[1]) + threshold),
        min(255, int(target_hsv[2]) + threshold)
    ], dtype=np.uint8)
    
    # Create mask
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    
    # Apply morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask


def apply_palette_with_masking_optimized(
    image_url_or_data: Union[str, BytesIO, bytes], 
    palette_colors: List[str], 
    blend_strength: float = 0.75
) -> bytes:
    """
    Apply a color palette to an image using simplified masking and recoloring.
    
    Args:
        image_url_or_data: URL of the image, BytesIO object, or raw bytes
        palette_colors: List of hex color codes
        blend_strength: How strongly to apply the new colors (0.0-1.0)
        
    Returns:
        Processed image as bytes
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Debug input
        logger.info(f"Applying palette to image, data type: {type(image_url_or_data)}")
        logger.info(f"Palette colors: {palette_colors}")
        
        if image_url_or_data is None:
            logger.error("Image data is None, cannot process")
            raise ValueError("Image data cannot be None")
            
        # For binary data, log the size
        if isinstance(image_url_or_data, bytes):
            logger.info(f"Processing binary image data: {len(image_url_or_data)} bytes")
        elif isinstance(image_url_or_data, BytesIO):
            logger.info(f"Processing BytesIO image data: {image_url_or_data.getbuffer().nbytes} bytes")
        elif isinstance(image_url_or_data, str):
            logger.info(f"Processing image from URL or path: {image_url_or_data[:100]}...")
        
        # Download/read image
        logger.info("Converting image to OpenCV format...")
        image = download_image(image_url_or_data)
        
        # Verify image data
        if image is None:
            logger.error("Failed to load image, returned None from download_image")
            raise ValueError("Image could not be loaded or decoded")
            
        logger.info(f"Image loaded successfully, shape: {image.shape}, dtype: {image.dtype}")
        
        # Find dominant colors in original image
        max_colors = min(5, len(palette_colors))
        logger.info(f"Finding {max_colors} dominant colors...")
        dominant_colors = find_dominant_colors(image, max_colors)
        logger.info(f"Found dominant colors: {dominant_colors}")
        
        # Convert palette hex colors to BGR
        palette_bgr = [hex_to_bgr(color) for color in palette_colors[:max_colors]]
        logger.info(f"Converted palette to BGR: {palette_bgr}")
        
        # Create a copy of the original image for recoloring
        result = image.copy()
        
        # For each dominant color, create a mask and replace with palette color
        for i, (dom_color, _) in enumerate(dominant_colors):
            if i >= len(palette_bgr):
                break
                
            logger.info(f"Processing dominant color {i+1}/{len(dominant_colors)}: {dom_color}")
            
            # Create mask for this dominant color
            mask = create_color_mask(image, dom_color)
            
            # Get the palette color to use
            target_color = palette_bgr[i]
            logger.info(f"Target color: {target_color}")
            
            # Create HSV versions for color shifting
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
            dom_hsv = cv2.cvtColor(np.uint8([[dom_color]]), cv2.COLOR_BGR2HSV)[0][0]
            target_hsv = cv2.cvtColor(np.uint8([[target_color]]), cv2.COLOR_BGR2HSV)[0][0]
            
            # Calculate color shift
            h_shift = int(target_hsv[0]) - int(dom_hsv[0])
            s_scale = float(target_hsv[1]) / max(1.0, float(dom_hsv[1]))  # Scale saturation
            v_scale = float(target_hsv[2]) / max(1.0, float(dom_hsv[2]))  # Value ratio for preserving lighting
            
            logger.info(f"HSV shift values - H: {h_shift}, S: {s_scale:.2f}, V: {v_scale:.2f}")
            
            # Apply the shift to the entire image
            shifted_hsv = hsv_image.copy()
            
            # Use mask to blend the recolored regions
            mask_3d = cv2.merge([mask, mask, mask]).astype(np.float32) / 255.0 * blend_strength
            
            # Create a recolored version with shifted HSV values
            # This vectorized approach is much faster than pixel-by-pixel operations
            shifted_hsv[..., 0] = (hsv_image[..., 0] + h_shift) % 180
            shifted_hsv[..., 1] = np.clip(hsv_image[..., 1] * s_scale, 0, 255)
            shifted_hsv[..., 2] = np.clip(hsv_image[..., 2] * v_scale, 0, 255)
            
            # Convert back to BGR
            shifted_bgr = cv2.cvtColor(shifted_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Blend with original using the mask
            for c in range(3):  # For each BGR channel
                # Use safe blend method to avoid overflow
                blended = (1 - mask_3d[..., c]) * result[..., c] + mask_3d[..., c] * shifted_bgr[..., c]
                # Clamp values to valid range
                result[..., c] = np.clip(blended, 0, 255).astype(np.uint8)
        
        # Make sure we have a valid image type before encoding
        result = result.astype(np.uint8)
        logger.info(f"Processing complete, encoding result as PNG...")
        
        # Convert the result to bytes
        _, buffer = cv2.imencode('.png', result)
        result_bytes = buffer.tobytes()
        logger.info(f"Successfully encoded result, size: {len(result_bytes)} bytes")
        return result_bytes
        
    except Exception as e:
        logger.error(f"Error applying palette with masking: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 