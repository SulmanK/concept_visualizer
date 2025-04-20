# Rate Limit Service

The Rate Limit Service manages rate limit information from the backend API. It tracks usage limits, remaining quota, and reset times for various API endpoints to help prevent hitting rate limits and to provide feedback to users.

## Core Features

- Fetches and caches rate limit information from the backend
- Extracts rate limit data from API response headers
- Maps API endpoints to rate limit categories
- Provides methods to check if actions are allowed based on limits
- Formats time remaining until limit reset in a user-friendly way
- Integrates with React Query for reactive cache management

## Key Interfaces

```typescript
export interface RateLimitInfo {
  limit: string;
  remaining: number;
  reset_after: number;
  error?: string;
}

export interface RateLimitsResponse {
  user_identifier: string;
  limits: {
    generate_concept: RateLimitInfo;
    refine_concept: RateLimitInfo;
    store_concept: RateLimitInfo;
    get_concepts: RateLimitInfo;
    sessions: RateLimitInfo;
    export_action: RateLimitInfo;
  };
  default_limits: string[];
}

export type RateLimitCategory = 
  | 'generate_concept' 
  | 'refine_concept' 
  | 'store_concept' 
  | 'get_concepts' 
  | 'sessions' 
  | 'export_action';
```

## Key Functions

| Function | Description |
|----------|-------------|
| `mapEndpointToCategory(endpoint)` | Maps an API endpoint path to its corresponding rate limit category |
| `extractRateLimitHeaders(response, endpoint)` | Extracts rate limit information from response headers and updates the cache |
| `getRateLimitInfoForCategory(category)` | Gets the current rate limit info for a specific category |
| `decrementRateLimit(category, amount)` | Optimistically decrements the remaining count for a category (for UI updates before API confirmation) |
| `fetchRateLimits(forceRefresh)` | Fetches rate limits from the backend API |
| `formatTimeRemaining(seconds)` | Formats seconds into a human-readable time string |

## Usage Examples

### Checking if an Action is Allowed

```typescript
import { getRateLimitInfoForCategory } from '../services/rateLimitService';

const canGenerateConcept = () => {
  const limits = getRateLimitInfoForCategory('generate_concept');
  return limits && limits.remaining > 0;
};

// In a component
const GenerateButton = () => {
  const disabled = !canGenerateConcept();
  
  return (
    <button disabled={disabled}>
      Generate Concept
    </button>
  );
};
```

### Displaying Rate Limit Information

```tsx
import { useRateLimitsQuery } from '../hooks/useRateLimitsQuery';
import { formatTimeRemaining } from '../services/rateLimitService';

const RateLimitDisplay = () => {
  const { data: rateLimits, isLoading } = useRateLimitsQuery();
  
  if (isLoading || !rateLimits) return <div>Loading limits...</div>;
  
  const generateLimit = rateLimits.limits.generate_concept;
  
  return (
    <div>
      <p>Concepts remaining: {generateLimit.remaining}</p>
      <p>Resets in: {formatTimeRemaining(generateLimit.reset_after)}</p>
    </div>
  );
};
```

## Implementation Notes

- Rate limits are stored in React Query's cache for reactive updates
- The service maintains a mapping between API endpoints and rate limit categories
- When response headers contain rate limit information, the cache is automatically updated
- For optimistic UI updates, the `decrementRateLimit` function can be called before API responses arrive
- Time formatting supports multiple granularities (seconds, minutes, hours) 