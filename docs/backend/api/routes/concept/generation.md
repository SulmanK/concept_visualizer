# Concept Generation Endpoints

This documentation covers the concept generation endpoints in the Concept Visualizer API.

## Overview

The `generation.py` module provides endpoints for generating visual concepts (logos and themes) based on text descriptions. It supports both:

- Direct generation with a synchronous endpoint that handles concept creation and storage
- Background task-based generation with palette variations to handle longer-running processes

## Models

### Request Models

```python
class PromptRequest(BaseModel):
    """Request model for concept generation."""
    logo_description: str
    theme_description: str
```

### Response Models

```python
class GenerationResponse(BaseModel):
    """Response model for concept generation."""
    prompt_id: str
    image_url: str
    logo_description: str
    theme_description: str
    created_at: str
    color_palette: Optional[Dict[str, Any]] = None
    original_image_url: Optional[str] = None
    refinement_prompt: Optional[str] = None
    variations: List[Dict[str, Any]] = []
```

```python
class TaskResponse(BaseModel):
    """Response model for background tasks."""
    task_id: str
    status: str
    message: Optional[str] = None
    type: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    completed_at: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    result_id: Optional[str] = None
    image_url: Optional[str] = None
    error_message: Optional[str] = None
```

## Available Endpoints

### Synchronous Concept Generation

```python
@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> GenerationResponse:
    """Generate a new visual concept based on the provided prompt and store it."""
```

This endpoint generates a concept, extracts colors from it, and stores both the image and concept metadata in the database. It returns the result immediately in the response.

#### Request

```
POST /api/concepts/generate
Content-Type: application/json

{
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling"
}
```

#### Response

```json
{
  "prompt_id": "1234-5678-9012-3456",
  "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling",
  "created_at": "2023-01-01T12:00:00.123456",
  "color_palette": null,
  "original_image_url": null,
  "refinement_prompt": null,
  "variations": []
}
```

The endpoint performs the following steps:

1. Validates input and checks rate limits
2. Generates the base concept using the concept service
3. Extracts colors from the generated image
4. Stores the image in Supabase Storage
5. Creates and stores concept metadata including extracted colors
6. Returns the concept details in the response

### Asynchronous Concept Generation with Palettes

```python
@router.post("/generate-with-palettes", response_model=TaskResponse)
async def generate_concept_with_palettes(
    request: PromptRequest,
    response: Response,
    req: Request,
    num_palettes: int = 7,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Generate a new visual concept with multiple color palettes."""
```

This endpoint creates a background task to generate a concept with multiple palette variations. It publishes a message to Google Pub/Sub to trigger the background processing. The endpoint returns immediately with a task ID that can be used to check the status.

#### Request

```
POST /api/concepts/generate-with-palettes?num_palettes=5
Content-Type: application/json

{
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling"
}
```

Parameters:

- `num_palettes`: Number of palette variations to generate (default: 7)

#### Response

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "pending",
  "message": "Concept generation task created and queued for processing",
  "type": "concept_generation",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": null,
  "completed_at": null,
  "metadata": {
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling",
    "num_palettes": 5
  },
  "result_id": null,
  "image_url": null,
  "error_message": null
}
```

The endpoint performs the following steps:

1. Creates a task record in the database
2. Publishes a message to Pub/Sub with task details
3. Returns task information in the response

### Task Status Check

```python
@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Get the status of a concept generation task."""
```

This endpoint allows checking the status of a background task, including retrieving the final result when complete.

#### Request

```
GET /api/concepts/task/task-1234-5678-9012-3456
```

#### Response (Pending)

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "processing",
  "message": "Task is processing",
  "type": "concept_generation",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:05.123456",
  "completed_at": null,
  "result_id": null,
  "image_url": null,
  "error_message": null,
  "metadata": {
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling",
    "num_palettes": 5
  }
}
```

#### Response (Completed)

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "completed",
  "message": "Task is completed",
  "type": "concept_generation",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:30.123456",
  "completed_at": "2023-01-01T12:00:30.123456",
  "result_id": "1234-5678-9012-3456",
  "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "error_message": null,
  "metadata": {
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling",
    "num_palettes": 5
  }
}
```

## Background Task Processing

The background task processing occurs in a Cloud Function triggered by the Pub/Sub message. The function performs the following steps:

1. Retrieves the task from the database
2. Updates the task status to "processing"
3. Generates the base concept
4. Creates palette variations
5. Stores all images in Supabase Storage
6. Stores concept metadata in the database
7. Updates the task with the final result or error information

## Rate Limiting

The concept generation endpoints are subject to the following rate limits:

- `/concepts/generate`: 10 requests per month
- `/concepts/generate-with-palettes`: 10 requests per month

Both endpoints also count against the `/concepts/store` limit of 10 stored concepts per month.

## Error Handling

The endpoints handle various error cases:

- `ValidationError`: If the request parameters are invalid
- `UnauthorizedError`: If the user is not authenticated
- `ServiceUnavailableError`: If the concept generation service is unavailable
- `BadRequestError`: For invalid parameters or rate limit exceeded
- `ResourceNotFoundError`: If the requested task is not found
- `InternalServerError`: For unexpected errors

## Usage Examples

### Client-Side Asynchronous Generation Flow

```javascript
// Start concept generation
async function generateConcept(logoDescription, themeDescription) {
  try {
    const response = await fetch("/api/concepts/generate-with-palettes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        logo_description: logoDescription,
        theme_description: themeDescription,
      }),
    });

    const data = await response.json();
    return data; // Contains task_id to track progress
  } catch (error) {
    console.error("Error starting concept generation:", error);
    throw error;
  }
}

// Check task status
async function checkTaskStatus(taskId) {
  try {
    const response = await fetch(`/api/concepts/task/${taskId}`);
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Error checking task status:", error);
    throw error;
  }
}

// Poll task status until complete
async function pollTaskUntilComplete(taskId, onProgress) {
  const poll = async () => {
    const status = await checkTaskStatus(taskId);
    onProgress(status);

    if (status.status === "completed" || status.status === "failed") {
      return status;
    }

    // Wait 2 seconds before checking again
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return poll();
  };

  return poll();
}
```

## Security Considerations

- All endpoints require authentication
- Tasks are user-scoped to prevent unauthorized access
- Rate limiting protects against abuse
- Error messages are sanitized to prevent information disclosure

## Related Files

- [Refinement](refinement.md): Endpoints for refining generated concepts
- [Error Handling](example_error_handling.md): Examples of proper error handling
- [Concept Models](../../../models/concept/request.md): Request models for concept generation
