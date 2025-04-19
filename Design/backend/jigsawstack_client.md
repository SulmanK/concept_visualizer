# JigsawStack Client Design Document

## Current Context
- The Concept Visualizer application requires integration with JigsawStack's APIs
- Two primary JigsawStack services will be used: Image Generation and Text Generation
- A clean, well-structured client is needed to abstract API interactions

## Requirements

### Functional Requirements
- Create an abstraction layer for interacting with JigsawStack APIs
- Support image generation for logo creation
- Support text generation for color palette creation
- Handle API authentication securely
- Process both successful responses and error scenarios
- Support async operation to prevent blocking

### Non-Functional Requirements
- Maintainable and extensible client architecture
- Comprehensive error handling and logging
- Configurable request parameters
- Rate limiting awareness
- Type safety through proper annotations

## Design Decisions

### 1. Client Structure
Will implement a modular JigsawStack client with:
- Core client class that handles authentication and shared logic
- Specialized modules for different API endpoints
- Dependency injection for testing and configuration

### 2. API Authentication
Will implement authentication using:
- API key stored in environment variables
- Centralized auth header generation
- No hardcoded credentials in code

### 3. Error Handling
Will implement robust error handling with:
- Custom exception classes for different error types
- Retry mechanism for transient errors
- Detailed error logging with context
- User-friendly error messages

## Technical Design

### 1. Core Components

```python
# backend/app/services/jigsawstack/client.py
from typing import Dict, Any, Optional, Union
import logging
import aiohttp
import json
from ...core.config import settings
from ...core.exceptions import (
    JigsawStackAPIError,
    JigsawStackConnectionError,
    JigsawStackAuthenticationError
)

class JigsawStackClient:
    """Base client for JigsawStack API interactions."""
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        base_url: str = "https://api.jigsawstack.com",
        timeout: int = 30,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize the JigsawStack client.
        
        Args:
            api_key: JigsawStack API key for authentication
            base_url: Base URL for the JigsawStack API
            timeout: Request timeout in seconds
            logger: Optional logger instance
        """
        self.api_key = api_key or settings.JIGSAWSTACK_API_KEY
        if not self.api_key:
            raise ValueError("JigsawStack API key is required")
            
        self.base_url = base_url
        self.timeout = timeout
        self.logger = logger or logging.getLogger("jigsawstack")
        
    async def _request(
        self, 
        method: str, 
        endpoint: str, 
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """Make a request to the JigsawStack API.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            data: Request payload
            params: Query parameters
            headers: Additional headers
            
        Returns:
            API response data
            
        Raises:
            JigsawStackConnectionError: Connection issues
            JigsawStackAuthenticationError: Authentication failures
            JigsawStackAPIError: API errors
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        default_headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if headers:
            default_headers.update(headers)
            
        try:
            async with aiohttp.ClientSession() as session:
                async with session.request(
                    method=method,
                    url=url,
                    json=data if method.upper() != "GET" else None,
                    params=params,
                    headers=default_headers,
                    timeout=self.timeout
                ) as response:
                    response_text = await response.text()
                    
                    try:
                        response_data = json.loads(response_text)
                    except json.JSONDecodeError:
                        response_data = {"raw_response": response_text}
                    
                    if response.status >= 400:
                        self._handle_error_response(response.status, response_data)
                    
                    return response_data
                    
        except aiohttp.ClientError as e:
            self.logger.error(f"Connection error: {str(e)}")
            raise JigsawStackConnectionError(f"Failed to connect to JigsawStack API: {str(e)}")
            
    def _handle_error_response(self, status_code: int, response_data: Dict[str, Any]) -> None:
        """Handle error responses from the API.
        
        Args:
            status_code: HTTP status code
            response_data: Response data
            
        Raises:
            JigsawStackAuthenticationError: For authentication issues
            JigsawStackAPIError: For other API errors
        """
        error_message = response_data.get("error", {}).get("message", "Unknown error")
        
        if status_code == 401:
            self.logger.error(f"Authentication error: {error_message}")
            raise JigsawStackAuthenticationError(f"Authentication failed: {error_message}")
        else:
            self.logger.error(f"API error ({status_code}): {error_message}")
            raise JigsawStackAPIError(
                message=error_message,
                status_code=status_code,
                response=response_data
            )
```

### 2. Image Generation Client

```python
# backend/app/services/jigsawstack/image.py
from typing import Dict, Any, Optional, List, Union
import logging
from .client import JigsawStackClient

class ImageGenerationClient:
    """Client for JigsawStack's Image Generation API."""
    
    def __init__(self, client: Optional[JigsawStackClient] = None):
        """Initialize the Image Generation client.
        
        Args:
            client: JigsawStackClient instance or None to create a new one
        """
        self.client = client or JigsawStackClient()
        self.logger = logging.getLogger("jigsawstack.image")
        
    async def generate_image(
        self,
        prompt: str,
        aspect_ratio: str = "1:1",
        width: Optional[int] = None,
        height: Optional[int] = None,
        steps: int = 30,
        negative_prompt: Optional[str] = None,
        guidance: Optional[float] = None,
        seed: Optional[int] = None
    ) -> Dict[str, Any]:
        """Generate an image based on the provided prompt.
        
        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Aspect ratio of the image (e.g., "1:1", "16:9")
            width: Width of the image in pixels (256-1920)
            height: Height of the image in pixels (256-1920)
            steps: Number of denoising steps (1-90)
            negative_prompt: Text describing what should not be in the image
            guidance: Controls how closely model follows prompt (1-28)
            seed: For deterministic generation
            
        Returns:
            Response containing image URL and metadata
        """
        payload = {
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "steps": steps
        }
        
        # Add optional parameters if provided
        if width:
            payload["width"] = width
            
        if height:
            payload["height"] = height
            
        # Add advanced configuration
        advance_config = {}
        
        if negative_prompt:
            advance_config["negative_prompt"] = negative_prompt
            
        if guidance:
            advance_config["guidance"] = guidance
            
        if seed:
            advance_config["seed"] = seed
            
        if advance_config:
            payload["advance_config"] = advance_config
            
        self.logger.info(f"Generating image with prompt: {prompt[:100]}...")
        
        response = await self.client._request(
            method="POST",
            endpoint="/v1/images/generate",
            data=payload
        )
        
        return response
```

### 3. Text Generation Client

```python
# backend/app/services/jigsawstack/text.py
from typing import Dict, Any, Optional, List, Union
import logging
from .client import JigsawStackClient

class TextGenerationClient:
    """Client for JigsawStack's Text Generation API."""
    
    def __init__(self, client: Optional[JigsawStackClient] = None):
        """Initialize the Text Generation client.
        
        Args:
            client: JigsawStackClient instance or None to create a new one
        """
        self.client = client or JigsawStackClient()
        self.logger = logging.getLogger("jigsawstack.text")
        
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 2000,
        temperature: float = 0.7,
        format: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Generate text based on the provided prompt.
        
        Args:
            prompt: Text prompt for generation
            max_tokens: Maximum number of tokens to generate
            temperature: Controls randomness (0-1)
            format: Optional format for the response (e.g., "json")
            stream: Whether to stream the response
            
        Returns:
            Response containing generated text
        """
        payload = {
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": stream
        }
        
        if format:
            payload["format"] = format
            
        self.logger.info(f"Generating text with prompt: {prompt[:100]}...")
        
        response = await self.client._request(
            method="POST",
            endpoint="/v1/text/generate",
            data=payload
        )
        
        return response
```

### 4. Factory Method

```python
# backend/app/services/jigsawstack/__init__.py
from typing import Optional
from .client import JigsawStackClient
from .image import ImageGenerationClient
from .text import TextGenerationClient

def create_jigsawstack_client(api_key: Optional[str] = None) -> JigsawStackClient:
    """Create a new JigsawStack client with the provided API key.
    
    Args:
        api_key: JigsawStack API key
        
    Returns:
        JigsawStackClient instance
    """
    return JigsawStackClient(api_key=api_key)

def create_image_client(client: Optional[JigsawStackClient] = None) -> ImageGenerationClient:
    """Create a new Image Generation client.
    
    Args:
        client: Optional JigsawStackClient to use
        
    Returns:
        ImageGenerationClient instance
    """
    return ImageGenerationClient(client=client)

def create_text_client(client: Optional[JigsawStackClient] = None) -> TextGenerationClient:
    """Create a new Text Generation client.
    
    Args:
        client: Optional JigsawStackClient to use
        
    Returns:
        TextGenerationClient instance
    """
    return TextGenerationClient(client=client)
```

## Integration Example

```python
# Example usage in a service
from ...services.jigsawstack import create_image_client, create_text_client

async def generate_concept(logo_description: str, theme_description: str):
    # Create clients
    image_client = create_image_client()
    text_client = create_text_client()
    
    # Generate image based on logo description
    image_response = await image_client.generate_image(
        prompt=logo_description,
        aspect_ratio="1:1",
        steps=30
    )
    
    # Generate color palettes based on theme description
    palette_prompt = f"""Generate 3 different color palettes in hex code format for: {theme_description}
    For each palette provide:
    1. A descriptive name (2-3 words)
    2. 5 hex color codes
    3. A one-sentence explanation of how it relates to the theme
    Format as JSON: [{{name: string, colors: string[], description: string}}]"""
    
    palette_response = await text_client.generate_text(
        prompt=palette_prompt,
        format="json"
    )
    
    return {
        "image_url": image_response.get("image_url"),
        "color_palettes": palette_response.get("generated_text")
    }
```

## Error Handling

```python
# backend/app/core/exceptions.py
from typing import Dict, Any, Optional

class JigsawStackError(Exception):
    """Base exception for JigsawStack-related errors."""
    pass

class JigsawStackConnectionError(JigsawStackError):
    """Raised when there's an issue connecting to the JigsawStack API."""
    pass

class JigsawStackAuthenticationError(JigsawStackError):
    """Raised when there's an authentication issue with the JigsawStack API."""
    pass

class JigsawStackAPIError(JigsawStackError):
    """Raised when the JigsawStack API returns an error."""
    
    def __init__(
        self, 
        message: str,
        status_code: Optional[int] = None,
        response: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.response = response
        super().__init__(message)
```

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_services/test_jigsawstack/test_client.py
import pytest
from unittest.mock import patch, AsyncMock
from app.services.jigsawstack.client import JigsawStackClient
from app.core.exceptions import JigsawStackAPIError, JigsawStackAuthenticationError

@pytest.mark.asyncio
async def test_request_success():
    client = JigsawStackClient(api_key="test_key")
    
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text.return_value = '{"result": "success"}'
        mock_request.return_value.__aenter__.return_value = mock_response
        
        result = await client._request("GET", "/test")
        
        assert result == {"result": "success"}
        mock_request.assert_called_once()

@pytest.mark.asyncio
async def test_request_auth_error():
    client = JigsawStackClient(api_key="invalid_key")
    
    with patch("aiohttp.ClientSession.request", new_callable=AsyncMock) as mock_request:
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text.return_value = '{"error": {"message": "Invalid API key"}}'
        mock_request.return_value.__aenter__.return_value = mock_response
        
        with pytest.raises(JigsawStackAuthenticationError):
            await client._request("GET", "/test")
```

## Future Considerations

### Potential Enhancements
- Implement caching for repeated requests
- Add support for streaming responses (for large generations)
- Support batch processing for multiple generations
- Add parameter validation before sending requests

### Known Limitations
- Limited error handling for specific API errors
- No implemented rate limiting protection
- Dependency on aiohttp for HTTP requests

## Dependencies

### Runtime Dependencies
- Python 3.9+
- aiohttp
- pydantic
- python-dotenv
- FastAPI (for integration)

### Development Dependencies
- pytest
- pytest-asyncio
- aioresponses (for mocking HTTP requests)

## Security Considerations
- API keys stored in environment variables
- No hardcoded credentials
- HTTPS for all API communications
- Logging sanitization for sensitive data

## References
- [JigsawStack API Documentation](https://jigsawstack.com/docs)
- [aiohttp Documentation](https://docs.aiohttp.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/) 