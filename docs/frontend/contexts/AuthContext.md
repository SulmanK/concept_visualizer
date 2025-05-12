# AuthContext

The `AuthContext` manages user authentication state throughout the application, providing a centralized way to access and manipulate user session data. It supports both anonymous and email-based authentication using Supabase Auth.

## Overview

This context provides authentication functionality with these key features:

- Automatic anonymous authentication for new users
- Email linking for converting anonymous users to identified users
- Session management and token refresh handling
- User state persistence across page reloads
- Real-time auth state synchronization

## Context Interface

The `AuthContext` provides the following properties and methods:

```typescript
interface AuthContextType {
  // Current session object from Supabase
  session: Session | null;

  // Current user object from Supabase
  user: User | null;

  // Whether the current user is anonymous
  isAnonymous: boolean;

  // Whether authentication is being initialized
  isLoading: boolean;

  // Any authentication error that occurred
  error: Error | null;

  // Function to sign out the current user
  signOut: () => Promise<boolean>;

  // Function to link an email to an anonymous user
  linkEmail: (email: string) => Promise<boolean>;
}
```

## Usage

The context is accessed through various custom hooks from `hooks/useAuth.ts` that expose specific parts of the auth state:

```tsx
import {
  useAuth,
  useAuthUser,
  useUserId,
  useIsAnonymous,
  useAuthIsLoading,
} from "../hooks/useAuth";

function ProfileSection() {
  // Get all auth state
  const { user, isAnonymous, linkEmail, signOut } = useAuth();

  const handleEmailLink = async () => {
    const email = prompt("Enter your email to save your work:");
    if (email) {
      const success = await linkEmail(email);
      if (success) {
        alert("Your account has been upgraded!");
      }
    }
  };

  return (
    <div>
      <h2>Your Profile</h2>
      {isAnonymous ? (
        <>
          <p>You're using the app as a guest</p>
          <button onClick={handleEmailLink}>Save my work</button>
        </>
      ) : (
        <>
          <p>Welcome, {user?.email}</p>
          <button onClick={signOut}>Sign Out</button>
        </>
      )}
    </div>
  );
}

// Example using selective hooks for optimized re-renders
function UserIdDisplay() {
  // Only get and subscribe to the user ID
  const userId = useUserId();
  return <span>User ID: {userId || "Not signed in"}</span>;
}

function AnonymousBadge() {
  // Only get and subscribe to anonymous status
  const isAnonymous = useIsAnonymous();
  if (isAnonymous) {
    return <span className="badge">Guest User</span>;
  }
  return null;
}

function AuthGuard({ children }) {
  // Only get and subscribe to loading state
  const isLoading = useAuthIsLoading();

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return children;
}
```

## Implementation Details

### Authentication Flow

1. On application startup, the context checks for an existing session
2. If no session exists, it automatically creates an anonymous user
3. The context listens for auth state changes from Supabase
4. When state changes (sign-in, sign-out, token refresh), the context updates its state
5. Changes in authentication state are propagated to consuming components

### Session Management

- The context maintains the current session object from Supabase
- When the session token is refreshed, only the session is updated (not user state)
- If a significant change occurs (e.g., user ID changes), the full user state is updated

### Anonymous Authentication

The context uses metadata to track whether a user is anonymous:

```typescript
function determineIsAnonymous(session: Session | null): boolean {
  if (!session || !session.user) return true;
  return session.user.app_metadata?.is_anonymous === true;
}
```

### Performance Optimization

The context uses several techniques to optimize performance:

1. **Selective State Updates**: Only updates state when significant changes occur
2. **State Memoization**: Uses `useMemo` to prevent unnecessary re-renders
3. **Selective Context Consumption**: Provides granular hooks that only subscribe to specific parts of the state using `use-context-selector`

## Exposed Hooks

The following hooks are available in `hooks/useAuth.ts`:

| Hook                 | Returns           | Description                                       |
| -------------------- | ----------------- | ------------------------------------------------- |
| `useAuth()`          | `AuthContextType` | Full auth context with all properties and methods |
| `useAuthUser()`      | `User \| null`    | Current user object only                          |
| `useUserId()`        | `string \| null`  | Current user ID only                              |
| `useIsAnonymous()`   | `boolean`         | Whether current user is anonymous                 |
| `useAuthIsLoading()` | `boolean`         | Whether auth is currently initializing            |

## Error Handling

The context includes centralized error handling:

- Authentication errors are captured in the `error` state
- The context listens for a special `auth-error-needs-logout` event that can be dispatched elsewhere in the application to force a logout when authentication errors occur

## Related

- [supabaseClient](../services/supabaseClient.md) - Authentication service used by the context
- [RateLimitContext](./RateLimitContext.md) - Often used alongside auth for user-specific rate limits
- [useAuth.ts](../hooks/useAuth.md) - Hooks for accessing auth context data
