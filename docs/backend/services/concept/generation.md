# Concept Generation Service

The concept generation module provides implementation details for generating visual concepts and color palettes using external AI services.

## Overview

This module is responsible for:

1. Converting user text prompts into polished visual concepts
2. Processing prompt inputs to optimize image generation
3. Calling the external image generation service (JigsawStack API)
4. Handling response parsing and error management
5. Initiating asynchronous processing tasks via Pub/Sub

## Asynchronous Processing Architecture

The concept generation service now uses an asynchronous architecture with Google Cloud Pub/Sub for processing intensive tasks:

1. API routes create a task record in the database and publish a message to Pub/Sub
2. A Cloud Run worker processes the message and performs the generation work
3. The worker updates the task status in the database as it progresses
4. Clients poll the task status endpoint to track progress and get results

### Component Responsibilities

- **API Routes**: Create tasks and send messages to Pub/Sub
- **Cloud Run Worker**: Processes messages from Pub/Sub and performs generation work
- **Task Service**: Manages task status and metadata
- **Polling Endpoint**: Allows clients to check task progress

## Service Integration

The generation module integrates with the JigsawStack service to perform AI-powered image generation. It extends the base concept service functionality by adding specialized concept generation capabilities.

## Key Functions

### Generate Base Image

```python
async def generate_base_image(
    prompt: str,
    model: str = "dall-e-3",
    width: int = 1024,
    height: int = 1024
) -> GeneratedImage:
    """Generate a base image from a text prompt."""
```

This function is responsible for:

1. Preprocessing the prompt to improve generation quality
2. Sending the generation request to the AI service
3. Processing the response into a standardized format
4. Handling any errors that occur during generation

**Parameters:**

- `prompt`: Text description of the image to generate
- `model`: AI model to use for generation (default: "dall-e-3")
- `width`: Desired image width in pixels (default: 1024)
- `height`: Desired image height in pixels (default: 1024)

**Returns:**

- `GeneratedImage`: Object containing the generated image data and metadata

**Raises:**

- `ServiceUnavailableError`: If the external API is unavailable
- `GenerationError`: If image generation fails for any reason

### Enhance Prompt

```python
def enhance_prompt(original_prompt: str, context: str = "logo") -> str:
    """Enhance the user's prompt with additional context for better results."""
```

This function improves raw user prompts by adding context and specificity to get better results from the AI model.

**Parameters:**

- `original_prompt`: The user's original text description
- `context`: The generation context (e.g., "logo", "icon")

**Returns:**

- Enhanced prompt string with additional details and specifications

## Cloud Run Worker

The Cloud Run worker processes generation tasks asynchronously:

```python
async def process_generation_task(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    num_palettes: int,
    services: Dict[str, Any],
) -> None:
    """Process a concept generation task."""
```

This function handles the end-to-end concept generation process:

1. Updates task status to "processing"
2. Generates the base concept image
3. Creates multiple color palette variations
4. Stores results in Supabase
5. Updates task status to "completed" with result information

For refinement tasks, a similar function processes the refinement workflow:

```python
async def process_refinement_task(
    task_id: str,
    user_id: str,
    refinement_prompt: str,
    original_image_url: str,
    logo_description: str,
    theme_description: str,
    services: Dict[str, Any],
) -> None:
    """Process a concept refinement task."""
```

## Task-Based API

The concept generation API now uses a task-based approach:

1. Client submits generation request
2. Server creates a task and returns task ID with 202 Accepted status
3. Client polls task status endpoint until completion
4. On completion, client receives result information

```python
@router.post("/generate-with-palettes", response_model=TaskResponse)
async def generate_concept_with_palettes(request: PromptRequest) -> TaskResponse:
    """Generate a new visual concept with multiple color palettes."""
```

This endpoint starts an asynchronous task and returns a task ID for polling.

## Error Handling

The generation module implements robust error handling:

1. Connection errors are caught and transformed into appropriate application exceptions
2. Timeout handling ensures the service remains responsive
3. Rate limit detection prevents excessive API usage
4. Response validation ensures the returned data meets expected formats
5. Task status updates reflect errors for client feedback

## Example Usage

```python
# Client-side code for asynchronous generation
import httpx
import time

# Submit generation request
response = await httpx.post(
    "https://api.example.com/concepts/generate-with-palettes",
    json={
        "logo_description": "A modern tech company logo with abstract geometric shapes",
        "theme_description": "Sleek, futuristic design with blue and purple gradient"
    }
)

# Get task ID from response
task_data = response.json()
task_id = task_data["task_id"]

# Poll for completion
while True:
    task_status = await httpx.get(f"https://api.example.com/concepts/task/{task_id}")
    status_data = task_status.json()

    if status_data["status"] == "completed":
        # Get the result
        concept_id = status_data["result_id"]
        image_url = status_data["image_url"]
        break
    elif status_data["status"] == "failed":
        # Handle error
        error_message = status_data["error_message"]
        break

    # Wait before polling again
    time.sleep(2)
```

## Performance Considerations

- Tasks are processed asynchronously to avoid blocking API responses
- Cloud Run worker instances can scale based on demand
- Long-running operations are segregated from API handling
- Task status updates provide visibility into processing progress
- Pub/Sub provides reliable message delivery with retry capabilities

## Related Documentation

- [Concept Service Interface](interface.md): Interface definition for all concept services
- [Concept Service](service.md): Main concept service implementation
- [Palette Service](palette.md): Service for generating color palettes
- [JigsawStack Client](../jigsawstack/client.md): Client for the external AI API
- [Generation API Routes](../../api/routes/concept/generation.md): API routes that use this service
- [Cloud Run Worker](../../../cloud_run/worker/README.md): Worker documentation
