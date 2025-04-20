# Task Response Models

This documentation covers the response models used for task-related API endpoints.

## Overview

The `response.py` module in `app/models/task/` defines Pydantic models for structuring responses from task management endpoints. These models provide a consistent format for task status updates and results.

## Models

### TaskResponse

```python
class TaskResponse(APIBaseModel):
    """Response model for task creation and status updates."""
    
    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status (pending, processing, completed, failed)")
    type: str = Field(..., description="Task type (e.g., concept_generation, concept_refinement)")
    message: str = Field(..., description="Human-readable status message")
    
    created_at: Optional[str] = Field(None, description="Task creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last status update timestamp")
    completed_at: Optional[str] = Field(None, description="Task completion timestamp")
    
    metadata: Optional[Dict[str, Any]] = Field(
        default={},
        description="Task-specific metadata (e.g., prompt info)"
    )
    
    result_id: Optional[str] = Field(
        None, 
        description="ID of the result resource (e.g., concept ID for generation tasks)"
    )
    
    image_url: Optional[str] = Field(
        None,
        description="URL of the generated image (for completed tasks)"
    )
    
    error_message: Optional[str] = Field(
        None,
        description="Error message if the task failed"
    )
```

This model represents the response for task creation and status updates with the following fields:

- `task_id`: Unique identifier for the task
- `status`: Current status of the task (one of: "pending", "processing", "completed", "failed")
- `type`: The type of task (e.g., "concept_generation", "concept_refinement")
- `message`: Human-readable status message explaining the current state
- `created_at`: Optional timestamp when the task was created
- `updated_at`: Optional timestamp when the task status was last updated
- `completed_at`: Optional timestamp when the task was completed
- `metadata`: Optional dictionary containing task-specific metadata (e.g., prompt information)
- `result_id`: Optional identifier for the result resource (e.g., concept ID for generation tasks)
- `image_url`: Optional URL of the generated image (available for completed tasks)
- `error_message`: Optional error message if the task failed

## Task Status Flow

The `status` field of the `TaskResponse` model follows a standard progression:

1. **pending**: Task has been created but not yet started processing
2. **processing**: Task is actively being processed
3. **completed**: Task has successfully completed
4. **failed**: Task has failed due to an error

## Usage Examples

### Task Creation Response

```json
{
  "task_id": "task_1234abcd",
  "type": "concept_generation",
  "status": "pending",
  "message": "Task created and queued for processing",
  "created_at": "2023-01-01T12:00:00.123456",
  "metadata": {
    "logo_description": "A modern, minimalist logo for a tech startup",
    "theme_description": "Modern tech aesthetic with blues and purples"
  }
}
```

### Task In Progress Response

```json
{
  "task_id": "task_1234abcd",
  "type": "concept_generation",
  "status": "processing",
  "message": "Generating concept image",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:05.123456",
  "metadata": {
    "logo_description": "A modern, minimalist logo for a tech startup",
    "theme_description": "Modern tech aesthetic with blues and purples"
  }
}
```

### Completed Task Response

```json
{
  "task_id": "task_1234abcd",
  "type": "concept_generation",
  "status": "completed",
  "message": "Concept generation completed successfully",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:30.123456",
  "completed_at": "2023-01-01T12:00:30.123456",
  "metadata": {
    "logo_description": "A modern, minimalist logo for a tech startup",
    "theme_description": "Modern tech aesthetic with blues and purples"
  },
  "result_id": "concept_5678efgh",
  "image_url": "https://storage.example.com/concepts/concept_5678efgh.png"
}
```

### Failed Task Response

```json
{
  "task_id": "task_1234abcd",
  "type": "concept_generation",
  "status": "failed",
  "message": "Task failed",
  "created_at": "2023-01-01T12:00:00.123456",
  "updated_at": "2023-01-01T12:00:15.123456",
  "metadata": {
    "logo_description": "A modern, minimalist logo for a tech startup",
    "theme_description": "Modern tech aesthetic with blues and purples"
  },
  "error_message": "External API service unavailable"
}
```

## Endpoints Using This Model

The `TaskResponse` model is used by various task-related endpoints in the API:

- `POST /api/concepts/generate-with-palettes`: Creates a concept generation task
- `POST /api/concepts/refine`: Creates a concept refinement task
- `GET /api/concepts/task/{task_id}`: Gets the status of a specific task
- `GET /api/tasks`: Gets a list of the user's tasks
- `GET /api/tasks/{task_id}`: Gets the status of a specific task

## Related Files

- [Task Service](../../services/task/service.md): Service implementing task management
- [Task Interface](../../services/task/interface.md): Interface definition for task services
- [Task Routes](../../api/routes/task/routes.md): API routes for task management
- [Concept Generation](../../api/routes/concept/generation.md): Uses tasks for asynchronous generation 
- [Concept Refinement](../../api/routes/concept/refinement.md): Uses tasks for asynchronous refinement 