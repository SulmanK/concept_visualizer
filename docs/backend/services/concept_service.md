# Concept Service

The `ConceptService` is responsible for creating, managing, and manipulating visual concepts within the application, serving as the core service for the concept visualization features.

## Overview

The Concept Service provides a high-level API for:

1. Creating visual concepts from user prompts and ideas
2. Managing concept metadata and relationships
3. Organizing concepts into collections and categories
4. Retrieving and filtering concepts based on various criteria
5. Exporting concepts in different formats
6. Analyzing concept usage and metrics

## Key Components

### ConceptService Class

```python
class ConceptService:
    """Service for creating and managing visual concepts."""
    
    def __init__(
        self, 
        image_service: ImageService,
        concept_persistence: ConceptPersistenceService,
        user_service: UserService,
        config: ConceptServiceConfig
    ):
        """Initialize the ConceptService with required dependencies."""
```

**Dependencies:**
- `image_service`: Service for generating and managing images
- `concept_persistence`: Service for persisting concept data in the database
- `user_service`: Service for user authentication and management
- `config`: Configuration parameters for the concept service

### Concept Creation

```python
async def create_concept(
    self,
    user_id: str,
    prompt: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: List[str] = [],
    image_params: Dict[str, Any] = {}
) -> Concept:
    """Create a new visual concept from a user prompt."""
```

Creates a new visual concept from a user prompt, generating an image and extracting color palettes.

**Parameters:**
- `user_id`: ID of the user creating the concept
- `prompt`: Text description of the concept to generate
- `name`: Optional name for the concept (defaults to a generated name)
- `description`: Optional detailed description of the concept
- `tags`: List of tags to associate with the concept
- `image_params`: Parameters for image generation (width, height, style, etc.)

**Returns:**
- `Concept`: The created concept with all associated data

```python
async def create_concept_variation(
    self,
    user_id: str,
    base_concept_id: str,
    variation_prompt: Optional[str] = None,
    variation_strength: float = 0.7,
    name: Optional[str] = None,
    description: Optional[str] = None,
    tags: List[str] = []
) -> Concept:
    """Create a variation of an existing concept."""
```

Creates a variation of an existing concept.

**Parameters:**
- `user_id`: ID of the user creating the variation
- `base_concept_id`: ID of the concept to create a variation from
- `variation_prompt`: Optional additional prompt to guide the variation
- `variation_strength`: Strength of the variation (0.0 to 1.0)
- `name`: Optional name for the variation
- `description`: Optional description for the variation
- `tags`: List of tags to associate with the variation

**Returns:**
- `Concept`: The created concept variation

### Concept Refinement

```python
async def refine_concept(
    self,
    user_id: str,
    concept_id: str,
    refinement_prompt: str,
    create_new_version: bool = True,
    preserve_palettes: bool = True,
    refinement_strength: float = 0.5,
    update_metadata: Dict[str, Any] = {}
) -> Concept:
    """Refine an existing concept based on a refinement prompt."""
```

Refines an existing concept based on a refinement prompt.

**Parameters:**
- `user_id`: ID of the user refining the concept
- `concept_id`: ID of the concept to refine
- `refinement_prompt`: Text description of the refinements to make
- `create_new_version`: Whether to create a new version or update the existing one
- `preserve_palettes`: Whether to preserve the existing color palettes
- `refinement_strength`: Strength of the refinement (0.0 to 1.0)
- `update_metadata`: Additional metadata to update

**Returns:**
- `Concept`: The refined concept

### Concept Retrieval

```python
async def get_concept(
    self,
    concept_id: str,
    user_id: str
) -> Concept:
    """Get a concept by ID."""
```

Retrieves a concept by ID.

**Parameters:**
- `concept_id`: ID of the concept to retrieve
- `user_id`: ID of the user requesting the concept

**Returns:**
- `Concept`: The requested concept

```python
async def list_concepts(
    self,
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    filter_params: Dict[str, Any] = {}
) -> List[ConceptSummary]:
    """List concepts for a user with filtering and pagination."""
```

Lists concepts for a user with filtering and pagination.

**Parameters:**
- `user_id`: ID of the user owning the concepts
- `limit`: Maximum number of concepts to return
- `offset`: Offset for pagination
- `filter_params`: Parameters for filtering (e.g., tags, date range, search term)

**Returns:**
- List of `ConceptSummary` objects

```python
async def search_concepts(
    self,
    user_id: str,
    search_term: str,
    limit: int = 20,
    filter_params: Dict[str, Any] = {}
) -> List[ConceptSummary]:
    """Search concepts by name, description, or tags."""
```

Searches concepts by name, description, or tags.

**Parameters:**
- `user_id`: ID of the user owning the concepts
- `search_term`: Term to search for
- `limit`: Maximum number of concepts to return
- `filter_params`: Additional parameters for filtering

**Returns:**
- List of `ConceptSummary` objects matching the search criteria

### Concept Organization

```python
async def create_collection(
    self,
    user_id: str,
    name: str,
    description: Optional[str] = None,
    concept_ids: List[str] = []
) -> Collection:
    """Create a new collection of concepts."""
```

Creates a new collection of concepts.

**Parameters:**
- `user_id`: ID of the user creating the collection
- `name`: Name of the collection
- `description`: Optional description of the collection
- `concept_ids`: List of concept IDs to include in the collection

**Returns:**
- `Collection`: The created collection

```python
async def add_concept_to_collection(
    self,
    user_id: str,
    collection_id: str,
    concept_id: str
) -> Collection:
    """Add a concept to a collection."""
```

Adds a concept to a collection.

**Parameters:**
- `user_id`: ID of the user owning the collection
- `collection_id`: ID of the collection
- `concept_id`: ID of the concept to add

**Returns:**
- `Collection`: The updated collection

```python
async def remove_concept_from_collection(
    self,
    user_id: str,
    collection_id: str,
    concept_id: str
) -> Collection:
    """Remove a concept from a collection."""
```

Removes a concept from a collection.

**Parameters:**
- `user_id`: ID of the user owning the collection
- `collection_id`: ID of the collection
- `concept_id`: ID of the concept to remove

**Returns:**
- `Collection`: The updated collection

### Concept Management

```python
async def update_concept_metadata(
    self,
    user_id: str,
    concept_id: str,
    metadata: Dict[str, Any]
) -> Concept:
    """Update metadata for a concept."""
```

Updates metadata for a concept.

**Parameters:**
- `user_id`: ID of the user owning the concept
- `concept_id`: ID of the concept to update
- `metadata`: Metadata to update (name, description, tags, etc.)

**Returns:**
- `Concept`: The updated concept

```python
async def delete_concept(
    self,
    user_id: str,
    concept_id: str
) -> bool:
    """Delete a concept."""
```

Deletes a concept.

**Parameters:**
- `user_id`: ID of the user owning the concept
- `concept_id`: ID of the concept to delete

**Returns:**
- Boolean indicating success

```python
async def clone_concept(
    self,
    user_id: str,
    source_concept_id: str,
    new_name: Optional[str] = None,
    new_description: Optional[str] = None,
    new_tags: Optional[List[str]] = None
) -> Concept:
    """Clone an existing concept."""
```

Clones an existing concept.

**Parameters:**
- `user_id`: ID of the user cloning the concept
- `source_concept_id`: ID of the concept to clone
- `new_name`: Optional new name for the cloned concept
- `new_description`: Optional new description for the cloned concept
- `new_tags`: Optional new tags for the cloned concept

**Returns:**
- `Concept`: The cloned concept

### Concept Export

```python
async def export_concept(
    self,
    user_id: str,
    concept_id: str,
    export_format: str = "png",
    export_options: Dict[str, Any] = {}
) -> bytes:
    """Export a concept in the specified format."""
```

Exports a concept in the specified format.

**Parameters:**
- `user_id`: ID of the user owning the concept
- `concept_id`: ID of the concept to export
- `export_format`: Format for export (e.g., "png", "jpg", "svg", "pdf")
- `export_options`: Options for the export (e.g., resolution, quality)

**Returns:**
- Binary data of the exported concept

```python
async def generate_concept_package(
    self,
    user_id: str,
    concept_id: str,
    package_options: Dict[str, Any] = {}
) -> str:
    """Generate a package containing all concept assets."""
```

Generates a package containing all concept assets.

**Parameters:**
- `user_id`: ID of the user owning the concept
- `concept_id`: ID of the concept to package
- `package_options`: Options for the package (e.g., formats to include)

**Returns:**
- URL to download the package

### Analytics and Insights

```python
async def get_concept_usage_metrics(
    self,
    user_id: str,
    concept_id: str
) -> ConceptMetrics:
    """Get usage metrics for a concept."""
```

Gets usage metrics for a concept.

**Parameters:**
- `user_id`: ID of the user owning the concept
- `concept_id`: ID of the concept

**Returns:**
- `ConceptMetrics`: Usage metrics for the concept

```python
async def analyze_concept_trends(
    self,
    user_id: str,
    time_period: str = "month"
) -> Dict[str, Any]:
    """Analyze trends in concept creation and usage."""
```

Analyzes trends in concept creation and usage.

**Parameters:**
- `user_id`: ID of the user
- `time_period`: Time period for analysis (e.g., "day", "week", "month", "year")

**Returns:**
- Dictionary containing trend analysis data

## Data Models

### Concept

```python
class Concept(BaseModel):
    """Represents a visual concept in the system."""
    
    concept_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    prompt: str
    tags: List[str] = []
    image_id: str
    image_url: str
    palettes: List[Palette] = []
    versions: List[ConceptVersion] = []
    parent_concept_id: Optional[str] = None
    is_variation: bool = False
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}
```

Represents a visual concept in the system.

### ConceptSummary

```python
class ConceptSummary(BaseModel):
    """Summary information about a concept."""
    
    concept_id: str
    name: str
    thumbnail_url: str
    created_at: datetime
    updated_at: datetime
    tags: List[str] = []
```

Summary information about a concept for listing and search results.

### ConceptVersion

```python
class ConceptVersion(BaseModel):
    """Represents a version of a concept."""
    
    version_id: str
    concept_id: str
    image_id: str
    image_url: str
    prompt: str
    refinement_prompt: Optional[str] = None
    palettes: List[Palette] = []
    created_at: datetime
    is_current: bool = False
    change_summary: Optional[str] = None
```

Represents a version of a concept, tracking changes over time.

### Collection

```python
class Collection(BaseModel):
    """Represents a collection of concepts."""
    
    collection_id: str
    user_id: str
    name: str
    description: Optional[str] = None
    concept_ids: List[str] = []
    created_at: datetime
    updated_at: datetime
    metadata: Dict[str, Any] = {}
```

Represents a collection of concepts for organization.

### ConceptMetrics

```python
class ConceptMetrics(BaseModel):
    """Usage metrics for a concept."""
    
    concept_id: str
    view_count: int = 0
    download_count: int = 0
    export_count: int = 0
    share_count: int = 0
    favorite_count: int = 0
    last_viewed_at: Optional[datetime] = None
    version_count: int = 0
    first_created_at: datetime
    time_spent_editing: int = 0  # seconds
```

Usage metrics for a concept.

## Usage Examples

### Creating a New Concept

```python
from app.services.concept_service import ConceptService
from app.services.image_service import ImageService
from app.services.persistence.concept_persistence import ConceptPersistenceService
from app.services.user_service import UserService
from app.config.concept_service_config import ConceptServiceConfig

# Initialize dependencies
image_service = ImageService(...)
concept_persistence = ConceptPersistenceService(...)
user_service = UserService(...)
config = ConceptServiceConfig(...)

# Create concept service
concept_service = ConceptService(
    image_service,
    concept_persistence,
    user_service,
    config
)

# Create a new concept
concept = await concept_service.create_concept(
    user_id="user123",
    prompt="A minimalist logo for a tech startup with blue and green colors",
    name="TechFlow Logo",
    description="Logo concept for TechFlow startup",
    tags=["logo", "tech", "minimalist"],
    image_params={
        "width": 1024,
        "height": 1024,
        "style": "minimal"
    }
)

# Get the concept URL
concept_url = f"/concepts/{concept.concept_id}"
```

### Refining a Concept

```python
# Refine an existing concept
refined_concept = await concept_service.refine_concept(
    user_id="user123",
    concept_id=concept.concept_id,
    refinement_prompt="Make the logo more rounded and add a subtle gradient",
    create_new_version=True,
    preserve_palettes=True,
    refinement_strength=0.6,
    update_metadata={
        "description": "Refined logo concept with rounded edges and gradient"
    }
)

# View the version history
for version in refined_concept.versions:
    print(f"Version {version.version_id}: {version.change_summary}")
    print(f"Created at: {version.created_at}")
    print(f"Image URL: {version.image_url}")
```

### Creating Variations

```python
# Create a variation of an existing concept
variation = await concept_service.create_concept_variation(
    user_id="user123",
    base_concept_id=concept.concept_id,
    variation_prompt="Make it more abstract and use purple instead of blue",
    variation_strength=0.7,
    name="TechFlow Logo - Abstract Variation",
    tags=["logo", "tech", "abstract", "purple"]
)

# Create multiple variations and compare them
variations = []
for i in range(3):
    variation = await concept_service.create_concept_variation(
        user_id="user123",
        base_concept_id=concept.concept_id,
        variation_strength=0.5 + (i * 0.1),
        name=f"Variation {i+1}"
    )
    variations.append(variation)
```

### Managing Collections

```python
# Create a collection
collection = await concept_service.create_collection(
    user_id="user123",
    name="Logo Designs",
    description="Collection of logo design concepts",
    concept_ids=[concept.concept_id]
)

# Add variations to the collection
for variation in variations:
    await concept_service.add_concept_to_collection(
        user_id="user123",
        collection_id=collection.collection_id,
        concept_id=variation.concept_id
    )

# List collections
collections = await concept_service.list_collections(user_id="user123")
```

### Searching and Filtering Concepts

```python
# Search for concepts by term
search_results = await concept_service.search_concepts(
    user_id="user123",
    search_term="logo",
    limit=10,
    filter_params={
        "tags": ["minimalist"],
        "date_range": {
            "start": "2023-01-01",
            "end": "2023-12-31"
        }
    }
)

# List recent concepts
recent_concepts = await concept_service.list_concepts(
    user_id="user123",
    limit=5,
    filter_params={
        "sort_by": "created_at",
        "sort_order": "desc"
    }
)
```

### Exporting Concepts

```python
# Export a concept as a PNG
png_data = await concept_service.export_concept(
    user_id="user123",
    concept_id=concept.concept_id,
    export_format="png",
    export_options={
        "resolution": "high",
        "background": "transparent"
    }
)

# Export a concept as SVG
svg_data = await concept_service.export_concept(
    user_id="user123",
    concept_id=concept.concept_id,
    export_format="svg"
)

# Generate a complete package with all assets
package_url = await concept_service.generate_concept_package(
    user_id="user123",
    concept_id=concept.concept_id,
    package_options={
        "formats": ["png", "jpg", "svg"],
        "include_palettes": True,
        "include_versions": True
    }
)
```

## Concept Workflow

The typical concept workflow includes:

1. **Creation**: User creates a concept from a prompt
2. **Refinement**: User refines the concept by providing additional guidance
3. **Variation**: User explores variations of the concept
4. **Organization**: User organizes concepts into collections
5. **Export**: User exports the final concept in desired formats

## Error Handling

Common exceptions that may be raised:

- `ConceptNotFoundError`: When a concept with the specified ID doesn't exist
- `UnauthorizedAccessError`: When a user attempts to access a concept they don't own
- `ConceptCreationError`: When an error occurs during concept creation
- `ValidationError`: When input data is invalid
- `PersistenceError`: When an error occurs in the persistence layer

## Integration Points

The `ConceptService` integrates with several components:

- **Image Service**: For generating and managing concept images
- **User Service**: For authentication and authorization
- **Concept Persistence Service**: For storing concept data in the database
- **Storage Provider**: For storing concept assets
- **Analytics Service**: For tracking concept usage and metrics

## Performance Considerations

The `ConceptService` implements several optimizations for better performance:

1. **Caching**: Frequently accessed concepts are cached
2. **Lazy Loading**: Concept details are loaded only when needed
3. **Batch Processing**: Multiple concepts can be processed in batches
4. **Asynchronous Processing**: Long-running operations are handled asynchronously
5. **Pagination**: Results are paginated to improve response times

## Related Documentation

- [Image Service](./image_service.md): Service for image generation and management
- [User Service](./user_service.md): Service for user authentication and management
- [Concept Persistence Service](./persistence/concept_persistence.md): Service for concept data persistence
- [Collection Service](./collection_service.md): Service for managing collections
- [Concept API Routes](../api/routes/concept_routes.md): API endpoints for concept operations 