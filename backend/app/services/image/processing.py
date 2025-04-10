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


def hex_to_lab(hex_color: str) -> Tuple[float, float, float]:
    """
    Convert hex color code to LAB tuple.
    
    Args:
        hex_color: Hexadecimal color code (e.g., '#FF5733')
        
    Returns:
        LAB tuple (L*, a*, b*)
    """
    # Convert hex to BGR first
    bgr = hex_to_bgr(hex_color)
    
    # Convert BGR to LAB
    # Need to reshape for OpenCV color conversion
    bgr_array = np.array([[bgr]], dtype=np.uint8)
    lab_array = cv2.cvtColor(bgr_array, cv2.COLOR_BGR2LAB)
    
    # Return as tuple
    return tuple(map(float, lab_array[0][0]))


def apply_palette_with_masking_optimized(
    image_url_or_data: Union[str, BytesIO, bytes], 
    palette_colors: List[str], 
    blend_strength: float = 0.75
) -> bytes:
    """
    Apply a color palette to an image using LAB color space for better color mapping.
    
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
        
        # Download/read image
        logger.info("Converting image to OpenCV format...")
        image = download_image(image_url_or_data)
        
        # Verify image data
        if image is None:
            logger.error("Failed to load image, returned None from download_image")
            raise ValueError("Image could not be loaded or decoded")
            
        logger.info(f"Image loaded successfully, shape: {image.shape}, dtype: {image.dtype}")
        
        # Clone image for later blending if needed
        original_image = image.copy()
        
        # Get number of palette colors
        num_colors = min(5, len(palette_colors))
        palette_colors = palette_colors[:num_colors]
        logger.info(f"Using {num_colors} palette colors")
        
        # 1. Use K-means clustering for better initial segmentation
        # This helps determine regions more semantically than just lightness
        pixels = image.reshape(-1, 3).astype(np.float32)
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.2)
        _, labels, centers = cv2.kmeans(pixels, num_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)
        
        # 2. Convert palette colors to BGR
        palette_bgr = [hex_to_bgr(color) for color in palette_colors]
        
        # 3. Sort both centers and palette colors by brightness (sum of BGR)
        centers_with_idx = [(sum(center), i, center) for i, center in enumerate(centers)]
        centers_with_idx.sort(key=lambda x: x[0])
        
        palette_with_idx = [(sum(color), i, color) for i, color in enumerate(palette_bgr)]
        palette_with_idx.sort(key=lambda x: x[0])
        
        # 4. Create mapping from center index to palette color
        center_to_palette = {}
        for i in range(num_colors):
            center_idx = centers_with_idx[i][1]
            palette_idx = palette_with_idx[i][1]
            center_to_palette[center_idx] = palette_bgr[palette_idx]
        
        # 5. Create a new image
        result = np.zeros_like(image)
        
        # 6. Map each pixel to its new color based on the cluster it belongs to
        labels = labels.reshape(-1)
        for i in range(num_colors):
            # Create mask for this cluster
            mask = (labels == i)
            # Get the original cluster center
            center_color = centers[i]
            # Get the target palette color
            target_color = center_to_palette[i]
            
            # Convert to LAB for better color transfer
            original_bgr = np.uint8([[center_color]])
            target_bgr = np.uint8([[target_color]])
            
            original_lab = cv2.cvtColor(original_bgr, cv2.COLOR_BGR2LAB)[0][0]
            target_lab = cv2.cvtColor(target_bgr, cv2.COLOR_BGR2LAB)[0][0]
            
            # Get the pixels for this cluster
            cluster_pixels = image.reshape(-1, 3)[mask]
            
            # Convert cluster pixels to LAB
            cluster_lab = cv2.cvtColor(cluster_pixels.reshape(-1, 1, 3), cv2.COLOR_BGR2LAB).reshape(-1, 3)
            
            # Calculate LAB difference between original center and target color
            l_diff = float(target_lab[0]) - float(original_lab[0])
            a_diff = float(target_lab[1]) - float(original_lab[1])
            b_diff = float(target_lab[2]) - float(original_lab[2])
            
            # Apply the difference to all pixels in this cluster
            # But preserve relative variations in lightness for better texture
            cluster_lab[:, 0] = np.clip(cluster_lab[:, 0] + l_diff * 0.7, 0, 255)  # Partial L adjustment
            cluster_lab[:, 1] = np.clip(cluster_lab[:, 1] + a_diff, 0, 255)        # Full a adjustment
            cluster_lab[:, 2] = np.clip(cluster_lab[:, 2] + b_diff, 0, 255)        # Full b adjustment
            
            # Convert back to BGR
            cluster_bgr = cv2.cvtColor(cluster_lab.reshape(-1, 1, 3), cv2.COLOR_LAB2BGR).reshape(-1, 3)
            
            # Update the result image for this cluster
            result.reshape(-1, 3)[mask] = cluster_bgr
        
        # 7. Optional: Blend with original for texture preservation
        # Higher blend strength = more of the new colors
        final_result = cv2.addWeighted(
            result, blend_strength,
            original_image, 1.0 - blend_strength,
            0
        )
        
        # 8. Apply a slight saturation boost to make the colors more vibrant
        hsv_result = cv2.cvtColor(final_result, cv2.COLOR_BGR2HSV).astype(np.float32)
        # Increase saturation by 20%
        hsv_result[:, :, 1] = np.clip(hsv_result[:, :, 1] * 1.2, 0, 255)
        final_result = cv2.cvtColor(hsv_result.astype(np.uint8), cv2.COLOR_HSV2BGR)
        
        # 9. Encode the result to PNG format
        _, buffer = cv2.imencode('.png', final_result)
        result_bytes = buffer.tobytes()
        
        logger.info(f"Successfully encoded result, size: {len(result_bytes)} bytes")
        return result_bytes
        
    except Exception as e:
        logger.error(f"Error applying palette with LAB mapping: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise 