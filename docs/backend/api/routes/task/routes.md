# Task Management Routes

The `routes.py` module in the task package provides API endpoints for managing background tasks in the Concept Visualizer application.

## Overview

The task management routes enable users to:

1. Retrieve a list of their background tasks
2. Get details about a specific task
3. Delete tasks that are no longer needed

These endpoints are crucial for providing visibility and control over asynchronous operations, such as concept generation and image processing, that may take time to complete.

## Router Configuration

```python
router = APIRouter()
```

The router is created without a specific prefix, as that's handled by the parent router.

## Endpoints

### Get Tasks

```python
@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    request: Request,
    status: Optional[str] = Query(None, description="Filter tasks by status"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of tasks to return"),
    commons: CommonDependencies = Depends(),
):
    """Get a list of tasks for the authenticated user."""
```

This endpoint retrieves a list of background tasks for the authenticated user, with optional filtering by status.

**Authentication:** Requires a valid user ID from the authenticated request

**Query Parameters:**
- `status`: Optional filter for task status (e.g., "pending", "running", "completed", "failed")
- `limit`: Maximum number of tasks to return (default: 10, max: 50)

**Response:**
- Array of task responses with the following information:
  - `task_id`: Unique identifier for the task
  - `status`: Current status of the task
  - `message`: Human-readable message about the task status
  - `type`: Type of task (e.g., "concept_generation", "image_processing")
  - `created_at`: Timestamp when the task was created
  - `updated_at`: Timestamp when the task was last updated
  - `result_id`: ID of the result resource (if task completed successfully)
  - `error`: Error message (if task failed)
  - `metadata`: Additional task-specific information

### Get Task Details

```python
@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    request: Request,
    commons: CommonDependencies = Depends(),
):
    """Get details of a specific task."""
```

This endpoint retrieves detailed information about a specific task by its ID.

**Authentication:** Requires a valid user ID from the authenticated request

**Path Parameters:**
- `task_id`: ID of the task to retrieve

**Response:**
- Detailed task information with the same structure as in the list endpoint

### Delete Task

```python
@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    request: Request,
    commons: CommonDependencies = Depends(),
):
    """Delete a task."""
```

This endpoint deletes a specific task by its ID.

**Authentication:** Requires a valid user ID from the authenticated request

**Path Parameters:**
- `task_id`: ID of the task to delete

**Response:**
- 204 No Content on successful deletion (no response body)

## Task Statuses

Tasks can have the following statuses:

| Status | Description |
|--------|-------------|
| pending | Task has been created but not yet started |
| running | Task is currently in progress |
| completed | Task has finished successfully |
| failed | Task has encountered an error and failed |
| cancelled | Task was cancelled before completion |

## Error Handling

The endpoints implement a consistent error handling approach:

1. **Authentication Errors**: Returns 401 Unauthorized if no valid user ID is found
2. **Resource Not Found**: Returns 404 Not Found if the requested task doesn't exist
3. **Service Unavailable**: Returns 503 Service Unavailable if the task service encounters an error
4. **Detailed Logging**: All errors are logged with appropriate severity, with full tracebacks in debug mode

## Usage Examples

### Retrieving All Tasks

```http
GET /api/v1/tasks
Authorization: Bearer {token}
```

### Retrieving Tasks with a Specific Status

```http
GET /api/v1/tasks?status=completed&limit=5
Authorization: Bearer {token}
```

### Retrieving a Specific Task

```http
GET /api/v1/tasks/task_abc123
Authorization: Bearer {token}
```

### Deleting a Task

```http
DELETE /api/v1/tasks/task_abc123
Authorization: Bearer {token}
```

## Security Considerations

The task routes implement several security measures:

1. **Authentication Check**: All operations require authentication
2. **Resource Ownership**: Users can only access and manage their own tasks
3. **ID Masking**: Task IDs are masked in logs to prevent information leakage
4. **Input Validation**: Request parameters are validated to prevent invalid operations

## Integration with Task Service

The task routes integrate with the TaskService through dependency injection, which provides the following capabilities:

1. **Task Tracking**: Creating and updating task records
2. **Status Management**: Updating task status as processing progresses
3. **Result Association**: Linking completed tasks to their result resources
4. **Error Handling**: Capturing and storing error information for failed tasks

## Related Documentation

- [Task Models](../../../models/task/response.md): Data models for task responses
- [Task Service](../../../services/task/service.md): Service for managing background tasks
- [Concept Generation](../concept/generation.md): Routes that create background tasks
- [Task Service Interface](../../../services/task/interface.md): Interface defining task service capabilities 