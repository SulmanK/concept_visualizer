# Image Conversion Service

The `conversion.py` module provides functionality for converting images between different formats and optimizing them for various use cases.

## Overview

The image conversion module offers specialized services for:

1. Converting images between different formats (PNG, JPEG, WebP, SVG)
2. Optimizing images for web delivery
3. Vectorizing raster images into SVG format
4. Preserving image quality during format transitions

This module is a critical component of the application's image processing pipeline, enabling flexible export options and efficient storage strategies.

## Key Functions

### Convert Image Format

```python
async def convert_image_format(
    image_data: bytes,
    source_format: str,
    target_format: str,
    quality: int = 90
) -> bytes:
    """Convert an image from one format to another."""
```

This function converts image data from one format to another while maintaining quality.

**Parameters:**

- `image_data`: Binary image data to convert
- `source_format`: Original image format (e.g., "png", "jpeg", "webp")
- `target_format`: Desired output format (e.g., "png", "jpeg", "webp", "svg")
- `quality`: Quality level for lossy formats (0-100, default: 90)

**Returns:**

- Binary data of the converted image

**Raises:**

- `UnsupportedFormatError`: If the source or target format is not supported
- `ImageConversionError`: If the conversion fails

### Raster to SVG Conversion

```python
async def convert_to_svg(
    image_data: bytes,
    mode: str = "color",
    path_precision: int = 2,
    simplify_paths: bool = True
) -> bytes:
    """Convert a raster image to SVG format."""
```

This function transforms raster images (PNG, JPEG, WebP) into scalable vector graphics.

**Parameters:**

- `image_data`: Binary image data to convert
- `mode`: SVG color mode ("color", "grayscale", or "lineart")
- `path_precision`: Decimal places for path coordinates (1-3)
- `simplify_paths`: Whether to simplify paths for smaller file size

**Returns:**

- Binary data of the SVG image

**Raises:**

- `ImageConversionError`: If the conversion fails
- `InvalidParameterError`: If parameters are invalid

### Optimize Image

```python
async def optimize_image(
    image_data: bytes,
    format: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    quality: int = 85
) -> bytes:
    """Optimize an image for web delivery."""
```

This function optimizes images for efficient delivery by resizing and compressing them.

**Parameters:**

- `image_data`: Binary image data to optimize
- `format`: Image format (e.g., "png", "jpeg", "webp")
- `width`: Optional target width (maintains aspect ratio if only width is specified)
- `height`: Optional target height (maintains aspect ratio if only height is specified)
- `quality`: Compression quality for lossy formats (0-100)

**Returns:**

- Binary data of the optimized image

**Raises:**

- `ImageProcessingError`: If optimization fails

## Format Support

The conversion module supports the following formats:

| Format | Extensions  | Support Level                                  |
| ------ | ----------- | ---------------------------------------------- |
| PNG    | .png        | Full support for reading and writing           |
| JPEG   | .jpg, .jpeg | Full support for reading and writing           |
| WebP   | .webp       | Full support for reading and writing           |
| SVG    | .svg        | Support for writing (via tracing)              |
| GIF    | .gif        | Limited support (conversion to static formats) |

## Implementation Details

### Image Processing Libraries

The module uses several image processing libraries:

1. **Pillow**: For basic image manipulation and format conversion
2. **svgwrite**: For SVG generation
3. **potrace**: For bitmap to vector conversion
4. **OpenCV**: For advanced image processing

### Conversion Process

The image conversion process follows these steps:

1. **Image Decoding**: Binary data is decoded into an in-memory image
2. **Format Transformation**: The image is processed according to the target format
3. **Quality Adjustment**: Parameters are applied based on the target format
4. **Encoding**: The processed image is encoded into binary data

### Threading and Async

- Heavy image processing operations run in a thread pool to avoid blocking the event loop
- All public functions are asynchronous and return awaitable results

## Performance Considerations

- Large images are processed in chunks to minimize memory usage
- Vectorization operations can be CPU-intensive and may take longer
- Caching is employed for frequently accessed conversion results
- File size optimization is balanced with quality preservation

## Usage Examples

### Converting PNG to JPEG

```python
from app.services.image.conversion import convert_image_format

# Read the original image
with open("image.png", "rb") as f:
    image_data = f.read()

# Convert to JPEG
jpeg_data = await convert_image_format(
    image_data=image_data,
    source_format="png",
    target_format="jpeg",
    quality=85
)

# Save the converted image
with open("image.jpg", "wb") as f:
    f.write(jpeg_data)
```

### Creating an SVG from a Raster Image

```python
from app.services.image.conversion import convert_to_svg

# Read the original image
with open("logo.png", "rb") as f:
    image_data = f.read()

# Convert to SVG
svg_data = await convert_to_svg(
    image_data=image_data,
    mode="color",
    path_precision=2
)

# Save the SVG
with open("logo.svg", "wb") as f:
    f.write(svg_data)
```

## Error Handling

The conversion module implements comprehensive error handling:

1. **Format Validation**: Checks if formats are supported before processing
2. **Parameter Validation**: Validates parameters before starting conversion
3. **Processing Errors**: Captures and wraps library-specific errors
4. **Resource Management**: Ensures resources are properly cleaned up

## Related Documentation

- [Image Service](service.md): Main image service that uses the conversion module
- [Image Processing](processing.md): Image processing techniques used in conversion
- [Processing Service](processing_service.md): Service that orchestrates image processing
- [Image Interface](interface.md): Interface for image services
- [Export Service](../export/service.md): Service that uses image conversion for exports
