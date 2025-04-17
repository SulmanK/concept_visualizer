# Concept Service

The Concept Service is a core component of the backend that handles the generation and refinement of visual concepts, integrating with JigsawStack API for image generation.

## Overview

The service provides an abstraction layer over the JigsawStack API, adding business logic for concept generation, refinement, and persistence. It uses a combination of specialized components to handle different aspects of concept processing.

## Structure

The Concept Service follows a modular architecture:

- `ConceptService`: Main service class that integrates specialized components
- `ConceptGenerator`: Specialized component for generating base concepts
- `ConceptRefiner`: Specialized component for refining existing concepts
- `PaletteGenerator`: Specialized component for generating color palettes

## Dependencies

The service relies on the following dependencies:

- `JigsawStackClient`: Client for communicating with the JigsawStack API
- `ImageService`: Service for processing and manipulating images
- `ConceptPersistenceService`: Service for storing concept data
- `ImagePersistenceService`: Service for storing image data

## Key Methods

### `generate_concept`

Generates a new concept image based on text descriptions.

```python
async def generate_concept(
    self,
    logo_description: str,
    theme_description: str,
    user_id: Optional[str] = None,
    skip_persistence: bool = False
) -> Dict[str, Any]
```

**Parameters**:
- `logo_description`: Text description of the logo
- `theme_description`: Text description of the theme
- `user_id`: Optional user ID to associate with the stored concept
- `skip_persistence`: If True, skip storing the concept in the database

**Returns**:
- Dictionary containing the concept details (image URL, path, concept ID, etc.)

**Process**:
1. Sends a generation request to JigsawStack API
2. Downloads the generated image (if user_id is provided)
3. Stores the image in Supabase Storage (if not skipping persistence)
4. Creates a concept record in the database (if not skipping persistence)
5. Returns the concept data with appropriate URLs

### `generate_concept_with_palettes`

Generates a concept with multiple palette variations.

```python
async def generate_concept_with_palettes(
    self, 
    logo_description: str, 
    theme_description: str, 
    num_palettes: int = 3,
    user_id: Optional[str] = None
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]
```

**Parameters**:
- `logo_description`: Description of the logo to generate
- `theme_description`: Description of the theme/color scheme
- `num_palettes`: Number of palette variations to generate
- `user_id`: Optional user ID for persisting the concept

**Returns**:
- Tuple containing:
  - The base generated concept
  - List of palette variations with image URLs

**Process**:
1. Generates a base concept using `generate_concept`
2. Generates multiple color palettes using the `PaletteGenerator`
3. Creates visual variations of the concept with different palettes
4. Returns both the base concept and variations

### `refine_concept`

Refines an existing concept based on a refinement prompt.

```python
async def refine_concept(
    self,
    original_image_url: str,
    logo_description: Optional[str],
    theme_description: Optional[str],
    refinement_prompt: str,
    preserve_aspects: List[str],
    user_id: Optional[str] = None
) -> GenerationResponse
```

**Parameters**:
- `original_image_url`: URL of the original concept image
- `logo_description`: Original logo description (optional)
- `theme_description`: Original theme description (optional)
- `refinement_prompt`: Text describing the desired changes
- `preserve_aspects`: List of aspects to preserve (e.g., "layout", "colors")
- `user_id`: Optional user ID for persisting the refined concept

**Returns**:
- Generation response containing the refined concept details

**Process**:
1. Downloads the original image
2. Sends a refinement request to JigsawStack API
3. Downloads the refined image
4. Stores the refined image in Supabase Storage (if user_id is provided)
5. Creates a concept record in the database (if user_id is provided)
6. Returns the refined concept data

### `generate_color_palettes`

Generates color palettes based on text descriptions.

```python
async def generate_color_palettes(
    self, 
    theme_description: str, 
    logo_description: Optional[str] = None,
    num_palettes: int = 7
) -> List[Dict[str, Any]]
```

**Parameters**:
- `theme_description`: Description of the desired theme/color scheme
- `logo_description`: Optional logo description for context
- `num_palettes`: Number of palettes to generate

**Returns**:
- List of palette objects with color values

**Process**:
1. Uses the `PaletteGenerator` to generate palettes
2. Returns the palette data

### `apply_palette_to_concept`

Applies a color palette to an existing concept image.

```python
async def apply_palette_to_concept(
    self,
    concept_image_url: str,
    palette_colors: List[str],
    user_id: Optional[str] = None,
    blend_strength: float = 0.75
) -> Tuple[str, str]
```

**Parameters**:
- `concept_image_url`: URL of the concept image
- `palette_colors`: List of hex color codes for the palette
- `user_id`: Optional user ID for persisting the result
- `blend_strength`: Strength of the palette application (0.0-1.0)

**Returns**:
- Tuple containing the image path and URL of the palette-applied image

**Process**:
1. Downloads the concept image
2. Uses the `ImageService` to apply the palette
3. Stores the result in Supabase Storage (if user_id is provided)
4. Returns the path and URL of the resulting image

## Error Handling

The service uses custom exceptions to handle various error scenarios:

- `ConceptError`: Base exception for concept-related errors
- `JigsawStackConnectionError`: For connection issues with the API
- `JigsawStackAuthenticationError`: For authentication failures
- `JigsawStackGenerationError`: For image generation failures

## Usage

The service is typically accessed through dependency injection in the API routes:

```python
@router.post("/concepts/generate", response_model=GenerationResponse)
async def generate_concept(
    request: GenerationRequest,
    concept_service: ConceptServiceInterface = Depends(get_concept_service),
    user_id: Optional[str] = Depends(get_current_user_id)
):
    result = await concept_service.generate_concept(
        logo_description=request.logo_description,
        theme_description=request.theme_description,
        user_id=user_id
    )
    return result
``` 