# Concept Response Models

This documentation covers the response models used in concept-related API endpoints.

## Overview

The `response.py` module in `app/models/concept/` defines Pydantic models for structuring responses from concept generation and refinement endpoints. These models ensure consistent and well-structured responses to clients.

## Models

### ColorPalette

```python
class ColorPalette(APIBaseModel):
    """Color palette model containing hex color codes."""
    
    primary: str = Field(..., description="Primary brand color")
    secondary: str = Field(..., description="Secondary brand color")
    accent: str = Field(..., description="Accent color")
    background: str = Field(..., description="Background color")
    text: str = Field(..., description="Text color")
    additional_colors: List[str] = Field(
        default=[],
        description="Additional color options"
    )
```

This model represents a color palette with standard brand color roles:

- `primary`: The primary brand color (hex code)
- `secondary`: The secondary brand color (hex code)
- `accent`: An accent color for highlighting (hex code)
- `background`: The background color (hex code)
- `text`: The text color (hex code)
- `additional_colors`: Optional list of additional colors (hex codes)

### PaletteVariation

```python
class PaletteVariation(APIBaseModel):
    """Model for a color palette variation with its own image."""
    
    name: str = Field(..., alias="palette_name", description="Name of the palette variation")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_url: HttpUrl = Field(..., description="URL of the image with this palette")
```

This model represents a variation of a concept with a different color palette:

- `name`: Name of the palette variation (aliased as `palette_name` in JSON)
- `colors`: List of hex color codes in the palette
- `description`: Optional description of the palette
- `image_url`: URL of the concept image rendered with this palette

### GenerationResponse

```python
class GenerationResponse(APIBaseModel):
    """Response model for concept generation and refinement."""
    
    prompt_id: str = Field(..., description="Unique ID for the generation")
    logo_description: str = Field(..., description="The logo description prompt")
    theme_description: str = Field(..., description="The theme description prompt")
    created_at: str = Field(..., description="Creation timestamp")
    
    # For backward compatibility - points to the first variation
    image_url: HttpUrl = Field(..., description="URL of the default generated image")
    color_palette: Optional[ColorPalette] = Field(
        None,
        description="Generated color palette (deprecated format, kept for backward compatibility)"
    )
    
    # New field for multiple variations
    variations: List[PaletteVariation] = Field(
        default=[],
        description="List of palette variations with distinct images"
    )
    
    # Optional fields for refinement responses
    original_image_url: Optional[HttpUrl] = Field(
        None,
        description="URL of the original image (for refinements)"
    )
    refinement_prompt: Optional[str] = Field(
        None,
        description="Prompt used for refinement"
    )
```

This model represents the response from concept generation:

- `prompt_id`: Unique identifier for the generation
- `logo_description`: The original logo description prompt
- `theme_description`: The original theme description prompt
- `created_at`: Timestamp when the concept was created
- `image_url`: URL of the default generated image (for backward compatibility)
- `color_palette`: Optional color palette in the deprecated format
- `variations`: List of palette variations with distinct images
- `original_image_url`: Optional URL of the original image (for refinements)
- `refinement_prompt`: Optional prompt used for refinement

### RefinementResponse

```python
class RefinementResponse(GenerationResponse):
    """Response model specifically for concept refinement."""
    
    original_image_url: HttpUrl = Field(..., description="URL of the original image that was refined")
    refinement_prompt: str = Field(..., description="Prompt used for refinement")
    original_concept_id: Optional[str] = Field(None, description="ID of the original concept")
```

This model extends `GenerationResponse` with additional fields specific to refinement:

- `original_image_url`: URL of the original image that was refined (required in this model)
- `refinement_prompt`: The prompt used for refinement (required in this model)
- `original_concept_id`: Optional ID of the original concept

### ConceptSummary

```python
class ConceptSummary(APIBaseModel):
    """Summary information about a concept for list views."""
    
    id: str = Field(..., description="Unique concept ID")
    created_at: str = Field(..., description="Creation timestamp")
    logo_description: str = Field(..., description="The logo description prompt")
    theme_description: str = Field(..., description="The theme description prompt")
    image_url: HttpUrl = Field(..., description="URL of the concept image")
    has_variations: bool = Field(default=True, description="Whether the concept has color variations")
    variations_count: int = Field(default=0, description="Number of available color variations")
    is_refinement: bool = Field(default=False, description="Whether this is a refinement of another concept")
    original_concept_id: Optional[str] = Field(None, description="ID of the original concept if this is a refinement")
    color_variations: List[PaletteVariation] = Field(
        default=[],
        description="List of all color variations with their images"
    )
```

This model provides summary information about a concept for list views:

- `id`: Unique concept identifier
- `created_at`: Timestamp when the concept was created
- `logo_description`: The logo description prompt
- `theme_description`: The theme description prompt 
- `image_url`: URL of the default concept image
- `has_variations`: Whether the concept has color variations
- `variations_count`: Number of available color variations
- `is_refinement`: Whether this is a refinement of another concept
- `original_concept_id`: ID of the original concept if this is a refinement
- `color_variations`: List of color variations with their images

### ConceptDetail

```python
class ConceptDetail(ConceptSummary):
    """Detailed information about a concept including all variations."""
    
    variations: List[PaletteVariation] = Field(
        default=[],
        description="List of all color variations with their images"
    )
    refinement_prompt: Optional[str] = Field(None, description="Prompt used for refinement, if applicable")
    original_image_url: Optional[HttpUrl] = Field(None, description="URL of the original image, if this is a refinement")
```

This model extends `ConceptSummary` with additional details:

- `variations`: List of all palette variations with their images
- `refinement_prompt`: Prompt used for refinement, if applicable
- `original_image_url`: URL of the original image, if this is a refinement

## Usage Examples

### Example Generation Response

```json
{
  "prompt_id": "concept-1234-5678-9012",
  "logo_description": "A modern, minimalist logo for a tech startup called 'Neuron'",
  "theme_description": "Modern tech aesthetic with blues and purples",
  "created_at": "2023-01-01T12:00:00.123456",
  "image_url": "https://storage.example.com/concepts/concept-1234-main.png",
  "variations": [
    {
      "palette_name": "Tech Blue",
      "colors": ["#1E3A8A", "#3B82F6", "#93C5FD", "#DBEAFE", "#F1F5F9"],
      "description": "Professional blue palette with technical feel",
      "image_url": "https://storage.example.com/concepts/concept-1234-var1.png"
    },
    {
      "palette_name": "Purple Fusion",
      "colors": ["#4C1D95", "#8B5CF6", "#C4B5FD", "#EDE9FE", "#F5F3FF"],
      "description": "Bold purple palette with creative energy",
      "image_url": "https://storage.example.com/concepts/concept-1234-var2.png"
    }
  ]
}
```

### Example Refinement Response

```json
{
  "prompt_id": "concept-2345-6789-0123",
  "logo_description": "A modern tech logo for 'Neuron' with simplified neural network imagery",
  "theme_description": "Modern tech aesthetic with lighter blues and subtle accents",
  "created_at": "2023-01-02T12:00:00.123456",
  "image_url": "https://storage.example.com/concepts/concept-2345-main.png",
  "variations": [
    {
      "palette_name": "Light Tech",
      "colors": ["#2563EB", "#60A5FA", "#BFDBFE", "#EFF6FF", "#F8FAFC"],
      "description": "Lighter blue palette with minimal contrast",
      "image_url": "https://storage.example.com/concepts/concept-2345-var1.png"
    }
  ],
  "original_image_url": "https://storage.example.com/concepts/concept-1234-main.png",
  "refinement_prompt": "Make the logo more minimalist and use lighter shades of blue",
  "original_concept_id": "concept-1234-5678-9012"
}
```

## Related Files

- [Request Models](request.md): Models for validating API requests
- [Domain Models](domain.md): Core domain models for concepts
- [Base Models](../common/base.md): Common base models and utilities 