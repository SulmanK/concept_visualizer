# Session Management API

This document describes the session management endpoints in the Concept Visualizer API.

## Overview

The session management API provides functionality to:
- Create and manage user sessions
- Synchronize client and server session IDs
- Track session data and usage statistics

Sessions are a core component of the application, enabling:
- Association of concepts with users without requiring authentication
- Rate limiting of resource-intensive operations
- Tracking of usage statistics
- Persistence of user preferences

## Endpoints

### Create or Get Session

```
POST /api/session/
```

Creates a new session or returns the existing one associated with the client.

#### Request Body

```json
{
  "client_session_id": "optional-client-provided-session-id"
}
```

Parameters:
- `client_session_id`: Optional client-provided session ID to sync with server (optional)

#### Response

```json
{
  "session_id": "unique-session-id",
  "is_new_session": true,
  "created_at": "2023-04-01T12:34:56Z",
  "last_active": "2023-04-01T12:34:56Z",
  "usage_stats": {
    "concepts_generated": 0,
    "concepts_refined": 0,
    "concepts_stored": 0
  }
}
```

The response also sets a cookie named `concept_session` with the session ID.

### Sync Session

```
POST /api/session/sync
```

Synchronizes client and server session IDs.

#### Request Body

```json
{
  "client_session_id": "client-provided-session-id"
}
```

Parameters:
- `client_session_id`: Client-provided session ID to sync with server (required)

#### Response

```json
{
  "session_id": "unique-session-id",
  "is_synced": true,
  "message": "Sessions synchronized successfully"
}
```

### Get Session Info

```
GET /api/session/info
```

Retrieves information about the current session.

#### Response

```json
{
  "session_id": "unique-session-id",
  "created_at": "2023-04-01T12:34:56Z",
  "last_active": "2023-04-01T12:34:56Z",
  "usage_stats": {
    "concepts_generated": 5,
    "concepts_refined": 2,
    "concepts_stored": 3
  },
  "rate_limits": {
    "concept_generation": {
      "limit": 10,
      "remaining": 5,
      "reset_at": "2023-05-01T00:00:00Z"
    },
    "concept_refinement": {
      "limit": 10,
      "remaining": 8,
      "reset_at": "2023-04-02T12:34:56Z"
    }
  }
}
```

## Implementation Details

### Session Storage

Sessions are stored in Supabase with metadata including:
1. Creation timestamp
2. Last activity timestamp
3. Usage statistics
4. Rate limit counters
5. Associated concepts

### Session ID Generation

Session IDs are UUID v4 strings generated server-side.

### Session Cookies

- Cookie name: `concept_session`
- SameSite: Lax
- Secure: True in production
- HttpOnly: True
- Max Age: 30 days

### Session Syncing

Session syncing allows users to:
1. Move between devices while maintaining the same session
2. Recover from cookie loss
3. Explicitly share sessions with others via the session ID

## Error Handling

Common errors:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 400 | validation_error | Invalid session ID format |
| 404 | resource_not_found | Session not found |
| 503 | service_unavailable | Session service unavailable |

## Best Practices

1. **Store the Session ID**: Client applications should store the session ID in local storage as a backup
2. **Handle Session Expiry**: Session cookies may expire; implement client-side logic to handle this
3. **Implement Session Syncing**: Allow users to manually sync sessions between devices when needed
4. **Respect Rate Limits**: Check remaining rate limits before making resource-intensive requests 