# Concept Request Models

This documentation covers the request models used in concept-related API endpoints.

## Overview

The `request.py` module in `app/models/concept/` defines Pydantic models for validating requests to concept generation and refinement endpoints. These models ensure that all required fields are present and that they meet validation criteria before processing by the application.

## Models

### PromptRequest

```python
class PromptRequest(APIBaseModel):
    """Request model for concept generation."""

    logo_description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Description of the logo to generate"
    )
    theme_description: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Description of the theme/color scheme to generate"
    )
```

This model is used for concept generation requests and requires two fields:

- `logo_description`: A string between 5-500 characters describing the logo to generate
- `theme_description`: A string between 5-500 characters describing the theme or color scheme to generate

#### Usage Example

```json
{
  "logo_description": "A modern, minimalist logo for a tech startup called 'Neuron'. The logo should incorporate abstract neural network imagery.",
  "theme_description": "Modern tech aesthetic with blues and purples. Clean, professional look suitable for a cutting-edge AI company."
}
```

### RefinementRequest

```python
class RefinementRequest(APIBaseModel):
    """Request model for concept refinement."""

    original_image_url: HttpUrl = Field(
        ...,
        description="URL of the original image to refine"
    )
    logo_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Updated description of the logo"
    )
    theme_description: Optional[str] = Field(
        None,
        min_length=5,
        max_length=500,
        description="Updated description of the theme/color scheme"
    )
    refinement_prompt: str = Field(
        ...,
        min_length=5,
        max_length=500,
        description="Specific instructions for refinement"
    )
    preserve_aspects: List[str] = Field(
        default=[],
        description="Aspects of the original design to preserve"
    )
```

This model is used for concept refinement requests and includes:

- `original_image_url`: A valid HTTP URL pointing to the image to be refined
- `logo_description`: (Optional) An updated description of the logo, between 5-500 characters
- `theme_description`: (Optional) An updated description of the theme/color scheme, between 5-500 characters
- `refinement_prompt`: Specific refinement instructions, between 5-500 characters
- `preserve_aspects`: (Optional) A list of aspects to preserve from the original design (valid values: "colors", "layout", "style", "shapes")

The `preserve_aspects` field has a custom validator that ensures only valid values are provided.

#### Usage Example

```json
{
  "original_image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "refinement_prompt": "Make the logo more minimalist and use lighter shades of blue",
  "logo_description": "A modern tech logo for 'Neuron' with simplified neural network imagery",
  "theme_description": "Modern tech aesthetic with lighter blues and subtle accents",
  "preserve_aspects": ["layout", "style"]
}
```

## Validation

Both models extend `APIBaseModel`, which includes common validation and serialization logic for API models. Specific validations include:

1. **Field Requirements**: Required fields must be provided
2. **String Length**: Text fields have minimum and maximum length requirements
3. **URL Validation**: The `original_image_url` must be a valid HTTP URL
4. **Preserve Aspects**: When specified, must be from the predefined list of valid values

## Related Files

- [Response Models](response.md): Models for structuring API responses
- [Domain Models](domain.md): Core domain models for concepts
- [Base Models](../common/base.md): Common base models and utilities
