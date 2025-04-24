# Concept Service

The `service.py` module implements the main concept service that orchestrates concept generation, refinement, and palette operations.

## Overview

The Concept Service is a central component that:

1. Implements the `ConceptServiceInterface`
2. Orchestrates the various concept operations (generation, refinement, palette management)
3. Handles interaction between specialized components
4. Provides a unified API for concept-related functionality

This service acts as a facade for the concept subsystem, simplifying interaction with the various concept-related components.

## Service Implementation

```python
class ConceptService(ConceptServiceInterface):
    """Main implementation of the concept service interface."""

    def __init__(
        self,
        client: JigsawStackClient,
        persistence_service: Optional[ConceptPersistenceServiceInterface] = None,
        image_persistence_service: Optional[ImagePersistenceServiceInterface] = None,
        task_service: Optional[TaskServiceInterface] = None
    ):
        """Initialize the concept service with required dependencies."""
        self.client = client
        self.persistence_service = persistence_service
        self.image_persistence_service = image_persistence_service
        self.task_service = task_service

        # Create specialized components
        self.generator = ConceptGenerator(client)
        self.refiner = ConceptRefiner(client, persistence_service)
        self.palette_generator = PaletteGenerator(client)

        self.logger = logging.getLogger("concept_service")
```

The ConceptService coordinates the work of specialized components, each responsible for a specific aspect of concept management.

## Key Methods

### Generate Concept

```python
async def generate_concept(
    self, logo_description: str, theme_description: str
) -> GenerationResponse:
    """Generate a new concept based on the provided descriptions."""
```

This method orchestrates the concept generation process:

1. Validates the input descriptions
2. Delegates to the generator component for image creation
3. Uses the palette generator for color scheme generation
4. Optionally persists the generated concept
5. Returns a comprehensive response with the generated concept details

**Parameters:**

- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme

**Returns:**

- `GenerationResponse`: Contains the generated image URL, color palettes, and metadata

**Raises:**

- `ValidationError`: If the input descriptions are invalid
- `GenerationError`: If concept generation fails
- `ServiceUnavailableError`: If required services are unavailable

### Refine Concept

```python
async def refine_concept(
    self, concept_id: str, refinement_prompt: str
) -> RefinementResponse:
    """Refine an existing concept with additional prompt guidance."""
```

This method handles the concept refinement workflow:

1. Validates the concept ID and refinement prompt
2. Retrieves the existing concept from persistence
3. Delegates to the refiner component for image refinement
4. Optionally persists the refined concept
5. Returns the refinement results with comparison information

**Parameters:**

- `concept_id`: ID of the concept to refine
- `refinement_prompt`: Text instructions for refining the concept

**Returns:**

- `RefinementResponse`: Contains the refined image URL, original image URL, and metadata

**Raises:**

- `ResourceNotFoundError`: If the concept doesn't exist
- `ValidationError`: If the refinement prompt is invalid
- `RefinementError`: If the refinement process fails

### Generate Color Palettes

```python
async def generate_color_palettes(
    self, theme_description: str, count: int = 3
) -> List[Palette]:
    """Generate color palettes based on a theme description."""
```

This method handles palette generation:

1. Validates the theme description
2. Delegates to the palette generator for color scheme creation
3. Returns the generated palettes

**Parameters:**

- `theme_description`: Text description of the desired color theme
- `count`: Number of palettes to generate (default: 3)

**Returns:**

- List of `Palette` objects containing colors and metadata

**Raises:**

- `ValidationError`: If the theme description is invalid
- `PaletteError`: If palette generation fails

### Apply Color Palette

```python
async def apply_color_palette(
    self, concept_id: str, palette_id: str
) -> PaletteApplicationResponse:
    """Apply a color palette to an existing concept."""
```

This method applies a palette to an existing concept:

1. Validates the concept and palette IDs
2. Retrieves the concept and palette from persistence
3. Applies the palette colors to the concept image
4. Optionally persists the recolored concept
5. Returns the result with the recolored image URL

**Parameters:**

- `concept_id`: ID of the concept to recolor
- `palette_id`: ID of the palette to apply

**Returns:**

- `PaletteApplicationResponse`: Contains the recolored image URL and palette details

**Raises:**

- `ResourceNotFoundError`: If the concept or palette doesn't exist
- `PaletteApplicationError`: If applying the palette fails

## Integration with Persistence

The ConceptService integrates with persistence services to:

1. Store generated concepts for later retrieval
2. Retrieve existing concepts for refinement
3. Store palettes and their associations with concepts
4. Track relationships between original and refined concepts

## Background Task Integration

For long-running operations, the service can optionally use a task service to:

1. Create background tasks for asynchronous processing
2. Track the progress of concept generation and refinement
3. Store results when tasks complete
4. Handle errors in the background process

## Error Handling

The service implements a comprehensive error handling strategy:

1. Input validation before performing operations
2. Precise error types for different failure scenarios
3. Consistent error propagation from specialized components
4. Detailed logging of errors with appropriate context

## Usage Examples

### Basic Concept Generation

```python
from app.services.concept.service import ConceptService
from app.services.jigsawstack.client import JigsawStackClient

# Create the client
client = JigsawStackClient(api_key="your_api_key")

# Initialize the service
concept_service = ConceptService(client)

# Generate a concept
result = await concept_service.generate_concept(
    logo_description="A modern tech company logo with abstract geometric shapes",
    theme_description="Professional, tech-focused with blue and gray tones"
)

# Access the generated concept
image_url = result.image_url
palettes = result.color_palettes
concept_id = result.concept_id
```

### Concept Refinement

```python
# Assuming we have a concept_id from a previous generation
refinement = await concept_service.refine_concept(
    concept_id="abc123",
    refinement_prompt="Make the logo more minimalist and use brighter colors"
)

# Access the refinement result
original_url = refinement.original_image_url
refined_url = refinement.refined_image_url
```

## Performance Considerations

- The service uses asynchronous operations to prevent blocking
- Heavy operations can be offloaded to background tasks
- Caching strategies are employed where appropriate
- Resources are efficiently managed to minimize memory usage

## Related Documentation

- [Concept Service Interface](interface.md): Interface implemented by this service
- [Concept Generation](generation.md): Details on the generation implementation
- [Concept Refinement](refinement.md): Details on the refinement implementation
- [Palette Generator](palette.md): Component for palette operations
- [JigsawStack Client](../jigsawstack/client.md): Client for the external AI service
- [Generation API Routes](../../api/routes/concept/generation.md): API routes that use this service
