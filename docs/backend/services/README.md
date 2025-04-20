# Services Documentation

The Services module contains the business logic and external service integrations for the Concept Visualizer application. Services implement the core functionality of the application.

## Structure

- [Concept](concept/README.md): Services for concept generation and refinement
- [Export](export/README.md): Services for exporting concepts
- [Image](image/README.md): Services for image processing and conversion
- [JigsawStack](jigsawstack/README.md): Integration with the JigsawStack API
- [Persistence](persistence/README.md): Services for data persistence
- [Task](task/README.md): Background task processing services

## Architecture

The Services layer follows these principles:

1. **Interface Abstraction**: Services define interfaces to allow for implementation swapping and testing
2. **Dependency Inversion**: Services depend on abstractions, not concrete implementations
3. **Single Responsibility**: Each service has a clear, well-defined responsibility
4. **Testability**: Services are designed to be easily testable

## Service Types

The application uses different types of services:

1. **Domain Services**: Implement core business logic
2. **Integration Services**: Interface with external APIs and services
3. **Infrastructure Services**: Provide infrastructure capabilities (persistence, caching, etc.)

## Example Usage

```python
from fastapi import Depends
from app.services.concept.interface import ConceptServiceInterface
from app.services.concept.service import ConceptService
from app.services.jigsawstack.service import JigsawStackService

# Service implementation
class ConceptService(ConceptServiceInterface):
    def __init__(
        self, 
        image_service: JigsawStackService = Depends()
    ):
        self.image_service = image_service
    
    async def generate_concept(self, prompt: str):
        # Business logic for concept generation
        image_url = await self.image_service.generate_image(prompt)
        
        # More business logic...
        return {
            "prompt": prompt,
            "image_url": image_url
        }

# Usage in API route
@router.post("/generate")
async def generate_concept(
    request: ConceptRequest,
    service: ConceptServiceInterface = Depends(ConceptService)
):
    return await service.generate_concept(request.prompt)
``` 