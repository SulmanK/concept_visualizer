"""Tests for the image processing utilities.

This module contains tests for the processing functions that handle
color operations, palette extraction, and palette application.
"""

import pytest
import numpy as np
import cv2
from unittest.mock import patch, AsyncMock, MagicMock
from io import BytesIO
from PIL import Image

from app.services.image.processing import (
    hex_to_bgr,
    bgr_to_hex,
    hex_to_lab,
    find_dominant_colors,
    extract_dominant_colors,
    create_color_mask,
    apply_palette_with_masking_optimized
)


@pytest.fixture
def sample_image_bytes():
    """Create a simple test image with distinct colors and return its bytes."""
    # Create a 100x100 image with 4 distinct colored quadrants
    img = Image.new('RGB', (100, 100), color='white')
    
    # Add red, green, blue, and yellow quadrants
    colors = [
        ('red', (255, 0, 0)),
        ('green', (0, 255, 0)),
        ('blue', (0, 0, 255)),
        ('yellow', (255, 255, 0))
    ]
    
    for i, (name, color) in enumerate(colors):
        x_start = 0 if i % 2 == 0 else 50
        y_start = 0 if i < 2 else 50
        
        for x in range(x_start, x_start + 50):
            for y in range(y_start, y_start + 50):
                img.putpixel((x, y), color)
    
    img_bytes = BytesIO()
    img.save(img_bytes, format='PNG')
    return img_bytes.getvalue()


@pytest.fixture
def sample_cv_image():
    """Create a simple OpenCV image with distinct colors."""
    # Create a 100x100 image with 4 distinct colored quadrants (in BGR format)
    img = np.ones((100, 100, 3), dtype=np.uint8) * 255  # White
    
    # BGR colors (OpenCV uses BGR)
    colors = [
        (0, 0, 255),    # Red in BGR
        (0, 255, 0),    # Green in BGR
        (255, 0, 0),    # Blue in BGR
        (0, 255, 255)   # Yellow in BGR
    ]
    
    for i, color in enumerate(colors):
        x_start = 0 if i % 2 == 0 else 50
        y_start = 0 if i < 2 else 50
        
        # Fill quadrant with color
        img[y_start:y_start+50, x_start:x_start+50] = color
    
    return img


class TestColorConversion:
    """Tests for color conversion functions."""

    def test_hex_to_bgr(self):
        """Test conversion from hex color code to BGR tuple."""
        # Test with hash prefix
        assert hex_to_bgr('#FF5733') == (51, 87, 255)
        
        # Test without hash prefix
        assert hex_to_bgr('00FF00') == (0, 255, 0)
        
        # Test black and white
        assert hex_to_bgr('#FFFFFF') == (255, 255, 255)
        assert hex_to_bgr('#000000') == (0, 0, 0)

    def test_bgr_to_hex(self):
        """Test conversion from BGR tuple to hex color code."""
        assert bgr_to_hex((51, 87, 255)) == '#ff5733'
        assert bgr_to_hex((0, 255, 0)) == '#00ff00'
        assert bgr_to_hex((255, 255, 255)) == '#ffffff'
        assert bgr_to_hex((0, 0, 0)) == '#000000'

    @patch('cv2.cvtColor')
    def test_hex_to_lab(self, mock_cvtcolor):
        """Test conversion from hex color to LAB color space."""
        # Mock the cv2.cvtColor to return a known LAB value
        mock_lab_value = np.array([[[50.0, 80.0, 70.0]]], dtype=np.float32)
        mock_cvtcolor.return_value = mock_lab_value
        
        # Execute
        lab = hex_to_lab('#FF0000')  # Pure red
        
        # Verify lab is a 3-tuple of floats
        assert isinstance(lab, tuple)
        assert len(lab) == 3
        assert all(isinstance(v, float) for v in lab)
        
        # Verify values match our mocked output
        assert lab == (50.0, 80.0, 70.0)
        
        # Verify cv2.cvtColor was called
        mock_cvtcolor.assert_called_once()


class TestDominantColors:
    """Tests for dominant color extraction functions."""

    @patch('cv2.kmeans')
    def test_find_dominant_colors(self, mock_kmeans, sample_cv_image):
        """Test finding dominant colors in an image."""
        # Setup mock kmeans results
        mock_labels = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1, 2, 3])
        mock_centers = np.array([
            [0, 0, 255],    # Red in BGR
            [0, 255, 0],    # Green in BGR
            [255, 0, 0],    # Blue in BGR
            [0, 255, 255]   # Yellow in BGR
        ], dtype=np.float32)
        
        mock_kmeans.return_value = (None, mock_labels, mock_centers)
        
        # Execute
        result = find_dominant_colors(sample_cv_image, num_colors=4)
        
        # Verify
        assert len(result) == 4
        
        # Each result should be a tuple of (BGR color, percentage)
        for color_tuple in result:
            assert len(color_tuple) == 2
            assert len(color_tuple[0]) == 3
            assert 0 <= color_tuple[1] <= 1.0

    @patch('cv2.cvtColor')
    @patch('app.services.image.processing.find_dominant_colors')
    async def test_extract_dominant_colors(self, mock_find_colors, mock_cvtcolor, sample_image_bytes):
        """Test extracting dominant colors from image bytes."""
        # Setup
        mock_find_colors.return_value = [
            ((0, 0, 255), 0.25),   # Red in BGR
            ((0, 255, 0), 0.25),   # Green in BGR
            ((255, 0, 0), 0.25),   # Blue in BGR
            ((0, 255, 255), 0.25)  # Yellow in BGR
        ]
        
        # Execute
        result = await extract_dominant_colors(sample_image_bytes, num_colors=4)
        
        # Verify
        assert len(result) == 4
        assert '#ff0000' in result  # Red
        assert '#00ff00' in result  # Green
        assert '#0000ff' in result  # Blue
        assert '#ffff00' in result  # Yellow
    
    @patch('PIL.Image.open')
    @patch('cv2.cvtColor')
    @patch('app.services.image.processing.find_dominant_colors')
    async def test_extract_dominant_colors_with_different_color_counts(self, mock_find_colors, mock_cvtcolor, mock_pil_open, sample_image_bytes):
        """Test extracting different numbers of dominant colors."""
        # Setup mock find_dominant_colors to return varying number of colors based on input
        def find_colors_side_effect(image, num_colors):
            # Generate the requested number of colors
            colors = []
            for i in range(num_colors):
                # Create some deterministic color based on index
                bgr = (i * 30, 255 - i * 30, i * 20)
                percentage = 1.0 / num_colors
                colors.append((bgr, percentage))
            return colors
        
        mock_find_colors.side_effect = find_colors_side_effect
        
        # Setup PIL Image
        mock_img = MagicMock()
        mock_pil_open.return_value = mock_img
        mock_img.convert.return_value = mock_img
        
        # Mock cv2.cvtColor to return a dummy BGR image
        mock_cvtcolor.return_value = np.zeros((10, 10, 3), dtype=np.uint8)
        
        # Test with different numbers of colors
        color_counts = [1, 3, 5, 8, 12]
        
        for count in color_counts:
            # Execute
            result = await extract_dominant_colors(sample_image_bytes, num_colors=count)
            
            # Verify
            assert len(result) == count, f"Expected {count} colors, got {len(result)}"
            
            # Verify find_dominant_colors was called with correct count
            mock_find_colors.assert_called_with(ANY, count)
    
    @patch('cv2.cvtColor')
    @patch('app.services.image.processing.find_dominant_colors')
    async def test_extract_dominant_colors_with_grayscale(self, mock_find_colors, mock_cvtcolor, sample_image_bytes):
        """Test extracting dominant colors from a grayscale image."""
        # Setup find_dominant_colors to return grayscale values
        mock_find_colors.return_value = [
            ((50, 50, 50), 0.3),   # Dark gray
            ((150, 150, 150), 0.3), # Medium gray
            ((200, 200, 200), 0.4)  # Light gray
        ]
        
        # Execute
        result = await extract_dominant_colors(sample_image_bytes, num_colors=3)
        
        # Verify
        assert len(result) == 3
        
        # The output colors should be converted to hex
        # (BGR values are flipped to RGB for hex)
        assert '#323232' in result  # Dark gray
        assert '#969696' in result  # Medium gray
        assert '#c8c8c8' in result  # Light gray
    
    @patch('cv2.cvtColor')
    @patch('app.services.image.processing.find_dominant_colors')
    async def test_extract_dominant_colors_sorting(self, mock_find_colors, mock_cvtcolor, sample_image_bytes):
        """Test that colors are sorted by dominance (percentage)."""
        # Setup colors with different percentages (out of order)
        mock_find_colors.return_value = [
            ((0, 0, 255), 0.1),    # Red - least dominant
            ((0, 255, 0), 0.6),    # Green - most dominant
            ((255, 0, 0), 0.3)     # Blue - middle
        ]
        
        # Execute
        result = await extract_dominant_colors(sample_image_bytes, num_colors=3)
        
        # Verify the order based on our knowledge of the hex colors
        assert result[0] == '#00ff00'  # Green (most dominant)
        assert result[1] == '#0000ff'  # Blue (middle)
        assert result[2] == '#ff0000'  # Red (least dominant)
    
    @patch('PIL.Image.open')
    async def test_extract_dominant_colors_with_tiny_image(self, mock_pil_open, sample_image_bytes):
        """Test extracting dominant colors from a very small image."""
        # Create a tiny 1x1 pixel image
        tiny_img_mock = MagicMock()
        tiny_arr = np.array([[[255, 0, 0]]])  # Single red pixel in RGB
        tiny_img_mock.convert.return_value.__array__ = lambda: tiny_arr
        mock_pil_open.return_value = tiny_img_mock
        
        # Execute with mocked cv2.cvtColor and kmeans
        with patch('cv2.cvtColor', return_value=np.array([[[0, 0, 255]]])), \
             patch('app.services.image.processing.find_dominant_colors') as mock_find_colors:
            
            # For a 1x1 image, there's only one color to find
            mock_find_colors.return_value = [((0, 0, 255), 1.0)]  # 100% red in BGR
            
            result = await extract_dominant_colors(sample_image_bytes, num_colors=5)
            
            # Even though we asked for 5 colors, we should only get 1
            assert len(result) == 1
            assert result[0] == '#ff0000'  # Red
    
    @patch('PIL.Image.open')
    async def test_extract_dominant_colors_empty_image(self, mock_pil_open, sample_image_bytes):
        """Test handling of an "empty" or single-color image."""
        # Create a black image
        black_img_mock = MagicMock()
        black_arr = np.zeros((10, 10, 3), dtype=np.uint8)  # All zeros (black)
        black_img_mock.convert.return_value.__array__ = lambda: black_arr
        mock_pil_open.return_value = black_img_mock
        
        # Execute with mocked cv2.cvtColor and find_dominant_colors
        with patch('cv2.cvtColor', return_value=np.zeros((10, 10, 3), dtype=np.uint8)), \
             patch('app.services.image.processing.find_dominant_colors') as mock_find_colors:
            
            # Even with a uniform black image, kmeans should find one center
            mock_find_colors.return_value = [((0, 0, 0), 1.0)]  # 100% black
            
            result = await extract_dominant_colors(sample_image_bytes, num_colors=3)
            
            assert len(result) == 1
            assert result[0] == '#000000'  # Black
    
    @patch('PIL.Image.open')
    async def test_extract_dominant_colors_error_handling(self, mock_pil_open):
        """Test error handling in extract_dominant_colors."""
        # Setup: Image.open raises an exception
        mock_pil_open.side_effect = Exception("Failed to open image")
        
        # Execute and verify
        with pytest.raises(Exception) as excinfo:
            await extract_dominant_colors(b"invalid_image_data", num_colors=3)
        
        assert "Failed to open image" in str(excinfo.value)


class TestColorMasking:
    """Tests for color masking functions."""

    def test_create_color_mask(self, sample_cv_image):
        """Test creating a binary mask for a target color."""
        # Test masking for red (BGR: 0, 0, 255)
        mask = create_color_mask(sample_cv_image, target_color=(0, 0, 255), threshold=20)
        
        # Verify mask is binary (0s and 255s)
        assert set(np.unique(mask)).issubset({0, 255})
        
        # Verify mask shape
        assert mask.shape == (100, 100)
        
        # The top-left quadrant should be mostly masked (255)
        # Calculate percentage of pixels that are 255 in top-left quadrant
        top_left_mask = mask[0:50, 0:50]
        masked_percentage = np.sum(top_left_mask == 255) / (50 * 50)
        assert masked_percentage > 0.9  # Allow for some imperfection due to HSV conversion

    def test_create_color_mask_with_different_thresholds(self, sample_cv_image):
        """Test color mask creation with different threshold values."""
        # Lower threshold should mask more pixels
        low_threshold_mask = create_color_mask(sample_cv_image, target_color=(0, 0, 255), threshold=50)
        
        # Higher threshold should mask fewer pixels
        high_threshold_mask = create_color_mask(sample_cv_image, target_color=(0, 0, 255), threshold=5)
        
        # Count masked pixels for each
        low_threshold_pixels = np.sum(low_threshold_mask == 255)
        high_threshold_pixels = np.sum(high_threshold_mask == 255)
        
        # Lower threshold should result in more masked pixels
        assert low_threshold_pixels >= high_threshold_pixels

    def test_create_color_mask_mixed_color(self, sample_cv_image):
        """Test creating a mask for a color that doesn't exactly match any region."""
        # Use a slightly off-red color (BGR: 20, 20, 235) 
        mask = create_color_mask(sample_cv_image, target_color=(20, 20, 235), threshold=30)
        
        # Should still primarily mask the red region (top-left)
        top_left_mask = mask[0:50, 0:50]
        top_left_percentage = np.sum(top_left_mask == 255) / (50 * 50)
        
        # Other regions should have fewer masked pixels
        other_regions = [
            mask[0:50, 50:100],  # Top-right
            mask[50:100, 0:50],  # Bottom-left
            mask[50:100, 50:100]  # Bottom-right
        ]
        
        other_percentages = [np.sum(region == 255) / (50 * 50) for region in other_regions]
        
        # Red region should have significant masked pixels
        assert top_left_percentage > 0.5, f"Top-left percentage: {top_left_percentage}"
        
        # At least one other region should have fewer masked pixels
        assert any(p < top_left_percentage for p in other_percentages), \
            f"Top-left: {top_left_percentage}, Others: {other_percentages}"

    def test_create_color_mask_hsv_conversion(self, sample_cv_image):
        """Test that create_color_mask uses HSV color space conversion."""
        # Count original calls to cv2.cvtColor
        original_cvtColor = cv2.cvtColor
        call_count = [0]
        hsv_calls = [0]
        
        def mock_cvtColor(img, color_code, *args, **kwargs):
            call_count[0] += 1
            if color_code == cv2.COLOR_BGR2HSV:
                hsv_calls[0] += 1
            return original_cvtColor(img, color_code, *args, **kwargs)
        
        # Patch the cv2.cvtColor function
        with patch('cv2.cvtColor', side_effect=mock_cvtColor):
            create_color_mask(sample_cv_image, target_color=(0, 0, 255), threshold=20)
            
            # Verify that cv2.cvtColor was called at least once with COLOR_BGR2HSV
            assert hsv_calls[0] > 0, "cv2.cvtColor was not called with COLOR_BGR2HSV"

    def test_create_color_mask_with_empty_image(self):
        """Test creating a mask with an empty image."""
        # Create a tiny 1x1 black image
        empty_image = np.zeros((1, 1, 3), dtype=np.uint8)
        
        # This should work without errors
        mask = create_color_mask(empty_image, target_color=(0, 0, 255), threshold=20)
        
        # Verify mask has the correct shape
        assert mask.shape == (1, 1)
        
        # The pixel should not be masked since it's black, not red
        assert mask[0, 0] == 0


class TestPaletteApplication:
    """Tests for palette application functions."""

    @patch('app.utils.http_utils.download_image')
    @patch('app.services.image.processing.cv2.kmeans')
    async def test_apply_palette_with_masking_from_bytes(self, mock_kmeans, mock_download, sample_image_bytes, sample_cv_image):
        """Test applying a color palette to image bytes."""
        # Setup mock kmeans results
        mock_labels = np.array([0, 1, 2, 3] * (100*100//4), dtype=np.int32).reshape(-1)
        mock_centers = np.array([
            [0, 0, 255],    # Red in BGR
            [0, 255, 0],    # Green in BGR
            [255, 0, 0],    # Blue in BGR
            [0, 255, 255]   # Yellow in BGR
        ], dtype=np.float32)
        
        mock_kmeans.return_value = (None, mock_labels, mock_centers)
        
        # Download should return the original image bytes (not actually downloading)
        mock_download.return_value = sample_image_bytes
        
        # Palette colors to apply
        palette_colors = ['#800080', '#008080', '#808000', '#800000']  # Purple, Teal, Olive, Maroon
        
        # Execute
        with patch('cv2.imdecode') as mock_imdecode, \
             patch('cv2.imencode') as mock_imencode, \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.addWeighted') as mock_addweighted:
            
            # Mock image decoding
            mock_imdecode.return_value = sample_cv_image
            
            # Mock color conversion to return predictable values
            def cvt_color_side_effect(img, conversion_code, *args, **kwargs):
                if conversion_code == cv2.COLOR_BGR2LAB:
                    # Return a pre-defined LAB array with same shape as input
                    return np.ones(img.shape, dtype=np.uint8) * 50
                elif conversion_code == cv2.COLOR_LAB2BGR:
                    # Return a pre-defined BGR array with same shape as input
                    return np.ones(img.shape, dtype=np.uint8) * 100
                elif conversion_code == cv2.COLOR_BGR2HSV:
                    # Return a pre-defined HSV array with same shape as input
                    return np.ones(img.shape, dtype=np.uint8) * 30
                elif conversion_code == cv2.COLOR_HSV2BGR:
                    # Return a pre-defined BGR array with same shape as input
                    return np.ones(img.shape, dtype=np.uint8) * 150
                else:
                    # Default case, just return the input with minor change
                    return img + 1
            
            mock_cvtcolor.side_effect = cvt_color_side_effect
            
            # Mock blending function
            mock_addweighted.return_value = np.ones((100, 100, 3), dtype=np.uint8) * 120
            
            # Mock image encoding
            fake_encoded = (None, np.array([1, 2, 3], dtype=np.uint8))
            mock_imencode.return_value = fake_encoded
            
            result = await apply_palette_with_masking_optimized(
                sample_image_bytes, 
                palette_colors, 
                blend_strength=0.8
            )
            
            # Verify
            assert mock_download.called is False  # Should not download for bytes input
            mock_kmeans.assert_called_once()
            mock_imencode.assert_called_once()
            mock_addweighted.assert_called_once()  # Verify blending was performed
            
            # Verify that color conversions occurred (BGR to LAB and LAB to BGR)
            bgr2lab_calls = sum(1 for call in mock_cvtcolor.call_args_list if call[0][1] == cv2.COLOR_BGR2LAB)
            lab2bgr_calls = sum(1 for call in mock_cvtcolor.call_args_list if call[0][1] == cv2.COLOR_LAB2BGR)
            assert bgr2lab_calls > 0, "BGR to LAB conversion not performed"
            assert lab2bgr_calls > 0, "LAB to BGR conversion not performed"
            
            assert isinstance(result, bytes)  # Result should be image bytes

    @patch('app.utils.http_utils.download_image')
    async def test_apply_palette_with_masking_from_url(self, mock_download, sample_image_bytes, sample_cv_image):
        """Test applying a color palette to image from URL."""
        # Setup
        mock_download.return_value = sample_image_bytes
        
        # Palette colors to apply
        palette_colors = ['#800080', '#008080', '#808000', '#800000']  # Purple, Teal, Olive, Maroon
        
        # Execute
        with patch('cv2.imdecode') as mock_imdecode, \
             patch('cv2.imencode') as mock_imencode, \
             patch('app.services.image.processing.cv2.kmeans') as mock_kmeans, \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.addWeighted') as mock_addweighted:
            
            # Mock k-means
            mock_labels = np.array([0, 1, 2, 3] * (100*100//4), dtype=np.int32).reshape(-1)
            mock_centers = np.array([
                [0, 0, 255],    # Red in BGR
                [0, 255, 0],    # Green in BGR
                [255, 0, 0],    # Blue in BGR
                [0, 255, 255]   # Yellow in BGR
            ], dtype=np.float32)
            mock_kmeans.return_value = (None, mock_labels, mock_centers)
            
            # Mock image decoding
            mock_imdecode.return_value = sample_cv_image
            
            # Mock color conversions
            def cvt_color_side_effect(img, conversion_code, *args, **kwargs):
                if conversion_code == cv2.COLOR_BGR2LAB or conversion_code == cv2.COLOR_LAB2BGR:
                    return np.ones(img.shape, dtype=np.uint8) * 50
                else:
                    return img + 1
            
            mock_cvtcolor.side_effect = cvt_color_side_effect
            
            # Mock blending function
            mock_addweighted.return_value = np.ones((100, 100, 3), dtype=np.uint8) * 120
            
            # Mock image encoding
            fake_encoded = (None, np.array([1, 2, 3], dtype=np.uint8))
            mock_imencode.return_value = fake_encoded
            
            result = await apply_palette_with_masking_optimized(
                "https://example.com/image.jpg", 
                palette_colors, 
                blend_strength=0.8
            )
            
            # Verify
            mock_download.assert_called_once_with("https://example.com/image.jpg")
            mock_kmeans.assert_called_once()
            mock_imencode.assert_called_once()
            mock_addweighted.assert_called_once()
            assert isinstance(result, bytes)  # Result should be image bytes
    
    @patch('app.utils.http_utils.download_image')
    async def test_apply_palette_clustering_logic(self, mock_download, sample_image_bytes, sample_cv_image):
        """Test the color clustering and mapping logic in apply_palette_with_masking_optimized."""
        # Setup
        mock_download.return_value = sample_image_bytes
        palette_colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00']  # Red, Green, Blue, Yellow
        
        # Execute
        with patch('cv2.imdecode') as mock_imdecode, \
             patch('cv2.imencode') as mock_imencode, \
             patch('app.services.image.processing.cv2.kmeans') as mock_kmeans, \
             patch('cv2.cvtColor') as mock_cvtcolor, \
             patch('cv2.addWeighted') as mock_addweighted:
            
            # Mock k-means
            mock_labels = np.array([0, 1, 2, 3] * (100*100//4), dtype=np.int32).reshape(-1)
            mock_centers = np.array([
                [0, 0, 255],    # Red in BGR
                [0, 255, 0],    # Green in BGR
                [255, 0, 0],    # Blue in BGR
                [0, 255, 255]   # Yellow in BGR
            ], dtype=np.float32)
            mock_kmeans.return_value = (None, mock_labels, mock_centers)
            
            # Mock image decoding
            mock_imdecode.return_value = sample_cv_image
            
            # Mock color conversions but keep track of the inputs and outputs
            conversion_calls = []
            def cvt_color_tracking(img, conversion_code, *args, **kwargs):
                # Store the conversion type and rough size of input
                conversion_calls.append((conversion_code, img.shape))
                
                # Return appropriate format
                if conversion_code == cv2.COLOR_BGR2LAB:
                    # Return a simple LAB array
                    return np.ones(img.shape, dtype=np.uint8) * 50
                elif conversion_code == cv2.COLOR_LAB2BGR:
                    # Return a BGR array
                    return np.ones(img.shape, dtype=np.uint8) * 100
                else:
                    return img
            
            mock_cvtcolor.side_effect = cvt_color_tracking
            
            # Mock image encoding
            fake_encoded = (None, np.array([1, 2, 3], dtype=np.uint8))
            mock_imencode.return_value = fake_encoded
            
            # Mock blending - this is where the color clusters are merged
            mock_addweighted.return_value = np.ones((100, 100, 3), dtype=np.uint8) * 120
            
            result = await apply_palette_with_masking_optimized(
                sample_image_bytes, 
                palette_colors, 
                blend_strength=0.6  # Different blend_strength to test that parameter
            )
            
            # Verify
            assert mock_kmeans.call_count == 1
            # Verify that the number of clusters matches palette colors
            kmeans_clusters = mock_kmeans.call_args[0][1]  # Second argument is num_clusters
            assert kmeans_clusters == min(5, len(palette_colors))
            
            # Verify blend_strength parameter was passed correctly
            blend_strength = mock_addweighted.call_args[0][1]  # Second arg is alpha for source1
            assert blend_strength == 0.6
            
            # Verify color space conversions happened for sorting by brightness
            assert any(code == cv2.COLOR_BGR2LAB for code, _ in conversion_calls)
            assert any(code == cv2.COLOR_LAB2BGR for code, _ in conversion_calls)
            
            assert isinstance(result, bytes)

    @patch('app.utils.http_utils.download_image')
    async def test_apply_palette_error_handling(self, mock_download):
        """Test error handling in palette application."""
        # Setup: Download raises an exception
        mock_download.side_effect = Exception("Download failed")
        
        # Execute and verify
        with pytest.raises(Exception) as excinfo:
            await apply_palette_with_masking_optimized(
                "https://example.com/image.jpg", 
                ['#FF0000', '#00FF00'], 
                blend_strength=0.8
            )
        
        assert "Download failed" in str(excinfo.value)

    @patch('app.utils.http_utils.download_image')
    async def test_image_load_failure(self, mock_download, sample_image_bytes):
        """Test handling of image loading failure."""
        # Setup
        mock_download.return_value = sample_image_bytes
        
        # Execute
        with patch('cv2.imdecode') as mock_imdecode:
            # Mock image decoding fails
            mock_imdecode.return_value = None
            
            with pytest.raises(ValueError) as excinfo:
                await apply_palette_with_masking_optimized(
                    "https://example.com/image.jpg", 
                    ['#FF0000', '#00FF00']
                )
            
            # Verify
            assert "could not be loaded" in str(excinfo.value)
            
    @patch('app.utils.http_utils.download_image')
    async def test_palette_blending_strength(self, mock_download, sample_image_bytes, sample_cv_image):
        """Test different blend strengths affect the output as expected."""
        # Setup
        mock_download.return_value = sample_image_bytes
        palette_colors = ['#800080', '#008080']  # Purple, Teal
        
        blend_strengths_to_test = [0.1, 0.5, 0.9]
        blend_results = {}
        
        # Execute with different blend strengths and save results
        for blend_strength in blend_strengths_to_test:
            with patch('cv2.imdecode') as mock_imdecode, \
                 patch('cv2.imencode') as mock_imencode, \
                 patch('app.services.image.processing.cv2.kmeans') as mock_kmeans, \
                 patch('cv2.cvtColor') as mock_cvtcolor, \
                 patch('cv2.addWeighted') as mock_addweighted:
                
                # Mock k-means
                mock_kmeans.return_value = (None, np.array([0, 1]), np.array([[0, 0, 255], [0, 255, 0]]))
                
                # Mock image decoding
                mock_imdecode.return_value = sample_cv_image
                
                # Mock color conversions
                mock_cvtcolor.return_value = np.zeros((10, 10, 3), dtype=np.uint8)
                
                # Important: capture the blend strength in addWeighted
                def add_weighted_side_effect(src1, alpha, src2, beta, gamma):
                    # Save the alpha value (blend_strength) used
                    blend_results[alpha] = True
                    return np.ones((100, 100, 3), dtype=np.uint8) * 100
                
                mock_addweighted.side_effect = add_weighted_side_effect
                
                # Mock image encoding
                fake_encoded = (None, np.array([alpha * 10 for alpha in range(1, 10)], dtype=np.uint8))
                mock_imencode.return_value = fake_encoded
                
                await apply_palette_with_masking_optimized(
                    sample_image_bytes, 
                    palette_colors, 
                    blend_strength=blend_strength
                )
        
        # Verify that each blend strength was used correctly
        for blend_strength in blend_strengths_to_test:
            assert blend_strength in blend_results, f"Blend strength {blend_strength} was not used" 