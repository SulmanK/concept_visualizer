# Image Processing Module

The `processing.py` module provides core functionality for analyzing, manipulating, and transforming images beyond basic conversion operations.

## Overview

The image processing module offers specialized capabilities for:

1. Analyzing image content and extracting information
2. Applying visual effects and transformations to images
3. Optimizing images for different contexts and use cases
4. Generating visual derivatives from existing images

These capabilities support the application's advanced image manipulation needs, enabling features like color analysis, image enhancement, and automated visual adjustments.

## Key Functions

### Extract Dominant Colors

```python
async def extract_dominant_colors(
    image_data: bytes,
    num_colors: int = 5,
    exclusion_threshold: float = 0.05
) -> List[Dict[str, str]]:
    """Extract the dominant colors from an image."""
```

This function analyzes an image and extracts its most prominent colors.

**Parameters:**

- `image_data`: Binary image data to analyze
- `num_colors`: Number of dominant colors to extract (default: 5)
- `exclusion_threshold`: Threshold to exclude similar colors (default: 0.05)

**Returns:**

- List of color dictionaries with hex, rgb, and hsl values

**Raises:**

- `ImageProcessingError`: If color extraction fails

### Apply Color Palette

```python
async def apply_color_palette(
    image_data: bytes,
    palette: List[str],
    preserve_luminance: bool = True
) -> bytes:
    """Apply a color palette to an image."""
```

This function transforms an image by mapping its colors to a target palette.

**Parameters:**

- `image_data`: Binary image data to transform
- `palette`: List of hex color codes to apply
- `preserve_luminance`: Whether to preserve the original brightness values

**Returns:**

- Binary data of the transformed image

**Raises:**

- `ImageProcessingError`: If palette application fails

### Enhance Image

```python
async def enhance_image(
    image_data: bytes,
    brightness: float = 1.0,
    contrast: float = 1.0,
    saturation: float = 1.0,
    sharpness: float = 1.0
) -> bytes:
    """Enhance an image by adjusting its visual properties."""
```

This function improves image quality by adjusting visual parameters.

**Parameters:**

- `image_data`: Binary image data to enhance
- `brightness`: Brightness adjustment factor (0.0-2.0, default: 1.0)
- `contrast`: Contrast adjustment factor (0.0-2.0, default: 1.0)
- `saturation`: Saturation adjustment factor (0.0-2.0, default: 1.0)
- `sharpness`: Sharpness adjustment factor (0.0-2.0, default: 1.0)

**Returns:**

- Binary data of the enhanced image

**Raises:**

- `ImageProcessingError`: If enhancement fails

### Generate Image Variations

```python
async def generate_variations(
    image_data: bytes,
    variation_types: List[str],
    params: Optional[Dict[str, Any]] = None
) -> Dict[str, bytes]:
    """Generate multiple variations of an image."""
```

This function creates different versions of an image for various use cases.

**Parameters:**

- `image_data`: Binary image data to process
- `variation_types`: List of variation types to generate (e.g., "thumbnail", "grayscale")
- `params`: Optional parameters for specific variation types

**Returns:**

- Dictionary mapping variation types to binary image data

**Raises:**

- `ImageProcessingError`: If variation generation fails
- `UnsupportedVariationError`: If a requested variation type is not supported

## Image Analysis

The module provides several image analysis capabilities:

### Color Analysis

- Dominant color extraction using clustering algorithms
- Color distribution histograms
- Color scheme classification (e.g., monochromatic, analogous)

### Composition Analysis

- Rule of thirds assessment
- Focal point detection
- Balance and symmetry analysis

### Quality Analysis

- Noise level detection
- Sharpness assessment
- Exposure evaluation

## Enhancement Techniques

The module implements several enhancement techniques:

### Color Enhancement

- Color balancing
- Saturation adjustment
- Color temperature correction

### Detail Enhancement

- Sharpening filters
- Detail boosting
- Noise reduction

### Tonal Enhancement

- Contrast adjustment
- Shadow and highlight recovery
- Histogram equalization

## Implementation Details

### Image Processing Libraries

The module uses several specialized libraries:

1. **Pillow/PIL**: For basic image manipulation
2. **scikit-image**: For advanced image analysis
3. **NumPy**: For efficient array operations
4. **OpenCV**: For computer vision techniques

### Processing Pipeline

Image processing operations follow a pipeline approach:

1. **Decoding**: Convert binary data to in-memory image
2. **Analysis**: Extract information from the image
3. **Transformation**: Apply requested modifications
4. **Encoding**: Convert back to binary data

### Threading and Async

- CPU-intensive operations are run in a thread pool
- All public functions are asynchronous
- Progress tracking is available for time-consuming operations

## Performance Considerations

- Operations are optimized for memory efficiency
- Processing time scales with image size and complexity
- Caching is used for expensive analysis operations
- Sequential operations are batched when possible

## Usage Examples

### Extracting and Using Dominant Colors

```python
from app.services.image.processing import extract_dominant_colors

# Extract dominant colors from an image
with open("logo.png", "rb") as f:
    image_data = f.read()

colors = await extract_dominant_colors(
    image_data=image_data,
    num_colors=5
)

# Use the extracted colors
for i, color in enumerate(colors):
    print(f"Color {i+1}: {color['hex']} (RGB: {color['rgb']})")
```

### Enhancing an Image

```python
from app.services.image.processing import enhance_image

# Read the original image
with open("photo.jpg", "rb") as f:
    image_data = f.read()

# Enhance the image
enhanced_image = await enhance_image(
    image_data=image_data,
    brightness=1.1,
    contrast=1.2,
    saturation=1.1,
    sharpness=1.3
)

# Save the enhanced image
with open("enhanced_photo.jpg", "wb") as f:
    f.write(enhanced_image)
```

## Error Handling

The module implements comprehensive error handling:

1. **Input Validation**: Validates parameters before processing
2. **Format Detection**: Verifies image formats and raises appropriate errors
3. **Resource Management**: Ensures resources are properly cleaned up
4. **Contextual Errors**: Provides detailed error messages with context

## Related Documentation

- [Image Service](service.md): Main image service that uses processing functions
- [Image Conversion](conversion.md): Format conversion operations
- [Processing Service](processing_service.md): Service that orchestrates processing
- [Image Interface](interface.md): Interface for image services
- [Concept Service](../concept/service.md): Service that uses image processing for concept generation
