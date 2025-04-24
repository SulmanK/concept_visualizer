# useSessionQuery

The `useSessionQuery` module provides hooks for session management, specifically for synchronizing client-side session state with the backend server.

## Overview

This module exports the `useSessionSyncMutation` hook, which enables applications to maintain session continuity between the frontend and backend. This is essential for features that require tracking user sessions across page refreshes, browser sessions, or different devices.

## Usage

```tsx
import { useEffect } from "react";
import { useSessionSyncMutation } from "../hooks/useSessionQuery";
import { generateSessionId } from "../utils/sessionUtils";

function SessionManager() {
  const sessionSync = useSessionSyncMutation();

  useEffect(() => {
    // Get or create client session ID from local storage
    let clientSessionId = localStorage.getItem("client_session_id");
    if (!clientSessionId) {
      clientSessionId = generateSessionId();
      localStorage.setItem("client_session_id", clientSessionId);
    }

    // Sync session with backend
    sessionSync.mutate(
      { client_session_id: clientSessionId },
      {
        onSuccess: (data) => {
          console.log(`Session synced successfully: ${data.session_id}`);
          // Store additional session data if needed
        },
      },
    );
  }, [sessionSync]);

  return null; // This component doesn't render anything
}
```

## API

### useSessionSyncMutation

A mutation hook that sends the client's session ID to the backend for validation and tracking.

#### Return Value

Returns a React Query `UseMutationResult` with the following structure:

```typescript
{
  mutate: (input: SyncSessionInput) => void;
  mutateAsync: (input: SyncSessionInput) => Promise<SessionResponse>;
  isLoading: boolean;
  isError: boolean;
  error: Error | null;
  isSuccess: boolean;
  data: SessionResponse | undefined;
  // Additional React Query mutation properties
}
```

#### Input Type

The mutation accepts a `SyncSessionInput` object:

```typescript
interface SyncSessionInput {
  client_session_id: string; // The client-side session identifier
}
```

#### Response Type

The mutation returns a `SessionResponse` object:

```typescript
interface SessionResponse {
  session_id: string; // The server-side session identifier
  created: boolean; // Whether a new session was created on the server
  [key: string]: any; // Additional session metadata returned by the server
}
```

## Security Considerations

1. **Session ID Masking**: The hook includes a utility function `maskSessionId` that masks most of the session ID when logging, revealing only a few characters at the beginning and end. This prevents complete session IDs from appearing in logs.

2. **Retry Logic**: The mutation includes a retry mechanism (1 retry attempt) in case of network failures, ensuring better reliability without excessive retries that could amplify errors.

## Implementation Details

- The hook makes a POST request to `/sessions/sync` with the client's session ID
- Error handling is managed through the application's central error handling system
- Logging includes masked session IDs for debugging while maintaining security
- A single retry is attempted for failed requests before reporting an error

## Related

- `apiClient` - Used for making API requests
- `useErrorHandling` - Used for standardized error handling
- `AuthContext` - Often used in conjunction with session management
