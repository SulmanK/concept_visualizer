# JigsawStack Client

The `client.py` module provides a low-level HTTP client for interacting with the JigsawStack API in the Concept Visualizer backend.

## Overview

The JigsawStack Client is responsible for:

1. Making direct HTTP requests to the JigsawStack API
2. Handling authentication with API keys
3. Processing API responses and errors
4. Managing binary data for image generation/refinement
5. Providing specialized endpoints for concept visualization

This client handles the complexities of the raw API, including enhancing prompts for better logo generation, handling binary data, and translating API errors into application-specific exceptions.

## JigsawStackClient Class

```python
class JigsawStackClient:
    """Client for interacting with JigsawStack API for concept generation and refinement."""

    def __init__(self, api_key: str, api_url: str):
        """
        Initialize the JigsawStack API client.

        Args:
            api_key: The API key for authentication
            api_url: The base URL for the JigsawStack API
        """
        self.api_key = api_key
        self.api_url = api_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "x-api-key": api_key  # Some endpoints use x-api-key instead of Authorization
        }
        logger.info(f"Initialized JigsawStack client with API URL: {api_url}")
```

## Key Operations

### Image Generation

```python
async def generate_image(
    self,
    prompt: str,
    width: int = 512,
    height: int = 512,
    model: str = "stable-diffusion-xl"
) -> Dict[str, str]:
    """
    Generate an image using the JigsawStack API.

    Args:
        prompt: The text prompt for image generation
        width: The width of the generated image
        height: The height of the generated image
        model: The model to use for generation

    Returns:
        Dictionary containing image URL and ID

    Raises:
        JigsawStackConnectionError: If connection to the API fails
        JigsawStackAuthenticationError: If authentication fails
        JigsawStackGenerationError: If the image generation fails
    """
    # Implementation details...
```

This method:

- Enhances logo prompts with specific design requirements
- Determines appropriate aspect ratio based on dimensions
- Uses negative prompts to avoid common issues in logo design
- Handles both JSON and binary response formats
- Provides detailed error handling

### Image Refinement

```python
async def refine_image(
    self,
    prompt: str,
    image_url: str,
    strength: float = 0.7,
    model: str = "stable-diffusion-xl"
) -> Dict[str, str]:
    """
    Refine an existing image using the JigsawStack API.

    Args:
        prompt: The refinement prompt
        image_url: URL of the image to refine
        strength: How much to change the original (0.0-1.0)
        model: Model to use for refinement

    Returns:
        Dictionary containing refined image URL and ID

    Raises:
        JigsawStackConnectionError: If connection to the API fails
        JigsawStackAuthenticationError: If authentication fails
        JigsawStackGenerationError: If the refinement fails
    """
    # Implementation details...
```

### Color Palette Generation

```python
async def generate_color_palettes(
    self,
    prompt: str,
    num_palettes: int = 5
) -> List[Dict[str, Any]]:
    """
    Generate color palettes using the JigsawStack API.

    Args:
        prompt: The prompt describing the desired color theme
        num_palettes: Number of palettes to generate

    Returns:
        List of palette dictionaries

    Raises:
        JigsawStackGenerationError: If palette generation fails
    """
    # Implementation details...
```

This specialized method:

- Formats the prompt for palette generation
- Validates the returned palettes for consistency
- Includes fallback to default palettes if generation fails
- Ensures each palette has a complete set of colors

### Advanced Operations

The client also includes several advanced operations:

```python
async def get_variation(self, image_url: str, model: str = "stable-diffusion-xl") -> bytes:
    """Generate a variation of an existing image."""
    # Implementation details...

async def generate_image_with_palette(
    self,
    logo_prompt: str,
    palette: List[str],
    palette_name: str = "",
    width: int = 512,
    height: int = 512
) -> bytes:
    """Generate an image using a specific color palette."""
    # Implementation details...
```

These advanced methods enable specialized workflows like:

- Creating variations of successful concepts
- Generating concepts with pre-selected color palettes
- Themed concept generation

## Helper Methods

The client includes several helper methods to process data:

```python
def _process_palette_colors(self, palette: Dict[str, Any]) -> Dict[str, Any]:
    """Process and normalize palette colors."""
    # Implementation details...

def _validate_and_clean_palettes(self, palettes: List[Dict[str, Any]], num_palettes: int, prompt: str) -> List[Dict[str, Any]]:
    """Validate and clean up generated palettes."""
    # Implementation details...

def _get_default_palettes(self, num_palettes: int, prompt: str) -> List[Dict[str, Any]]:
    """Get default palettes when generation fails."""
    # Implementation details...
```

## Client Factory

A factory function simplifies client creation:

```python
@lru_cache()
def get_jigsawstack_client() -> JigsawStackClient:
    """
    Get a singleton instance of the JigsawStackClient.

    Returns:
        JigsawStackClient: Client for JigsawStack API operations
    """
    # Implementation details...
```

## Typed Structures

The client uses TypedDict for precise typing of structures:

```python
class PaletteColor(TypedDict):
    """Color definition with hex value and name."""
    hex: str
    name: str

class Palette(TypedDict):
    """Color palette definition."""
    name: str
    description: str
    colors: List[PaletteColor]

class GenerationResponse(TypedDict):
    """Response from image generation API."""
    url: str  # URL to the generated image
    id: str   # Image ID
```

## Error Handling

The client uses specialized exceptions for different error cases:

```python
# Connection failures
raise JigsawStackConnectionError(
    message=f"Failed to connect to JigsawStack API: {str(e)}",
    details={"endpoint": endpoint}
)

# Authentication issues
raise JigsawStackAuthenticationError(
    message="Authentication failed with JigsawStack API",
    details={"status_code": response.status_code}
)

# Generation failures
raise JigsawStackGenerationError(
    message="Image generation failed",
    content_type="image",
    prompt=prompt,
    details={
        "status_code": response.status_code,
        "endpoint": endpoint,
        "response_content": str(response.content[:100])
    }
)
```

## Usage Examples

The client is typically used through the higher-level JigsawStackService, but can be used directly:

```python
# Create a client instance
client = JigsawStackClient(
    api_key=settings.JIGSAWSTACK_API_KEY,
    api_url=settings.JIGSAWSTACK_API_URL
)

# Generate an image
result = await client.generate_image(
    prompt="A minimalist logo for a tech startup called 'Horizon'",
    width=512,
    height=512
)

# Process the result
image_url = result["url"]
```

## Security Considerations

The client implements several security measures:

1. **API Key Protection**: Never logs API keys
2. **Prompt Privacy**: Avoids logging full prompts which might contain sensitive data
3. **Response Truncation**: Limits response content in error logs
4. **Error Details**: Provides enough detail for debugging without exposing sensitive information

## Related Documentation

- [JigsawStack Service](service.md): Higher-level service that uses this client
- [JigsawStack Interface](interface.md): Interface for the service layer
- [Core Exceptions](../../core/exceptions.md): Domain-specific exceptions used by this client
- [Configuration](../../core/config.md): Application settings for JigsawStack integration
