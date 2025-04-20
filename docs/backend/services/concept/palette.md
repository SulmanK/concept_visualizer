# Concept Palette Service

The `palette.py` module provides specialized functionality for generating and managing color palettes for visual concepts.

## Overview

The color palette service is responsible for:

1. Generating harmonious color palettes based on textual descriptions
2. Creating multiple palette variations for each concept
3. Applying palettes to existing images
4. Managing palette metadata and organization

This service works closely with the concept generation service to enhance visual concepts with appropriate color schemes.

## Key Components

### PaletteGenerator

```python
class PaletteGenerator:
    """Service for generating color palettes based on textual descriptions."""
    
    def __init__(self, client: JigsawStackClient):
        """Initialize the palette generator with an API client."""
        self.client = client
        self.logger = logging.getLogger("concept_service.palette")
```

The PaletteGenerator is a specialized component that converts textual theme descriptions into coordinated color schemes.

## Core Functionality

### Generate Palettes

```python
async def generate_palettes(
    self, theme_description: str, count: int = 3
) -> List[Palette]:
    """Generate color palettes based on a theme description."""
```

This method creates multiple color palettes based on a textual theme description.

**Parameters:**
- `theme_description`: Textual description of the desired color theme
- `count`: Number of different palette variations to generate (default: 3)

**Returns:**
- List of `Palette` objects containing color information and metadata

**Raises:**
- `ServiceUnavailableError`: If the external palette service is unavailable
- `PaletteGenerationError`: If there's an error generating palettes

### Process Theme Description

```python
def process_theme_description(self, theme_description: str) -> str:
    """Process the theme description to optimize palette generation."""
```

This method enhances raw theme descriptions to improve palette generation results.

**Parameters:**
- `theme_description`: Original theme description from the user

**Returns:**
- Enhanced description optimized for palette generation

### Apply Palette to Image

```python
async def apply_palette_to_image(
    self, image_data: bytes, palette: Palette
) -> bytes:
    """Apply a color palette to an existing image."""
```

This method transforms an image by applying a specific color palette to it.

**Parameters:**
- `image_data`: Binary image data to transform
- `palette`: Palette object containing colors to apply

**Returns:**
- Binary data of the transformed image

**Raises:**
- `ImageProcessingError`: If there's an error processing the image
- `PaletteApplicationError`: If there's an error applying the palette

## Palette Structure

Each generated palette contains:

1. A unique identifier
2. A descriptive name based on the theme
3. A list of 5-7 coordinated colors with their RGB, HSL, and hex values
4. Metadata about how the palette was generated
5. A preview image showing the palette colors

## Integration with Other Services

The palette service integrates with:

1. **JigsawStack API**: For AI-powered palette generation
2. **Image Processing Service**: For applying palettes to images
3. **Concept Service**: For creating complete concepts with palettes

## Usage Examples

### Generating Palettes from a Theme

```python
from app.services.concept.palette import PaletteGenerator
from app.services.jigsawstack.client import JigsawStackClient

# Create the generator
client = JigsawStackClient(api_key="your_api_key")
palette_generator = PaletteGenerator(client)

# Generate multiple palettes
palettes = await palette_generator.generate_palettes(
    theme_description="A modern tech company with blue and gray tones",
    count=3
)

# Access the palette colors
for palette in palettes:
    print(f"Palette: {palette.name}")
    for color in palette.colors:
        print(f"- {color.name}: {color.hex}")
```

### Applying a Palette to an Image

```python
# Assume we have an image and a palette
with open("original_image.png", "rb") as f:
    image_data = f.read()

# Apply the first palette to the image
transformed_image = await palette_generator.apply_palette_to_image(
    image_data=image_data,
    palette=palettes[0]
)

# Save the transformed image
with open("transformed_image.png", "wb") as f:
    f.write(transformed_image)
```

## Error Handling

The palette service implements comprehensive error handling:

1. **Connection Errors**: Errors connecting to the JigsawStack API
2. **Processing Errors**: Errors processing images or applying palettes
3. **Validation Errors**: Errors validating palette data structures

## Performance Considerations

- Palette generation is performed asynchronously to avoid blocking
- Multiple palettes can be generated in parallel for efficiency
- Image transformation is optimized for memory usage and speed

## Related Documentation

- [Concept Service](service.md): Main concept service that uses the palette generator
- [Concept Generation](generation.md): Details on concept image generation
- [Image Processing](../image/processing.md): Details on image transformation techniques
- [JigsawStack Client](../jigsawstack/client.md): Client for the external AI service
- [Palette Models](../../models/concept/domain.md): Data models for palette data structures 