# Task Service

The `service.py` module provides the implementation of the task management service for the Concept Visualizer API.

## Overview

The Task Service manages asynchronous background tasks in the application, offering:

1. Task creation with metadata for long-running operations
2. Status tracking for operations like concept generation and refinement
3. User-specific task history and management
4. Error handling and status reporting

This service uses Supabase as the underlying storage mechanism for tasks.

## TaskService Class

The primary implementation class:

```python
class TaskService(TaskServiceInterface):
    """Service for managing background tasks."""
    
    def __init__(self, client: SupabaseClient):
        """
        Initialize task service with Supabase client.
        
        Args:
            client: Supabase client for interacting with the database
        """
        self.client = client
        self.logger = logging.getLogger("task_service")
```

## Key Operations

### Creating Tasks

```python
async def create_task(
    self, 
    user_id: str, 
    task_type: str, 
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]:
    """
    Create a new task record.
    
    Args:
        user_id: ID of the user who owns the task
        task_type: Type of task (e.g. 'concept_generation', 'concept_refinement')
        metadata: Optional metadata associated with the task
            
    Returns:
        Task data including the generated task ID
        
    Raises:
        TaskError: If creation fails
    """
    # Implementation...
```

This method:
- Generates a unique UUID for the task
- Records creation timestamp
- Initializes the task with "pending" status
- Stores metadata for context
- Uses service role client where available for privileged operations
- Provides fallback to regular client if needed

### Updating Task Status

```python
async def update_task_status(
    self,
    task_id: str,
    status: str,
    result_id: Optional[str] = None,
    error_message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Update the status of a task.
    
    Args:
        task_id: ID of the task to update
        status: New status ('processing', 'completed', 'failed')
        result_id: Optional ID of the result entity (e.g. concept_id)
        error_message: Optional error message if status is 'failed'
        
    Returns:
        Updated task data
        
    Raises:
        TaskNotFoundError: If task not found
        TaskError: If update fails
    """
    # Implementation...
```

Key features:
- Updates timestamps for tracking progress
- Links to result entities (like generated concepts)
- Records error information for failed tasks
- Provides detailed logging with sensitive ID masking

### Task Retrieval

```python
async def get_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
    """
    Get a task by ID.
    
    Args:
        task_id: ID of the task to retrieve
        user_id: ID of the user who owns the task
        
    Returns:
        Task data
        
    Raises:
        TaskNotFoundError: If task not found
        TaskError: If retrieval fails
    """
    # Implementation...
```

```python
async def get_tasks_by_user(
    self, 
    user_id: str, 
    status: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Get tasks for a user.
    
    Args:
        user_id: ID of the user who owns the tasks
        status: Optional status to filter by
        limit: Maximum number of tasks to return
        
    Returns:
        List of task data
        
    Raises:
        TaskError: If retrieval fails
    """
    # Implementation...
```

These methods provide:
- User-specific task filtering for security
- Optional status filtering for UI displays
- Pagination control with limits
- Consistent error handling

### Looking Up Tasks by Result

```python
async def get_task_by_result_id(self, result_id: str, user_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a task by result ID.
    
    Args:
        result_id: ID of the result entity (e.g. concept_id)
        user_id: ID of the user who owns the task
        
    Returns:
        Task data if found, None otherwise
        
    Raises:
        TaskError: If retrieval fails
    """
    # Implementation...
```

This specialized lookup:
- Finds the task that generated a particular result
- Enables tracking the origin of generated content
- Maintains user security boundaries

### Task Deletion

```python
async def delete_task(self, task_id: str, user_id: str) -> bool:
    """
    Delete a task.
    
    Args:
        task_id: ID of the task to delete
        user_id: ID of the user who owns the task
        
    Returns:
        True if successfully deleted
        
    Raises:
        TaskNotFoundError: If task not found
        TaskError: If deletion fails
    """
    # Implementation...
```

Supports:
- User-specific cleanup operations
- Security validation before deletion
- Comprehensive error handling and logging

## Custom Exceptions

The service defines task-specific exceptions:

```python
class TaskError(Exception):
    """Base exception for task-related errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(TaskError):
    """Exception raised when a task is not found."""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        message = f"Task with ID {mask_id(task_id)} not found"
        super().__init__(message)
```

These exceptions:
- Provide specific error types for different scenarios
- Include automatic ID masking for security
- Enable consistent error handling across the application

## Security Considerations

The task service implements several security measures:

1. **User Verification**: All operations verify the requesting user owns the task
2. **PII Protection**: Uses `mask_id()` for all logged IDs
3. **Service Role Escalation**: Uses the service role only when necessary
4. **Graceful Fallbacks**: Degrades gracefully if service role not available

## Usage Examples

### Creating a Task for Concept Generation

```python
# Create a task for concept generation
task = await task_service.create_task(
    user_id=user_id,
    task_type="concept_generation",
    metadata={
        "logo_description": "A modern logo for a tech startup",
        "theme_description": "Futuristic with blue tones"
    }
)

# Use the task ID for tracking
task_id = task["id"]
```

### Updating Task Progress

```python
# Update to processing status when starting work
await task_service.update_task_status(
    task_id=task_id,
    status="processing"
)

# When concept is generated, update to completed with the result ID
await task_service.update_task_status(
    task_id=task_id,
    status="completed",
    result_id=concept_id
)

# If something goes wrong, record the error
await task_service.update_task_status(
    task_id=task_id,
    status="failed",
    error_message="Failed to generate concept: Invalid prompt"
)
```

## Related Documentation

- [Task Service Interface](interface.md): Interface implemented by this service
- [API Task Routes](../../api/routes/task/routes.md): API routes that use this service
- [Task Response Models](../../models/task/response.md): Data models for task responses
- [Supabase Client](../../core/supabase/client.md): Database client used by this service 