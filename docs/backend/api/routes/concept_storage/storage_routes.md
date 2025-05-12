# Concept Storage Routes

The `storage_routes.py` module provides API endpoints for storing and retrieving visual concepts from the database.

## Overview

The concept storage routes handle the persistence of visual concepts, including:

1. Generating and storing concepts with palette variations in a single operation
2. Retrieving recently created concepts for a user
3. Fetching detailed information about specific concepts

These endpoints integrate concept generation capabilities with persistence services, allowing users to save their generated designs and access them later.

## Router Configuration

```python
router = APIRouter()
```

The router is created without a specific prefix, as that's handled by the parent router.

## Endpoints

### Generate and Store Concept

```python
@router.post("/store", response_model=GenerationResponse)
async def generate_and_store_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends()
) -> GenerationResponse:
    """Generate and store a new concept based on prompt."""
```

This endpoint provides a comprehensive workflow that:

1. Generates a base image using the concept service
2. Generates color palettes based on the theme description
3. Creates color variations of the base image using the palettes
4. Stores all assets (images and metadata) in Supabase Storage and Database
5. Returns a response with the image URL and concept information

**Authentication:** Requires a valid user ID from the authenticated request

**Request Body:**

```json
{
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling"
}
```

**Response:**

```json
{
  "prompt_id": "1234-5678-9012-3456",
  "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling",
  "created_at": "2023-01-01T12:00:00.123456",
  "color_palette": {
    "primary": "#4A2C2A",
    "secondary": "#6B4226",
    "accent": "#D4A762",
    "background": "#F5EFE7",
    "text": "#2D2424",
    "additional_colors": []
  },
  "original_image_url": null,
  "refinement_prompt": null,
  "variations": [
    {
      "palette_name": "Earthy Tones",
      "colors": ["#4A2C2A", "#6B4226", "#D4A762", "#F5EFE7", "#2D2424"],
      "description": "Warm coffee-inspired palette with earthy browns",
      "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456-v1.png"
    },
    {
      "palette_name": "Cool Beans",
      "colors": ["#362F2D", "#594D45", "#8C7A6B", "#BFB1A3", "#E8DFD5"],
      "description": "Monochromatic brown scheme with subtle contrast",
      "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456-v2.png"
    }
  ]
}
```

**Note:** This endpoint provides a more comprehensive generation and storage approach compared to `/concepts/generate`, which performs basic generation and storage without palette variations. Use this endpoint when you need both generation and multiple color variations in a single call.

### Get Recent Concepts

```python
@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    req: Request,
    limit: int = Query(10, ge=1, le=50),
    commons: CommonDependencies = Depends()
) -> List[Dict[str, Any]]:
    """Get recent concepts for the current user."""
```

This endpoint retrieves a summary of recently created concepts for the authenticated user.

**Authentication:** Requires a valid user ID from the authenticated request

**Query Parameters:**

- `limit`: Maximum number of concepts to return (default: 10, max: 50)

**Response:**

Array of concept summaries with:

- `id`: Concept identifier
- `created_at`: Timestamp when the concept was created
- `logo_description`: Original text description of the logo
- `theme_description`: Original text description of the theme
- `image_url`: URL to the generated base image
- `has_variations`: Whether the concept has color variations
- `variations_count`: Number of available color variations
- `is_refinement`: Whether this is a refinement of another concept
- `original_concept_id`: ID of the original concept if this is a refinement
- `color_variations`: Array of color palette variations with images

**URL Generation:** If a stored concept or color variation doesn't have a pre-generated URL, this endpoint will generate a signed URL on-the-fly.

### Get Concept Detail

```python
@router.get("/concept/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: str,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends()
) -> Dict[str, Any]:
    """Get detailed information about a specific concept."""
```

This endpoint retrieves detailed information about a specific concept by its ID.

**Authentication:** Requires a valid user ID from the authenticated request

**Path Parameters:**

- `concept_id`: ID of the concept to retrieve

**Response:**

Comprehensive concept details including:

- Base concept information (ID, descriptions, creation time)
- Image URL for the main concept
- Color palette variations with images
- Metadata about the generation process

**URL Generation:** Similar to the `/recent` endpoint, this endpoint will generate signed URLs on-the-fly for any stored images that don't have pre-generated URLs.

## Error Handling

The endpoints implement a consistent error handling approach:

1. **Authentication Errors**: Returns 401 Unauthorized if no valid user ID is found
2. **Resource Not Found**: Returns 404 Not Found with details if a concept doesn't exist
3. **Service Unavailable**: Returns 503 Service Unavailable if backend services fail
4. **Detailed Logging**: All errors are logged with appropriate severity

## Integration with Services

The concept storage routes integrate with several services:

1. **ConceptService**: For generating base images and palettes
2. **ImageService**: For processing and creating palette variations
3. **ConceptPersistenceService**: For storing and retrieving concept data
4. **ImagePersistenceService**: For storing images and generating URLs

## Related Documentation

- [Concept Models](../../../models/concept/domain.md): Data models for concepts
- [Concept Service](../../../services/concept/service.md): Service for generating concepts
- [Persistence Service](../../../services/persistence/concept_persistence_service.md): Service for storing concepts
- [Concept Generation Routes](../concept/generation.md): Routes for on-demand concept generation
