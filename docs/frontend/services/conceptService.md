# conceptService

The `conceptService` provides a specialized API interface for interacting with concept-related endpoints. It encapsulates the logic for creating, fetching, and managing visual concepts within the application.

## Overview

This service acts as a facade over the general `apiClient`, providing concept-specific API methods. It handles:

- Fetching recent concepts for the current user
- Retrieving detailed concept information
- Facilitating the concept generation workflow
- Logging and error handling specific to concept operations

## API Methods

### fetchRecentConceptsFromApi

Retrieves a list of recently generated concepts for a user.

```typescript
function fetchRecentConceptsFromApi(
  userId: string,
  limit: number = 10,
): Promise<ConceptData[]>;
```

**Parameters:**

- `userId`: The ID of the user whose concepts to fetch
- `limit`: Maximum number of concepts to return (default: 10)

**Returns:**

- `Promise<ConceptData[]>`: A promise that resolves to an array of concept data objects

**Example:**

```typescript
import { fetchRecentConceptsFromApi } from "../services/conceptService";

// Usage in a component
async function getRecentConcepts(userId) {
  try {
    const concepts = await fetchRecentConceptsFromApi(userId, 5);
    console.log(`Found ${concepts.length} recent concepts`);
    return concepts;
  } catch (error) {
    console.error("Failed to fetch recent concepts:", error);
    return [];
  }
}
```

### fetchConceptDetailFromApi

Retrieves detailed information about a specific concept.

```typescript
function fetchConceptDetailFromApi(
  conceptId: string,
): Promise<ConceptData | null>;
```

**Parameters:**

- `conceptId`: The ID of the concept to fetch

**Returns:**

- `Promise<ConceptData | null>`: A promise that resolves to the concept data or null if not found

**Example:**

```typescript
import { fetchConceptDetailFromApi } from "../services/conceptService";

// Usage in a component
async function getConceptDetail(id) {
  try {
    const concept = await fetchConceptDetailFromApi(id);
    if (concept) {
      return concept;
    } else {
      console.log("Concept not found");
      return null;
    }
  } catch (error) {
    console.error("Error fetching concept detail:", error);
    return null;
  }
}
```

## Data Types

The service operates with the following data structures:

```typescript
interface ConceptData {
  id: string;
  user_id: string;
  prompt_text: string;
  theme_text?: string;
  created_at: string;
  updated_at: string;

  // Main concept image
  image_url?: string;

  // Color variations of the concept
  color_variations?: ColorVariation[];

  // Additional metadata
  metadata?: {
    generation_params?: any;
    tags?: string[];
    [key: string]: any;
  };
}

interface ColorVariation {
  id: string;
  concept_id: string;
  colors: string[];
  image_url?: string;
  created_at: string;
}
```

## Implementation Details

### Error Handling

The service includes specialized error handling for concept-related operations:

- For concept detail fetching, 404 errors are transformed into `null` returns rather than exceptions
- All other errors are logged and re-thrown for handling by the calling code

### Logging

The service includes detailed logging for debugging purposes:

- Logs the start and end time of API calls
- Records the number of concepts fetched
- Details color variation information when available
- Calculates and logs API call duration

## Usage with React Hooks

This service is typically used with custom hooks for data fetching:

```typescript
// In a custom hook
import { useQuery } from "@tanstack/react-query";
import { fetchRecentConceptsFromApi } from "../services/conceptService";

export function useRecentConcepts(userId: string, limit: number = 10) {
  return useQuery({
    queryKey: ["concepts", "recent", userId, limit],
    queryFn: () => fetchRecentConceptsFromApi(userId, limit),
    staleTime: 60000, // 1 minute
  });
}
```

## Related

- [apiClient](./apiClient.md) - The underlying HTTP client used by this service
- [useConceptQueries](../hooks/useConceptQueries.md) - React Query hooks for concepts
- [useConceptMutations](../hooks/useConceptMutations.md) - Mutation hooks for concepts
