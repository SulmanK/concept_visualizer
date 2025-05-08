# Concept Service Interface

The `interface.py` module defines the abstract interface for all concept services, establishing a contract that must be implemented by concrete service classes.

## Overview

The concept service interface provides a well-defined contract for handling visual concept operations, ensuring that all implementations follow a consistent pattern and provide the required functionality. This allows for dependency injection and easy testing of components that depend on concept services.

## Interface Definition

```python
class ConceptServiceInterface(abc.ABC):
    """Interface for concept generation and refinement services."""

    @abc.abstractmethod
    async def generate_concept(
        self,
        logo_description: str,
        theme_description: str,
        user_id: Optional[str] = None,
        skip_persistence: bool = False,
    ) -> Dict[str, Any]:
        """Generate a new visual concept based on provided descriptions."""
        ...

    @abc.abstractmethod
    async def generate_concept_with_palettes(
        self,
        logo_description: str,
        theme_description: str,
        num_palettes: int = 3
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """Generate a concept with multiple palette variations."""
        ...

    @abc.abstractmethod
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
        ...

    @abc.abstractmethod
    async def generate_color_palettes(
        self,
        theme_description: str,
        logo_description: Optional[str] = None,
        num_palettes: int = 7,
    ) -> List[Dict[str, Any]]:
        """Generate multiple color palettes based on a theme description."""
        ...
```

## Key Methods

### Generate Concept

The `generate_concept` method creates a new visual concept based on textual descriptions.

**Parameters:**

- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme for the concept
- `user_id`: Optional user ID for storing the concept
- `skip_persistence`: If True, don't store the concept in the database

**Returns:**

- Dictionary containing the generated concept with keys like:
  - `image_url`: URL to the generated image
  - `image_path`: Storage path if saved
  - `concept_id`: ID if stored in database
  - `image_data`: Optional binary image data

**Expected Behavior:**

- Should generate an image based on the logo description
- Should optionally download the generated image
- Should optionally store the image and concept metadata if user_id is provided and skip_persistence is False
- Should return both the image URL and potentially binary image data for further processing

### Generate Concept with Palettes

The `generate_concept_with_palettes` method creates a concept with multiple palette variations.

**Parameters:**

- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme
- `num_palettes`: Number of palette variations to generate (default: 3)

**Returns:**

- Tuple containing:
  - List of palette dictionaries with name, colors, description
  - List of dictionaries with palette variation images

**Expected Behavior:**

- Should generate a base image first
- Should generate multiple color palette options
- Should recolor the base image with each palette
- Should return both the palettes and the variation images

### Refine Concept

The `refine_concept` method modifies an existing concept based on user feedback.

**Parameters:**

- `original_image_url`: URL of the original image to refine
- `refinement_prompt`: Specific instructions for refinement
- `logo_description`: Updated description of the logo (optional)
- `theme_description`: Updated description of the theme (optional)
- `user_id`: Optional user ID for storing the refined concept
- `skip_persistence`: If True, don't store the refined concept
- `strength`: Control how much to preserve of the original (0.0-1.0)

**Returns:**

- Dictionary containing the refined concept with keys similar to generate_concept

**Expected Behavior:**

- Should download the original image
- Should apply the refinement instructions
- Should optionally store the refined image and metadata
- Should return both the image URL and potentially binary image data

### Generate Color Palettes

The `generate_color_palettes` method creates color schemes based on textual descriptions.

**Parameters:**

- `theme_description`: Description of the theme/color scheme
- `logo_description`: Optional description of the logo to help contextualize
- `num_palettes`: Number of palettes to generate (default: 7)

**Returns:**

- List of palette dictionaries, each containing name, colors, and description

**Expected Behavior:**

- Should create cohesive and aesthetically pleasing color combinations
- Should ensure palette diversity if multiple palettes are requested
- Should use the theme description as the primary guide
- Should consider the logo description for context if provided

## Error Handling

Service implementations should handle and raise the following exception types:

- `ConceptError`: Base error for all concept service errors
- `JigsawStackConnectionError`: When connection to the API fails
- `JigsawStackAuthenticationError`: When authentication fails
- `JigsawStackGenerationError`: When generation fails due to API errors

## Dependency Injection

The interface supports dependency injection through FastAPI's dependency system:

```python
def get_concept_service(
    jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client),
    image_service: ImageServiceInterface = Depends(get_image_service),
    concept_persistence_service: ConceptPersistenceServiceInterface = Depends(get_concept_persistence_service),
    image_persistence_service: ImagePersistenceServiceInterface = Depends(get_image_persistence_service),
) -> ConceptServiceInterface:
    """Dependency for getting a concept service instance."""
    return ConceptService(
        client=jigsawstack_client,
        image_service=image_service,
        concept_persistence_service=concept_persistence_service,
        image_persistence_service=image_persistence_service,
    )
```

## Using the Service

Code that needs concept functionality should depend on the interface rather than concrete implementations:

```python
async def process_concept(
    service: ConceptServiceInterface,
    logo_description: str,
    theme_description: str,
    user_id: str
):
    """Process a concept using any service that implements the interface."""
    result = await service.generate_concept(
        logo_description=logo_description,
        theme_description=theme_description,
        user_id=user_id
    )
    # Further processing...
    return result
```

## Related Documentation

- [Concept Service](service.md): Main implementation of this interface
- [Concept Generation](generation.md): Details on the generation implementation
- [Concept Refinement](refinement.md): Details on the refinement implementation
- [Palette Service](palette.md): Service for generating color palettes
- [API Routes](../../api/routes/concept/generation.md): API routes that use this interface
