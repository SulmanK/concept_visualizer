# Concept Service

The `service.py` module implements the main concept service that orchestrates concept generation, refinement, and palette operations.

## Overview

The Concept Service is a central component that:

1. Implements the `ConceptServiceInterface`
2. Orchestrates the various concept operations (generation, refinement, palette management)
3. Handles interaction between specialized components and persistence services
4. Provides a unified API for concept-related functionality

This service acts as a facade for the concept subsystem, simplifying interaction with the various concept-related components.

## Service Implementation

```python
class ConceptService(ConceptServiceInterface):
    """Service for generating and refining visual concepts."""

    def __init__(
        self,
        client: JigsawStackClient,
        image_service: ImageServiceInterface,
        concept_persistence_service: ConceptPersistenceServiceInterface,
        image_persistence_service: ImagePersistenceServiceInterface,
    ):
        """Initialize the concept service with specialized components."""
        self.client = client
        self.image_service = image_service
        self.concept_persistence = concept_persistence_service
        self.image_persistence = image_persistence_service
        self.logger = get_logger("concept_service")

        # Initialize specialized components
        self.generator = ConceptGenerator(client)
        self.refiner = ConceptRefiner(client)
        self.palette_generator = PaletteGenerator(client)
```

The ConceptService coordinates the work of specialized components and integrates with persistence services to store and retrieve concepts and images.

## Key Methods

### Generate Concept

```python
async def generate_concept(
    self,
    logo_description: str,
    theme_description: str,
    user_id: Optional[str] = None,
    skip_persistence: bool = False,
) -> Dict[str, Any]:
    """Generate a new concept image based on text descriptions and store it if user_id provided."""
```

This method handles the concept generation process:

1. Uses the JigsawStack client to generate an image based on the logo description
2. Downloads the generated image if a user ID is provided
3. Optionally stores the image and concept metadata if persistence is not skipped
4. Returns a dictionary with the concept details including the image URL and potentially the binary image data

**Parameters:**

- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme
- `user_id`: Optional user ID to associate with the stored concept
- `skip_persistence`: If True, skip storing the concept in the database

**Returns:**

- Dictionary containing the concept details with keys:
  - `image_url`: URL to the generated image
  - `image_path`: Storage path if saved
  - `concept_id`: ID if stored in database
  - `logo_description`: Original logo description
  - `theme_description`: Original theme description
  - `image_data`: Optional binary image data

**Raises:**

- `ConceptError`: If image generation or storage fails

### Generate Concept with Palettes

```python
async def generate_concept_with_palettes(
    self,
    logo_description: str,
    theme_description: str,
    num_palettes: int = 3,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Generate a concept with multiple palette variations, each with its own image."""
```

This method creates a concept with multiple palette variations:

1. Generates a base image using the logo description
2. Generates multiple color palettes based on the theme description
3. Creates variations of the base image with each palette
4. Returns both the palettes and the variation images

**Parameters:**

- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme
- `num_palettes`: Number of palette variations to generate (default: 3)

**Returns:**

- Tuple containing:
  - List of palette dictionaries with name, colors, description
  - List of dictionaries with palette info and image data

**Raises:**

- `ConceptError`: If image generation or palette application fails

### Refine Concept

```python
async def refine_concept(
    self,
    original_image_url: str,
    refinement_prompt: str,
    logo_description: Optional[str] = None,
    theme_description: Optional[str] = None,
    user_id: Optional[str] = None,
    skip_persistence: bool = False,
    strength: float = 0.7,
) -> Dict[str, Any]:
    """Refine an existing concept based on provided instructions."""
```

This method handles the concept refinement process:

1. Downloads the original image from the provided URL
2. Uses the JigsawStack client to refine the image based on the prompt
3. Optionally stores the refined image and metadata if a user ID is provided and persistence is not skipped
4. Returns a dictionary with the refined concept details

**Parameters:**

- `original_image_url`: URL of the original image to refine
- `refinement_prompt`: Specific instructions for refinement
- `logo_description`: Updated description of the logo (optional)
- `theme_description`: Updated description of the theme (optional)
- `user_id`: Optional user ID for storing the refined concept
- `skip_persistence`: If True, don't store the refined concept
- `strength`: Control how much to preserve of the original (0.0-1.0)

**Returns:**

- Dictionary containing the refined concept details with keys similar to generate_concept

**Raises:**

- `ConceptError`: If image refinement or storage fails

### Generate Color Palettes

```python
async def generate_color_palettes(
    self,
    theme_description: str,
    logo_description: Optional[str] = None,
    num_palettes: int = 7,
) -> List[Dict[str, Any]]:
    """Generate multiple color palettes based on a theme description."""
```

This method handles palette generation:

1. Uses the JigsawStack client to generate color palettes based on the theme
2. Formats the palette data for use in the application
3. Returns a list of palette dictionaries

**Parameters:**

- `theme_description`: Description of the theme/color scheme
- `logo_description`: Optional description of the logo to help contextualize
- `num_palettes`: Number of palettes to generate (default: 7)

**Returns:**

- List of palette dictionaries, each containing name, colors, and description

**Raises:**

- `ConceptError`: If palette generation fails

### Apply Palette to Concept

```python
async def apply_palette_to_concept(
    self,
    concept_image_url: str,
    palette_colors: List[str],
    user_id: Optional[str] = None,
    blend_strength: float = 0.75,
) -> Tuple[str, str]:
    """Apply a color palette to an existing concept image."""
```

This method applies a palette to an existing concept image:

1. Downloads the original image from the provided URL
2. Uses the image service to apply the palette colors to the image
3. Optionally stores the recolored image if a user ID is provided
4. Returns the URL and path of the recolored image

**Parameters:**

- `concept_image_url`: URL of the image to recolor
- `palette_colors`: List of hex color codes to apply
- `user_id`: Optional user ID for storing the recolored image
- `blend_strength`: How strongly to apply the palette (0.0-1.0)

**Returns:**

- Tuple of (image_url, image_path) for the recolored image

**Raises:**

- `ConceptError`: If image recoloring or storage fails

## Integration with Persistence

The ConceptService integrates with persistence services to:

1. Store generated images in Supabase Storage
2. Store concept metadata in Supabase Database
3. Retrieve images and concepts for processing
4. Generate signed URLs for stored images

## Error Handling

The service implements a comprehensive error handling strategy:

1. Catches and wraps errors from external services
2. Provides detailed error messages and logging
3. Preserves original error context when possible
4. Uses custom error types for specific failure scenarios

## Usage Examples

### Basic Concept Generation

```python
from app.services.concept.service import ConceptService
from app.services.jigsawstack.client import JigsawStackClient
from app.services.image.service import ImageService
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.persistence.image_persistence_service import ImagePersistenceService

# Create dependencies
client = JigsawStackClient(api_key="your_api_key")
image_service = ImageService(client)
concept_persistence = ConceptPersistenceService(supabase_client)
image_persistence = ImagePersistenceService(supabase_client)

# Initialize the service
concept_service = ConceptService(
    client=client,
    image_service=image_service,
    concept_persistence_service=concept_persistence,
    image_persistence_service=image_persistence
)

# Generate a concept
result = await concept_service.generate_concept(
    logo_description="A modern tech company logo with abstract geometric shapes",
    theme_description="Professional, tech-focused with blue and gray tones",
    user_id="user-123"
)

# Access the generated concept
image_url = result["image_url"]
concept_id = result["concept_id"]
```

### Concept Refinement

```python
# Refine an existing concept
refinement = await concept_service.refine_concept(
    original_image_url="https://example.com/original.png",
    refinement_prompt="Make the logo more minimalist and use brighter colors",
    logo_description="Minimalist tech logo",
    theme_description="Bright modern colors",
    user_id="user-123"
)

# Access the refinement result
refined_url = refinement["image_url"]
```

### Generating and Applying Palettes

```python
# Generate palettes
palettes = await concept_service.generate_color_palettes(
    theme_description="Warm autumn colors with earthy tones",
    num_palettes=5
)

# Apply a palette to an image
recolored_url, _ = await concept_service.apply_palette_to_concept(
    concept_image_url="https://example.com/original.png",
    palette_colors=palettes[0]["colors"],
    user_id="user-123"
)
```

## Related Documentation

- [Concept Service Interface](interface.md): Interface implemented by this service
- [Concept Generation](generation.md): Details on the generation implementation
- [Concept Refinement](refinement.md): Details on the refinement implementation
- [Palette Generator](palette.md): Component for palette operations
