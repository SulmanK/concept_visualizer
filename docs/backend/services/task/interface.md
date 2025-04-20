# Task Service Interface

The `interface.py` module defines the interface for task management services in the Concept Visualizer API, establishing a contract for handling background tasks.

## Overview

The Task Service Interface provides a standardized contract for:

1. Creating and managing asynchronous background tasks
2. Tracking task status and progress
3. Associating tasks with their results
4. Retrieving task information for status monitoring

This interface ensures consistent task management across the application and allows for alternative implementations (e.g., for testing).

## TaskServiceInterface

The primary interface class:

```python
class TaskServiceInterface(abc.ABC):
    """Interface for services that handle task management."""
    
    @abc.abstractmethod
    async def create_task(
        self, 
        user_id: str, 
        task_type: str, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """Create a new task record."""
        pass
    
    # Other abstract methods...
```

## Key Operations

### Creating Tasks

```python
@abc.abstractmethod
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
    pass
```

### Updating Task Status

```python
@abc.abstractmethod
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
    pass
```

### Retrieving Tasks

```python
@abc.abstractmethod
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
    pass
```

```python
@abc.abstractmethod
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
    pass
```

### Lookups by Result ID

```python
@abc.abstractmethod
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
    pass
```

### Deleting Tasks

```python
@abc.abstractmethod
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
    pass
```

## Expected Implementations

Implementations of this interface should:

1. Provide proper task isolation between users
2. Support asynchronous operation
3. Handle race conditions with concurrent updates
4. Provide appropriate error handling
5. Support task metadata for flexible use cases

## Usage in Dependency Injection

This interface is typically used with FastAPI's dependency injection system:

```python
# In API routes
@router.post("/tasks/concept", response_model=TaskResponse)
async def create_concept_task(
    request: TaskRequest,
    task_service: TaskServiceInterface = Depends(get_task_service)
):
    task = await task_service.create_task(
        user_id=request.user_id,
        task_type="concept_generation",
        metadata={"prompt": request.prompt}
    )
    return {"task_id": task["id"]}
```

## Related Documentation

- [Task Service](service.md): Implementation of this interface
- [API Task Routes](../../api/routes/task/routes.md): API routes that use the task service
- [Task Response Models](../../models/task/response.md): Data models for task responses 