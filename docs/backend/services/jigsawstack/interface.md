# JigsawStack Service Interface

The `interface.py` module defines the interface for services that interact with the JigsawStack API in the Concept Visualizer backend.

## Overview

This interface establishes a contract for services that:

1. Generate images based on text prompts
2. Refine existing images with new prompts
3. Generate color palettes based on text descriptions

By defining this interface, the application can:

- Maintain separation between API implementation details and business logic
- Swap implementations for testing or future API changes
- Establish clear boundaries for what the service provides

## JigsawStackServiceInterface

```python
class JigsawStackServiceInterface(abc.ABC):
    """Interface for JigsawStack API operations."""

    @abc.abstractmethod
    async def generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "stable-diffusion-xl"
    ) -> Dict[str, Any]:
        """Generate an image based on a prompt."""
        pass

    # Other abstract methods...
```

## Key Operations

### Image Generation

```python
@abc.abstractmethod
async def generate_image(
    self,
    prompt: str,
    width: int = 512,
    height: int = 512,
    model: str = "stable-diffusion-xl"
) -> Dict[str, Any]:
    """
    Generate an image based on a prompt.

    Args:
        prompt: The image generation prompt
        width: Width of the generated image
        height: Height of the generated image
        model: Model to use for generation

    Returns:
        Dictionary containing image URL and/or binary data

    Raises:
        JigsawStackGenerationError: If generation fails
    """
    pass
```

This method defines the contract for generating a new image from a text prompt.

### Image Refinement

```python
@abc.abstractmethod
async def refine_image(
    self,
    prompt: str,
    image_url: str,
    strength: float = 0.7,
    model: str = "stable-diffusion-xl"
) -> Dict[str, Any]:
    """
    Refine an existing image based on a prompt.

    Args:
        prompt: The refinement prompt
        image_url: URL of the original image
        strength: How much to change the original (0.0-1.0)
        model: Model to use for refinement

    Returns:
        Dictionary containing refined image URL and/or binary data

    Raises:
        JigsawStackGenerationError: If refinement fails
    """
    pass
```

This method defines how to refine an existing image with a new prompt, maintaining some aspects of the original image.

### Color Palette Generation

```python
@abc.abstractmethod
async def generate_color_palettes(
    self,
    prompt: str,
    num_palettes: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate color palettes based on a prompt.

    Args:
        prompt: The color palette generation prompt
        num_palettes: Number of palettes to generate

    Returns:
        List of palette dictionaries

    Raises:
        JigsawStackGenerationError: If palette generation fails
    """
    pass
```

This method establishes how to generate color palettes that match a text description.

## Expected Return Structures

### Image Generation/Refinement Response

```python
{
    "url": "https://api.jigsawstack.com/path/to/image.png",
    "id": "img_123456789"
}
```

### Color Palette Response

```python
[
    {
        "name": "Ocean Breeze",
        "description": "A calming palette inspired by coastal waters",
        "colors": [
            {"hex": "#1a535c", "name": "Deep Ocean Blue"},
            {"hex": "#4ecdc4", "name": "Aqua"},
            {"hex": "#f7fff7", "name": "Sea Foam"},
            {"hex": "#ff6b6b", "name": "Coral"},
            {"hex": "#ffe66d", "name": "Sandy Beach"}
        ]
    },
    # Additional palettes...
]
```

## Error Handling

Implementations of this interface should raise appropriate exceptions:

```python
# For connection issues
raise JigsawStackConnectionError(
    message="Failed to connect to JigsawStack API",
    details={"endpoint": endpoint}
)

# For generation failures
raise JigsawStackGenerationError(
    message="Failed to generate image",
    content_type="image",
    prompt=prompt,
    details={"status_code": 500}
)
```

## Usage in Dependency Injection

This interface is typically used with FastAPI's dependency injection:

```python
# In a concept generation API endpoint
@router.post("/generate", response_model=ConceptResponse)
async def generate_concept(
    request: ConceptRequest,
    jigsawstack_service: JigsawStackServiceInterface = Depends(get_jigsawstack_service)
):
    # Use the service through its interface
    image_result = await jigsawstack_service.generate_image(
        prompt=request.logo_description,
        width=512,
        height=512
    )

    # Process the result
    return {"image_url": image_result["url"], ...}
```

## Related Documentation

- [JigsawStack Service](service.md): Implementation of this interface
- [JigsawStack Client](client.md): Lower-level client used by the service
- [Concept Service](../concept/service.md): Higher-level service that uses this service
