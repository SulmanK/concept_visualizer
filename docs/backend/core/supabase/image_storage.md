# Image Storage

The `image_storage.py` module provides specialized functionality for handling image files in Supabase Storage for the Concept Visualizer API.

## Overview

This module is responsible for:

1. Uploading and downloading images to/from Supabase Storage
2. Managing image access with signed URLs
3. Enforcing user-specific access patterns through path structure
4. Handling various image formats and transformations
5. Supporting both direct uploads and URL-based transfers

## ImageStorage Class

The primary class for managing image data:

```python
class ImageStorage:
    """Handles image storage operations in Supabase Storage."""

    def __init__(self, client: Client):
        """
        Initialize the image storage with a Supabase client.

        Args:
            client: Supabase client instance
        """
        # Implementation...
```

## Key Operations

### Uploading Images

```python
def upload_image(
    self,
    image_data: Union[bytes, BytesIO, UploadFile],
    path: str,
    content_type: str = "image/png",
    user_id: Optional[str] = None,
    is_palette: bool = False,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Upload an image to Supabase Storage.

    Args:
        image_data: Image data as bytes, BytesIO, or UploadFile
        path: Storage path (should include user_id as first segment)
        content_type: Content type of the image
        user_id: User ID for access control
        is_palette: Whether this is a palette image (uses different bucket)
        metadata: Optional metadata to store with the image

    Returns:
        Storage path of the uploaded image

    Raises:
        ImageStorageError: If upload fails
    """
    # Implementation...
```

The method supports various input formats and ensures proper authentication with JWT tokens.

### Downloading Images

```python
def download_image(self, path: str, bucket_name: str) -> bytes:
    """
    Download an image from Supabase Storage.

    Args:
        path: Path to the image in storage
        bucket_name: Name of the bucket

    Returns:
        Image data as bytes

    Raises:
        ImageNotFoundError: If image is not found
        ImageStorageError: If download fails
    """
    # Implementation...
```

### Creating Signed URLs

```python
def create_signed_url(
    self,
    path: str,
    bucket_name: str,
    expires_in: int = 259200  # 3 days
) -> str:
    """
    Create a signed URL for accessing an image.

    Args:
        path: Path to the image in storage
        bucket_name: Name of the bucket
        expires_in: Expiration time in seconds

    Returns:
        Signed URL with temporary access

    Raises:
        ImageStorageError: If URL creation fails
    """
    # Implementation...
```

This method generates time-limited access URLs with proper JWT authentication.

### Removing Images

```python
def remove_image(self, path: str, bucket_name: str) -> bool:
    """
    Remove an image from storage.

    Args:
        path: Path to the image in storage
        bucket_name: Name of the bucket

    Returns:
        True if successful, False otherwise

    Raises:
        ImageStorageError: If removal fails
    """
    # Implementation...
```

### Bucket Management

```python
def delete_all_storage_objects(
    self,
    bucket_name: str,
    user_id: Optional[str] = None
) -> bool:
    """
    Delete all storage objects for a user or all objects in a bucket.

    WARNING: This is destructive and will delete all files permanently.

    Args:
        bucket_name: Name of the bucket
        user_id: Optional user ID to limit deletion to user's files

    Returns:
        True if successful, False otherwise
    """
    # Implementation...
```

This administrative method allows for bulk deletion with proper safeguards.

### Image Variations

```python
def apply_color_palette(
    self,
    image_path: str,
    palette_colors: List[str],
    output_path: Optional[str] = None,
    bucket_name: str = "concept-images"
) -> Tuple[str, str]:
    """
    Apply a color palette to an image.

    Args:
        image_path: Path to the source image
        palette_colors: List of hex color codes
        output_path: Optional custom output path
        bucket_name: Name of the source bucket

    Returns:
        Tuple of (storage_path, signed_url)

    Raises:
        ImageStorageError: If palette application fails
    """
    # Implementation...
```

This method creates color variations of images using provided palettes.

### URL-Based Operations

```python
def upload_image_from_url(
    self,
    url: str,
    path: str,
    bucket_name: str,
    user_id: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Upload an image from a URL to storage.

    Args:
        url: URL of the image to download
        path: Destination path in storage
        bucket_name: Name of the bucket
        user_id: Optional user ID for access control
        metadata: Optional metadata to store with the image

    Returns:
        Storage path of the uploaded image

    Raises:
        ImageStorageError: If upload fails
    """
    # Implementation...
```

This method allows fetching and storing images from external URLs.

## Authentication and Security

The module implements several security features:

1. **Path-Based Access Control**: User IDs are embedded in paths for Row Level Security (RLS)
2. **JWT Authentication**: All storage operations use JWT tokens with proper claims
3. **Signed URLs**: Time-limited access to images with proper authentication
4. **Metadata Validation**: Ensures metadata includes required user identification

Example of path structure for security:

```
user-123/concept-456/image.png
```

This structure enables Supabase RLS policies to restrict access based on the user ID in the path.

## Error Handling

The module includes comprehensive error handling:

- Specific exceptions for common errors like `ImageNotFoundError`
- Detailed error messages with context
- Connection retries for transient issues
- Fallbacks for certain operations

## Usage Examples

### Storing a User Image

```python
from app.core.supabase import get_supabase_client, ImageStorage
from io import BytesIO
from PIL import Image

# Create a client and storage instance
client = get_supabase_client(session_id="user-session-123")
storage = ImageStorage(client)

# Create a test image
img = Image.new('RGB', (100, 100), color='red')
buffer = BytesIO()
img.save(buffer, format='PNG')
image_data = buffer.getvalue()

# Upload the image
user_id = "user-123"
path = f"{user_id}/test-image.png"

try:
    uploaded_path = storage.upload_image(
        image_data=image_data,
        path=path,
        content_type="image/png",
        user_id=user_id
    )

    # Get a signed URL
    signed_url = storage.create_signed_url(
        path=uploaded_path,
        bucket_name="concept-images"
    )

    print(f"Image available at: {signed_url}")

except Exception as e:
    print(f"Error: {str(e)}")
```

### Applying a Color Palette

```python
# Apply a color palette to an existing image
palette_colors = ["#FF5733", "#33FF57", "#3357FF"]
source_path = f"{user_id}/original-image.png"

try:
    new_path, new_url = storage.apply_color_palette(
        image_path=source_path,
        palette_colors=palette_colors,
        bucket_name="concept-images"
    )

    print(f"Palette variation available at: {new_url}")

except Exception as e:
    print(f"Error: {str(e)}")
```

## Implementation Details

### Direct HTTP Requests

For better control over authentication and content types, some operations use direct HTTP requests instead of the Supabase client library:

```python
# Example of direct upload implementation (simplified)
def _direct_upload(self, path: str, content: bytes, content_type: str, bucket: str):
    token = create_supabase_jwt_for_storage(path)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": content_type,
    }
    url = f"{self.storage_url}/object/{bucket}/{path}"
    response = requests.post(url, headers=headers, data=content)
    # Process response...
```

### JWT Token Creation

The module relies on specialized JWT tokens for storage operations:

```python
# Creating a storage-specific JWT token (implementation in jwt_utils.py)
token = create_supabase_jwt_for_storage(
    path=path,
    expiry=3600  # 1 hour
)
```

## Related Documentation

- [Client](client.md): Base Supabase client used by image storage
- [Concept Storage](concept_storage.md): Storage for concept data that references images
- [Image Persistence Service](../../services/persistence/image_persistence_service.md): Higher-level service that uses this storage
- [JWT Utils](../../utils/jwt_utils.md): JWT token utilities used for authentication
