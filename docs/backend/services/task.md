# Task Service

The Task Service is responsible for managing background tasks in the application, providing functionality to create, update, retrieve, and delete task records.

## Overview

The Task Service provides a layer of abstraction for working with asynchronous task records in the database. It handles operations related to tracking the state of long-running operations, such as concept generation and refinement.

## Dependencies

The service relies on the following dependencies:

- `SupabaseClient`: Client for interacting with the Supabase database

## Key Methods

### `create_task`

Creates a new task record in the database.

```python
async def create_task(
    self, 
    user_id: str, 
    task_type: str, 
    metadata: Dict[str, Any] = None
) -> Dict[str, Any]
```

**Parameters**:
- `user_id`: ID of the user who owns the task
- `task_type`: Type of task (e.g., 'concept_generation', 'concept_refinement')
- `metadata`: Optional metadata associated with the task

**Returns**:
- Task data including the generated task ID

**Process**:
1. Generates a unique task ID
2. Creates a record with initial status 'pending'
3. Stores the record in the database
4. Returns the created task data

### `update_task_status`

Updates the status of an existing task.

```python
async def update_task_status(
    self,
    task_id: str,
    status: str,
    result_id: Optional[str] = None,
    error_message: Optional[str] = None
) -> Dict[str, Any]
```

**Parameters**:
- `task_id`: ID of the task to update
- `status`: New status ('processing', 'completed', 'failed')
- `result_id`: Optional ID of the result entity (e.g., concept_id)
- `error_message`: Optional error message if status is 'failed'

**Returns**:
- Updated task data

**Process**:
1. Prepares update data with new status and timestamp
2. Updates the task record in the database
3. Returns the updated task data

### `get_task`

Retrieves a task by its ID.

```python
async def get_task(self, task_id: str, user_id: str) -> Dict[str, Any]
```

**Parameters**:
- `task_id`: ID of the task to retrieve
- `user_id`: ID of the user who owns the task

**Returns**:
- Task data

**Process**:
1. Queries the database for the task with matching ID and user ID
2. Returns the task data if found
3. Raises a `TaskNotFoundError` if not found

### `get_tasks_by_user`

Retrieves multiple tasks for a specific user.

```python
async def get_tasks_by_user(
    self, 
    user_id: str, 
    status: Optional[str] = None,
    limit: int = 10
) -> List[Dict[str, Any]]
```

**Parameters**:
- `user_id`: ID of the user whose tasks to retrieve
- `status`: Optional status filter (e.g., 'pending', 'completed')
- `limit`: Maximum number of tasks to return

**Returns**:
- List of task data objects

**Process**:
1. Builds a query for tasks with matching user ID
2. Adds status filter if provided
3. Orders tasks by creation date (descending)
4. Limits the number of results
5. Returns the list of tasks

### `delete_task`

Deletes a task or marks it as deleted.

```python
async def delete_task(self, task_id: str, user_id: str) -> bool
```

**Parameters**:
- `task_id`: ID of the task to delete
- `user_id`: ID of the user who owns the task

**Returns**:
- Boolean indicating success or failure

**Process**:
1. Queries the database for the task with matching ID and user ID
2. If found, marks the task as deleted or removes it entirely
3. Returns True if deletion was successful, False otherwise

### `get_task_by_result_id`

Retrieves a task by the ID of its result.

```python
async def get_task_by_result_id(self, result_id: str, user_id: str) -> Optional[Dict[str, Any]]
```

**Parameters**:
- `result_id`: ID of the result entity (e.g., concept_id)
- `user_id`: ID of the user who owns the task

**Returns**:
- Task data if found, None otherwise

**Process**:
1. Queries the database for tasks with matching result ID and user ID
2. Returns the first matching task if found, None otherwise

## Error Handling

The service uses custom exceptions to handle various error scenarios:

- `TaskError`: Base exception for task-related errors
- `TaskNotFoundError`: Exception for when a task is not found

## Usage

The service is typically accessed through dependency injection in the API routes:

```python
@router.get("/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    task_service: TaskServiceInterface = Depends(get_task_service),
    user_id: str = Depends(get_current_user_id)
):
    try:
        task = await task_service.get_task(task_id=task_id, user_id=user_id)
        return task
    except TaskNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task not found")
```

## Service Role Client

The service attempts to use a service role client for database operations to bypass Row Level Security (RLS) policies, with a fallback to the regular client if the service role client is not available. This ensures that the service can perform operations even when called from background tasks where the user context may not be available. 