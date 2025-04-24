# useConfigQuery

The `useConfigQuery` hook is responsible for fetching and caching application configuration data from the backend. It provides a standardized way to access global application settings across the application.

## Overview

This hook leverages React Query to fetch configuration data from the `/health/config` endpoint with appropriate caching strategies. The configuration data is essential for various features of the application to operate correctly.

## Usage

```tsx
import { useConfigQuery } from "../hooks/useConfigQuery";

function MyComponent() {
  const { data: config, isLoading, error } = useConfigQuery();

  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      <h1>Application Configuration</h1>
      <p>Version: {config?.version}</p>
      <p>Storage enabled: {config?.storage?.enabled ? "Yes" : "No"}</p>
      {/* Display other configuration options as needed */}
    </div>
  );
}
```

## Parameters

The hook accepts an optional `options` object with the following properties:

| Parameter              | Type    | Default | Description                                                             |
| ---------------------- | ------- | ------- | ----------------------------------------------------------------------- |
| `enabled`              | boolean | `true`  | Controls whether the query should automatically execute                 |
| `refetchOnWindowFocus` | boolean | `false` | Controls whether the query should refetch when the window regains focus |

## Return Value

Returns a React Query `UseQueryResult` with the following structure:

```typescript
{
  data: AppConfig | undefined; // The configuration data if available
  isLoading: boolean; // True when the query is in progress
  isError: boolean; // True if the query encountered an error
  error: Error | null; // Error object if query failed
  // Additional React Query properties
}
```

## Error Handling

When the API request fails, the hook will:

1. Log the error to the console
2. Return a default configuration object to prevent application crashes
3. Report the error via the error handling system (but will not show a toast notification by default)

## Configuration Object Structure

The configuration object (`AppConfig`) typically includes:

```typescript
{
  version: string; // Application version
  environment: string; // Current environment (dev, test, prod)
  features: {
    // Feature flags
    [featureName: string]: boolean;
  };
  limits: {
    // API rate limits configuration
    [endpoint: string]: number;
  };
  storage: {
    // Storage configuration
    enabled: boolean;
    provider: string;
  };
  // Additional configuration properties
}
```

## Caching Strategy

- `staleTime`: 1 hour (3,600,000ms) - Configuration is considered fresh for an hour
- `cacheTime`: 24 hours (86,400,000ms) - Configuration is kept in cache for a day

The long cache times reflect that configuration data typically changes infrequently.

## Related

- `apiClient` - Used for making API requests
- `useErrorHandling` - Used for standardized error handling
- `configService` - Provides default configuration values and types
