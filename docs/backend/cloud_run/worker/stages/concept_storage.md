# Concept Storage Stage

The Concept Storage stage contains functions for storing base images and complete concepts in the persistence layer.

## Functions

### store_base_image

```python
async def store_base_image(
    task_id: str,
    image_data: bytes,
    user_id: str,
    logo_description: str,
    theme_description: str,
    image_persistence_service: Any
) -> Tuple[str, str]:
    """Store the base image for a concept.

    Args:
        task_id: The ID of the task
        image_data: Image data as bytes
        user_id: User ID
        logo_description: Logo description
        theme_description: Theme description
        image_persistence_service: ImagePersistenceService instance

    Returns:
        Tuple containing image path and URL

    Raises:
        Exception: If storing the image fails
    """
```

This function stores the base image for a concept:

1. Calls the image persistence service's `store_image` method
2. Includes relevant metadata such as logo and theme descriptions
3. Returns the path and URL of the stored image

### store_concept

```python
async def store_concept(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    image_path: str,
    image_url: str,
    color_palettes: List[Dict[str, Any]],
    is_anonymous: bool,
    concept_persistence_service: Any
) -> str:
    """Store a concept in the database.

    Args:
        task_id: The ID of the task
        user_id: User ID
        logo_description: Logo description
        theme_description: Theme description
        image_path: Path to the stored image
        image_url: URL of the stored image
        color_palettes: List of color palettes with image URLs
        is_anonymous: Whether the concept is anonymous
        concept_persistence_service: ConceptPersistenceService instance

    Returns:
        Concept ID

    Raises:
        Exception: If storing the concept fails
    """
```

This function stores a complete concept in the database:

1. Creates a concept data dictionary with all the provided information
2. Calls the concept persistence service's `store_concept` method
3. Returns the ID of the stored concept

## Usage Example

```python
# Store the base image
image_path, image_url = await store_base_image(
    task_id=task_id,
    image_data=image_data,
    user_id=user_id,
    logo_description=logo_description,
    theme_description=theme_description,
    image_persistence_service=image_persistence_service
)

# Create palette variations
# ...

# Store the complete concept
concept_id = await store_concept(
    task_id=task_id,
    user_id=user_id,
    logo_description=logo_description,
    theme_description=theme_description,
    image_path=image_path,
    image_url=image_url,
    color_palettes=variations,
    is_anonymous=True,
    concept_persistence_service=concept_persistence_service
)
```

## Error Handling

Both functions include error handling specific to storage operations:

- Database errors are caught and reported with context
- Result validation ensures that storage operations were successful
- Timing information is captured for performance monitoring

## Concept Data Structure

The concept data structure includes:

```python
{
    "user_id": "user123",                  # ID of the user who created the concept
    "logo_description": "A minimalist fox", # Description of the logo
    "theme_description": "Modern tech",     # Description of the theme
    "image_path": "path/to/image.png",      # Storage path of the base image
    "image_url": "https://example.com/image.png", # Accessible URL of the base image
    "color_palettes": [                    # List of palette variations
        {
            "name": "Cool Blue",
            "colors": ["#123456", "#789ABC", "#DEF012"],
            "description": "A cool blue palette",
            "image_path": "path/to/variation1.png",
            "image_url": "https://example.com/variation1.png"
        },
        # ...more palettes...
    ],
    "is_anonymous": True,                   # Whether the concept is anonymous
    "task_id": "task123"                    # Associated task ID
}
```

## Storage Process

The storage process follows these steps:

1. **Base Image Storage**: The base image is stored first to obtain its path and URL
2. **Palette Variations**: Palette variations are created and stored with the base image
3. **Concept Storage**: The complete concept, including base image and variations, is stored

This process ensures that all components of a concept are properly stored and linked together.
