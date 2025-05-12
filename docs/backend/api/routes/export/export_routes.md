# Export Routes

The `export_routes.py` module provides API endpoints for exporting generated images in different formats and sizes.

## Overview

The export routes enable users to:

1. Convert images between different formats (PNG, JPEG, SVG, etc.)
2. Resize images to specific dimensions
3. Download processed images for use in other applications

These endpoints are essential for providing flexibility in how users can utilize the generated visual concepts outside of the application.

## Router Configuration

```python
router = APIRouter()
```

The router is created without a specific prefix, as that's handled by the parent router.

## Endpoints

### Process Export

```python
@router.post("/process")
async def export_action(
    request_data: ExportRequest,
    req: Request,
    current_user: Dict = Depends(get_current_user),
    export_service = Depends(get_export_service),
    image_persistence_service: ImagePersistenceServiceInterface = Depends(get_image_persistence_service),
) -> StreamingResponse:
    """Process an export request and return the file."""
```

This endpoint handles processing an export request, converting the image to the requested format and size, and returning it as a downloadable file.

**Authentication:** Requires a valid user ID from the authenticated request

**Request Body:**

- `image_identifier`: Path to the image to export
- `storage_bucket`: Storage bucket where the image is stored (e.g., "concept-images", "palette-images")
- `target_format`: Desired output format (e.g., "png", "jpg", "svg")
- `target_size`: Optional desired dimensions (width, height) or preset size ("small", "medium", "large", "original")
- `svg_params`: Optional parameters for SVG export

**Response:**

- A `StreamingResponse` containing the processed file with appropriate headers for download
- Content-Type header set according to the target format (e.g., "image/png")
- Content-Disposition header with appropriate filename for attachment download

## Processing Flow

The export process follows these steps:

1. Authenticate the user and verify they have access to the requested image
2. Fetch the original image data from the storage service
3. Process the image according to the requested parameters:
   - Convert to the target format
   - Resize to the target dimensions
   - Apply any format-specific processing (e.g., SVG tracing options)
4. Return the processed image as a downloadable file

## Security Considerations

The export routes implement several security measures:

1. **Authentication Check**: All export operations require authentication
2. **Resource Ownership**: Users can only export images they own
3. **Path Masking**: Image paths are masked in logs to prevent information leakage
4. **Input Validation**: Request parameters are validated to prevent invalid operations

## Error Handling

The endpoints implement a consistent error handling approach:

1. **Authentication Errors**: Returns 401 Unauthorized if no valid user ID is found
2. **Permission Errors**: Returns 403 Forbidden if the user doesn't own the requested image
3. **Resource Not Found**: Returns 404 Not Found if the requested image doesn't exist
4. **Processing Errors**: Returns 500 Internal Server Error if export processing fails
5. **Detailed Logging**: All errors are logged with appropriate severity and masked identifiers

## Usage Example

```http
POST /api/v1/export/process
Content-Type: application/json
Authorization: Bearer {token}

{
  "image_identifier": "user123/concepts/logo_abc123.png",
  "storage_bucket": "concept-images",
  "target_format": "svg",
  "target_size": "large",
  "svg_params": {
    "color_mode": "color",
    "path_precision": 1
  }
}
```

## Supported Export Formats

The export service supports conversion between the following formats:

| Source Format | Target Formats  |
| ------------- | --------------- |
| PNG           | JPEG, WebP, SVG |
| JPEG          | PNG, WebP, SVG  |
| WebP          | PNG, JPEG, SVG  |
| SVG           | PNG, JPEG, WebP |

## Integration with Services

The export routes integrate with several services:

1. **ExportService**: For handling the actual export processing
2. **ImagePersistenceService**: For retrieving the original image data

## Performance Considerations

The export system is designed with performance in mind:

1. **Streaming Response**: Uses FastAPI's StreamingResponse to efficiently handle large files
2. **Async Processing**: All operations are implemented asynchronously
3. **Memory Management**: Images are processed in a streaming fashion where possible

## Related Documentation

- [Export Models](../../../models/export/request.md): Data models for export requests
- [Export Service](../../../services/export/service.md): Service for handling exports
- [Image Service](../../../services/image/service.md): Service for image processing
- [Image Conversion](../../../services/image/conversion.md): Details on image format conversion
