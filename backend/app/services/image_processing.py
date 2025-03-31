"""
Image processing utilities for color manipulation and palette application.

This module provides utilities for image color processing, including
dominant color extraction, color masking, and palette application.
"""

import logging
import numpy as np
import cv2
from io import BytesIO
from typing import List, Dict, Any, Tuple
from PIL import Image

logger = logging.getLogger(__name__)

def download_image(image_url: str) -> np.ndarray:
    """Download an image from a URL and convert to OpenCV format.
    
    Args:
        image_url: URL of the image to download
        
    Returns:
        Image as a numpy array in BGR format (OpenCV default)
        
    Raises:
        Exception: If image download or conversion fails
    """
    try:
        import requests
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        
        # Convert to numpy array via PIL
        image = Image.open(BytesIO(response.content))
        image_rgb = np.array(image.convert("RGB"))
        
        # Convert from RGB to BGR (OpenCV format)
        return cv2.cvtColor(image_rgb, cv2.COLOR_RGB2BGR)
    except Exception as e:
        logger.error(f"Error downloading image: {str(e)}")
        raise

def hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color code to BGR tuple (OpenCV format).
    
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

def find_dominant_colors(image: np.ndarray, num_colors: int = 5) -> List[Tuple[Tuple[int, int, int], float]]:
    """Find dominant colors in an image.
    
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

def create_color_mask(image: np.ndarray, target_color: Tuple[int, int, int], threshold: int = 18) -> np.ndarray:
    """Create a binary mask for pixels close to the target color.
    
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

def apply_palette_with_masking(image_url: str, palette_colors: List[str]) -> bytes:
    """Apply a color palette to an image using simplified masking and recoloring.
    
    Args:
        image_url: URL of the image to process
        palette_colors: List of hex color codes
        
    Returns:
        Processed image as bytes
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Download image
        image = download_image(image_url)
        
        # Find dominant colors in original image
        dominant_colors = find_dominant_colors(image, min(5, len(palette_colors)))
        
        # Convert palette hex colors to BGR
        palette_bgr = [hex_to_bgr(color) for color in palette_colors]
        
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
            s_shift = target_hsv[1] / max(1, dom_hsv[1])  # Scale saturation
            v_ratio = target_hsv[2] / max(1, dom_hsv[2])  # Value ratio for preserving lighting
            
            # Create a mask stack (3 channels)
            mask_stack = cv2.merge([mask, mask, mask]) // 255
            
            # Create recolored image using the dominant color mask
            # Apply the new palette color while preserving shading variations
            for y in range(image.shape[0]):
                for x in range(image.shape[1]):
                    if mask[y, x] > 0:
                        # Get current pixel in HSV
                        h, s, v = hsv_image[y, x]
                        
                        # Apply color shift while maintaining lighting variations
                        new_h = (h + h_shift) % 180
                        new_s = min(255, s * s_shift)
                        new_v = min(255, v * v_ratio)
                        
                        # Set the new HSV values
                        hsv_image[y, x] = [new_h, new_s, new_v]
            
            # Convert back to BGR
            shifted_image = cv2.cvtColor(hsv_image.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Update result with the recolored pixels from this mask
            mask_3d = mask_stack.astype(bool)
            result[mask_3d] = shifted_image[mask_3d]
        
        # Convert the result to bytes
        _, buffer = cv2.imencode('.png', result)
        return buffer.tobytes()
        
    except Exception as e:
        logger.error(f"Error applying palette with masking: {str(e)}")
        raise

def apply_palette_with_masking_optimized(image_url: str, palette_colors: List[str], blend_strength: float = 0.75) -> bytes:
    """Apply a color palette to an image using simplified masking and recoloring (optimized version).
    
    This is a more efficient implementation of the masking approach that avoids pixel-by-pixel operations.
    
    Args:
        image_url: URL of the image to process
        palette_colors: List of hex color codes
        blend_strength: How strongly to apply the new colors (0.0-1.0)
        
    Returns:
        Processed image as bytes
        
    Raises:
        Exception: If image processing fails
    """
    try:
        # Download image
        image = download_image(image_url)
        
        # Find dominant colors in original image
        dominant_colors = find_dominant_colors(image, min(5, len(palette_colors)))
        
        # Convert palette hex colors to BGR
        palette_bgr = [hex_to_bgr(color) for color in palette_colors]
        
        # Create a copy of the original image for recoloring
        result = image.copy()
        
        # For each dominant color, create a mask and replace with palette color
        for i, (dom_color, _) in enumerate(dominant_colors):
            if i >= len(palette_bgr):
                break
                
            # Create mask for this dominant color 
            # We use a smaller threshold for more precise masking
            mask = create_color_mask(image, dom_color, threshold=15)
            
            # Create a 3-channel mask for vector operations
            mask_3d = cv2.merge([mask, mask, mask]) // 255
            
            # Get corresponding palette color
            new_color = palette_bgr[i]
            
            # Apply color to masked area while preserving luminance
            # Convert to HSV for better color manipulation
            hsv_img = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            
            # Create an image filled with the new color
            color_img = np.full(image.shape, new_color, dtype=np.uint8)
            color_img_hsv = cv2.cvtColor(color_img, cv2.COLOR_BGR2HSV)
            
            # Create hybrid HSV image - using hue and saturation from new color
            # but better preserving value (brightness) from original image
            hybrid_hsv = hsv_img.copy()
            
            # Wherever mask applies, take H and S from color_img_hsv
            hybrid_hsv[:,:,0] = np.where(mask == 255, color_img_hsv[:,:,0], hybrid_hsv[:,:,0])
            hybrid_hsv[:,:,1] = np.where(mask == 255, color_img_hsv[:,:,1], hybrid_hsv[:,:,1])
            
            # Improved luminance preservation - calculate the ratio between original and 
            # new color brightness, and adjust the new brightness accordingly
            luminance_ratio = np.divide(hsv_img[:,:,2], np.maximum(1, color_img_hsv[:,:,2]))
            luminance_ratio = np.clip(luminance_ratio, 0.4, 2.0)  # Prevent extreme values
            hybrid_hsv[:,:,2] = np.where(
                mask == 255, 
                np.clip(color_img_hsv[:,:,2] * luminance_ratio, 0, 255), 
                hybrid_hsv[:,:,2]
            )
            
            # Convert back to BGR
            hybrid_bgr = cv2.cvtColor(hybrid_hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
            
            # Create temp result with the recolored area
            temp_result = np.where(mask_3d == 1, hybrid_bgr, result)
            
            # Blend between original and recolored version to preserve textures
            blended = cv2.addWeighted(
                temp_result, blend_strength,
                result, 1.0 - blend_strength,
                0
            )
            
            # Only update the masked region
            result = np.where(mask_3d == 1, blended, result)
        
        # Final blending to maintain more of the original texture
        final_result = cv2.addWeighted(result, 0.9, image, 0.1, 0)
        
        # Convert the result to bytes
        _, buffer = cv2.imencode('.png', final_result)
        return buffer.tobytes()
        
    except Exception as e:
        logger.error(f"Error applying palette with masking (optimized): {str(e)}")
        raise 