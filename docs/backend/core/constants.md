# Constants Module

The `constants.py` module defines application-wide constants used throughout the Concept Visualizer application to ensure consistency and avoid hardcoding values.

## Overview

This module centralizes important string constants, status codes, and other values that are referenced across multiple parts of the application. Using these constants instead of hardcoded values helps maintain consistency and makes future changes easier to implement.

## Task Status Constants

```python
TASK_STATUS_PENDING = "pending"
TASK_STATUS_PROCESSING = "processing"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"
```

These constants represent the various states of an asynchronous task in the system. They are used in:

- Task status tracking
- API responses
- Database records
- Frontend status displays

## Task Type Constants

```python
TASK_TYPE_GENERATION = "concept_generation"
TASK_TYPE_REFINEMENT = "concept_refinement"
```

These constants define the different types of tasks that can be performed in the application:

- `TASK_TYPE_GENERATION`: Creating a new concept from a prompt
- `TASK_TYPE_REFINEMENT`: Refining an existing concept with additional guidance

## Storage Constants

```python
BUCKET_NAME_CONCEPTS = settings.STORAGE_BUCKET_CONCEPT
BUCKET_NAME_PALETTES = settings.STORAGE_BUCKET_PALETTE
```

These constants define the storage bucket names used for storing different types of assets:

- `BUCKET_NAME_CONCEPTS`: Storage location for generated concept images
- `BUCKET_NAME_PALETTES`: Storage location for color palettes

Note that these values are loaded from the application settings, allowing them to be configured via environment variables.

## Usage Examples

### Using Task Status Constants

```python
from app.core.constants import TASK_STATUS_PENDING, TASK_STATUS_COMPLETED

async def update_task_status(task_id: str, status: str):
    """Update the status of a task."""
    # Validate status using constants
    valid_statuses = [TASK_STATUS_PENDING, TASK_STATUS_PROCESSING, 
                     TASK_STATUS_COMPLETED, TASK_STATUS_FAILED]
    
    if status not in valid_statuses:
        raise ValueError(f"Invalid status: {status}")
    
    # Update database
    await db.update_task(task_id, {"status": status})
    
    # If task is complete, perform additional actions
    if status == TASK_STATUS_COMPLETED:
        await notify_task_completion(task_id)
```

### Using Storage Constants

```python
from app.core.constants import BUCKET_NAME_CONCEPTS

async def store_concept_image(concept_id: str, image_data: bytes):
    """Store a concept image in the appropriate bucket."""
    path = f"{concept_id}/image.png"
    
    # Use the constant for bucket name
    await storage_client.upload(
        bucket=BUCKET_NAME_CONCEPTS,
        path=path,
        data=image_data,
        content_type="image/png"
    )
    
    return f"{BUCKET_NAME_CONCEPTS}/{path}"
```

## Best Practices

When using constants from this module:

1. Always import the specific constants you need, rather than the entire module
2. Use constants for any string or numeric value that appears in multiple places
3. Consider proposing new constants for the module when you find yourself repeating the same values

## Related Documentation

- [Config](config.md): Settings module that provides values for some constants
- [Task Service](../services/task/service.md): Service that uses task status constants 