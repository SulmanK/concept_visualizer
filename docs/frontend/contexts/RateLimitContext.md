# RateLimitContext

The `RateLimitContext` manages API rate limit information across the application, providing components with access to current usage limits and methods for optimistic updates.

## Overview

This context is responsible for:

- Fetching and caching rate limit data from the backend
- Providing real-time access to remaining API call quotas
- Supporting optimistic UI updates when limits are consumed
- Enabling components to refresh limit data when needed

## Context Interface

The context provides the following properties and methods:

```typescript
interface RateLimitContextType {
  // Current rate limits data from the API
  rateLimits: RateLimitsResponse | null;

  // Whether rate limits are being fetched
  isLoading: boolean;

  // Any error that occurred during fetching
  error: string | null;

  // Function to refresh rate limit data
  refetch: (forceRefresh?: boolean) => Promise<void>;

  // Function to optimistically update a rate limit
  decrementLimit: (category: RateLimitCategory, amount?: number) => void;
}
```

## Usage

The context provides specialized selector hooks for optimal performance:

```tsx
import {
  useRateLimitsData,
  useRateLimitsLoading,
  useRateLimitsError,
  useRateLimitsRefetch,
  useRateLimitsDecrement,
  useRateLimitContext,
} from "../contexts/RateLimitContext";

// Component that only needs to display limits
function RateLimitDisplay() {
  // Only subscribes to the limits data, not other context changes
  const limits = useRateLimitsData();
  const isLoading = useRateLimitsLoading();

  if (isLoading) return <LoadingSpinner />;

  return (
    <div className="rate-limits">
      <h3>API Usage</h3>
      {limits &&
        Object.entries(limits.limits).map(([category, limit]) => (
          <div key={category} className="limit-item">
            <span>{category}: </span>
            <span>
              {limit.remaining}/{limit.limit}
            </span>
            <small>Resets: {new Date(limit.reset).toLocaleTimeString()}</small>
          </div>
        ))}
    </div>
  );
}

// Component that needs to consume a limit
function ConceptGenerator() {
  // Only subscribes to the decrement function
  const decrementLimit = useRateLimitsDecrement();

  const handleGenerate = async () => {
    // Update UI immediately
    decrementLimit("concept-generation");

    // Then make the actual API call
    await generateConcept(formData);
  };

  return <button onClick={handleGenerate}>Generate Concept</button>;
}

// Component that needs full rate limit context
function RateLimitManager() {
  // Uses the comprehensive hook (less performant but simpler)
  const { rateLimits, isLoading, error, refetch, decrementLimit } =
    useRateLimitContext();

  const handleRefresh = () => {
    refetch(true); // Force a fresh fetch
  };

  return (
    <div>
      <button onClick={handleRefresh}>Refresh Limits</button>
      {/* Display current limits and errors */}
    </div>
  );
}
```

## Rate Limits Data Structure

The rate limits data has the following structure:

```typescript
interface RateLimitsResponse {
  limits: {
    [category: string]: {
      limit: number; // Maximum allowed requests
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

## Implementation Details

### Data Fetching

The context uses the `useRateLimitsQuery` hook from React Query to fetch and cache rate limit data:

- Default polling every 60 seconds
- Background refreshes to avoid UI disruptions
- Cache invalidation when forcing a refresh

### Optimistic Updates

When a component indicates it will consume a rate limit (e.g., before making an API call), the `decrementLimit` function:

1. Gets the current rate limits from cache
2. Creates a copy to avoid mutation
3. Decrements the remaining count for the specified category
4. Updates the cache with the new values

This provides immediate UI feedback before the server confirms the limit change.

### Performance Optimization

The context uses several techniques to optimize performance:

1. **Selective Context Consumption**: Specialized hooks that only subscribe to specific parts of the state
2. **Context Selector Pattern**: Uses `use-context-selector` to prevent unnecessary re-renders
3. **Memoization**: Uses `useMemo` to prevent context value recreations

## Exposed Hooks

| Hook                       | Returns                                       | Description                 |
| -------------------------- | --------------------------------------------- | --------------------------- |
| `useRateLimitsData()`      | `RateLimitsResponse \| null`                  | Just the rate limits data   |
| `useRateLimitsLoading()`   | `boolean`                                     | Just the loading state      |
| `useRateLimitsError()`     | `string \| null`                              | Just the error state        |
| `useRateLimitsRefetch()`   | `(forceRefresh?: boolean) => Promise<void>`   | Just the refetch function   |
| `useRateLimitsDecrement()` | `(category: string, amount?: number) => void` | Just the decrement function |
| `useRateLimitContext()`    | `RateLimitContextType`                        | The complete context object |

## Related

- [useRateLimitsQuery](../hooks/useRateLimitsQuery.md) - The underlying hook used for data fetching
- [rateLimitService](../services/rateLimitService.md) - API service for rate limits
- [RateLimitsPanel](../components/RateLimitsPanel/RateLimitsPanel.md) - UI component that displays rate limits
