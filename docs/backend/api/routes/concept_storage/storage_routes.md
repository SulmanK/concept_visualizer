# Concept Storage Routes

The `storage_routes.py` module provides API endpoints for storing and retrieving visual concepts from the database.

## Overview

The concept storage routes handle the persistence of generated visual concepts, including:

1. Generating and storing new concepts
2. Retrieving recently created concepts for a user
3. Fetching detailed information about specific concepts

These endpoints integrate the concept generation capabilities with persistence services, allowing users to save their generated designs and access them later.

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
):
    """Generate and store a new concept based on prompt."""
```

This endpoint provides a comprehensive workflow that:

1. Generates a base image using the logo description
2. Generates color palettes based on the theme description
3. Creates color variations of the base image using the palettes
4. Stores all assets (images and metadata) in the database
5. Returns a complete response with image URLs and palette information

**Authentication:** Requires a valid user ID from the authenticated request

**Request Body:**

- `logo_description`: Text description of the logo to generate
- `theme_description`: Text description of the theme/color scheme

**Response:**

- `prompt_id`: Unique identifier for the stored concept
- `image_url`: URL to the generated image
- `color_palettes`: Array of generated color palettes with images

### Get Recent Concepts

```python
@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    req: Request,
    limit: int = Query(10, ge=1, le=50),
    commons: CommonDependencies = Depends()
):
    """Get recent concepts for the current user."""
```

This endpoint retrieves a summary of recently created concepts for the authenticated user.

**Authentication:** Requires a valid user ID from the authenticated request

**Query Parameters:**

- `limit`: Maximum number of concepts to return (default: 10, max: 50)

**Response:**

- Array of concept summaries with basic information:
  - `id`: Concept identifier
  - `created_at`: Timestamp when the concept was created
  - `logo_description`: Original text description of the logo
  - `theme_description`: Original text description of the theme
  - `image_url`: URL to the generated base image
  - `color_variations`: Array of color palette variations with images

### Get Concept Detail

```python
@router.get("/concept/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: str,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends()
):
    """Get detailed information about a specific concept."""
```

This endpoint retrieves detailed information about a specific concept by its ID.

**Authentication:** Requires a valid user ID from the authenticated request

**Path Parameters:**

- `concept_id`: ID of the concept to retrieve

**Response:**

- Comprehensive concept details including:
  - Base concept information (ID, descriptions, creation time)
  - Image URL for the main concept
  - Color palette variations with images
  - Metadata about the generation process
  - User information

## Error Handling

The endpoints implement a consistent error handling approach:

1. **Authentication Errors**: Returns 401 Unauthorized if no valid user ID is found
2. **Resource Not Found**: Returns 404 Not Found with details if a concept doesn't exist
3. **Service Unavailable**: Returns 503 Service Unavailable if backend services fail
4. **Detailed Logging**: All errors are logged with appropriate severity

## Usage Examples

### Generating and Storing a Concept

```http
POST /api/v1/concept-storage/store
Content-Type: application/json

{
  "logo_description": "A modern tech company logo with abstract geometric shapes",
  "theme_description": "Professional, modern, tech-focused with blues and grays"
}
```

### Retrieving Recent Concepts

```http
GET /api/v1/concept-storage/recent?limit=5
Authorization: Bearer {token}
```

### Retrieving a Specific Concept

```http
GET /api/v1/concept-storage/concept/abc123
Authorization: Bearer {token}
```

## Integration with Services

The concept storage routes integrate with several services:

1. **ConceptService**: For generating images and palettes
2. **ImageService**: For processing palette variations
3. **ConceptPersistenceService**: For storing and retrieving concept data
4. **ImagePersistenceService**: For storing and retrieving image assets

## Related Documentation

- [Concept Models](../../../models/concept/domain.md): Data models for concepts
- [Concept Service](../../../services/concept/service.md): Service for generating concepts
- [Persistence Service](../../../services/persistence/concept_persistence_service.md): Service for storing concepts
- [Concept Generation Routes](../concept/generation.md): Routes for on-demand concept generation
