# Concept Service Interface

The `interface.py` module defines the abstract interface for all concept services, establishing a contract that must be implemented by concrete service classes.

## Overview

The concept service interface provides a well-defined contract for handling visual concept operations, ensuring that all implementations follow a consistent pattern and provide the required functionality. This allows for dependency injection and easy testing of components that depend on concept services.

## Interface Definition

```python
class ConceptServiceInterface(Protocol):
    """Interface for concept service operations."""
    
    async def generate_concept(
        self, logo_description: str, theme_description: str
    ) -> GenerationResponse:
        """Generate a new concept based on the provided descriptions."""
        ...
        
    async def refine_concept(
        self, concept_id: str, refinement_prompt: str
    ) -> RefinementResponse:
        """Refine an existing concept with additional prompt guidance."""
        ...
        
    async def generate_color_palettes(
        self, theme_description: str, count: int = 3
    ) -> List[Palette]:
        """Generate color palettes based on the theme description."""
        ...
        
    async def apply_color_palette(
        self, concept_id: str, palette_id: str
    ) -> PaletteApplicationResponse:
        """Apply a color palette to an existing concept."""
        ...
```

## Key Methods

### Generate Concept

The `generate_concept` method creates a new visual concept based on textual descriptions.

**Parameters:**
- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme for the concept

**Returns:**
- `GenerationResponse`: Contains the generated image URL, color palettes, and metadata

**Expected Behavior:**
- Should process input descriptions to create an optimized prompt
- Should generate both a base image and color palettes
- Should handle errors gracefully with appropriate exceptions

### Refine Concept

The `refine_concept` method modifies an existing concept based on user feedback.

**Parameters:**
- `concept_id`: Identifier of the concept to refine
- `refinement_prompt`: Text instructions for how to refine the concept

**Returns:**
- `RefinementResponse`: Contains the refined image URL and comparison information

**Expected Behavior:**
- Should retrieve the original concept using the ID
- Should apply the refinement prompt to create an improved version
- Should maintain a reference to the original for comparison

### Generate Color Palettes

The `generate_color_palettes` method creates color schemes based on textual descriptions.

**Parameters:**
- `theme_description`: Text description of the desired color theme
- `count`: Number of palettes to generate (default: 3)

**Returns:**
- List of `Palette` objects containing colors and metadata

**Expected Behavior:**
- Should create cohesive and aesthetically pleasing color combinations
- Should ensure palette diversity if multiple palettes are requested
- Should return consistent number of colors per palette

### Apply Color Palette

The `apply_color_palette` method recolors an existing concept with a new color scheme.

**Parameters:**
- `concept_id`: Identifier of the concept to recolor
- `palette_id`: Identifier of the palette to apply

**Returns:**
- `PaletteApplicationResponse`: Contains the recolored image URL and palette details

**Expected Behavior:**
- Should retrieve both the concept and palette using their IDs
- Should apply the palette colors to the concept image
- Should preserve the original concept structure while changing colors

## Service Lifecycle

Implementations of the concept service interface should:

1. Initialize with necessary dependencies (API clients, configuration)
2. Manage connection states to external services
3. Handle cleanup of resources when no longer needed
4. Provide proper error handling and logging

## Error Handling

Service implementations should use the following exception hierarchy:

- `ConceptServiceError`: Base error for all concept service errors
  - `GenerationError`: For errors during concept generation
  - `RefinementError`: For errors during concept refinement
  - `PaletteError`: For errors related to palettes
  - `ResourceNotFoundError`: For when requested resources don't exist

## Dependency Injection

The interface supports dependency injection through FastAPI's dependency system:

```python
def get_concept_service(
    jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client),
) -> ConceptServiceInterface:
    """Dependency for getting a concept service instance."""
    return ConceptService(client=jigsawstack_client)
```

## Using the Service

Code that needs concept functionality should depend on the interface rather than concrete implementations:

```python
async def process_concept(
    service: ConceptServiceInterface,
    logo_description: str,
    theme_description: str
):
    """Process a concept using any service that implements the interface."""
    result = await service.generate_concept(logo_description, theme_description)
    # Further processing...
    return result
```

## Related Documentation

- [Concept Service](service.md): Main implementation of this interface
- [Concept Generation](generation.md): Details on the generation implementation
- [Concept Refinement](refinement.md): Details on the refinement implementation
- [Palette Service](palette.md): Service for generating color palettes
- [API Routes](../../api/routes/concept/generation.md): API routes that use this interface 