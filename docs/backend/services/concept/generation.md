# Concept Generation Service

The concept generation module provides implementation details for generating visual concepts and color palettes using external AI services.

## Overview

This module is responsible for:

1. Converting user text prompts into polished visual concepts
2. Processing prompt inputs to optimize image generation
3. Calling the external image generation service (JigsawStack API)
4. Handling response parsing and error management
5. Supporting the task-based asynchronous processing architecture

## ConceptGenerator

```python
class ConceptGenerator:
    """Service for generating visual concepts based on text descriptions."""

    def __init__(self, client: JigsawStackClient):
        """Initialize the generator with JigsawStack client."""
        self.client = client
        self.logger = get_logger("concept_service.generator")
```

The ConceptGenerator provides specialized functionality for creating visual concepts from text descriptions, serving as the core implementation used by the ConceptService.

## Key Methods

### Generate Image

```python
async def generate_image(
    self,
    prompt: str,
    width: int = 512,
    height: int = 512,
    model: str = "dall-e-3",
) -> Dict[str, Any]:
    """Generate an image based on the provided prompt."""
```

This method handles the core image generation process:

1. Optimizes the prompt for better results
2. Sends the prompt to the JigsawStack API
3. Processes the API response
4. Returns the generated image data

**Parameters:**

- `prompt`: Text description of the image to generate
- `width`: Width of the generated image in pixels
- `height`: Height of the generated image in pixels
- `model`: AI model to use for generation

**Returns:**

- Dictionary containing the generation response with keys like:
  - `url`: URL to the generated image (if available)
  - `binary_data`: Binary image data (if available)

**Raises:**

- `JigsawStackConnectionError`: If connection to the API fails
- `JigsawStackAuthenticationError`: If authentication fails
- `JigsawStackGenerationError`: If generation fails due to API errors
- `ConceptError`: For other generation-related errors

### Enhance Prompt

```python
def enhance_prompt(
    self,
    logo_description: str,
    theme_description: Optional[str] = None,
) -> str:
    """Enhance the user's prompt with additional context for better results."""
```

This method improves raw user prompts by adding context and specificity:

1. Adds specific instructions for generating a logo
2. Includes theme information if provided
3. Sets parameters for image style and quality

**Parameters:**

- `logo_description`: User's description of the logo
- `theme_description`: Optional description of the theme/color scheme

**Returns:**

- Enhanced prompt optimized for the AI model

## Integration with Task-Based System

The concept generation module integrates with the task-based system for handling longer-running operations:

### Direct Generation

For simple generation, the ConceptService's `generate_concept` method uses the ConceptGenerator directly:

```python
async def generate_concept(
    self,
    logo_description: str,
    theme_description: str,
    user_id: Optional[str] = None,
    skip_persistence: bool = False,
) -> Dict[str, Any]:
    """Generate a new concept image based on text descriptions."""

    # Generate the image using the JigsawStack client
    image_response = await self.client.generate_image(prompt=logo_description, width=512, height=512)

    # Process response...
    # Optionally persist...

    return response
```

### Asynchronous Generation with Palettes

For more complex generation with palette variations, the task-based approach is used:

1. API endpoints create tasks and send messages to Google Pub/Sub
2. A Cloud Function processes these messages and performs the generation
3. The function updates the task status as it progresses
4. Clients poll for task completion

## Pub/Sub Message Processing

The Cloud Function processes messages from Pub/Sub:

```python
async def process_pubsub_message(event, context):
    """Process a Pub/Sub message containing task information."""
    try:
        # Parse the message data
        message_data = base64.b64decode(event['data']).decode('utf-8')
        task_info = json.loads(message_data)

        # Extract task information
        task_id = task_info.get('task_id')
        task_type = task_info.get('task_type')
        user_id = task_info.get('user_id')

        # Process based on task type
        if task_type == TASK_TYPE_GENERATION:
            await process_generation_task(
                task_id=task_id,
                user_id=user_id,
                logo_description=task_info.get('logo_description'),
                theme_description=task_info.get('theme_description'),
                num_palettes=task_info.get('num_palettes', 7),
                services=get_services(),
            )
        elif task_type == TASK_TYPE_REFINEMENT:
            # Process refinement task...
            pass
    except Exception as e:
        logger.error(f"Error processing Pub/Sub message: {str(e)}")
```

## Generation Task Processing

The generation task processing follows these steps:

1. Update task status to "processing"
2. Generate base concept using the ConceptService
3. Generate color palettes
4. Apply each palette to create variations
5. Store all assets (images and metadata)
6. Update task with results

```python
async def process_generation_task(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    num_palettes: int,
    services: Dict[str, Any],
) -> None:
    """Process a concept generation task with palettes."""

    # Extract services
    concept_service = services['concept_service']
    task_service = services['task_service']

    try:
        # Update task status
        await task_service.update_task_status(task_id, TASK_STATUS_PROCESSING)

        # Generate base concept
        concept = await concept_service.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description,
            user_id=user_id,
        )

        # Generate and apply palettes
        # Store results
        # Update task status
    except Exception as e:
        # Update task with error information
        await task_service.update_task_status(
            task_id=task_id,
            status=TASK_STATUS_FAILED,
            error_message=str(e),
        )
```

## Error Handling

The generation module implements robust error handling:

1. JigsawStack API errors are caught and transformed into specific error types
2. Task status is updated to reflect failures
3. Error details are logged and included in task updates
4. Temporary failures vs. permanent failures are distinguished

## Client-Side Integration

Client applications interact with the generation system through the API endpoints:

```javascript
// Direct generation
async function generateConcept(logoDescription, themeDescription) {
  const response = await fetch("/api/concepts/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      logo_description: logoDescription,
      theme_description: themeDescription,
    }),
  });

  return await response.json();
}

// Asynchronous generation with palettes
async function generateConceptWithPalettes(logoDescription, themeDescription) {
  const response = await fetch("/api/concepts/generate-with-palettes", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      logo_description: logoDescription,
      theme_description: themeDescription,
    }),
  });

  const taskData = await response.json();
  return taskData; // Contains task_id to track progress
}

// Poll for task completion
async function pollTaskUntilComplete(taskId, onProgress) {
  const poll = async () => {
    const status = await checkTaskStatus(taskId);
    onProgress(status);

    if (status.status === "completed" || status.status === "failed") {
      return status;
    }

    await new Promise((resolve) => setTimeout(resolve, 2000));
    return poll();
  };

  return poll();
}
```

## Related Documentation

- [Concept Service](service.md): Main service using the generator
- [Task Service](../task/service.md): Service for managing background tasks
- [JigsawStack Client](../jigsawstack/client.md): Client for the external AI service
- [Generation API Routes](../../api/routes/concept/generation.md): API routes for concept generation
