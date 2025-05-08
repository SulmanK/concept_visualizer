# Concept Refinement Endpoints

This documentation covers the concept refinement endpoints in the Concept Visualizer API.

## Overview

The `refinement.py` module provides endpoints for refining existing visual concepts based on additional instructions or prompts. Refinement allows users to make targeted improvements to generated concepts rather than starting over. It uses a background task approach through Google Pub/Sub for processing.

## Models

### Request Model

```python
class RefinementRequest(BaseModel):
    """Request model for concept refinement."""
    original_image_url: str
    refinement_prompt: str
    logo_description: Optional[str] = None
    theme_description: Optional[str] = None
```

- `original_image_url`: URL of the concept image to refine
- `refinement_prompt`: Instructions for how to refine the concept
- `logo_description`: Original logo description (optional)
- `theme_description`: Original theme description (optional)

### Response Model

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

### Concept Refinement

```python
@router.post("/refine", response_model=TaskResponse)
async def refine_concept(
    request: RefinementRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Refine a concept based on refinement prompt."""
```

This endpoint creates a background task to refine an existing concept based on specific instructions. It publishes a message to Google Pub/Sub to trigger the processing and returns immediately with a task ID that can be used to check the status.

#### Request

```
POST /api/concepts/refine
Content-Type: application/json

{
  "original_image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "refinement_prompt": "Make the logo more minimalist and use lighter shades of brown",
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling"
}
```

#### Response (202 Accepted)

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "pending",
  "message": "Concept refinement task created and queued for processing",
  "type": "concept_refinement",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": null,
  "completed_at": null,
  "metadata": {
    "original_image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
    "refinement_prompt": "Make the logo more minimalist and use lighter shades of brown",
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling"
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

#### Response (409 Conflict)

If a refinement task is already in progress for the user, the endpoint returns a 409 Conflict status with details about the existing task:

```json
{
  "task_id": "task-1234-5678-9012-3456",
  "status": "processing",
  "message": "A concept refinement task is already in progress",
  "type": "concept_refinement",
  "created_at": "2023-01-01T11:50:00.123456",
  "updated_at": "2023-01-01T11:50:05.123456",
  "completed_at": null,
  "metadata": {
    "original_image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
    "refinement_prompt": "Make the logo more minimalist",
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling"
  },
  "result_id": null,
  "image_url": null,
  "error_message": null
}
```

## Background Task Processing

The refinement task is processed by a Cloud Function triggered by the Pub/Sub message. The function performs the following steps:

1. Retrieves the task from the database
2. Updates the task status to "processing"
3. Downloads the original image
4. Sends the image and refinement prompt to the concept service
5. Stores the refined image in Supabase Storage
6. Updates the task with the final result or error information

## Task Lifecycle

The refinement task goes through the following states:

1. **Pending**: Task created and queued
2. **Processing**: Task is actively being processed
3. **Completed**: Task completed successfully with refined concept
4. **Failed**: Task failed due to an error

## Error Handling

The endpoint handles various error cases:

- `ValidationError`: If the request parameters are invalid
- `ResourceNotFoundError`: If the specified concept does not exist
- `ServiceUnavailableError`: If the refinement service is unavailable

## Rate Limiting

The concept refinement endpoint is subject to the following rate limits:

- `/concepts/refine`: 10 requests per month

## Usage Examples

### Client-Side Refinement Flow

```javascript
// Start concept refinement
async function refineConceptWithPrompt(
  originalImageUrl,
  refinementPrompt,
  logoDesc,
  themeDesc,
) {
  try {
    const response = await fetch("/api/concepts/refine", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        original_image_url: originalImageUrl,
        refinement_prompt: refinementPrompt,
        logo_description: logoDesc,
        theme_description: themeDesc,
      }),
    });

    // Check for conflict (existing task)
    if (response.status === 409) {
      const existingTask = await response.json();
      console.log("A refinement task is already in progress:", existingTask);
      return existingTask;
    }

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.detail || "Concept refinement failed");
    }

    const taskData = await response.json();
    return taskData; // Contains task_id to track progress
  } catch (error) {
    console.error("Error starting concept refinement:", error);
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

- [Generation](generation.md): Endpoints for generating concepts
- [Example Error Handling](example_error_handling.md): Examples of proper error handling
- [Task Routes](../task/routes.md): Endpoints for managing background tasks
