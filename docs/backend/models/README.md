# Models Documentation

The Models module contains data structures used throughout the Concept Visualizer application, primarily implemented using Pydantic models for validation and serialization.

## Structure

- [Common](common/README.md): Base models and shared data structures
- [Concept](concept/README.md): Models related to concept generation and refinement
- [Export](export/README.md): Models for export functionality
- [Task](task/README.md): Models for background task handling

## Key Features

- **Type Safety**: All models use Python type hints for improved developer experience
- **Validation**: Input validation through Pydantic
- **Documentation**: Automatic OpenAPI schema generation
- **JSON Serialization**: Consistent serialization/deserialization
- **Domain Organization**: Models are organized by domain and feature

## Model Types

The application uses different types of models:

1. **Request Models**: Validate incoming API requests
2. **Response Models**: Define API response structures
3. **Domain Models**: Represent core business entities
4. **Internal Models**: Used for internal data processing

## Example Usage

```python
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Request model
class ConceptRequest(BaseModel):
    prompt: str = Field(..., min_length=10, max_length=1000)
    style: Optional[str] = Field(None, examples=["minimal", "vibrant", "dark"])
    
    class Config:
        schema_extra = {
            "example": {
                "prompt": "A logo for a coffee shop called 'Morning Brew'",
                "style": "minimal"
            }
        }

# Domain model
class Concept:
    id: str
    prompt: str
    image_url: str
    created_at: datetime
    
    # Domain logic methods
    def is_recent(self) -> bool:
        return (datetime.now() - self.created_at).days < 7 