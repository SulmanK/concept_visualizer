# Concept Refinement Endpoints

This documentation covers the concept refinement endpoints in the Concept Visualizer API.

## Overview

The `refinement.py` module provides endpoints for refining existing visual concepts based on additional instructions or prompts. Refinement allows users to make targeted improvements to generated concepts rather than starting over.

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
    created_at: datetime
    updated_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    result: Optional[Dict[str, Any]] = None
```

## Available Endpoints

### Concept Refinement

```python
@router.post("/refine", response_model=TaskResponse)
async def refine_concept(
    request: RefinementRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
):
    """Refine a concept based on refinement prompt."""
```

This endpoint creates a background task to refine an existing concept based on specific instructions. It returns immediately with a task ID that can be used to check the status.

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
  "metadata": {
    "original_image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
    "refinement_prompt": "Make the logo more minimalist and use lighter shades of brown",
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling"
  }
}
```

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
  "metadata": {
    "original_image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
    "refinement_prompt": "Make the logo more minimalist",
    "logo_description": "A modern coffee shop logo with coffee beans",
    "theme_description": "Warm brown tones, natural feeling"
  }
}
```

## Background Task Implementation

The module implements a background task processor for refining concepts:

```python
async def refine_concept_background_task(
    task_id: str,
    refinement_prompt: str,
    original_image_url: str,
    logo_description: str,
    theme_description: str,
    user_id: str,
    image_service: ImageServiceInterface,
    concept_service: ConceptServiceInterface,
    concept_persistence_service: ConceptPersistenceServiceInterface,
    image_persistence_service: ImagePersistenceServiceInterface,
    task_service: TaskServiceInterface
):
    """Background task function to refine a concept."""
```

This function:
1. Updates the task status to "processing"
2. Downloads the original image
3. Sends the image and refinement prompt to the concept service
4. Stores the refined image in Supabase Storage
5. Updates the task with the final result or error information

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
async function refineConceptWithPrompt(originalImageUrl, refinementPrompt, logoDesc, themeDesc) {
  try {
    // Submit the refinement request
    const response = await fetch('/api/concepts/refine', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${getAuthToken()}`
      },
      body: JSON.stringify({
        original_image_url: originalImageUrl,
        refinement_prompt: refinementPrompt,
        logo_description: logoDesc,
        theme_description: themeDesc
      })
    });
    
    // Check for conflict (existing task)
    if (response.status === 409) {
      const existingTask = await response.json();
      console.log('A refinement task is already in progress:', existingTask);
      return existingTask;
    }
    
    if (!response.ok) {
      throw new Error('Concept refinement failed');
    }
    
    const taskData = await response.json();
    
    // Start polling for task status
    return pollTaskStatus(taskData.task_id);
  } catch (error) {
    console.error('Failed to start concept refinement:', error);
    return null;
  }
}

// Poll for task status until complete
async function pollTaskStatus(taskId, maxAttempts = 30, interval = 2000) {
  for (let attempt = 0; attempt < maxAttempts; attempt++) {
    try {
      const response = await fetch(`/api/concepts/task/${taskId}`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to check task status');
      }
      
      const taskData = await response.json();
      
      // If task is complete or failed, return the result
      if (taskData.status === 'completed' || taskData.status === 'failed') {
        return taskData;
      }
      
      // Update UI with current status
      updateRefinementStatus(taskData.status, taskData.message);
      
      // Wait before polling again
      await new Promise(resolve => setTimeout(resolve, interval));
    } catch (error) {
      console.error('Error polling task status:', error);
      // Continue polling despite errors
    }
  }
  
  throw new Error('Task polling timed out');
}
```

## Related Files

- [Generation](generation.md): Endpoints for generating concepts
- [Example Error Handling](example_error_handling.md): Examples of proper error handling
- [Task Routes](../task/routes.md): Endpoints for managing background tasks 