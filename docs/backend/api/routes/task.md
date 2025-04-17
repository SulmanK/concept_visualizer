# Task API Routes

This document describes the API routes for managing background tasks.

## Base Path

```
/api/tasks
```

## Authentication

All routes require authentication with a valid user token in the `Authorization` header:

```
Authorization: Bearer <user_id>
```

## Data Models

### Task Response

```json
{
  "id": "task-uuid",
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:01:00.000Z",
  "user_id": "user-uuid",
  "type": "concept_generation",
  "status": "completed",
  "result_id": "concept-uuid",
  "metadata": {
    "logo_description": "A modern tree logo",
    "theme_description": "Blue and green color scheme"
  },
  "error_message": null
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the task |
| `created_at` | string | Timestamp of task creation |
| `updated_at` | string | Timestamp of last update |
| `user_id` | string | ID of the user who owns the task |
| `type` | string | Type of task (e.g., 'concept_generation') |
| `status` | string | Current status ('pending', 'processing', 'completed', 'failed') |
| `result_id` | string | ID of the result entity (e.g., concept_id) if completed |
| `metadata` | object | Additional information about the task |
| `error_message` | string | Error message if status is 'failed' |

## Routes

### Get Task

Retrieves a specific task by its ID.

**URL**: `/api/tasks/{task_id}`

**Method**: `GET`

**URL Parameters**:
- `task_id`: The ID of the task to retrieve

**Success Response**:
- **Code**: 200 OK
- **Content**: Task Response object

**Error Responses**:
- **Code**: 404 Not Found
  - **Content**: `{ "detail": "Task not found" }`
- **Code**: 401 Unauthorized
  - **Content**: `{ "detail": "Unauthorized" }`

**Example**:

```http
GET /api/tasks/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer user-123
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "created_at": "2023-01-01T00:00:00.000Z",
  "updated_at": "2023-01-01T00:01:00.000Z",
  "user_id": "user-123",
  "type": "concept_generation",
  "status": "completed",
  "result_id": "concept-456",
  "metadata": {
    "logo_description": "A modern tree logo",
    "theme_description": "Blue and green color scheme"
  },
  "error_message": null
}
```

### Get User Tasks

Retrieves all tasks for the authenticated user.

**URL**: `/api/tasks`

**Method**: `GET`

**Query Parameters**:
- `status` (optional): Filter tasks by status ('pending', 'processing', 'completed', 'failed')
- `limit` (optional): Maximum number of tasks to return (default: 10)

**Success Response**:
- **Code**: 200 OK
- **Content**: Array of Task Response objects

**Error Responses**:
- **Code**: 401 Unauthorized
  - **Content**: `{ "detail": "Unauthorized" }`

**Example**:

```http
GET /api/tasks?status=completed&limit=5
Authorization: Bearer user-123
```

Response:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2023-01-01T00:00:00.000Z",
    "updated_at": "2023-01-01T00:01:00.000Z",
    "user_id": "user-123",
    "type": "concept_generation",
    "status": "completed",
    "result_id": "concept-456",
    "metadata": {
      "logo_description": "A modern tree logo"
    }
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "created_at": "2023-01-02T00:00:00.000Z",
    "updated_at": "2023-01-02T00:01:00.000Z",
    "user_id": "user-123",
    "type": "concept_refinement",
    "status": "completed",
    "result_id": "concept-789",
    "metadata": {
      "refinement_prompt": "Add more blue"
    }
  }
]
```

### Delete Task

Deletes a specific task.

**URL**: `/api/tasks/{task_id}`

**Method**: `DELETE`

**URL Parameters**:
- `task_id`: The ID of the task to delete

**Success Response**:
- **Code**: 200 OK
- **Content**: `{ "success": true }`

**Error Responses**:
- **Code**: 404 Not Found
  - **Content**: `{ "detail": "Task not found" }`
- **Code**: 401 Unauthorized
  - **Content**: `{ "detail": "Unauthorized" }`

**Example**:

```http
DELETE /api/tasks/550e8400-e29b-41d4-a716-446655440000
Authorization: Bearer user-123
```

Response:
```json
{
  "success": true
}
```

## Integration with Other Features

Tasks are typically created as part of other operations in the API, such as concept generation and refinement. For example:

1. When a user initiates a concept generation (`POST /api/concepts/generate-with-palettes`), a task is created
2. The task ID is returned to the client immediately with status 'pending'
3. The generation process continues in the background
4. The client can poll the task status using `GET /api/tasks/{task_id}` to check progress
5. When the task completes, the status is updated to 'completed' and a `result_id` is added
6. The client can then retrieve the completed concept using `GET /api/concepts/{result_id}`

This pattern allows for efficient handling of long-running operations while providing clients with immediate feedback and a way to track progress. 