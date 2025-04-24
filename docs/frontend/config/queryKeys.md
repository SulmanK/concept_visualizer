# Query Keys Configuration

## Overview

The `queryKeys.ts` file defines a structured set of React Query cache keys used throughout the application. These keys are essential for proper caching, data invalidation, and dependency management in React Query.

## File Details

- **File Path**: `frontend/my-app/src/config/queryKeys.ts`
- **Type**: TypeScript Configuration File

## Query Keys Structure

```typescript
export const queryKeys = {
  concepts: {
    all: () => ["concepts"] as const,
    recent: (userId?: string, limit?: number) =>
      [...queryKeys.concepts.all(), "recent", userId, limit] as const,
    detail: (id?: string, userId?: string) =>
      [...queryKeys.concepts.all(), "detail", id, userId] as const,
  },

  tasks: {
    all: () => ["tasks"] as const,
    detail: (id?: string) => [...queryKeys.tasks.all(), "detail", id] as const,
  },

  mutations: {
    conceptGeneration: () => ["conceptGeneration"] as const,
    conceptRefinement: () => ["conceptRefinement"] as const,
    exportImage: () => ["exportImage"] as const,
  },

  rateLimits: () => ["rateLimits"] as const,

  user: {
    all: () => ["user"] as const,
    preferences: (userId?: string) =>
      [...queryKeys.user.all(), "preferences", userId] as const,
  },
};
```

Each key is a function that returns an array, allowing for parameters to be included in the key. The `as const` assertion ensures type safety.

## Key Categories

### Concept Keys

- `concepts.all()`: Base key for all concept-related queries
- `concepts.recent(userId, limit)`: Key for recent concepts queries, parameterized by user ID and limit
- `concepts.detail(id, userId)`: Key for specific concept details, parameterized by concept ID and user ID

### Task Keys

- `tasks.all()`: Base key for all task-related queries
- `tasks.detail(id)`: Key for specific task details, parameterized by task ID

### Mutation Keys

- `mutations.conceptGeneration()`: Key for concept generation mutations
- `mutations.conceptRefinement()`: Key for concept refinement mutations
- `mutations.exportImage()`: Key for image export mutations

### Other Keys

- `rateLimits()`: Key for rate limit queries
- `user.all()`: Base key for all user-related queries
- `user.preferences(userId)`: Key for user preferences queries

## Usage Examples

### In Query Hooks

```typescript
import { useQuery, useMutation, useQueryClient } from "react-query";
import { queryKeys } from "../config/queryKeys";
import { conceptService } from "../services/conceptService";

// Using in a query
export const useRecentConceptsQuery = (userId?: string, limit?: number) => {
  return useQuery(
    queryKeys.concepts.recent(userId, limit),
    () => conceptService.getRecentConcepts(userId, limit),
    {
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  );
};

// Using in a mutation with cache invalidation
export const useConceptGenerationMutation = () => {
  const queryClient = useQueryClient();

  return useMutation((data) => conceptService.generateConcept(data), {
    onSuccess: () => {
      // Invalidate and refetch recent concepts when a new one is created
      queryClient.invalidateQueries(queryKeys.concepts.all());
    },
  });
};
```

### For Cache Invalidation

```typescript
import { queryKeys } from "../config/queryKeys";

// In a component or service
const handleConceptUpdate = async (conceptId) => {
  await updateConcept(conceptId, updatedData);

  // Invalidate only the specific concept detail
  queryClient.invalidateQueries(queryKeys.concepts.detail(conceptId));

  // Also invalidate the recent concepts list
  queryClient.invalidateQueries(queryKeys.concepts.recent());
};
```

## Best Practices

1. **Always use these functions** instead of hardcoded arrays for query keys
2. **Structure keys hierarchically** with parent-child relationships
3. **Include relevant parameters** in keys to properly separate cache entries
4. **Use TypeScript's `as const`** for type safety
5. **Build related keys from base keys** for consistency
6. **Include user ID** in keys for user-specific data to ensure proper data isolation
