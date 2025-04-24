# useRateLimitsQuery

The `useRateLimitsQuery` hook provides access to API rate limit information and manages the caching and refresh of this data throughout the application. It also offers utilities for optimistically updating rate limit counts.

## Overview

This hook fetches rate limit data from the backend and maintains it in the React Query cache. It's designed to ensure that users have up-to-date information about their API usage limits, without requiring frequent server requests.

## Usage

```tsx
import { useRateLimitsQuery } from "../hooks/useRateLimitsQuery";

function RateLimitDisplay() {
  const {
    data: rateLimits,
    isLoading,
    error,
    decrementLimit,
    refetch,
  } = useRateLimitsQuery();

  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;

  const conceptGenLimit = rateLimits?.limits?.["concept-generation"];

  const handleGenerateConcept = () => {
    // Optimistically update rate limit before making the API call
    decrementLimit("concept-generation");

    // Make your API call...
  };

  return (
    <div>
      <h2>Rate Limits</h2>
      {conceptGenLimit && (
        <div>
          <p>
            Concept Generation: {conceptGenLimit.remaining}/
            {conceptGenLimit.limit}
          </p>
          <p>Resets: {new Date(conceptGenLimit.reset).toLocaleString()}</p>
        </div>
      )}
      <button onClick={() => refetch()}>Refresh Limits</button>
      <button onClick={handleGenerateConcept}>Generate Concept</button>
    </div>
  );
}
```

## Return Value

The hook returns an object with the following properties:

| Property         | Type                                                     | Description                                          |
| ---------------- | -------------------------------------------------------- | ---------------------------------------------------- |
| `data`           | `RateLimitsResponse \| undefined`                        | The rate limits data from the server                 |
| `isLoading`      | `boolean`                                                | True when the query is loading                       |
| `error`          | `Error \| null`                                          | Error object if the query failed                     |
| `refetch`        | `() => Promise<...>`                                     | Function to force a fresh data fetch from the server |
| `decrementLimit` | `(category: RateLimitCategory, amount?: number) => void` | Function to optimistically decrement a limit         |

## Rate Limits Response Structure

The `RateLimitsResponse` object has the following structure:

```typescript
interface RateLimitsResponse {
  limits: {
    [category: string]: {
      limit: number; // Maximum number of requests allowed
      remaining: number; // Number of requests remaining
      reset: number; // Timestamp when the limit will reset
    };
  };
  global?: {
    limit: number;
    remaining: number;
    reset: number;
  };
}
```

Common categories include:

- `'concept-generation'`
- `'concept-refinement'`
- `'export'`

## Optimistic Updates

The `decrementLimit` function allows for optimistic updates to the rate limit cache. This is useful for providing immediate feedback to users before the server confirms the request. The updates are performed by:

1. Retrieving the current rate limits from the React Query cache
2. Creating a deep copy to avoid mutation
3. Decrementing the remaining count for the specified category
4. Updating the cache with the new values

## Enhanced Refetch

The hook provides a custom `refetch` function that:

1. Forces a fresh request to the server with `force=true`
2. Updates the React Query cache with the fresh data
3. Handles error cases gracefully

## Companion Hook: useOptimisticRateLimitUpdate

The module also exports a separate hook `useOptimisticRateLimitUpdate` that provides just the `decrementLimit` functionality without fetching the rate limits. This is useful for components that need to update limits but don't need to display them.

```tsx
import { useOptimisticRateLimitUpdate } from "../hooks/useRateLimitsQuery";

function ConceptGenerator() {
  const { decrementLimit } = useOptimisticRateLimitUpdate();

  const handleGenerate = async () => {
    decrementLimit("concept-generation");
    // Generate concept logic...
  };

  return <button onClick={handleGenerate}>Generate</button>;
}
```

## Related

- `rateLimitService` - Provides the API client for rate limit data
- `useErrorHandling` - Used for standardized error handling
- `RateLimitContext` - For application-wide access to rate limit status
