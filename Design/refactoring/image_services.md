# Image Services Refactoring Design Document

## Problem Statement

The current image services in the project have grown significantly in size and complexity:

- `image/service.py` (595 lines): Handles image generation, storage, and processing
- `image/storage.py` (339 lines): Manages image storage in Supabase
- `image/processing.py` (312 lines): Provides image processing functionality
- `image/conversion.py` (282 lines): Manages format conversions

These large files violate the Single Responsibility Principle, making the code difficult to maintain, test, and extend. Each file contains multiple interrelated but conceptually distinct responsibilities.

## Goals

1. Split large modules into smaller, more focused components
2. Improve separation of concerns
3. Enhance testability with smaller, focused components
4. Create clear interfaces for each service type
5. Maintain backward compatibility with existing service users
6. Reduce code duplication
7. Improve error handling consistency

## Design

### 1. Overall Architecture

The refactored design will use a composition-based approach with the following structure:

```
app/services/image/
├── __init__.py                 # Export factory functions and interfaces
├── interfaces/                 # Service interfaces
│   ├── __init__.py
│   ├── generation.py           # Image generation interfaces
│   ├── storage.py              # Storage interfaces
│   ├── processing.py           # Processing interfaces
│   └── conversion.py           # Conversion interfaces
├── generation/                 # Image generation services
│   ├── __init__.py
│   ├── jigsawstack.py          # JigsawStack implementation
│   └── factory.py              # Factory functions
├── storage/                    # Storage services
│   ├── __init__.py
│   ├── supabase.py             # Supabase implementation
│   ├── metadata.py             # Metadata management
│   ├── permissions.py          # Access control
│   └── factory.py              # Factory functions
├── processing/                 # Image processing services
│   ├── __init__.py
│   ├── color.py                # Color operations
│   ├── transformation.py       # Image transformations
│   ├── filters.py              # Visual filters
│   └── factory.py              # Factory functions
├── conversion/                 # Format conversion services
│   ├── __init__.py
│   ├── format.py               # Format conversion
│   ├── svg.py                  # SVG-specific operations
│   ├── enhancement.py          # Image enhancement
│   └── factory.py              # Factory functions
├── service.py                  # Main image service (uses composition)
└── factory.py                  # Main factory functions
```

### 2. Component Descriptions

#### 2.1 Image Generation Services (`generation/`)

This module will focus solely on generating images via different providers:

```python
class JigsawStackImageGenerator(ImageGeneratorInterface):
    """JigsawStack implementation of image generation."""
    
    def __init__(self, jigsawstack_client: JigsawImageClientProtocol):
        """Initialize with a JigsawStack client."""
        self.client = jigsawstack_client
        self.logger = logging.getLogger(__name__)
    
    async def generate_image(
        self, 
        prompt: str,
        width: int = 512,
        height: int = 512
    ) -> bytes:
        """Generate an image based on a prompt."""
        # Implementation...
    
    async def refine_image(
        self, 
        prompt: str,
        original_image_url: str,
        strength: float = 0.7
    ) -> bytes:
        """Refine an existing image using a prompt."""
        # Implementation...
```

#### 2.2 Storage Services (`storage/`)

Split the storage functionality into smaller components:

```python
class SupabaseImageStorage(ImageStorageInterface):
    """Supabase implementation of image storage."""
    
    def __init__(self, supabase_client: SupabaseClient):
        """Initialize with a Supabase client."""
        self.client = supabase_client
        self.logger = logging.getLogger(__name__)
    
    async def store_image(
        self, 
        image_data: bytes,
        path: Optional[str] = None,
        content_type: str = "image/png",
        bucket: str = "concept-images"
    ) -> str:
        """Store an image and return its path."""
        # Implementation...
    
    async def get_image(self, path: str, bucket: str = "concept-images") -> bytes:
        """Retrieve an image by path."""
        # Implementation...
```

```python
class ImageMetadataService:
    """Service for managing image metadata."""
    
    def __init__(self, supabase_client: SupabaseClient):
        """Initialize with a Supabase client."""
        self.client = supabase_client
        self.logger = logging.getLogger(__name__)
    
    async def store_metadata(
        self, 
        image_path: str,
        metadata: Dict[str, Any],
        bucket: str = "concept-images"
    ) -> bool:
        """Store metadata for an image."""
        # Implementation...
    
    async def get_metadata(
        self, 
        image_path: str,
        bucket: str = "concept-images"
    ) -> Optional[Dict[str, Any]]:
        """Retrieve metadata for an image."""
        # Implementation...
```

#### 2.3 Processing Services (`processing/`)

Split image processing into specialized components:

```python
class ColorProcessor:
    """Service for color-related image processing."""
    
    async def extract_dominant_colors(
        self, 
        image_data: bytes,
        num_colors: int = 5
    ) -> List[Dict[str, Any]]:
        """Extract dominant colors from an image."""
        # Implementation...
    
    async def apply_palette(
        self, 
        image_data: bytes,
        palette: List[str],
        blend_strength: float = 0.75
    ) -> bytes:
        """Apply a color palette to an image."""
        # Implementation...
```

```python
class ImageTransformer:
    """Service for image transformation operations."""
    
    async def resize(
        self, 
        image_data: bytes,
        width: int,
        height: int,
        maintain_aspect_ratio: bool = True
    ) -> bytes:
        """Resize an image to specified dimensions."""
        # Implementation...
    
    async def crop(
        self, 
        image_data: bytes,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> bytes:
        """Crop an image to specified dimensions."""
        # Implementation...
```

#### 2.4 Conversion Services (`conversion/`)

Split conversion functionality into specialized components:

```python
class FormatConverter:
    """Service for image format conversion."""
    
    async def convert_to_format(
        self, 
        image_data: bytes,
        target_format: str,
        quality: int = 90
    ) -> bytes:
        """Convert image to specified format."""
        # Implementation...
    
    async def get_image_info(self, image_data: bytes) -> Dict[str, Any]:
        """Get information about an image."""
        # Implementation...
```

```python
class SVGProcessor:
    """Service for SVG-specific operations."""
    
    async def rasterize_svg(
        self, 
        svg_data: bytes,
        width: int,
        height: int,
        background_color: Optional[str] = None
    ) -> bytes:
        """Convert SVG to raster image."""
        # Implementation...
    
    async def optimize_svg(self, svg_data: bytes) -> bytes:
        """Optimize SVG file size and structure."""
        # Implementation...
```

#### 2.5 Main Image Service (`service.py`)

The main ImageService will use composition with specialized services:

```python
class ImageService:
    """Main service for image operations using composition."""
    
    def __init__(
        self,
        generator: ImageGeneratorInterface,
        storage: ImageStorageInterface,
        processor: ImageProcessorInterface,
        converter: ImageConverterInterface
    ):
        """Initialize with specialized services."""
        self.generator = generator
        self.storage = storage
        self.processor = processor
        self.converter = converter
        self.logger = logging.getLogger(__name__)
    
    # Delegate to specialized services
    async def generate_and_store_image(self, prompt: str, session_id: str) -> Tuple[Optional[str], Optional[str]]:
        """Generate an image and store it in storage."""
        try:
            # Generate image
            image_data = await self.generator.generate_image(prompt)
            
            # Generate path
            path = f"{session_id}/{uuid.uuid4()}.png"
            
            # Store image
            stored_path = await self.storage.store_image(image_data, path)
            
            # Get public URL
            public_url = await self.storage.get_public_url(stored_path)
            
            return stored_path, public_url
        except Exception as e:
            self.logger.error(f"Error in generate_and_store_image: {e}")
            return None, None
    
    # Other methods delegating to specialized services...
```

### 3. Interfaces (`interfaces/`)

Define clear interfaces for each service type:

```python
class ImageGeneratorInterface(Protocol):
    """Interface for image generation services."""
    
    async def generate_image(
        self, 
        prompt: str,
        width: int = 512,
        height: int = 512
    ) -> bytes: ...
    
    async def refine_image(
        self, 
        prompt: str,
        original_image_url: str,
        strength: float = 0.7
    ) -> bytes: ...

class ImageStorageInterface(Protocol):
    """Interface for image storage services."""
    
    async def store_image(
        self, 
        image_data: bytes,
        path: Optional[str] = None,
        content_type: str = "image/png",
        bucket: str = "concept-images"
    ) -> str: ...
    
    async def get_image(
        self, 
        path: str,
        bucket: str = "concept-images"
    ) -> bytes: ...
```

### 4. Factory Functions (`factory.py`)

Create factory functions to instantiate services:

```python
def get_image_generator(
    jigsawstack_client: Optional[JigsawImageClientProtocol] = None
) -> ImageGeneratorInterface:
    """Get an image generator implementation."""
    if jigsawstack_client is None:
        jigsawstack_client = get_jigsawstack_image_client()
    
    return JigsawStackImageGenerator(jigsawstack_client)

def get_image_storage(
    supabase_client: Optional[SupabaseClient] = None
) -> ImageStorageInterface:
    """Get an image storage implementation."""
    if supabase_client is None:
        supabase_client = get_supabase_client()
    
    return SupabaseImageStorage(supabase_client)

# Main image service factory
def get_image_service(
    generator: Optional[ImageGeneratorInterface] = None,
    storage: Optional[ImageStorageInterface] = None,
    processor: Optional[ImageProcessorInterface] = None,
    converter: Optional[ImageConverterInterface] = None
) -> ImageService:
    """Get the main image service."""
    generator = generator or get_image_generator()
    storage = storage or get_image_storage()
    processor = processor or get_image_processor()
    converter = converter or get_image_converter()
    
    return ImageService(generator, storage, processor, converter)
```

## Implementation Plan

### Phase 1: Interface Definition

1. Create the directory structure
2. Define interfaces for all service types
3. Create placeholder factory functions

### Phase 2: Storage Services

1. Implement SupabaseImageStorage
2. Implement ImageMetadataService
3. Implement factory functions

### Phase 3: Processing and Conversion Services

1. Implement ColorProcessor
2. Implement ImageTransformer
3. Implement FormatConverter
4. Implement SVGProcessor
5. Implement factory functions

### Phase 4: Generation Services

1. Implement JigsawStackImageGenerator
2. Implement factory functions

### Phase 5: Main Service Implementation

1. Implement ImageService with composition
2. Create main factory function
3. Add backward compatibility layer

### Phase 6: Service Updates

1. Update service dependencies to use new interfaces
2. Update service implementations to use specialized components
3. Update tests

## Testing Strategy

1. Create unit tests for each service component
2. Mock dependencies for isolated testing
3. Create integration tests to verify correct interactions
4. Test backwards compatibility with existing code
5. Verify performance is equivalent or improved

## Risks and Mitigations

1. **Risk**: Breaking changes affecting production
   **Mitigation**: Maintain backward compatibility and thorough testing

2. **Risk**: Performance overhead from increased abstraction
   **Mitigation**: Careful design to minimize method call overhead

3. **Risk**: Incomplete interface definitions missing required functionality
   **Mitigation**: Comprehensive review of current usage patterns before finalization

## Timeline

- Phase 1 (Interface Definition): 1 day
- Phase 2 (Storage Services): 2 days
- Phase 3 (Processing/Conversion): 3 days
- Phase 4 (Generation Services): 1 day
- Phase 5 (Main Service): 1 day
- Phase 6 (Service Updates): 2 days
- Testing: 2 days

Total: 12 days 