# Service Layer Design Document

## Current Context

- The service layer sits between the API routes and external service clients
- It orchestrates the business logic for concept generation and refinement
- Two primary services are needed: concept generation and color palette generation

## Requirements

### Functional Requirements

- Orchestrate the generation of visual concepts using the JigsawStack API
- Generate color palettes based on theme descriptions
- Support refinement of existing concepts with additional details
- Validate inputs before passing to external services
- Properly handle and transform API responses

### Non-Functional Requirements

- Maintain separation of concerns between API and external services
- Ensure testability through proper dependency injection
- Implement appropriate error handling and logging
- Ensure type safety through proper annotations
- Optimize for performance and resource utilization

## Design Decisions

### 1. Service Architecture

Will implement a service-oriented architecture with:

- Services as classes with specific responsibilities
- Dependency injection for external clients
- Clear interfaces between components
- Stateless service implementation

### 2. Concept Service Design

Will implement the concept service with:

- Combined coordination of image and color palette generation
- Proper error handling and retries
- Caching for improved performance
- Asynchronous operations for non-blocking execution

### 3. Color Palette Generation

Will implement color palette generation using:

- JigsawStack Text Generation API as the primary method
- Structured prompting for consistent results
- Parsing and validation of generated responses
- Fallback mechanisms for handling errors

## Technical Design

### 1. Concept Service

```python
# backend/app/services/concept_service.py
from typing import Dict, List, Any, Optional
import logging
import uuid
import json
from ..models.response import ColorPalette, GenerationResponse
from .jigsawstack import create_image_client, create_text_client
from ..core.exceptions import AppException

class ConceptService:
    """Service for generating and refining concepts."""

    def __init__(self):
        """Initialize the concept service."""
        self.logger = logging.getLogger("concept_service")
        self.image_client = create_image_client()
        self.text_client = create_text_client()

        # In-memory cache for original prompts
        # In a production environment, this would be replaced with a database
        self._prompt_cache = {}

    async def generate_concept(
        self,
        logo_description: str,
        theme_description: str
    ) -> GenerationResponse:
        """Generate a new concept based on text descriptions.

        Args:
            logo_description: Description of the logo to generate
            theme_description: Description of the theme/style for color palettes

        Returns:
            GenerationResponse containing image URL and color palettes

        Raises:
            AppException: On generation failure
        """
        self.logger.info(f"Generating concept for logo: {logo_description[:50]}...")

        # Generate a unique ID for this prompt
        prompt_id = str(uuid.uuid4())

        try:
            # Generate image based on logo description
            image_response = await self.image_client.generate_image(
                prompt=logo_description,
                aspect_ratio="1:1",
                steps=30
            )

            # Extract image URL from response
            image_url = image_response.get("image_url")
            if not image_url:
                raise AppException(
                    status_code=500,
                    detail="Failed to generate image: No image URL in response"
                )

            # Generate color palettes based on theme description
            color_palettes = await self._generate_color_palettes(theme_description)

            # Store the original prompt information for potential refinement
            self._prompt_cache[prompt_id] = {
                "logo_description": logo_description,
                "theme_description": theme_description
            }

            # Construct and return the response
            return GenerationResponse(
                prompt_id=prompt_id,
                image_url=image_url,
                color_palettes=color_palettes
            )

        except Exception as e:
            self.logger.error(f"Error generating concept: {str(e)}")
            raise AppException(
                status_code=500,
                detail=f"Failed to generate concept: {str(e)}"
            )

    async def refine_concept(
        self,
        original_prompt_id: str,
        additional_details: str
    ) -> GenerationResponse:
        """Refine an existing concept with additional details.

        Args:
            original_prompt_id: ID of the original prompt to refine
            additional_details: Additional details to refine the concept

        Returns:
            GenerationResponse containing refined image URL and color palettes

        Raises:
            ValueError: If original prompt ID is not found
            AppException: On refinement failure
        """
        self.logger.info(f"Refining concept {original_prompt_id} with: {additional_details[:50]}...")

        # Check if original prompt exists
        original_prompt = self._prompt_cache.get(original_prompt_id)
        if not original_prompt:
            raise ValueError(f"Original prompt ID not found: {original_prompt_id}")

        try:
            # Combine original descriptions with additional details
            refined_logo_description = (
                f"{original_prompt['logo_description']}. "
                f"Additional details: {additional_details}"
            )

            refined_theme_description = (
                f"{original_prompt['theme_description']}. "
                f"Additional details: {additional_details}"
            )

            # Generate refined image
            image_response = await self.image_client.generate_image(
                prompt=refined_logo_description,
                aspect_ratio="1:1",
                steps=30
            )

            # Extract image URL from response
            image_url = image_response.get("image_url")
            if not image_url:
                raise AppException(
                    status_code=500,
                    detail="Failed to generate refined image: No image URL in response"
                )

            # Generate refined color palettes
            color_palettes = await self._generate_color_palettes(refined_theme_description)

            # Generate a new prompt ID for the refinement
            new_prompt_id = str(uuid.uuid4())

            # Store the refined prompt information
            self._prompt_cache[new_prompt_id] = {
                "logo_description": refined_logo_description,
                "theme_description": refined_theme_description,
                "original_prompt_id": original_prompt_id
            }

            # Construct and return the response
            return GenerationResponse(
                prompt_id=new_prompt_id,
                image_url=image_url,
                color_palettes=color_palettes
            )

        except Exception as e:
            self.logger.error(f"Error refining concept: {str(e)}")
            raise AppException(
                status_code=500,
                detail=f"Failed to refine concept: {str(e)}"
            )

    async def _generate_color_palettes(self, theme_description: str) -> List[ColorPalette]:
        """Generate color palettes based on theme description.

        Args:
            theme_description: Description of the theme/style for color palettes

        Returns:
            List of ColorPalette objects

        Raises:
            AppException: On palette generation failure
        """
        try:
            # Construct a prompt for color palette generation
            palette_prompt = f"""Generate 3 different color palettes in hex code format for: {theme_description}
            For each palette provide:
            1. A descriptive name (2-3 words)
            2. 5 hex color codes
            3. A one-sentence explanation of how it relates to the theme
            Format as JSON: [{{name: string, colors: string[], description: string}}]"""

            # Generate text using JigsawStack Text API
            palette_response = await self.text_client.generate_text(
                prompt=palette_prompt,
                format="json"
            )

            # Extract and parse the generated text
            generated_text = palette_response.get("generated_text")
            if not generated_text:
                raise AppException(
                    status_code=500,
                    detail="Failed to generate color palettes: No text in response"
                )

            # Parse the JSON response
            return self._parse_color_palette_response(generated_text)

        except Exception as e:
            self.logger.error(f"Error generating color palettes: {str(e)}")
            raise AppException(
                status_code=500,
                detail=f"Failed to generate color palettes: {str(e)}"
            )

    def _parse_color_palette_response(self, response_text: str) -> List[ColorPalette]:
        """Parse the color palette response from JigsawStack.

        Args:
            response_text: The generated text containing color palettes

        Returns:
            List of ColorPalette objects

        Raises:
            ValueError: If response cannot be parsed
        """
        try:
            # Use json.loads to parse the response
            palettes_data = json.loads(response_text)

            # Validate and convert to ColorPalette objects
            result = []
            for palette_data in palettes_data:
                # Validate required fields
                if not isinstance(palette_data, dict):
                    continue

                if "name" not in palette_data or "colors" not in palette_data:
                    continue

                if not isinstance(palette_data["colors"], list):
                    continue

                # Create ColorPalette object
                palette = ColorPalette(
                    name=palette_data["name"],
                    colors=palette_data["colors"],
                    description=palette_data.get("description")
                )

                result.append(palette)

            # Ensure we have at least one valid palette
            if not result:
                raise ValueError("No valid color palettes found in response")

            return result

        except json.JSONDecodeError:
            # Handle the case where the response is not valid JSON
            self.logger.error(f"Failed to parse color palette response: {response_text[:100]}")
            raise ValueError("Color palette response is not valid JSON")

        except Exception as e:
            self.logger.error(f"Error parsing color palette response: {str(e)}")
            raise ValueError(f"Failed to parse color palette response: {str(e)}")
```

### 2. Factory Method

```python
# backend/app/services/__init__.py
from .concept_service import ConceptService

def create_concept_service() -> ConceptService:
    """Create a new instance of the ConceptService.

    Returns:
        ConceptService instance
    """
    return ConceptService()
```

### 3. Dependency Injection for FastAPI

```python
# backend/app/api/dependencies.py
from fastapi import Depends
from ..services import create_concept_service
from ..services.concept_service import ConceptService

def get_concept_service() -> ConceptService:
    """Dependency for injecting the ConceptService into routes.

    Returns:
        ConceptService instance
    """
    return create_concept_service()
```

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_services/test_concept_service.py
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import json
from app.services.concept_service import ConceptService
from app.models.response import ColorPalette
from app.core.exceptions import AppException

@pytest.fixture
def concept_service():
    """Fixture for creating a ConceptService with mocked clients."""
    service = ConceptService()
    service.image_client = MagicMock()
    service.text_client = MagicMock()
    return service

@pytest.mark.asyncio
async def test_generate_concept_success(concept_service):
    # Mock image client response
    image_response = {"image_url": "https://example.com/image.png"}
    concept_service.image_client.generate_image = AsyncMock(return_value=image_response)

    # Mock text client response
    palette_data = [
        {
            "name": "Test Palette",
            "colors": ["#000000", "#FFFFFF", "#FF0000", "#00FF00", "#0000FF"],
            "description": "Test description"
        }
    ]
    palette_response = {"generated_text": json.dumps(palette_data)}
    concept_service.text_client.generate_text = AsyncMock(return_value=palette_response)

    # Call the method
    result = await concept_service.generate_concept(
        logo_description="Test logo",
        theme_description="Test theme"
    )

    # Assertions
    assert result.image_url == "https://example.com/image.png"
    assert len(result.color_palettes) == 1
    assert result.color_palettes[0].name == "Test Palette"
    assert len(result.color_palettes[0].colors) == 5
    assert result.prompt_id is not None

@pytest.mark.asyncio
async def test_generate_concept_image_failure(concept_service):
    # Mock image client to raise an exception
    concept_service.image_client.generate_image = AsyncMock(side_effect=Exception("Test error"))

    # Call the method and expect an exception
    with pytest.raises(AppException) as excinfo:
        await concept_service.generate_concept(
            logo_description="Test logo",
            theme_description="Test theme"
        )

    # Assertions
    assert "Failed to generate concept" in str(excinfo.value.detail)
    assert excinfo.value.status_code == 500

@pytest.mark.asyncio
async def test_parse_color_palette_response(concept_service):
    # Valid JSON input
    valid_json = json.dumps([
        {
            "name": "Ocean Blue",
            "colors": ["#001F3F", "#0074D9", "#7FDBFF", "#39CCCC", "#FFFFFF"],
            "description": "Cool and calming blue tones"
        }
    ])

    # Call the method
    result = concept_service._parse_color_palette_response(valid_json)

    # Assertions
    assert len(result) == 1
    assert isinstance(result[0], ColorPalette)
    assert result[0].name == "Ocean Blue"
    assert len(result[0].colors) == 5
    assert result[0].description == "Cool and calming blue tones"

    # Invalid JSON input
    with pytest.raises(ValueError):
        concept_service._parse_color_palette_response("not valid json")
```

## Service Integration

The following diagram illustrates how the service layer integrates with the rest of the application:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│   API Routes    │─────▶│  Service Layer  │─────▶│ External Clients│
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
       │                        │                        │
       │                        │                        │
       ▼                        ▼                        ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  Request Models │      │ Business Logic  │      │   JigsawStack   │
│                 │      │                 │      │      APIs       │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                │
                                │
                                ▼
                         ┌─────────────────┐
                         │                 │
                         │ Response Models │
                         │                 │
                         └─────────────────┘
```

## Future Considerations

### Potential Enhancements

- Implement a proper persistence layer for storing prompts and generated concepts
- Add background job processing for long-running generations
- Support for additional types of visual concepts beyond logos
- Implement more sophisticated color palette generation algorithms
- Add user preferences and history tracking

### Known Limitations

- In-memory cache is not suitable for production use
- Limited error recovery mechanisms
- No retry policy for transient errors
- Limited validation of generated content

## Dependencies

### Runtime Dependencies

- Python 3.9+
- FastAPI (for integration with API layer)
- Pydantic (for data validation)
- JigsawStack client (for external API interactions)
- UUID (for generating unique identifiers)
- JSON (for parsing responses)

### Development Dependencies

- Pytest (for testing)
- Pytest-asyncio (for testing async functions)
- Mock (for mocking dependencies in tests)

## Security Considerations

- No sensitive information is stored in-memory
- Input validation before sending to external services
- Error messages do not expose sensitive information
- Proper exception handling for expected error cases

## Logging Strategy

- Service-level logging for tracking operations
- Redaction of sensitive information in logs
- Structured logging for machine processing
- Appropriate log levels for different operations

## References

- [JigsawStack API Documentation](https://jigsawstack.com/docs/)
- [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [Python AsyncIO](https://docs.python.org/3/library/asyncio.html)
