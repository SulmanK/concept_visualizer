# Contexts

The `contexts` directory contains React Context providers and hooks that manage global application state across components. These contexts enable components to access shared data and functionality without prop drilling.

## Overview

React Context is used in this application to provide state management for cross-cutting concerns that impact multiple components across the component tree. Each context follows a similar pattern:

1. A context object is created using `React.createContext()`
2. A provider component manages the state and exposes methods to update it
3. Custom hooks are exposed for consuming components to access the context

## Available Contexts

| Context                                   | Purpose                           | Key Features                                                      |
| ----------------------------------------- | --------------------------------- | ----------------------------------------------------------------- |
| [AuthContext](./AuthContext.md)           | Manages user authentication state | User sign-in/sign-out, session management, auth state persistence |
| [RateLimitContext](./RateLimitContext.md) | Tracks API rate limits            | Rate limit tracking, limit enforcement, real-time updates         |
| [TaskContext](./TaskContext.md)           | Manages background tasks          | Task tracking, notifications, progress updates                    |

## Design Principles

Our context implementation follows these principles:

1. **Self-contained state**: Each context manages its own internal state
2. **Minimalist API**: Contexts expose only what consuming components need
3. **Performance optimized**: Using memoization and careful re-rendering
4. **Type safety**: Full TypeScript support with proper typing
5. **Error handling**: Proper error states and recovery mechanisms

## Usage Pattern

Contexts are typically consumed using custom hooks:

```tsx
// Example of using the AuthContext
import { useAuth } from "../contexts/AuthContext";

function ProfileComponent() {
  const { user, isLoading, signOut } = useAuth();

  if (isLoading) return <LoadingIndicator />;

  if (!user) return <NotSignedInMessage />;

  return (
    <div>
      <h1>Welcome, {user.name}</h1>
      <button onClick={signOut}>Sign Out</button>
    </div>
  );
}
```

## Provider Setup

The context providers are typically mounted near the root of the application in the component tree:

```tsx
// In App.tsx or similar root component
import { AuthProvider } from "./contexts/AuthContext";
import { RateLimitProvider } from "./contexts/RateLimitContext";
import { TaskProvider } from "./contexts/TaskContext";

function App() {
  return (
    <AuthProvider>
      <RateLimitProvider>
        <TaskProvider>{/* Rest of the application */}</TaskProvider>
      </RateLimitProvider>
    </AuthProvider>
  );
}
```

## Related

- [hooks](../hooks/README.md) - Custom hooks that often work with contexts
- [services](../services/README.md) - Service layer that contexts often use for data access
