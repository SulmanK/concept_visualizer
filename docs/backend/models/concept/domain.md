# Concept Domain Models

This documentation covers the domain models used for concept-related data structures.

## Overview

The `domain.py` module in `app/models/concept/` defines the core Pydantic models for concepts, color palettes, and related data structures used within the application domain. These models represent the internal data structures used by services and persistence layers, as opposed to the request/response models used at API boundaries.

## Models

### ColorPalette

```python
class ColorPalette(APIBaseModel):
    """Model for a color palette."""
    
    name: str = Field(..., description="Name of the palette")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_url: Optional[str] = Field(None, description="URL to the palette image")
    image_path: Optional[str] = Field(None, description="Storage path for the palette image")
```

This model represents a color palette for concepts:

- `name`: Name of the palette (e.g., "Ocean Blue", "Forest Green")
- `colors`: List of hex color codes in the palette
- `description`: Optional description of the palette
- `image_url`: Optional public URL to the palette image
- `image_path`: Optional storage path for the palette image in the storage system

### ConceptSummary

```python
class ConceptSummary(APIBaseModel):
    """Model for a concept summary (used in list views)."""
    
    id: uuid.UUID = Field(..., description="Unique identifier for the concept")
    created_at: datetime = Field(..., description="Creation timestamp")
    logo_description: str = Field(..., description="Description of the logo")
    theme_description: str = Field(..., description="Description of the theme/color scheme")
    image_url: str = Field(..., description="URL to the concept image")
    image_path: str = Field(..., description="Storage path for the concept image")
    color_variations: List[ColorPalette] = Field(..., description="Color variations for this concept")
```

This model provides summary information about a concept (typically used in list views):

- `id`: Unique UUID identifier for the concept
- `created_at`: Timestamp when the concept was created
- `logo_description`: The description of the logo
- `theme_description`: The description of the theme/color scheme
- `image_url`: Public URL to the concept image
- `image_path`: Storage path for the concept image
- `color_variations`: List of color palette variations for this concept

### ConceptDetail

```python
class ConceptDetail(APIBaseModel):
    """Model for detailed concept information."""
    
    id: uuid.UUID = Field(..., description="Unique identifier for the concept")
    created_at: datetime = Field(..., description="Creation timestamp")
    session_id: uuid.UUID = Field(..., description="ID of the session that created this concept")
    logo_description: str = Field(..., description="Description of the logo")
    theme_description: str = Field(..., description="Description of the theme/color scheme")
    image_url: str = Field(..., description="URL to the concept image")
    image_path: str = Field(..., description="Storage path for the concept image")
    color_variations: List[ColorPalette] = Field(..., description="Color variations for this concept")
```

This model provides detailed information about a concept:

- `id`: Unique UUID identifier for the concept
- `created_at`: Timestamp when the concept was created
- `session_id`: UUID of the session that created this concept
- `logo_description`: The description of the logo
- `theme_description`: The description of the theme/color scheme
- `image_url`: Public URL to the concept image
- `image_path`: Storage path for the concept image
- `color_variations`: List of color palette variations for this concept

### ConceptCreate

```python
class ConceptCreate(APIBaseModel):
    """Model for creating a new concept."""
    
    session_id: uuid.UUID = Field(..., description="ID of the session creating this concept")
    logo_description: str = Field(..., description="Description of the logo")
    theme_description: str = Field(..., description="Description of the theme/color scheme")
    image_path: str = Field(..., description="Storage path for the concept image")
    image_url: Optional[str] = Field(None, description="URL to the concept image")
```

This model is used when creating a new concept in the system:

- `session_id`: UUID of the session creating this concept
- `logo_description`: The description of the logo
- `theme_description`: The description of the theme/color scheme
- `image_path`: Storage path for the concept image
- `image_url`: Optional public URL to the concept image (may be generated after creation)

### ColorVariationCreate

```python
class ColorVariationCreate(APIBaseModel):
    """Model for creating a new color variation."""
    
    concept_id: uuid.UUID = Field(..., description="ID of the concept this variation belongs to")
    palette_name: str = Field(..., description="Name of the palette")
    colors: List[str] = Field(..., description="List of hex color codes")
    description: Optional[str] = Field(None, description="Description of the palette")
    image_path: str = Field(..., description="Storage path for the variation image") 
    image_url: Optional[str] = Field(None, description="URL to the variation image")
```

This model is used when creating a new color variation for an existing concept:

- `concept_id`: UUID of the concept this variation belongs to
- `palette_name`: Name of the palette
- `colors`: List of hex color codes in the palette
- `description`: Optional description of the palette
- `image_path`: Storage path for the variation image
- `image_url`: Optional public URL to the variation image (may be generated after creation)

## Usage within the Application

Domain models are used internally by services and persistence layers. They differ from request/response models in several ways:

1. They include internal fields like `image_path` that aren't exposed in API responses
2. They use proper UUID and datetime types instead of strings
3. They represent the complete data structure as stored in the database
4. They don't include presentation-specific fields or aliases

### Example Service Usage

```python
async def create_concept(
    logo_description: str,
    theme_description: str,
    session_id: uuid.UUID,
    image_path: str
) -> ConceptDetail:
    """Create a new concept and store it."""
    
    # Create the concept record
    concept_create = ConceptCreate(
        session_id=session_id,
        logo_description=logo_description,
        theme_description=theme_description,
        image_path=image_path
    )
    
    # Store it in the database and get back the full record
    concept = await concept_repository.create(concept_create)
    
    # Return as a domain model
    return ConceptDetail(
        id=concept.id,
        created_at=concept.created_at,
        session_id=concept.session_id,
        logo_description=concept.logo_description,
        theme_description=concept.theme_description,
        image_url=concept.image_url,
        image_path=concept.image_path,
        color_variations=[]  # New concept has no variations yet
    )
```

## Related Files

- [Request Models](request.md): Models for validating API requests
- [Response Models](response.md): Models for structuring API responses
- [Base Models](../common/base.md): Common base models and utilities 