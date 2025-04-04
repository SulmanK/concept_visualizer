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


def download_image(image_url_or_data: Union[str, BytesIO]) -> np.ndarray:
    """
    Download or read an image and convert to OpenCV format.
    
    Args:
        image_url_or_data: URL of the image to download or BytesIO object
        
    Returns:
        Image as a numpy array in BGR format (OpenCV default)
        
    Raises:
        Exception: If image download or conversion fails
    """
    try:
        # Handle BytesIO input
        if isinstance(image_url_or_data, BytesIO):
            image = Image.open(image_url_or_data)
            image_rgb = np.array(image.convert("RGB"))
            return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
        
        # Handle URL input
        import requests
        response = requests.get(image_url_or_data, timeout=10)
        response.raise_for_status()
        
        # Convert to numpy array via PIL
        image = Image.open(BytesIO(response.content))
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
    lower_bound = np.array([
        max(0, target_hsv[0] - threshold),
        max(0, target_hsv[1] - threshold),
        max(0, target_hsv[2] - threshold)
    ])
    upper_bound = np.array([
        min(179, target_hsv[0] + threshold),
        min(255, target_hsv[1] + threshold),
        min(255, target_hsv[2] + threshold)
    ])
    
    # Create mask
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    
    # Apply morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    
    return mask


def apply_palette_with_masking_optimized(
    image_url_or_data: Union[str, BytesIO], 
    palette_colors: List[str], 
    blend_strength: float = 0.75
) -> bytes:
    """
    Apply a color palette to an image using simplified masking and recoloring.
    
    Args:
        image_url_or_data: URL of the image or BytesIO object
        palette_colors: List of hex color codes
        blend_strength: How strongly to apply the new colors (0.0-1.0)
        
    Returns:
        Processed image as bytes
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Download/read image
        image = download_image(image_url_or_data)
        
        # Find dominant colors in original image
        max_colors = min(5, len(palette_colors))
        dominant_colors = find_dominant_colors(image, max_colors)
        
        # Convert palette hex colors to BGR
        palette_bgr = [hex_to_bgr(color) for color in palette_colors[:max_colors]]
        
        # Create a copy of the original image for recoloring
        result = image.copy()
        
        # For each dominant color, create a mask and replace with palette color
        for i, (dom_color, _) in enumerate(dominant_colors):
            if i >= len(palette_bgr):
                break
                
            # Create mask for this dominant color
            mask = create_color_mask(image, dom_color)
            
            # Get the palette color to use
            target_color = palette_bgr[i]
            
            # Create HSV versions for color shifting
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV).astype(np.float32)
            dom_hsv = cv2.cvtColor(np.uint8([[dom_color]]), cv2.COLOR_BGR2HSV)[0][0]
            target_hsv = cv2.cvtColor(np.uint8([[target_color]]), cv2.COLOR_BGR2HSV)[0][0]
            
            # Calculate color shift
            h_shift = target_hsv[0] - dom_hsv[0]
            s_scale = target_hsv[1] / max(1, dom_hsv[1])  # Scale saturation
            v_scale = target_hsv[2] / max(1, dom_hsv[2])  # Value ratio for preserving lighting
            
            # Apply the shift to the entire image
            shifted_hsv = hsv_image.copy()
            
            # Use mask to blend the recolored regions
            mask_3d = cv2.merge([mask, mask, mask]).astype(np.float32) / 255.0 * blend_strength
            
            # Create a recolored version with shifted HSV values
            # This vectorized approach is much faster than pixel-by-pixel operations
            shifted_hsv[..., 0] = (hsv_image[..., 0] + h_shift) % 180
            shifted_hsv[..., 1] = np.minimum(255, hsv_image[..., 1] * s_scale)
            shifted_hsv[..., 2] = np.minimum(255, hsv_image[..., 2] * v_scale)
            
            # Convert back to BGR
            shifted_bgr = cv2.cvtColor(shifted_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Blend with original using the mask
            for c in range(3):  # For each BGR channel
                result[..., c] = (1 - mask_3d[..., c]) * result[..., c] + mask_3d[..., c] * shifted_bgr[..., c]
        
        # Convert the result to bytes
        _, buffer = cv2.imencode('.png', result)
        return buffer.tobytes()
        
    except Exception as e:
        logger.error(f"Error applying palette with masking: {str(e)}")
        raise 