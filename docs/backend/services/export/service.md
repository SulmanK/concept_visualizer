# Export Service

The `service.py` module provides an implementation of the export service for converting and exporting images in the Concept Visualizer API.

## Overview

The Export Service is responsible for:

1. Converting images between various formats (PNG, JPEG, SVG)
2. Resizing and optimizing images for different use cases
3. Creating vector versions of bitmap images
4. Processing color palettes for visual display
5. Generating thumbnails for efficient display

This service uses the PIL (Pillow) library for raster image processing and VTracer for vectorization.

## ExportService Class

```python
class ExportService:
    """Service for exporting images in different formats."""
    
    def __init__(
        self, 
        image_service: ImageServiceInterface = Depends(get_image_service),
        processing_service: ImageProcessingServiceInterface = Depends(get_image_processing_service),
    ):
        """Initialize export service with required dependencies."""
        self.image_service = image_service
        self.processing_service = processing_service
        self.logger = logging.getLogger("export_service")
```

## Key Operations

### Processing Exports

```python
async def process_export(
    self,
    image_data: bytes,
    original_filename: str,
    target_format: Literal["png", "jpg", "svg"],
    target_size: Literal["small", "medium", "large", "original"],
    svg_params: Optional[Dict] = None,
) -> Tuple[bytes, str, str]:
    """
    Process the image export request.
    
    Args:
        image_data: Binary image data to export
        original_filename: Original filename for generating export filename
        target_format: Target format for export (png, jpg, svg)
        target_size: Target size for export (small, medium, large, original)
        svg_params: Optional parameters for SVG conversion
        
    Returns:
        Tuple containing:
            - Processed image bytes
            - Filename for the exported file
            - Content type for the exported file
        
    Raises:
        ExportError: If the export processing fails
    """
    # Implementation...
```

This method is the main entry point for processing exports, handling:
- Format determination and conversion
- Size adjustments based on predefined presets
- SVG vectorization when requested
- Error handling and logging
- Filename and content type generation

### Raster Image Processing

```python
async def _process_raster_image(
    self,
    image_data: bytes,
    original_filename: str,
    target_format: Literal["png", "jpg"],
    target_size: Literal["small", "medium", "large", "original"],
) -> Tuple[bytes, str, str]:
    """
    Process a raster image (resize and convert format).
    
    Args:
        image_data: Original image bytes
        original_filename: Original filename
        target_format: Target format (png, jpg)
        target_size: Target size (small, medium, large, original)
        
    Returns:
        Tuple containing:
            - Processed image bytes
            - Filename for the exported file
            - Content type for the exported file
    """
    # Implementation...
```

This method handles:
- Size mapping for predefined dimensions ("small", "medium", "large")
- Format conversion for raster images
- Quality settings for different formats
- Resize operations with aspect ratio preservation

### SVG Conversion

```python
async def _convert_to_svg(
    self,
    image_data: bytes,
    original_filename: str,
    svg_params: Optional[Dict] = None,
) -> Tuple[bytes, str, str]:
    """
    Convert an image to SVG format.
    
    Args:
        image_data: Original image bytes
        original_filename: Original filename
        svg_params: Optional parameters for SVG conversion
        
    Returns:
        Tuple containing:
            - Processed SVG bytes
            - Filename for the exported SVG
            - Content type for the SVG file
    """
    # Implementation...
```

This method implements:
- Bitmap to vector conversion using VTracer
- Temporary file handling for processing
- SVG optimization and cleaning
- Fallback to simple SVG conversion if VTracer fails

### Simple SVG Creation

```python
def _create_simple_svg_from_image(self, image: Image.Image, output_path: str) -> None:
    """
    Create a simple SVG representation of an image.
    
    Args:
        image: PIL Image object
        output_path: Path to save the SVG file
    """
    # Implementation...
```

This fallback method:
- Creates a basic SVG representation when full vectorization fails
- Uses simple rectangles to represent the image
- Maintains proportions and visual structure
- Provides a valid SVG even for complex images

## Error Handling

The service defines a custom exception for export-related errors:

```python
class ExportError(Exception):
    """Exception raised for image export errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)
```

Throughout the service, errors are:
- Logged with appropriate detail
- Wrapped in domain-specific exceptions
- Masked to protect sensitive information (paths, IDs)
- Gracefully handled with sensible defaults

## Service Factory

A dependency injection factory is provided:

```python
async def get_export_service(
    image_service: ImageServiceInterface = Depends(get_image_service),
    processing_service: ImageProcessingServiceInterface = Depends(get_image_processing_service),
) -> ExportService:
    """
    Factory function for the ExportService.
    
    Args:
        image_service: Service for image operations
        processing_service: Service for image processing
        
    Returns:
        ExportService instance
    """
    return ExportService(
        image_service=image_service,
        processing_service=processing_service
    )
```

This function:
- Injects required dependencies
- Creates properly configured service instances
- Simplifies service instantiation in API routes

## Size Mapping

The service uses predefined size mappings:

```python
size_mapping = {
    "small": (500, 500),    # Max dimensions: 500x500
    "medium": (1000, 1000), # Max dimensions: 1000x1000
    "large": (2000, 2000),  # Max dimensions: 2000x2000
    "original": None        # No resizing
}
```

These sizes ensure:
- Consistent output dimensions
- Optimized file sizes for different use cases
- Preserved aspect ratios

## Usage Examples

### Exporting a Concept Image as SVG

```python
# Get the export service
export_service = get_export_service(
    image_service=image_service,
    processing_service=processing_service
)

# Process the export to SVG
processed_bytes, filename, content_type = await export_service.process_export(
    image_data=concept_image_data,
    original_filename="concept_123.png",
    target_format="svg",
    target_size="original"
)

# Result: SVG bytes, "concept_123.svg", "image/svg+xml"
```

### Exporting a Resized JPEG

```python
# Process the export to a medium-sized JPEG
processed_bytes, filename, content_type = await export_service.process_export(
    image_data=concept_image_data,
    original_filename="concept_123.png",
    target_format="jpg",
    target_size="medium"
)

# Result: JPEG bytes (max 1000x1000), "concept_123.jpg", "image/jpeg"
```

## Related Documentation

- [Export Interface](interface.md): Interface implemented by this service
- [Image Processing Service](../image/processing_service.md): Used for image manipulation
- [Image Service](../image/service.md): Used for image retrieval
- [Export API Routes](../../api/routes/export/export_routes.md): API endpoints that use this service 