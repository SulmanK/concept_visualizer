# Export Service Interface

The `interface.py` module defines the interface for services that handle exporting concepts and images in the Concept Visualizer API.

## Overview

The Export Service Interface defines a contract for:

1. Exporting images in various formats (PNG, JPEG, SVG, etc.)
2. Converting color palettes to visual representations
3. Creating concept packages with multiple export formats
4. Generating thumbnails for optimized display

This interface ensures that export functionality is consistently implemented and can be easily mocked for testing.

## ExportServiceInterface

```python
class ExportServiceInterface(abc.ABC):
    """Interface for export services."""
    
    @abc.abstractmethod
    async def export_image(
        self,
        image_path: str,
        format: str,
        size: Optional[Dict[str, int]] = None,
        quality: Optional[int] = None,
        user_id: Optional[str] = None,
        include_original: bool = False,
        color_mode: str = "color"
    ) -> Dict[str, Any]:
        """Export an image with specified format and parameters."""
        pass
    
    # Other abstract methods...
```

## Key Operations

### Image Export

```python
@abc.abstractmethod
async def export_image(
    self,
    image_path: str,
    format: str,
    size: Optional[Dict[str, int]] = None,
    quality: Optional[int] = None,
    user_id: Optional[str] = None,
    include_original: bool = False,
    color_mode: str = "color"
) -> Dict[str, Any]:
    """
    Export an image with specified format and parameters.
    
    Args:
        image_path: Path or URL of the image to export
        format: Target format (PNG, JPEG, SVG, etc.)
        size: Optional dictionary with width and/or height
        quality: Quality for lossy formats (0-100)
        user_id: Optional user ID for tracking exports
        include_original: Whether to include the original image
        color_mode: Color mode of the export (color, grayscale, etc.)
        
    Returns:
        Dictionary containing the exported image data and metadata
        
    Raises:
        ExportError: If export fails
        ResourceNotFoundError: If the image is not found
    """
    pass
```

This method defines the contract for exporting an image with various options for format, size, and quality.

### Palette Export

```python
@abc.abstractmethod
async def export_palette(
    self, 
    palette_data: List[str],
    format: str = "png",
    size: Optional[Dict[str, int]] = None
) -> bytes:
    """
    Export a color palette as an image.
    
    Args:
        palette_data: List of color values (hex codes)
        format: Target format for the palette image
        size: Optional dictionary with width and/or height
        
    Returns:
        Binary data of the exported palette image
        
    Raises:
        ExportError: If export fails
    """
    pass
```

This method defines how to convert a list of color values into a visual palette image.

### Concept Package Export

```python
@abc.abstractmethod
async def export_concept_package(
    self,
    concept_id: str,
    user_id: str,
    formats: List[str],
    include_palettes: bool = True
) -> Dict[str, Any]:
    """
    Export a complete concept package with multiple formats.
    
    Args:
        concept_id: ID of the concept to export
        user_id: User ID owning the concept
        formats: List of formats to include
        include_palettes: Whether to include palette images
        
    Returns:
        Dictionary with paths to exported files
        
    Raises:
        ExportError: If export fails
        ResourceNotFoundError: If the concept is not found
    """
    pass
```

This comprehensive method defines how to export a complete concept including main image and palettes in multiple formats.

### Thumbnail Generation

```python
@abc.abstractmethod
async def generate_thumbnail(
    self,
    image_data: Union[bytes, str, BinaryIO],
    width: int,
    height: int,
    format: str = "png"
) -> bytes:
    """
    Generate a thumbnail of an image.
    
    Args:
        image_data: Image data or path or file-like object
        width: Thumbnail width
        height: Thumbnail height
        format: Output format
        
    Returns:
        Thumbnail image data
        
    Raises:
        ExportError: If thumbnail generation fails
    """
    pass
```

This method defines how to create efficiently sized thumbnails for various use cases.

## Expected Return Structures

### Export Image Response

```python
{
    "data": bytes,  # Binary image data
    "filename": "exported_image.png",
    "content_type": "image/png",
    "size": {
        "width": 512,
        "height": 512
    },
    "format": "png",
    "original_included": False
}
```

### Concept Package Response

```python
{
    "concept_id": "concept-123",
    "exports": {
        "png": "/path/to/exported/image.png",
        "svg": "/path/to/exported/image.svg",
        "jpg": "/path/to/exported/image.jpg"
    },
    "palettes": [
        {
            "name": "Ocean Breeze",
            "exports": {
                "png": "/path/to/exported/palette_ocean_breeze.png"
            }
        },
        # Additional palettes...
    ],
    "download_url": "https://example.com/download/package.zip"
}
```

## Error Handling

Implementations should raise appropriate exceptions:

```python
# For export processing issues
raise ExportError("Failed to convert image to SVG format")

# For resources not found
raise ResourceNotFoundError("Image not found")
```

## Usage in Dependency Injection

This interface is typically used with FastAPI's dependency injection:

```python
# In an API endpoint
@router.post("/export/image", response_model=ExportResponse)
async def export_image(
    request: ExportRequest,
    export_service: ExportServiceInterface = Depends(get_export_service)
):
    # Use the service through its interface
    result = await export_service.export_image(
        image_path=request.image_path,
        format=request.format,
        size=request.size,
        quality=request.quality
    )
    
    # Return the result
    return result
```

## Related Documentation

- [Export Service](service.md): Implementation of this interface
- [Image Processing](../image/processing.md): Used for image manipulation
- [Export API Routes](../../api/routes/export/export_routes.md): API endpoints that use this service 