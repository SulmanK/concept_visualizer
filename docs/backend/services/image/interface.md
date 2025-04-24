# Image Service Interface

The `interface.py` module defines the abstract interface for image services, establishing a consistent contract for all image-related operations in the application.

## Overview

The image service interface provides a standardized way to interact with image processing functionality, regardless of the underlying implementation. This enables dependency injection, easier testing, and the possibility of swapping implementations without affecting dependent code.

## Interface Definition

```python
class ImageServiceInterface(Protocol):
    """Interface for image processing services."""

    async def convert_format(
        self, image_data: bytes, source_format: str, target_format: str, **kwargs
    ) -> bytes:
        """Convert an image from one format to another."""
        ...

    async def resize_image(
        self, image_data: bytes, width: int, height: int, preserve_aspect_ratio: bool = True
    ) -> bytes:
        """Resize an image to the specified dimensions."""
        ...

    async def optimize_image(
        self, image_data: bytes, format: str, quality: int = 85
    ) -> bytes:
        """Optimize an image for web delivery."""
        ...

    async def create_thumbnail(
        self, image_data: bytes, max_size: int = 300
    ) -> bytes:
        """Create a thumbnail version of an image."""
        ...

    async def extract_dominant_colors(
        self, image_data: bytes, num_colors: int = 5
    ) -> List[Dict[str, str]]:
        """Extract the dominant colors from an image."""
        ...
```

## Key Methods

### Convert Format

```python
async def convert_format(
    self, image_data: bytes, source_format: str, target_format: str, **kwargs
) -> bytes:
    """Convert an image from one format to another."""
```

This method converts image data between different formats.

**Parameters:**

- `image_data`: Binary image data to convert
- `source_format`: Format of the input image (e.g., "png", "jpeg")
- `target_format`: Desired output format (e.g., "png", "jpeg", "webp", "svg")
- `**kwargs`: Additional format-specific parameters (e.g., quality for JPEG)

**Returns:**

- Binary data of the converted image

**Expected Behavior:**

- Should handle common formats (PNG, JPEG, WebP, SVG)
- Should preserve image quality as much as possible
- Should throw appropriate exceptions for unsupported conversions

### Resize Image

```python
async def resize_image(
    self, image_data: bytes, width: int, height: int, preserve_aspect_ratio: bool = True
) -> bytes:
    """Resize an image to the specified dimensions."""
```

This method resizes an image to the specified dimensions.

**Parameters:**

- `image_data`: Binary image data to resize
- `width`: Target width in pixels
- `height`: Target height in pixels
- `preserve_aspect_ratio`: Whether to maintain the original aspect ratio

**Returns:**

- Binary data of the resized image

**Expected Behavior:**

- Should handle various image formats
- Should respect aspect ratio when requested
- Should use high-quality resizing algorithms

### Optimize Image

```python
async def optimize_image(
    self, image_data: bytes, format: str, quality: int = 85
) -> bytes:
    """Optimize an image for web delivery."""
```

This method optimizes an image for web delivery by reducing file size while maintaining acceptable quality.

**Parameters:**

- `image_data`: Binary image data to optimize
- `format`: Format of the image (e.g., "png", "jpeg", "webp")
- `quality`: Quality level for lossy formats (0-100)

**Returns:**

- Binary data of the optimized image

**Expected Behavior:**

- Should reduce file size through appropriate compression
- Should balance quality and size based on the quality parameter
- Should apply format-specific optimizations

### Create Thumbnail

```python
async def create_thumbnail(
    self, image_data: bytes, max_size: int = 300
) -> bytes:
    """Create a thumbnail version of an image."""
```

This method creates a smaller thumbnail version of an image.

**Parameters:**

- `image_data`: Binary image data to process
- `max_size`: Maximum dimension (width or height) in pixels

**Returns:**

- Binary data of the thumbnail image

**Expected Behavior:**

- Should maintain aspect ratio
- Should optimize the result for web display
- Should handle various input formats

### Extract Dominant Colors

```python
async def extract_dominant_colors(
    self, image_data: bytes, num_colors: int = 5
) -> List[Dict[str, str]]:
    """Extract the dominant colors from an image."""
```

This method analyzes an image and extracts its dominant colors.

**Parameters:**

- `image_data`: Binary image data to analyze
- `num_colors`: Number of dominant colors to extract

**Returns:**

- List of color dictionaries with hex, rgb, and hsl values

**Expected Behavior:**

- Should identify visually significant colors
- Should return colors in multiple formats (hex, RGB, HSL)
- Should handle various input image formats

## Error Handling

Implementations of the image service interface should use the following exception types:

- `ImageProcessingError`: Base exception for all image processing errors
  - `FormatConversionError`: For errors during format conversion
  - `ResizeError`: For errors during image resizing
  - `OptimizationError`: For errors during image optimization
  - `UnsupportedFormatError`: For unsupported image formats

## Dependency Injection

The interface supports dependency injection through FastAPI's dependency system:

```python
def get_image_service() -> ImageServiceInterface:
    """Dependency for getting an image service instance."""
    return ImageService()
```

## Implementation Requirements

Implementations of this interface should:

1. Be thread-safe for concurrent operations
2. Use asynchronous I/O for potentially blocking operations
3. Include appropriate logging for debugging
4. Handle errors gracefully with appropriate exceptions
5. Clean up temporary resources properly

## Usage Example

Code that depends on image processing should use the interface rather than concrete implementations:

```python
async def process_user_image(
    uploaded_file: bytes,
    target_format: str,
    image_service: ImageServiceInterface = Depends(get_image_service)
):
    """Process a user-uploaded image."""
    # Detect source format
    source_format = detect_image_format(uploaded_file)

    # Convert to desired format
    converted_image = await image_service.convert_format(
        image_data=uploaded_file,
        source_format=source_format,
        target_format=target_format,
        quality=85
    )

    # Create a thumbnail
    thumbnail = await image_service.create_thumbnail(
        image_data=converted_image,
        max_size=200
    )

    # Return both processed versions
    return {
        "image": base64.b64encode(converted_image).decode("utf-8"),
        "thumbnail": base64.b64encode(thumbnail).decode("utf-8"),
        "format": target_format
    }
```

## Related Documentation

- [Image Service](service.md): Main implementation of this interface
- [Image Conversion](conversion.md): Details on format conversion
- [Image Processing](processing.md): Details on image manipulation
- [Processing Service](processing_service.md): Specialized processing service
- [Export Service](../export/service.md): Service that uses image processing for exports
