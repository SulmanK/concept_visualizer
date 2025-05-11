# Refinement Stage

The Refinement stage contains functions for refining concept images based on user prompts. It handles downloading original images, applying refinements, and storing the results.

## Functions

### download_original_image

```python
async def download_original_image(task_id: str, original_image_url: str) -> bytes:
    """Download the original image for refinement.

    Args:
        task_id: The ID of the task
        original_image_url: URL of the original image

    Returns:
        bytes: The image data

    Raises:
        Exception: If downloading the image fails
    """
```

This function downloads the original image that will be refined:

1. Makes an HTTP request to the provided URL
2. Validates that the response contains valid image data
3. Returns the image data as bytes

### refine_concept_image

```python
async def refine_concept_image(
    task_id: str,
    original_image_url: str,
    refinement_prompt: str,
    logo_description: str,
    theme_description: str,
    concept_service: Any
) -> bytes:
    """Refine a concept image based on a refinement prompt.

    Args:
        task_id: The ID of the task
        original_image_url: URL of the original image
        refinement_prompt: User's refinement instructions
        logo_description: Original logo description
        theme_description: Original theme description
        concept_service: ConceptService instance

    Returns:
        bytes: The refined image data

    Raises:
        Exception: If refinement fails
    """
```

This function refines a concept image based on the user's instructions:

1. Calls the concept service's `refine_concept` method with the original image URL and refinement prompt
2. Extracts image data from the response, either directly or by downloading from a URL
3. Returns the refined image data as bytes

### store_refined_image

```python
async def store_refined_image(
    task_id: str,
    refined_image_data: bytes,
    user_id: str,
    logo_description: str,
    theme_description: str,
    refinement_prompt: str,
    image_persistence_service: Any
) -> Tuple[str, str]:
    """Store the refined image.

    Args:
        task_id: The ID of the task
        refined_image_data: The refined image data
        user_id: User ID
        logo_description: Original logo description
        theme_description: Original theme description
        refinement_prompt: User's refinement instructions
        image_persistence_service: ImagePersistenceService instance

    Returns:
        Tuple containing image path and URL

    Raises:
        Exception: If storing the image fails
    """
```

This function stores the refined image:

1. Calls the image persistence service's `store_image` method
2. Includes metadata about the refinement, such as the prompt and original descriptions
3. Returns the path and URL of the stored refined image

### store_refined_concept

```python
async def store_refined_concept(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    refinement_prompt: str,
    refined_image_path: str,
    refined_image_url: str,
    original_image_url: str,
    concept_persistence_service: Any
) -> str:
    """Store refined concept data in the database.

    Args:
        task_id: The ID of the task
        user_id: User ID
        logo_description: Original logo description
        theme_description: Original theme description
        refinement_prompt: User's refinement instructions
        refined_image_path: Path to the stored refined image
        refined_image_url: URL of the stored refined image
        original_image_url: URL of the original image
        concept_persistence_service: ConceptPersistenceService instance

    Returns:
        Concept ID

    Raises:
        Exception: If storing the concept fails
    """
```

This function stores the refined concept in the database:

1. Creates a concept data dictionary with refinement-specific fields
2. Calls the concept persistence service's `store_concept` method
3. Returns the ID of the stored refined concept

## Usage Example

```python
# Refine the image
refined_image_data = await refine_concept_image(
    task_id=task_id,
    original_image_url=original_image_url,
    refinement_prompt=refinement_prompt,
    logo_description=logo_description,
    theme_description=theme_description,
    concept_service=concept_service
)

# Store the refined image
refined_image_path, refined_image_url = await store_refined_image(
    task_id=task_id,
    refined_image_data=refined_image_data,
    user_id=user_id,
    logo_description=logo_description,
    theme_description=theme_description,
    refinement_prompt=refinement_prompt,
    image_persistence_service=image_persistence_service
)

# Store the refined concept
concept_id = await store_refined_concept(
    task_id=task_id,
    user_id=user_id,
    logo_description=logo_description,
    theme_description=theme_description,
    refinement_prompt=refinement_prompt,
    refined_image_path=refined_image_path,
    refined_image_url=refined_image_url,
    original_image_url=original_image_url,
    concept_persistence_service=concept_persistence_service
)
```

## Refinement Process

The refinement process follows these steps:

1. **Download Original**: The original image is downloaded from the provided URL
2. **Apply Refinement**: The original image is refined based on the user's instructions
3. **Store Refined Image**: The refined image is stored in the persistence layer
4. **Store Refined Concept**: The complete refined concept is stored with references to both the original and refined images

## Refined Concept Data Structure

The refined concept data structure includes:

```python
{
    "user_id": "user123",
    "logo_description": "A minimalist fox",
    "theme_description": "Modern tech with autumn colors", # Combined with refinement prompt
    "image_path": "path/to/refined.png",
    "image_url": "https://example.com/refined.png",
    "color_palettes": [],  # Empty list since we're not generating variations
    "is_anonymous": True,
    "refinement_prompt": "Make it more autumn-themed with orange and red",
    "original_image_url": "https://example.com/original.png",
    "task_id": "task123"
}
```

## Error Handling

Each function includes specific error handling for its operation:

- The download function handles network errors and invalid image data
- The refinement function handles JigsawStack API errors and missing image data
- The storage functions handle database errors and result validation

All errors are wrapped in appropriate exceptions with context.
