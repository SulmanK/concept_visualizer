# JigsawStack Service

The `service.py` module provides the implementation of the JigsawStack service interface for the Concept Visualizer API.

## Overview

The JigsawStack Service is a mid-level service that:

1. Wraps the lower-level JigsawStackClient
2. Adds business logic and error handling
3. Follows the JigsawStackServiceInterface contract
4. Provides a simplified API for image generation and refinement

This implementation serves as a bridge between the raw API functionality and the application's business requirements.

## JigsawStackService Class

```python
class JigsawStackService(JigsawStackServiceInterface):
    """Service for JigsawStack API operations."""

    def __init__(self, client: JigsawStackClient):
        """
        Initialize the JigsawStack service.

        Args:
            client: The JigsawStackClient for API interactions
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
```

## Key Implementations

### Image Generation

```python
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
    try:
        # Log only the length of the prompt to avoid exposing sensitive data
        self.logger.info(f"Generating image with prompt length: {len(prompt)}")

        # Use the client to generate the image
        result = await self.client.generate_image(
            prompt=prompt,
            width=width,
            height=height,
            model=model
        )

        self.logger.info("Image generation successful")
        return result

    except JigsawStackError as e:
        # Already a specific JigsawStack error, just re-raise
        self.logger.error(f"JigsawStack error during image generation: {str(e)}")
        raise
    except Exception as e:
        # Unexpected error, wrap in a generic JigsawStackGenerationError
        self.logger.error(f"Unexpected error during image generation: {str(e)}")
        raise JigsawStackGenerationError(
            message=f"Unexpected error during image generation: {str(e)}",
            content_type="image",
            prompt=prompt
        )
```

The service handles:

- Privacy by not logging the full prompt content
- Standard error handling for expected errors
- Wrapping unexpected errors in domain-specific exceptions
- Delegating the actual API calls to the client

### Image Refinement

```python
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
    # Implementation follows similar pattern to generate_image
```

### Color Palette Generation

```python
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
    # Implementation follows similar pattern to generate_image
```

## Service Factory

A factory function is provided to simplify dependency injection:

```python
@lru_cache()
def get_jigsawstack_service() -> JigsawStackService:
    """
    Get a singleton instance of the JigsawStackService.

    Returns:
        JigsawStackService: Service for JigsawStack operations
    """
    api_key = settings.JIGSAWSTACK_API_KEY
    api_url = settings.JIGSAWSTACK_API_URL

    if not api_key or not api_url:
        raise ValueError("JigsawStack API key and URL must be provided in settings")

    # Create the client and service
    client = JigsawStackClient(api_key=api_key, api_url=api_url)
    return JigsawStackService(client=client)
```

This function:

- Uses LRU caching to create a singleton instance
- Validates required configuration
- Creates the client with appropriate credentials
- Wraps the client in the service

## Error Handling Strategy

The service employs a consistent error handling strategy:

1. **Log appropriately**: Log errors at the right level but avoid sensitive data
2. **Preserve specific errors**: Pass through domain-specific errors
3. **Wrap general errors**: Convert general errors to domain-specific ones
4. **Provide context**: Include relevant context in error details

This approach ensures that errors are:

- Properly categorized for the caller
- Well-documented for troubleshooting
- Secure (not leaking sensitive information)
- Consistent across the application

## Usage Examples

### In Concept Generation

```python
# In concept generation service
async def generate_concept(self, logo_description: str, theme_description: str):
    # Generate the base image
    image_result = await self.jigsawstack_service.generate_image(
        prompt=logo_description,
        width=512,
        height=512
    )

    # Generate color palettes
    palettes = await self.jigsawstack_service.generate_color_palettes(
        prompt=f"{logo_description} {theme_description}",
        num_palettes=5
    )

    # Return the concept
    return {
        "image_url": image_result["url"],
        "palettes": palettes
    }
```

### In Concept Refinement

```python
# In concept refinement service
async def refine_concept(self, concept_id: str, refinement_prompt: str):
    # Get the original concept
    original_concept = await self.persistence_service.get_concept(concept_id)

    # Refine the image
    refined_image = await self.jigsawstack_service.refine_image(
        prompt=refinement_prompt,
        image_url=original_concept["image_url"],
        strength=0.7
    )

    # Return the refined concept
    return {
        "original_image_url": original_concept["image_url"],
        "refined_image_url": refined_image["url"]
    }
```

## Related Documentation

- [JigsawStack Interface](interface.md): Interface implemented by this service
- [JigsawStack Client](client.md): Lower-level client used by this service
- [Concept Generation Service](../concept/generation.md): Service that uses this implementation
- [Core Exceptions](../../core/exceptions.md): Domain-specific exceptions used by this service
