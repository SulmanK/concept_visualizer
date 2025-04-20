# Image Service

The `service.py` module implements the main image service, which provides a unified interface for all image-related operations in the application.

## Overview

The Image Service:

1. Implements the `ImageServiceInterface`
2. Orchestrates interactions between specialized image processing components
3. Provides a cohesive API for image manipulation, analysis, and conversion
4. Handles resource management and error handling for image operations

As a primary service in the application, it abstracts away the complexities of the underlying image processing libraries and provides a consistent, high-level interface for client code.

## Service Implementation

```python
class ImageService(ImageServiceInterface):
    """Main implementation of the image service interface."""
    
    def __init__(
        self,
        processing_service: Optional[ImageProcessingService] = None,
        cache_service: Optional[CacheServiceInterface] = None
    ):
        """Initialize the image service with optional dependencies."""
        self.processing_service = processing_service or ImageProcessingService()
        self.cache_service = cache_service
        self.logger = logging.getLogger("image_service")
```

The service is designed to work with optional dependencies, which can be injected for customization and testing.

## Interface Method Implementations

### Convert Format

```python
async def convert_format(
    self, image_data: bytes, source_format: str, target_format: str, **kwargs
) -> bytes:
    """Convert an image from one format to another."""
```

This method implements the interface method for format conversion, delegating to the appropriate specialized functions.

**Parameters:**
- `image_data`: Binary image data to convert
- `source_format`: Format of the input image (e.g., "png", "jpeg")
- `target_format`: Desired output format (e.g., "png", "jpeg", "webp", "svg")
- `**kwargs`: Additional format-specific parameters (e.g., quality for JPEG)

**Returns:**
- Binary data of the converted image

**Raises:**
- `UnsupportedFormatError`: If the format conversion is not supported
- `FormatConversionError`: If the conversion fails

### Resize Image

```python
async def resize_image(
    self, image_data: bytes, width: int, height: int, preserve_aspect_ratio: bool = True
) -> bytes:
    """Resize an image to the specified dimensions."""
```

This method implements the interface method for image resizing.

**Parameters:**
- `image_data`: Binary image data to resize
- `width`: Target width in pixels
- `height`: Target height in pixels
- `preserve_aspect_ratio`: Whether to maintain the original aspect ratio

**Returns:**
- Binary data of the resized image

**Raises:**
- `ResizeError`: If the resize operation fails

### Optimize Image

```python
async def optimize_image(
    self, image_data: bytes, format: str, quality: int = 85
) -> bytes:
    """Optimize an image for web delivery."""
```

This method implements the interface method for image optimization.

**Parameters:**
- `image_data`: Binary image data to optimize
- `format`: Format of the image (e.g., "png", "jpeg", "webp")
- `quality`: Quality level for lossy formats (0-100)

**Returns:**
- Binary data of the optimized image

**Raises:**
- `OptimizationError`: If the optimization fails

### Create Thumbnail

```python
async def create_thumbnail(
    self, image_data: bytes, max_size: int = 300
) -> bytes:
    """Create a thumbnail version of an image."""
```

This method implements the interface method for thumbnail creation.

**Parameters:**
- `image_data`: Binary image data to process
- `max_size`: Maximum dimension (width or height) in pixels

**Returns:**
- Binary data of the thumbnail image

**Raises:**
- `ImageProcessingError`: If thumbnail creation fails

### Extract Dominant Colors

```python
async def extract_dominant_colors(
    self, image_data: bytes, num_colors: int = 5
) -> List[Dict[str, str]]:
    """Extract the dominant colors from an image."""
```

This method implements the interface method for color extraction.

**Parameters:**
- `image_data`: Binary image data to analyze
- `num_colors`: Number of dominant colors to extract

**Returns:**
- List of color dictionaries with hex, rgb, and hsl values

**Raises:**
- `ImageProcessingError`: If color extraction fails

## Additional Methods

### Apply Effects

```python
async def apply_effects(
    self, image_data: bytes, effects: List[Dict[str, Any]]
) -> bytes:
    """Apply a series of visual effects to an image."""
```

This method applies multiple visual effects to an image in sequence.

**Parameters:**
- `image_data`: Binary image data to process
- `effects`: List of effect configurations

**Returns:**
- Binary data of the processed image

**Raises:**
- `UnsupportedEffectError`: If an effect is not supported
- `ImageProcessingError`: If effect application fails

### Generate Image Preview

```python
async def generate_preview(
    self, image_data: bytes, preview_type: str, params: Dict[str, Any] = None
) -> bytes:
    """Generate a preview of an image for a specific context."""
```

This method creates specialized preview images for different contexts.

**Parameters:**
- `image_data`: Binary image data to process
- `preview_type`: Type of preview to generate (e.g., "web", "print", "social")
- `params`: Preview-specific parameters

**Returns:**
- Binary data of the preview image

**Raises:**
- `UnsupportedPreviewTypeError`: If the preview type is not supported
- `ImageProcessingError`: If preview generation fails

## Dependency Injection

The service is available through FastAPI's dependency injection system:

```python
def get_image_service(
    processing_service: ImageProcessingService = Depends(get_processing_service),
    cache_service: Optional[CacheServiceInterface] = Depends(get_optional_cache_service)
) -> ImageServiceInterface:
    """Dependency for getting an image service instance."""
    return ImageService(
        processing_service=processing_service,
        cache_service=cache_service
    )
```

## Resource Management

The service implements efficient resource management:

1. **Memory Usage**: Monitors and controls memory consumption
2. **Concurrency**: Controls the number of concurrent operations
3. **Cleanup**: Ensures temporary resources are properly released
4. **Caching**: Uses caching where appropriate to improve performance

## Error Handling

The service implements a comprehensive error handling strategy:

1. **Input Validation**: Validates parameters before processing
2. **Specific Exceptions**: Uses typed exceptions for different error scenarios
3. **Logging**: Records detailed logs for troubleshooting
4. **Graceful Degradation**: Falls back to simpler processing when needed

## Format Support

The service supports the following image formats:

| Format | Read Support | Write Support | Notes |
|--------|--------------|--------------|-------|
| PNG    | Full         | Full         | Supports transparency |
| JPEG   | Full         | Full         | Configurable quality |
| WebP   | Full         | Full         | Modern efficient format |
| SVG    | Limited      | Full         | Vector format |
| GIF    | Limited      | Limited      | Static images only |

## Usage Examples

### Basic Image Operations

```python
from app.services.image.service import ImageService

# Initialize the service
image_service = ImageService()

# Read an image file
with open("example.png", "rb") as f:
    image_data = f.read()

# Convert to JPEG
jpeg_data = await image_service.convert_format(
    image_data=image_data,
    source_format="png",
    target_format="jpeg",
    quality=85
)

# Create a thumbnail
thumbnail = await image_service.create_thumbnail(
    image_data=image_data,
    max_size=200
)

# Extract colors
colors = await image_service.extract_dominant_colors(
    image_data=image_data,
    num_colors=5
)

# Save the results
with open("converted.jpg", "wb") as f:
    f.write(jpeg_data)

with open("thumbnail.png", "wb") as f:
    f.write(thumbnail)

print("Dominant colors:")
for color in colors:
    print(f"- {color['hex']}")
```

### Applying Multiple Effects

```python
# Define effects to apply
effects = [
    {
        "type": "adjustment",
        "brightness": 1.1,
        "contrast": 1.2
    },
    {
        "type": "filter",
        "name": "sharpen",
        "amount": 0.5
    },
    {
        "type": "crop",
        "left": 10,
        "top": 10,
        "width": 500,
        "height": 500
    }
]

# Apply the effects
processed_image = await image_service.apply_effects(
    image_data=image_data,
    effects=effects
)

# Save the result
with open("processed.png", "wb") as f:
    f.write(processed_image)
```

## Related Documentation

- [Image Interface](interface.md): Interface implemented by this service
- [Image Processing](processing.md): Core image processing functions
- [Image Conversion](conversion.md): Image format conversion details
- [Processing Service](processing_service.md): Advanced processing service
- [Export Service](../export/service.md): Service that uses image service for exports 