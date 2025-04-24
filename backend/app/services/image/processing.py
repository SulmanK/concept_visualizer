"""Image processing utilities.

This module provides utilities for image color processing, including
dominant color extraction, color masking, and palette application.
"""

import logging
from io import BytesIO
from typing import List, Tuple

import cv2
import numpy as np
import qrcode
from PIL import Image

logger = logging.getLogger(__name__)


def hex_to_bgr(hex_color: str) -> Tuple[int, int, int]:
    """Convert hex color code to BGR tuple (OpenCV format).

    Args:
        hex_color: Hexadecimal color code (e.g., '#FF5733')

    Returns:
        BGR tuple (Blue, Green, Red)
    """
    # Remove # if present
    if hex_color.startswith("#"):
        hex_color = hex_color[1:]

    # Parse hex values
    red = int(hex_color[0:2], 16)
    green = int(hex_color[2:4], 16)
    blue = int(hex_color[4:6], 16)

    # Return in BGR order for OpenCV
    return (blue, green, red)


def bgr_to_hex(bgr: Tuple[int, int, int]) -> str:
    """Convert BGR tuple to hex color code.

    Args:
        bgr: BGR tuple (Blue, Green, Red)

    Returns:
        Hexadecimal color code (e.g., '#FF5733')
    """
    blue, green, red = bgr
    return f"#{red:02x}{green:02x}{blue:02x}"


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

    # Convert None to np.array for proper typing
    best_labels = np.array([])
    # OpenCV kmeans will initialize and populate centers
    centers = np.array([])

    # Apply kmeans clustering
    _, labels, centers = cv2.kmeans(pixels, num_colors, best_labels, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Count labels to find percentages
    unique_labels, counts = np.unique(labels, return_counts=True)
    total_pixels = len(labels)

    # Create list of ((B,G,R), percentage) tuples
    colors: List[Tuple[Tuple[int, int, int], float]] = []
    for i in range(len(centers)):
        # Ensure we get exactly 3 integers for BGR
        b = int(centers[i][0])
        g = int(centers[i][1])
        r = int(centers[i][2])
        bgr = (b, g, r)
        percentage = float(counts[i] / total_pixels)
        colors.append((bgr, percentage))

    # Sort by percentage (most dominant first)
    colors.sort(key=lambda x: x[1], reverse=True)

    return colors[:num_colors]


async def extract_dominant_colors(image_data: bytes, num_colors: int = 8) -> List[str]:
    """Extract dominant colors from an image and return as hex codes.

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

    # Create a properly shaped array with the target color and convert to HSV
    target_color_array = np.array([[[target_color[0], target_color[1], target_color[2]]]], dtype=np.uint8)
    target_hsv = cv2.cvtColor(target_color_array, cv2.COLOR_BGR2HSV)[0][0]

    # Create range for target color
    # Explicitly convert to uint8 to avoid type mismatches and overflows
    h_thresh = min(threshold, 90)  # Limit hue threshold to avoid wrapping issues

    # Create bounds with proper types and clamping
    lower_bound = np.array(
        [
            max(0, int(target_hsv[0]) - h_thresh),
            max(0, int(target_hsv[1]) - threshold),
            max(0, int(target_hsv[2]) - threshold),
        ],
        dtype=np.uint8,
    )

    upper_bound = np.array(
        [
            min(179, int(target_hsv[0]) + h_thresh),
            min(255, int(target_hsv[1]) + threshold),
            min(255, int(target_hsv[2]) + threshold),
        ],
        dtype=np.uint8,
    )

    # Create mask
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)

    # Apply morphological operations to clean up the mask
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    return mask


def hex_to_lab(hex_color: str) -> Tuple[float, float, float]:
    """Convert hex color code to LAB tuple.

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

    # Return as a properly sized tuple of exactly 3 float values
    lab_values = lab_array[0][0]
    return (float(lab_values[0]), float(lab_values[1]), float(lab_values[2]))


def create_qr_code(data: str, fill_color: Tuple[int, int, int], back_color: Tuple[int, int, int]) -> np.ndarray:
    """Create a QR code image with specified colors.

    Args:
        data: Data to encode in the QR code
        fill_color: Fill color as (r, g, b)
        back_color: Background color as (r, g, b)

    Returns:
        QR code image as numpy array
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create QR code image with PIL
    img = qr.make_image(fill_color=fill_color, back_color=back_color)
    img = img.convert("RGB")

    # Convert PIL image to numpy array
    img_array = np.array(img)

    # Convert RGB to BGR for OpenCV compatibility
    img_bgr = cv2.cvtColor(img_array.astype(np.uint8), cv2.COLOR_RGB2BGR)

    return img_bgr


def apply_palette_with_masking_optimized(image: np.ndarray, palette: List[Tuple[int, int, int]], k: int = 10) -> np.ndarray:
    """Apply color palette to an image with optimized masking.

    Args:
        image: Input image as numpy array in BGR format
        palette: List of BGR colors to use
        k: Number of clusters for segmentation

    Returns:
        Processed image with palette colors
    """
    # Convert to LAB color space for better clustering
    lab_image = cv2.cvtColor(image.astype(np.uint8), cv2.COLOR_BGR2LAB)

    # Reshape for clustering
    pixels = lab_image.reshape(-1, 3).astype(np.float32)

    # Define criteria and apply kmeans
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 100, 0.1)

    # Initialize centers with shape (k, 3) for k clusters of 3D points
    initial_centers = np.zeros((k, 3), dtype=np.float32)

    # Apply KMeans clustering
    _, labels, centers = cv2.kmeans(pixels, k, initial_centers, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

    # Reshape labels to original image dimensions
    segmented_lab = centers[labels.flatten()].reshape(image.shape)

    # Convert back to BGR
    segmented_bgr = cv2.cvtColor(segmented_lab.astype(np.uint8), cv2.COLOR_LAB2BGR)

    # Create output image
    result = segmented_bgr.copy()

    # For each segment, find the closest palette color
    for i in range(k):
        # Create mask for this segment
        mask = (labels.reshape(image.shape[0], image.shape[1]) == i).astype(np.uint8)
        mask_expanded = np.expand_dims(mask, axis=2).repeat(3, axis=2)

        # Calculate average color of this segment in BGR
        segment_indices = np.where(mask == 1)
        if len(segment_indices[0]) == 0:
            continue  # Skip empty segments

        segment_colors = segmented_bgr[segment_indices]
        avg_color = np.mean(segment_colors, axis=0)

        # Find closest color in palette
        closest_color = min(palette, key=lambda color: np.sum((np.array(color) - avg_color) ** 2))

        # Apply palette color to this segment
        color_img = np.zeros_like(result)
        color_img[:] = closest_color

        # Apply mask
        np.copyto(result, color_img, where=mask_expanded.astype(bool))

    # Ensure we return the correct type
    return np.asarray(result, dtype=np.uint8)
