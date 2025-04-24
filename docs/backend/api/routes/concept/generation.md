# Concept Generation Endpoints

This documentation covers the concept generation endpoints in the Concept Visualizer API.

## Overview

The `generation.py` module provides endpoints for generating visual concepts (logos and themes) based on text descriptions. It supports both synchronous and asynchronous generation processes with background task management.

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
    concept_id: str
    image_url: str
    logo_description: str
    theme_description: str
    created_at: datetime
    palette_variations: List[PaletteVariation] = []
```

```python
class TaskResponse(BaseModel):
    """Response model for background tasks."""
    task_id: str
    status: str
    message: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    result: Optional[Dict[str, Any]] = None
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
):
    """Generate a new visual concept based on the provided prompt and store it."""
```

This endpoint generates a concept immediately and returns the result in the response. It's suitable for simple concepts but may time out for complex generations.

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
  "concept_id": "1234-5678-9012-3456",
  "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling",
  "created_at": "2023-01-01T12:00:00.123456",
  "palette_variations": []
}
```

### Asynchronous Concept Generation with Palettes

```python
@router.post("/generate-with-palettes", response_model=TaskResponse)
async def generate_concept_with_palettes(
    request: PromptRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    req: Request,
    num_palettes: int = 7,
    commons: CommonDependencies = Depends(),
):
    """Generate a new visual concept with palette variations as a background task."""
```

This endpoint creates a background task to generate a concept with multiple palette variations. It returns immediately with a task ID that can be used to check the status.

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

- `num_palettes`: Number of palette variations to generate (default: 7, max: 10)

#### Response

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "pending",
  "message": "Concept generation started",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": null,
  "result": null
}
```

### Task Status Check

```python
@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    req: Request,
    commons: CommonDependencies = Depends(),
):
    """Get the status of a background task."""
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
  "message": "Generating palette variations",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:05.123456",
  "result": null
}
```

#### Response (Completed)

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "completed",
  "message": "Concept generation completed",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:30.123456",
  "result": {
    "concept_id": "1234-5678-9012-3456",
    "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling",
    "created_at": "2023-01-01T12:00:30.123456",
    "palette_variations": [
      {
        "id": "palette-1",
        "image_url": "https://storage.example.com/palettes/palette-1.png",
        "colors": ["#5A3921", "#8C593B", "#D9B18C", "#F2E2CE"]
      },
      {
        "id": "palette-2",
        "image_url": "https://storage.example.com/palettes/palette-2.png",
        "colors": ["#3C280D", "#704E2E", "#B7906F", "#E8D4B5"]
      }
      // Additional palette variations...
    ]
  }
}
```

## Background Task Implementation

The module implements a background task processor for generating concepts with palette variations:

```python
async def generate_concept_background_task(
    task_id: str,
    logo_description: str,
    theme_description: str,
    user_id: str,
    num_palettes: int,
    image_service: ImageServiceInterface,
    concept_service: ConceptServiceInterface,
    concept_persistence_service: StorageServiceInterface,
    task_service: TaskServiceInterface
):
    """Background task for generating concepts with palette variations."""
```

This function:

1. Updates the task status to "processing"
2. Generates the base concept
3. Creates palette variations
4. Stores all images in Supabase Storage
5. Updates the task with the final result or error information

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
- `InternalServerError`: For unexpected errors

## Usage Examples

### Client-Side Asynchronous Generation Flow

```javascript
// Start concept generation
async function generateConcept(logoDescription, themeDescription) {
  try {
    // Submit the generation request
    const response = await fetch("/api/concepts/generate-with-palettes", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${getAuthToken()}`,
      },
      body: JSON.stringify({
        logo_description: logoDescription,
        theme_description: themeDescription,
      }),
    });

    if (!response.ok) {
      throw new Error("Concept generation failed");
    }

    const taskData = await response.json();

    // Start polling for task status
    return pollTaskStatus(taskData.task_id);
  } catch (error) {
    console.error("Failed to start concept generation:", error);
    return null;
  }
}

// Poll for task status until complete
async function pollTaskStatus(taskId, maxAttempts = 30, interval = 2000) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await fetch(`/api/concepts/task/${taskId}`, {
        headers: {
          Authorization: `Bearer ${getAuthToken()}`,
        },
      });

      if (!response.ok) {
        throw new Error("Failed to check task status");
      }

      const taskData = await response.json();

      // If task is complete or failed, return the result
      if (taskData.status === "completed" || taskData.status === "failed") {
        return taskData;
      }

      // Wait before polling again
      await new Promise((resolve) => setTimeout(resolve, interval));
    } catch (error) {
      console.error("Error polling task status:", error);
      // Continue polling despite errors
    }
  }

  throw new Error("Task polling timed out");
}
```

## Related Files

- [Refinement](refinement.md): Endpoints for refining generated concepts
- [Error Handling](example_error_handling.md): Examples of proper error handling
- [Concept Models](../../../models/concept/request.md): Request models for concept generation
