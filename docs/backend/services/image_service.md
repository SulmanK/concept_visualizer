# Image Service

The `ImageService` is responsible for generating, processing, manipulating, and storing visual assets within the application.

## Overview

The Image Service provides a high-level API for:

1. Generating images using AI models
2. Processing and transforming images
3. Managing image storage and retrieval
4. Creating and managing color palettes
5. Optimizing images for different use cases

## Key Components

### ImageService Class

```python
class ImageService:
    """Service for image generation and manipulation."""

    def __init__(
        self,
        image_persistence: ImagePersistenceService,
        ai_client: JigsawStackClient,
        storage_provider: StorageProvider,
        config: ImageServiceConfig
    ):
        """Initialize the ImageService with required dependencies."""
```

**Dependencies:**

- `image_persistence`: Service for persisting image data in the database
- `ai_client`: Client for interacting with AI image generation APIs
- `storage_provider`: Provider for storing image files
- `config`: Configuration parameters for the image service

### Image Generation

```python
async def generate_image(
    self,
    prompt: str,
    width: int = 512,
    height: int = 512,
    style: str = "default",
    model: str = "stable-diffusion-xl",
    negative_prompt: Optional[str] = None
) -> GeneratedImage:
    """Generate an image using AI based on the provided prompt."""
```

Generates an image using AI based on the provided prompt.

**Parameters:**

- `prompt`: Text description of the image to generate
- `width`: Width of the generated image
- `height`: Height of the generated image
- `style`: Style of the image (e.g., "default", "photorealistic", "abstract")
- `model`: AI model to use for generation
- `negative_prompt`: Text description of what to avoid in the image

**Returns:**

- `GeneratedImage`: The generated image with metadata

```python
async def generate_variations(
    self,
    base_image_id: str,
    num_variations: int = 3,
    variation_strength: float = 0.75
) -> List[GeneratedImage]:
    """Generate variations of an existing image."""
```

Generates variations of an existing image.

**Parameters:**

- `base_image_id`: ID of the base image
- `num_variations`: Number of variations to generate
- `variation_strength`: Strength of variation (0.0 to 1.0)

**Returns:**

- List of generated image variations

### Image Refinement

```python
async def refine_image(
    self,
    image_id: str,
    refinement_prompt: str,
    preserve_structure: bool = True,
    refinement_strength: float = 0.5
) -> GeneratedImage:
    """Refine an existing image based on a refinement prompt."""
```

Refines an existing image based on a refinement prompt.

**Parameters:**

- `image_id`: ID of the image to refine
- `refinement_prompt`: Text description of the refinements to make
- `preserve_structure`: Whether to preserve the overall structure of the image
- `refinement_strength`: Strength of the refinement (0.0 to 1.0)

**Returns:**

- `GeneratedImage`: The refined image with metadata

### Color Palette Management

```python
async def generate_color_palette(
    self,
    image_id: str,
    num_colors: int = 5,
    palette_type: str = "dominant"
) -> Palette:
    """Generate a color palette from an image."""
```

Generates a color palette from an image.

**Parameters:**

- `image_id`: ID of the image to extract colors from
- `num_colors`: Number of colors in the palette
- `palette_type`: Type of palette to generate (e.g., "dominant", "vibrant", "muted")

**Returns:**

- `Palette`: Color palette extracted from the image

```python
async def generate_multiple_palettes(
    self,
    image_id: str,
    palette_options: Dict[str, Any] = {}
) -> List[Palette]:
    """Generate multiple color palette options from an image."""
```

Generates multiple color palette options from an image.

**Parameters:**

- `image_id`: ID of the image to extract colors from
- `palette_options`: Options for palette generation

**Returns:**

- List of color palettes extracted from the image

```python
async def apply_palette_to_image(
    self,
    image_id: str,
    palette_id: str,
    strength: float = 1.0
) -> GeneratedImage:
    """Apply a color palette to an image."""
```

Applies a color palette to an image.

**Parameters:**

- `image_id`: ID of the image to modify
- `palette_id`: ID of the palette to apply
- `strength`: Strength of the application (0.0 to 1.0)

**Returns:**

- `GeneratedImage`: Image with the palette applied

### Image Processing

```python
async def resize_image(
    self,
    image_id: str,
    width: int,
    height: int,
    maintain_aspect_ratio: bool = True
) -> ProcessedImage:
    """Resize an image to the specified dimensions."""
```

Resizes an image to the specified dimensions.

**Parameters:**

- `image_id`: ID of the image to resize
- `width`: Target width
- `height`: Target height
- `maintain_aspect_ratio`: Whether to maintain the aspect ratio

**Returns:**

- `ProcessedImage`: Resized image with metadata

```python
async def crop_image(
    self,
    image_id: str,
    x: int,
    y: int,
    width: int,
    height: int
) -> ProcessedImage:
    """Crop an image to the specified region."""
```

Crops an image to the specified region.

**Parameters:**

- `image_id`: ID of the image to crop
- `x`: X-coordinate of the top-left corner
- `y`: Y-coordinate of the top-left corner
- `width`: Width of the crop region
- `height`: Height of the crop region

**Returns:**

- `ProcessedImage`: Cropped image with metadata

```python
async def apply_filter(
    self,
    image_id: str,
    filter_type: str,
    filter_params: Dict[str, Any] = {}
) -> ProcessedImage:
    """Apply a filter to an image."""
```

Applies a filter to an image.

**Parameters:**

- `image_id`: ID of the image to filter
- `filter_type`: Type of filter to apply
- `filter_params`: Parameters for the filter

**Returns:**

- `ProcessedImage`: Filtered image with metadata

### Image Storage and Retrieval

```python
async def upload_image(
    self,
    file_data: bytes,
    filename: str,
    content_type: str,
    metadata: Dict[str, Any] = {}
) -> UploadedImage:
    """Upload a user-provided image."""
```

Uploads a user-provided image.

**Parameters:**

- `file_data`: Binary data of the image
- `filename`: Name of the file
- `content_type`: MIME type of the image
- `metadata`: Additional metadata for the image

**Returns:**

- `UploadedImage`: Uploaded image with metadata

```python
async def get_image(
    self,
    image_id: str
) -> ImageAsset:
    """Get an image by ID."""
```

Retrieves an image by ID.

**Parameters:**

- `image_id`: ID of the image to retrieve

**Returns:**

- `ImageAsset`: Image with metadata

```python
async def get_image_url(
    self,
    image_id: str,
    expiration: int = 3600
) -> str:
    """Get a temporary URL for accessing an image."""
```

Gets a temporary URL for accessing an image.

**Parameters:**

- `image_id`: ID of the image
- `expiration`: Expiration time of the URL in seconds

**Returns:**

- Temporary URL for accessing the image

### Image Export and Format Conversion

```python
async def export_image(
    self,
    image_id: str,
    format: str = "png",
    quality: int = 90,
    include_metadata: bool = False
) -> bytes:
    """Export an image in the specified format."""
```

Exports an image in the specified format.

**Parameters:**

- `image_id`: ID of the image to export
- `format`: Format to export to (e.g., "png", "jpg", "webp")
- `quality`: Quality of the export (0 to 100)
- `include_metadata`: Whether to include metadata in the export

**Returns:**

- Binary data of the exported image

## Data Models

### ImageAsset

```python
class ImageAsset(BaseModel):
    """Represents an image asset in the system."""

    image_id: str
    filename: str
    content_type: str
    width: int
    height: int
    file_size: int
    storage_path: str
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}
```

Represents an image asset in the system.

### GeneratedImage

```python
class GeneratedImage(ImageAsset):
    """Represents an AI-generated image."""

    prompt: str
    model: str
    generation_params: Dict[str, Any] = {}
    negative_prompt: Optional[str] = None
    guidance_scale: Optional[float] = None
    generation_steps: Optional[int] = None
```

Represents an AI-generated image.

### ProcessedImage

```python
class ProcessedImage(ImageAsset):
    """Represents a processed image."""

    source_image_id: str
    processing_type: str
    processing_params: Dict[str, Any] = {}
```

Represents a processed image.

### UploadedImage

```python
class UploadedImage(ImageAsset):
    """Represents a user-uploaded image."""

    uploader_id: str
    original_filename: str
```

Represents a user-uploaded image.

### PaletteColor

```python
class PaletteColor(BaseModel):
    """Represents a color in a palette."""

    hex: str
    rgb: Tuple[int, int, int]
    hsv: Tuple[float, float, float]
    name: Optional[str] = None
    proportion: Optional[float] = None
```

Represents a color in a palette.

### Palette

```python
class Palette(BaseModel):
    """Represents a color palette."""

    palette_id: str
    name: str
    source_image_id: Optional[str] = None
    colors: List[PaletteColor]
    created_at: datetime
    type: str = "custom"
```

Represents a color palette.

## Usage Examples

### Image Generation

```python
from app.services.image_service import ImageService
from app.services.persistence.image_persistence import ImagePersistenceService
from app.clients.jigsaw_stack_client import JigsawStackClient
from app.storage.storage_provider import S3StorageProvider
from app.config.image_service_config import ImageServiceConfig

# Initialize dependencies
image_persistence = ImagePersistenceService(...)
ai_client = JigsawStackClient(api_key="your_api_key")
storage_provider = S3StorageProvider(...)
config = ImageServiceConfig(...)

# Create image service
image_service = ImageService(
    image_persistence,
    ai_client,
    storage_provider,
    config
)

# Generate an image
generated_image = await image_service.generate_image(
    prompt="A futuristic city skyline with flying cars and neon lights",
    width=1024,
    height=768,
    style="photorealistic",
    model="stable-diffusion-xl"
)

# Get the image URL
image_url = await image_service.get_image_url(generated_image.image_id)
```

### Color Palette Generation and Application

```python
# Generate a color palette from an image
palette = await image_service.generate_color_palette(
    image_id=generated_image.image_id,
    num_colors=5,
    palette_type="vibrant"
)

# Generate multiple palette options
palette_options = await image_service.generate_multiple_palettes(
    image_id=generated_image.image_id,
    palette_options={
        "palette_types": ["dominant", "vibrant", "muted"],
        "num_colors": 5
    }
)

# Apply a palette to an image
modified_image = await image_service.apply_palette_to_image(
    image_id=generated_image.image_id,
    palette_id=palette.palette_id,
    strength=0.8
)
```

### Image Processing and Manipulation

```python
# Resize an image
resized_image = await image_service.resize_image(
    image_id=generated_image.image_id,
    width=512,
    height=512,
    maintain_aspect_ratio=True
)

# Crop an image
cropped_image = await image_service.crop_image(
    image_id=generated_image.image_id,
    x=100,
    y=100,
    width=800,
    height=600
)

# Apply a filter to an image
filtered_image = await image_service.apply_filter(
    image_id=generated_image.image_id,
    filter_type="gaussian_blur",
    filter_params={"radius": 5}
)
```

### Image Refinement and Variations

```python
# Refine an image
refined_image = await image_service.refine_image(
    image_id=generated_image.image_id,
    refinement_prompt="Add more flying cars and make the neon lights brighter",
    preserve_structure=True,
    refinement_strength=0.7
)

# Generate variations of an image
variations = await image_service.generate_variations(
    base_image_id=generated_image.image_id,
    num_variations=3,
    variation_strength=0.6
)
```

### Image Export and Format Conversion

```python
# Export an image as JPG
jpg_data = await image_service.export_image(
    image_id=generated_image.image_id,
    format="jpg",
    quality=85
)

# Export an image as WebP
webp_data = await image_service.export_image(
    image_id=generated_image.image_id,
    format="webp",
    quality=90
)
```

## Image Generation Workflow

The typical image generation workflow includes:

1. **Prompt Creation**: User provides a text description of the desired image
2. **Image Generation**: Service generates an image based on the prompt
3. **Color Palette Extraction**: Service extracts color palettes from the generated image
4. **Refinement**: User refines the image by providing additional guidance
5. **Variation Generation**: User explores variations of the image
6. **Export**: User exports the final image in the desired format

## Error Handling

Common exceptions that may be raised:

- `ImageNotFoundError`: When an image with the specified ID doesn't exist
- `ImageGenerationError`: When an error occurs during image generation
- `StorageError`: When an error occurs while storing or retrieving an image
- `InvalidImageError`: When an uploaded image is invalid or corrupted
- `ProcessingError`: When an error occurs during image processing

## Integration Points

The `ImageService` integrates with several components:

- **AI Client**: For generating and refining images
- **Storage Provider**: For storing and retrieving image files
- **Image Persistence Service**: For storing image metadata in the database
- **Color Processing Service**: For extracting and manipulating color palettes

## Performance Considerations

The `ImageService` implements several optimizations for better performance:

1. **Caching**: Frequently accessed images are cached
2. **Lazy Loading**: Image data is loaded only when needed
3. **Image Optimization**: Images are optimized for different use cases
4. **CDN Integration**: Images can be served from a CDN for faster delivery
5. **Batch Processing**: Multiple images can be processed in batches

## Related Documentation

- [Image Persistence Service](./persistence/image_persistence.md): Service for image data persistence
- [JigsawStack Client](../clients/jigsaw_stack_client.md): Client for AI image generation
- [Storage Provider](../storage/storage_provider.md): Provider for storing image files
- [Image API Routes](../api/routes/image_routes.md): API endpoints for image operations
- [Color Palette API Routes](../api/routes/palette_routes.md): API endpoints for color palette operations
