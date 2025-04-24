# JigsawStack Client Refactoring Design Document

## Problem Statement

The current JigsawStack client module (`app/services/jigsawstack/client.py`) has grown to over 850 lines of code with multiple responsibilities:

1. Authentication and request handling
2. Image generation and refinement
3. Color palette generation and processing
4. Error handling and logging

This violates the Single Responsibility Principle and makes the code difficult to maintain, test, and extend. The large file size also makes it challenging to understand the client's capabilities and proper usage patterns.

## Goals

1. Split the monolithic client into smaller, purpose-specific client modules
2. Improve separation of concerns
3. Enhance testability with smaller, focused components
4. Create clear interfaces for each client type
5. Maintain backward compatibility with existing service users
6. Reduce code duplication across client methods
7. Improve error handling consistency

## Design

### 1. Overall Architecture

The refactored design will use a composition-based approach with the following components:

```
app/services/jigsawstack/
├── __init__.py                 # Export factory functions and classes
├── base.py                     # Base client with common functionality
├── image.py                    # Image generation/refinement client
├── palette.py                  # Color palette generation client
├── interfaces.py               # Client interfaces
├── utils.py                    # Shared utilities
├── exceptions.py               # Client-specific exceptions
└── factory.py                  # Factory functions for clients
```

### 2. Component Descriptions

#### 2.1 Base Client (`base.py`)

The `BaseJigsawClient` will provide:

- Authentication handling
- Common HTTP request methods
- Rate limiting and retry logic
- Basic error handling
- Logging setup

```python
class BaseJigsawClient:
    """Base client for JigsawStack API with common functionality."""

    def __init__(self, api_key: str, api_url: str):
        """Initialize the client with API credentials."""
        self.api_key = api_key
        self.api_url = api_url
        self.headers = self._get_default_headers()
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests."""
        # Implementation...

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> httpx.Response:
        """Make an HTTP request to the JigsawStack API."""
        # Implementation...
```

#### 2.2 Image Client (`image.py`)

The `JigsawImageClient` will provide:

- Image generation
- Image refinement
- Image variation
- Palette-based image creation
- Binary data handling for images

```python
class JigsawImageClient(BaseJigsawClient):
    """Client for JigsawStack image generation and manipulation."""

    async def generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "stable-diffusion-xl"
    ) -> Dict[str, str]:
        """Generate an image based on a text prompt."""
        # Implementation...

    async def refine_image(
        self,
        prompt: str,
        image_url: str,
        strength: float = 0.7,
        model: str = "stable-diffusion-xl"
    ) -> bytes:
        """Refine an existing image using a text prompt."""
        # Implementation...

    # Other image-related methods...
```

#### 2.3 Palette Client (`palette.py`)

The `JigsawPaletteClient` will provide:

- Color palette generation
- Palette validation and processing
- Default/fallback palette handling

```python
class JigsawPaletteClient(BaseJigsawClient):
    """Client for JigsawStack color palette generation."""

    async def generate_multiple_palettes(
        self,
        logo_description: str,
        theme_description: str,
        num_palettes: int = 7
    ) -> List[Dict[str, Any]]:
        """Generate multiple color palettes based on descriptions."""
        # Implementation...

    # Other palette-related methods...
```

#### 2.4 Interfaces (`interfaces.py`)

Define clear interfaces using Protocol classes to support dependency injection and testing:

```python
class JigsawImageClientProtocol(Protocol):
    """Interface for JigsawStack image client."""

    async def generate_image(
        self,
        prompt: str,
        width: int = 512,
        height: int = 512,
        model: str = "stable-diffusion-xl"
    ) -> Dict[str, str]: ...

    # Other method signatures...

class JigsawPaletteClientProtocol(Protocol):
    """Interface for JigsawStack palette client."""

    async def generate_multiple_palettes(
        self,
        logo_description: str,
        theme_description: str,
        num_palettes: int = 7
    ) -> List[Dict[str, Any]]: ...

    # Other method signatures...
```

#### 2.5 Factory Functions (`factory.py`)

Create factory functions to instantiate clients:

```python
@lru_cache()
def get_jigsawstack_image_client() -> JigsawImageClientProtocol:
    """Factory function for JigsawImageClient instances."""
    return JigsawImageClient(
        api_key=settings.JIGSAWSTACK_API_KEY,
        api_url=settings.JIGSAWSTACK_API_URL
    )

@lru_cache()
def get_jigsawstack_palette_client() -> JigsawPaletteClientProtocol:
    """Factory function for JigsawPaletteClient instances."""
    return JigsawPaletteClient(
        api_key=settings.JIGSAWSTACK_API_KEY,
        api_url=settings.JIGSAWSTACK_API_URL
    )

# Legacy support
@lru_cache()
def get_jigsawstack_client() -> JigsawStackClient:
    """Factory function for the original combined client (for backward compatibility)."""
    return JigsawStackClient(
        api_key=settings.JIGSAWSTACK_API_KEY,
        api_url=settings.JIGSAWSTACK_API_URL
    )
```

### 3. Backward Compatibility

To ensure backward compatibility, we will:

1. Keep the current `JigsawStackClient` class and factory function
2. Refactor `JigsawStackClient` to use composition with the new specialized clients
3. Update the documentation to encourage using the new specialized clients

```python
class JigsawStackClient:
    """Legacy client for JigsawStack API (uses composition with specialized clients)."""

    def __init__(self, api_key: str, api_url: str):
        """Initialize the client with API credentials."""
        self.api_key = api_key
        self.api_url = api_url
        self._image_client = JigsawImageClient(api_key, api_url)
        self._palette_client = JigsawPaletteClient(api_key, api_url)
        # ... other initialization

    # Delegate to specialized clients
    async def generate_image(self, *args, **kwargs):
        """Generate an image. Delegates to image client."""
        return await self._image_client.generate_image(*args, **kwargs)

    async def generate_multiple_palettes(self, *args, **kwargs):
        """Generate palettes. Delegates to palette client."""
        return await self._palette_client.generate_multiple_palettes(*args, **kwargs)

    # ... other delegated methods
```

## Implementation Plan

### Phase 1: Infrastructure

1. Create the new directory structure
2. Implement `interfaces.py` with Protocol classes
3. Implement `base.py` with the base client
4. Create utility functions in `utils.py`

### Phase 2: Specialized Clients

1. Implement `image.py` with the image client
2. Implement `palette.py` with the palette client
3. Create factory functions in `factory.py`

### Phase 3: Legacy Support

1. Refactor `JigsawStackClient` to use composition
2. Update `__init__.py` to export all clients and factories
3. Add deprecation warnings to legacy methods

### Phase 4: Service Updates

1. Update service dependencies to use specialized clients
2. Update tests to use the new client interfaces
3. Add new tests for the specialized clients

## Testing Strategy

1. Create unit tests for each client class with mocked HTTP responses
2. Create integration tests against a mock JigsawStack API
3. Test backwards compatibility with existing code
4. Test error scenarios and edge cases
5. Verify performance is equivalent or improved

## Risks and Mitigations

1. **Risk**: Breaking changes affecting production
   **Mitigation**: Maintain backward compatibility and extensive testing

2. **Risk**: Overhead from additional classes
   **Mitigation**: Careful design to minimize duplication

3. **Risk**: Inconsistent behavior between old and new implementations
   **Mitigation**: Thorough validation and test coverage

## Future Extensions

After this refactoring, we can:

1. Add more specialized clients as needed (e.g., text generation)
2. Implement advanced features like request batching
3. Add caching for frequently used responses
4. Create more sophisticated error handling and retries

## Timeline

- Phase 1 (Infrastructure): 1 day
- Phase 2 (Specialized Clients): 2 days
- Phase 3 (Legacy Support): 1 day
- Phase 4 (Service Updates): 1 day
- Testing: 1 day

Total: 6 days
