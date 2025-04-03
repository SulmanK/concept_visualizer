# Concept Storage and Retrieval API

This document describes the concept storage and retrieval endpoints in the Concept Visualizer API.

## Overview

The concept storage API provides functionality to:
- Store generated concepts for later retrieval
- List all concepts associated with a session
- Retrieve specific concepts by ID
- Delete concepts

## Endpoints

### Store Concept

```
POST /api/concept/store
```

Stores a generated concept in the database.

#### Request Body

```json
{
  "concept": {
    "image_b64": "base64-encoded-image-data",
    "color_palette": ["#1A2B3C", "#DEFABC", "#456789"],
    "prompt": "Generated prompt used for this concept"
  },
  "metadata": {
    "title": "My Company Logo",
    "description": "Logo design for my tech startup",
    "tags": ["tech", "modern", "blue"]
  }
}
```

Parameters:
- `concept`: The concept to store (required)
- `metadata`: Additional metadata about the concept (optional)

#### Response

```json
{
  "concept_id": "unique-concept-id",
  "created_at": "2023-04-01T12:34:56Z",
  "status": "success"
}
```

### List Concepts

```
GET /api/concept/list
```

Retrieves a list of all concepts associated with the current session.

#### Query Parameters

- `limit`: Maximum number of concepts to return (default: 10)
- `offset`: Offset for pagination (default: 0)
- `sort`: Sort order - "newest", "oldest" (default: "newest")
- `tags`: Filter by tags (comma-separated list)

#### Response

```json
{
  "concepts": [
    {
      "concept_id": "unique-concept-id-1",
      "thumbnail": "base64-encoded-thumbnail",
      "color_palette": ["#1A2B3C", "#DEFABC", "#456789"],
      "title": "My Company Logo",
      "created_at": "2023-04-01T12:34:56Z",
      "tags": ["tech", "modern", "blue"]
    },
    {
      "concept_id": "unique-concept-id-2",
      "thumbnail": "base64-encoded-thumbnail",
      "color_palette": ["#FFFFFF", "#000000", "#FF0000"],
      "title": "Alternative Logo Design",
      "created_at": "2023-04-01T11:22:33Z",
      "tags": ["tech", "bold", "red"]
    }
  ],
  "total": 5,
  "limit": 10,
  "offset": 0
}
```

### Get Concept

```
GET /api/concept/{concept_id}
```

Retrieves a specific concept by ID.

#### Path Parameters

- `concept_id`: The unique ID of the concept to retrieve

#### Response

```json
{
  "concept": {
    "concept_id": "unique-concept-id",
    "image_b64": "base64-encoded-image-data",
    "color_palette": ["#1A2B3C", "#DEFABC", "#456789"],
    "prompt": "Generated prompt used for this concept",
    "metadata": {
      "title": "My Company Logo",
      "description": "Logo design for my tech startup",
      "tags": ["tech", "modern", "blue"]
    },
    "created_at": "2023-04-01T12:34:56Z",
    "updated_at": "2023-04-01T12:34:56Z"
  }
}
```

### Delete Concept

```
DELETE /api/concept/{concept_id}
```

Deletes a specific concept by ID.

#### Path Parameters

- `concept_id`: The unique ID of the concept to delete

#### Response

```json
{
  "status": "success",
  "message": "Concept deleted successfully"
}
```

## Implementation Details

### Storage Backend

Concepts are stored in Supabase with the following components:
1. Database table for metadata and references
2. Storage bucket for actual image data
3. Thumbnails are generated automatically

### Access Control

- Concepts are associated with a specific session ID
- Only the session that created a concept can access it
- Session authentication is handled via cookies

### Data Retention

- Concepts are stored for a maximum of 30 days
- Automatic cleanup processes remove expired concepts
- There is a maximum limit of 50 concepts per session

## Error Handling

Common errors:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | validation_error | Invalid request parameters |
| 404 | resource_not_found | Concept not found |
| 401 | authentication_error | Invalid session ID |
| 503 | service_unavailable | Storage service unavailable |

## Best Practices

1. **Provide Descriptive Titles**: Add meaningful titles to your concepts for easier organization
2. **Use Tags**: Tags make it easier to filter and find concepts later
3. **Implement Pagination**: When retrieving lists, use pagination to improve performance
4. **Handle Image Loading Asynchronously**: Base64 images can be large, load them asynchronously in the client 