# Data Models Design Document

## Current Context
- The Concept Visualizer requires well-defined data models for request/response handling
- Pydantic will be used for data validation and serialization
- Models must support both API interactions and internal data flow

## Requirements

### Functional Requirements
- Define data structures for API requests and responses
- Provide validation for user inputs
- Ensure proper serialization/deserialization of data
- Support documentation through OpenAPI schema
- Represent internal data structures for business logic

### Non-Functional Requirements
- Type safety through proper annotations
- Self-documenting code with clear field descriptions
- Consistent naming conventions
- Performance optimization for serialization/deserialization
- Maintainability through proper organization

## Design Decisions

### 1. Model Organization
Will organize models into logical categories:
- Request models for API inputs
- Response models for API outputs
- Internal models for service layer

### 2. Validation Strategy
Will implement validation using:
- Field constraints (min/max length, regex patterns)
- Field descriptions for documentation
- Example values for API documentation
- Custom validators where needed

### 3. Serialization Strategy
Will implement serialization using:
- Pydantic's built-in JSON serialization
- Custom serializers for complex types
- Configuration for controlling output format

## Technical Design

### 1. Request Models

```python
# backend/app/models/request.py
from pydantic import BaseModel, Field
from typing import Optional

class PromptRequest(BaseModel):
    """Request model for generating a concept."""
    
    logo_description: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Description of the logo to generate"
    )
    
    theme_description: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Description of the theme/style for color palettes"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "logo_description": "A modern tech startup logo with abstract geometric shapes",
                "theme_description": "Professional corporate theme with a touch of creativity"
            }
        }
        
class RefinementRequest(BaseModel):
    """Request model for refining an existing concept."""
    
    original_prompt_id: str = Field(
        ...,
        description="ID of the original prompt to refine"
    )
    
    additional_details: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Additional details to refine the concept"
    )
    
    class Config:
        schema_extra = {
            "example": {
                "original_prompt_id": "abc123",
                "additional_details": "Make the logo more minimalist and use blue tones"
            }
        }
```

### 2. Response Models

```python
# backend/app/models/response.py
from pydantic import BaseModel, Field
from typing import List, Optional

class ColorPalette(BaseModel):
    """Model for a color palette."""
    
    name: str = Field(..., description="Name of the color palette")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the color palette")
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Ocean Breeze",
                "colors": ["#1A535C", "#4ECDC4", "#F7FFF7", "#FF6B6B", "#FFE66D"],
                "description": "Fresh and calming palette inspired by coastal scenes"
            }
        }

class GenerationResponse(BaseModel):
    """Response model for concept generation/refinement."""
    
    prompt_id: str = Field(..., description="Unique identifier for the prompt")
    image_url: str = Field(..., description="URL of the generated image")
    color_palettes: List[ColorPalette] = Field(..., description="Generated color palettes")
    
    class Config:
        schema_extra = {
            "example": {
                "prompt_id": "abc123",
                "image_url": "https://example.com/images/abc123.png",
                "color_palettes": [
                    {
                        "name": "Corporate Trust",
                        "colors": ["#0A1128", "#001F54", "#034078", "#1282A2", "#FEFCFB"],
                        "description": "Professional palette with reliable blue tones"
                    }
                ]
            }
        }

class HealthResponse(BaseModel):
    """Response model for health check."""
    
    status: str = Field(..., description="API status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Deployment environment")
    
    class Config:
        schema_extra = {
            "example": {
                "status": "ok",
                "version": "0.1.0",
                "environment": "development"
            }
        }

class ErrorResponse(BaseModel):
    """Response model for error responses."""
    
    detail: str = Field(..., description="Error message")
    
    class Config:
        schema_extra = {
            "example": {
                "detail": "Failed to generate concept: Internal server error"
            }
        }
```

### 3. Internal Models

```python
# backend/app/models/internal.py
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
import re

class StoredPrompt(BaseModel):
    """Internal model for storing prompt information."""
    
    logo_description: str
    theme_description: str
    original_prompt_id: Optional[str] = None
    
class HexColor(str):
    """Custom type for validating hex color codes."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
        
    @classmethod
    def validate(cls, v):
        if not isinstance(v, str):
            raise TypeError("string required")
            
        # Check if it's a valid hex color code
        if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", v):
            raise ValueError("invalid hex color format")
            
        return v
        
class ValidatedColorPalette(BaseModel):
    """Internal model for color palette with validation."""
    
    name: str
    colors: List[HexColor]
    description: Optional[str] = None
    
    @validator("colors")
    def validate_colors_count(cls, v):
        if len(v) < 3 or len(v) > 10:
            raise ValueError("color palette must have between 3 and 10 colors")
        return v
        
    class Config:
        json_encoders = {
            HexColor: lambda v: str(v)
        }
```

### 4. Model Integration with FastAPI

```python
# Example usage in API routes
from fastapi import APIRouter, Depends, HTTPException
from ..models.request import PromptRequest
from ..models.response import GenerationResponse

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(request: PromptRequest):
    """
    Generate a new concept based on text descriptions.
    
    This endpoint takes a logo description and theme description,
    and returns a generated image and color palettes.
    """
    # Implementation...
    pass
```

### 5. Example Model Validation

```python
# Example of how validation works
from pydantic import ValidationError
from app.models.request import PromptRequest

try:
    # This will fail validation due to short logo_description
    prompt = PromptRequest(
        logo_description="", 
        theme_description="Professional theme"
    )
except ValidationError as e:
    print(e.json())
    # {
    #   "type": "value_error.any_str.min_length",
    #   "loc": ["logo_description"],
    #   "msg": "ensure this value has at least 3 characters",
    #   "input": "",
    #   "ctx": {"limit_value": 3}
    # }
```

### 6. JSON Schema Generation

Pydantic models automatically generate JSON Schema, which FastAPI uses for documentation:

```python
from app.models.response import GenerationResponse
import json

# Get the JSON schema for the model
schema = GenerationResponse.schema_json(indent=2)
print(schema)
# {
#   "title": "GenerationResponse",
#   "description": "Response model for concept generation/refinement.",
#   "type": "object",
#   "properties": {
#     "prompt_id": {
#       "title": "Prompt Id",
#       "description": "Unique identifier for the prompt",
#       "type": "string"
#     },
#     "image_url": {
#       "title": "Image Url",
#       "description": "URL of the generated image",
#       "type": "string"
#     },
#     "color_palettes": {
#       "title": "Color Palettes",
#       "description": "Generated color palettes",
#       "type": "array",
#       "items": {"$ref": "#/definitions/ColorPalette"}
#     }
#   },
#   "required": ["prompt_id", "image_url", "color_palettes"],
#   "definitions": {
#     "ColorPalette": {
#       "title": "ColorPalette",
#       "description": "Model for a color palette.",
#       "type": "object",
#       "properties": {
#         "name": {
#           "title": "Name",
#           "description": "Name of the color palette",
#           "type": "string"
#         },
#         "colors": {
#           "title": "Colors",
#           "description": "List of hex color codes",
#           "type": "array",
#           "items": {"type": "string"}
#         },
#         "description": {
#           "title": "Description",
#           "description": "Description of the color palette",
#           "type": "string"
#         }
#       },
#       "required": ["name", "colors"]
#     }
#   }
# }
```

## Data Flow Diagram

The following diagram illustrates how data models flow through the application:

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│   API Client    │─────▶│ Request Models  │─────▶│  API Routes     │
│   (Frontend)    │      │ (Validation)    │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                          │
                                                          │
                                                          ▼
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│   API Client    │◀─────│ Response Models │◀─────│  Service Layer  │
│   (Frontend)    │      │ (Serialization) │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                          │
                                                          │
                                                          ▼
                                               ┌─────────────────┐
                                               │                 │
                                               │ Internal Models │
                                               │                 │
                                               └─────────────────┘
```

## Testing Strategy

### Unit Tests

```python
# backend/tests/test_models/test_request_models.py
import pytest
from pydantic import ValidationError
from app.models.request import PromptRequest, RefinementRequest

def test_prompt_request_validation():
    # Valid data
    valid_data = {
        "logo_description": "A modern tech startup logo",
        "theme_description": "Professional corporate theme"
    }
    
    prompt = PromptRequest(**valid_data)
    assert prompt.logo_description == valid_data["logo_description"]
    assert prompt.theme_description == valid_data["theme_description"]
    
    # Invalid data: logo_description too short
    invalid_data = {
        "logo_description": "Ab",  # Too short
        "theme_description": "Professional corporate theme"
    }
    
    with pytest.raises(ValidationError) as excinfo:
        PromptRequest(**invalid_data)
    
    errors = excinfo.value.errors()
    assert any(e["loc"][0] == "logo_description" for e in errors)
    
def test_refinement_request_validation():
    # Valid data
    valid_data = {
        "original_prompt_id": "abc123",
        "additional_details": "Make it more blue"
    }
    
    refinement = RefinementRequest(**valid_data)
    assert refinement.original_prompt_id == valid_data["original_prompt_id"]
    assert refinement.additional_details == valid_data["additional_details"]
```

## Future Considerations

### Potential Enhancements
- Add versioning to models for API evolution
- Implement caching for frequently used models
- Support additional color formats (RGB, HSL)
- Add more sophisticated validation for color harmony
- Implement serialization optimizations for large responses

### Known Limitations
- Limited validation for creative inputs
- No localization support for error messages
- Simple in-memory storage of prompts
- No persistence of models across application restarts

## Dependencies

### Runtime Dependencies
- Pydantic (for model validation and serialization)
- FastAPI (for API schema generation)
- typing_extensions (for advanced type annotations)

### Development Dependencies
- Pytest (for testing)
- JSON Schema validator (for schema validation)

## References
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [FastAPI Schema Documentation](https://fastapi.tiangolo.com/tutorial/schema/)
- [JSON Schema](https://json-schema.org/) 