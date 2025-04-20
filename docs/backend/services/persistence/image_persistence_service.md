# Image Persistence Service

The `image_persistence_service.py` module provides a high-level service for storing and retrieving images in the Concept Visualizer API.

## Overview

This service acts as an abstraction layer over the Supabase Storage backend, providing:

1. Simplified image storage and retrieval operations
2. Consistent error handling for image operations
3. Support for various image formats and transformations
4. Security controls for image access
5. Metadata management for images

## ImagePersistenceService Class

The primary class for image persistence operations:

```python
class ImagePersistenceService:
    """Service for storing and retrieving images from Supabase storage."""

    def __init__(self, client: Client):
        """
        Initialize the image persistence service.
        
        Args:
            client: Supabase client instance
        """
        self.supabase = client
        self.concept_bucket = settings.STORAGE_BUCKET_CONCEPT
        self.palette_bucket = settings.STORAGE_BUCKET_PALETTE
        self.logger = logging.getLogger(__name__)
        self.storage = ImageStorage(client)
```

## Key Operations

### Storing Images

```python
def store_image(
    self, 
    image_data: Union[bytes, BytesIO, UploadFile], 
    user_id: str,
    concept_id: Optional[str] = None,
    file_name: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    is_palette: bool = False
) -> Tuple[str, str]:
    """
    Store an image in the storage bucket with user ID metadata.
    
    Args:
        image_data: Image data as bytes, BytesIO or UploadFile
        user_id: User ID for access control
        concept_id: Optional concept ID to associate with the image
        file_name: Optional file name (generated if not provided)
        metadata: Optional metadata to store with the image
        is_palette: Whether the image is a palette (uses palette-images bucket)
        
    Returns:
        Tuple[str, str]: (image_path, image_url)
        
    Raises:
        ImageStorageError: If image storage fails
    """
    # Implementation...
```

This comprehensive method handles:
- Different input formats (bytes, BytesIO, UploadFile)
- Automatic format detection
- Filename generation
- Path construction with security considerations
- Content type selection
- Metadata preparation
- Logging with PII masking

### Retrieving Images

```python
def get_image(self, image_path: str, is_palette: bool = False) -> bytes:
    """
    Retrieve an image from storage.
    
    Args:
        image_path: Path of the image in storage
        is_palette: Whether the image is a palette (uses palette-images bucket)
        
    Returns:
        Image data as bytes
        
    Raises:
        ImageNotFoundError: If image is not found
        ImageStorageError: If image retrieval fails
    """
    # Implementation...
```

```python
async def get_image_async(self, image_path_or_url: str, is_palette: bool = False) -> bytes:
    """
    Asynchronously retrieve an image from storage or URL.
    
    Args:
        image_path_or_url: Path or URL of the image
        is_palette: Whether the image is a palette (uses palette-images bucket)
        
    Returns:
        Image data as bytes
        
    Raises:
        ImageNotFoundError: If image is not found
        ImageStorageError: If image retrieval fails
    """
    # Implementation...
```

The service provides both synchronous and asynchronous retrieval options.

### URL Generation

```python
def get_signed_url(self, path: str, is_palette: bool = False, expiry_seconds: int = 259200) -> str:
    """
    Get a signed URL for an image.
    
    Args:
        path: Path of the image in storage
        is_palette: Whether the image is a palette (uses palette-images bucket)
        expiry_seconds: Expiry time in seconds (default: 3 days)
        
    Returns:
        Signed URL for the image
        
    Raises:
        ImageStorageError: If URL signing fails
    """
    # Implementation...
```

```python
def get_image_url(self, image_path: str, is_palette: bool = False) -> str:
    """
    Get a signed URL for an image in storage.
    
    Args:
        image_path: Path to the image in storage
        is_palette: Whether this is a palette image
        
    Returns:
        Signed URL for the image
    """
    # Implementation...
```

### Image Management

```python
def delete_image(self, image_path: str, is_palette: bool = False) -> bool:
    """
    Delete an image from storage.
    
    Args:
        image_path: Path of the image in storage
        is_palette: Whether the image is a palette (uses palette-images bucket)
        
    Returns:
        True if deletion was successful
        
    Raises:
        ImageStorageError: If image deletion fails
    """
    # Implementation...
```

```python
def list_images(self, concept_id: Optional[str] = None, is_palette: bool = False) -> List[Dict[str, Any]]:
    """
    List images in storage.
    
    Args:
        concept_id: Optional concept ID to filter by
        is_palette: Whether to list palette images
        
    Returns:
        List of image metadata objects
    """
    # Implementation...
```

### Authenticated Access

```python
async def authenticate_url(self, path: str, user_id: str, is_palette: bool = False) -> str:
    """
    Create an authenticated URL for an image.
    
    Args:
        path: Path to the image in storage
        user_id: User ID for access control
        is_palette: Whether this is a palette image
        
    Returns:
        Authenticated URL for the image
    """
    # Implementation...
```

```python
def get_image_with_token(self, path: str, token: str, is_palette: bool = False) -> bytes:
    """
    Get an image using a token for authentication.
    
    Args:
        path: Path to the image in storage
        token: Authentication token
        is_palette: Whether this is a palette image
        
    Returns:
        Image data as bytes
        
    Raises:
        ImageNotFoundError: If image is not found
        ImageStorageError: If image retrieval fails
        AuthenticationError: If token is invalid
    """
    # Implementation...
```

## Usage Examples

### Storing an Image

```python
from app.services.persistence import ImagePersistenceService
from app.core.supabase import get_supabase_client
from io import BytesIO
from PIL import Image

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
buffer = BytesIO()
img.save(buffer, format='PNG')
image_data = buffer.getvalue()

# Initialize service
client = get_supabase_client()
service = ImagePersistenceService(client)

# Store the image
try:
    path, url = service.store_image(
        image_data=image_data,
        user_id="user-123",
        concept_id="concept-456",
        metadata={"description": "Test image"}
    )
    
    print(f"Image stored at {path}")
    print(f"Access URL: {url}")
    
except Exception as e:
    print(f"Error storing image: {str(e)}")
```

### Retrieving an Image

```python
# Retrieve the image
try:
    image_data = service.get_image(path)
    
    # Use the image data
    from PIL import Image
    from io import BytesIO
    
    img = Image.open(BytesIO(image_data))
    img.show()
    
except Exception as e:
    print(f"Error retrieving image: {str(e)}")
```

### Listing User Images

```python
# List all images for a concept
try:
    images = service.list_images(concept_id="concept-456")
    
    for image in images:
        print(f"Image path: {image['name']}")
        print(f"Created: {image['created_at']}")
        print(f"Size: {image['metadata'].get('size', 'Unknown')}")
        
except Exception as e:
    print(f"Error listing images: {str(e)}")
```

## Error Handling

The service includes comprehensive error handling:

1. **Specific Exceptions**: Uses custom exceptions like `ImageNotFoundError` and `ImageStorageError`
2. **Detailed Logging**: Logs operations with appropriate masking of sensitive information
3. **Graceful Degradation**: Falls back to alternative methods when possible
4. **Consistent Patterns**: Provides consistent error handling across all methods

Example error handling pattern:

```python
try:
    # Attempt operation
    result = self.storage.some_operation(...)
    return result
except Exception as e:
    error_msg = f"Failed to perform operation: {str(e)}"
    self.logger.error(error_msg)
    
    if "404" in str(e) or "not found" in str(e).lower():
        raise ImageNotFoundError(f"Image not found: {image_path}")
        
    raise ImageStorageError(error_msg)
```

## Security Considerations

The service implements several security features:

1. **Path-Based Control**: Embeds user IDs in paths to enable Row Level Security
2. **Metadata Tagging**: Adds owner user ID to metadata
3. **PII Masking**: Masks sensitive data like user IDs in logs
4. **Time-Limited URLs**: Uses signed URLs with expiration times
5. **Access Validation**: Validates access rights before operations

## Implementation Details

### Image Format Handling

The service automatically detects and handles various image formats:

```python
# Try to determine file format from content
try:
    img = Image.open(BytesIO(content))
    if img.format:
        ext = img.format.lower()
except Exception as e:
    self.logger.warning(f"Could not determine image format: {str(e)}")
```

### URL Types

The service supports different URL types:

1. **Signed URLs**: Time-limited URLs with authentication
2. **Public URLs**: Long-lived URLs for public access
3. **Direct URLs**: For internal system use

### Async Support

Many methods have both synchronous and asynchronous versions:

```python
# Synchronous
image_data = service.get_image(path)

# Asynchronous
image_data = await service.get_image_async(path)
```

## Related Documentation

- [Image Storage](../../../core/supabase/image_storage.md): Low-level storage operations
- [Supabase Client](../../../core/supabase/client.md): Base client for Supabase
- [Image Service](../../image/service.md): Image processing service
- [Concept Persistence Service](concept_persistence_service.md): Persistence for concept data 