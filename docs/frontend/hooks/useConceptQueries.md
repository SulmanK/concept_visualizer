# useConceptQueries Hooks

The `useConceptQueries` module provides a collection of React Query hooks for fetching concept data from the API.

## Overview

These hooks handle data fetching, caching, and state management for concept-related API requests. They provide a standardized way to access concept data throughout the application, with built-in loading, error, and success states.

## Available Hooks

### `useRecentConcepts`

Fetches a list of the user's recent concepts with pagination, sorting, and filtering options.

#### Usage

```tsx
import { useConceptQueries } from 'hooks/useConceptQueries';

function RecentConceptsList() {
  const { 
    data, 
    isLoading, 
    error 
  } = useConceptQueries.useRecentConcepts({
    limit: 10,
    page: 1,
    sortOrder: 'newest'
  });
  
  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;
  
  return (
    <div>
      {data?.items.map(concept => (
        <ConceptCard key={concept.id} concept={concept} />
      ))}
    </div>
  );
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `options` | `RecentConceptsOptions` | No | See below | Query parameters |

```tsx
interface RecentConceptsOptions {
  limit?: number;              // Number of concepts per page
  page?: number;               // Page number (1-based)
  sortOrder?: SortOrder;       // Sort order ('newest', 'oldest', 'name', 'name-desc')
  searchTerm?: string;         // Search term to filter by
  status?: ConceptStatus[];    // Filter by status ('draft', 'complete', 'in-progress')
  tags?: string[];             // Filter by tags
  startDate?: Date | string;   // Filter by creation date range start
  endDate?: Date | string;     // Filter by creation date range end
}
```

Default options:

```tsx
{
  limit: 12,
  page: 1,
  sortOrder: 'newest'
}
```

#### Return Value

The hook returns a React Query result object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| `data` | `ConceptsResponse \| undefined` | Paginated concept data if successful |
| `isLoading` | `boolean` | `true` during initial load |
| `isFetching` | `boolean` | `true` during any loading state (including background refreshes) |
| `error` | `Error \| null` | Error object if the request failed |
| `refetch` | `() => Promise<QueryObserverResult>` | Function to manually refetch data |

```tsx
interface ConceptsResponse {
  items: Concept[];            // Array of concept objects
  totalItems: number;          // Total number of concepts matching query
  totalPages: number;          // Total number of pages
  currentPage: number;         // Current page number
}
```

### `useConceptById`

Fetches a single concept by its ID.

#### Usage

```tsx
import { useConceptQueries } from 'hooks/useConceptQueries';

function ConceptDetail({ conceptId }) {
  const { 
    data: concept, 
    isLoading, 
    error 
  } = useConceptQueries.useConceptById(conceptId);
  
  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;
  if (!concept) return <NotFoundMessage />;
  
  return (
    <div>
      <h1>{concept.title}</h1>
      <ConceptImage imageUrl={concept.imageUrl} />
      {/* Other concept details */}
    </div>
  );
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `conceptId` | `string` | Yes | - | ID of the concept to fetch |
| `options` | `UseQueryOptions` | No | - | React Query options |

#### Return Value

The hook returns a React Query result object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| `data` | `Concept \| undefined` | Concept data if successful |
| `isLoading` | `boolean` | `true` during initial load |
| `isFetching` | `boolean` | `true` during any loading state |
| `error` | `Error \| null` | Error object if the request failed |
| `refetch` | `() => Promise<QueryObserverResult>` | Function to manually refetch data |

### `useConceptVersionHistory`

Fetches the version history for a concept.

#### Usage

```tsx
import { useConceptQueries } from 'hooks/useConceptQueries';

function ConceptVersions({ conceptId }) {
  const { 
    data: versions, 
    isLoading 
  } = useConceptQueries.useConceptVersionHistory(conceptId);
  
  if (isLoading) return <LoadingIndicator />;
  
  return (
    <div>
      <h2>Version History</h2>
      <ul>
        {versions?.map(version => (
          <li key={version.id}>
            Version {version.version} - {new Date(version.createdAt).toLocaleDateString()}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

#### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `conceptId` | `string` | Yes | - | ID of the concept to fetch history for |
| `options` | `UseQueryOptions` | No | - | React Query options |

#### Return Value

The hook returns a React Query result object similar to the others, but with `data` being an array of concept versions:

```tsx
interface ConceptVersion {
  id: string;
  conceptId: string;
  version: number;
  imageUrl: string;
  prompt: string;
  createdAt: string;
}
```

## Implementation Details

These hooks are built with React Query for data fetching and state management. Key aspects include:

- **Automatic Caching**: Results are cached to minimize API requests
- **Background Refreshing**: Data is refreshed in the background when windows are refocused
- **Retry Logic**: Failed requests are automatically retried
- **Pagination Support**: Handles paginated data with metadata
- **Type Safety**: Fully typed parameters and return values

## Related Hooks

- [useConceptMutations](./useConceptMutations.md) - For creating and updating concepts
- [useExportImageMutation](./useExportImageMutation.md) - For exporting concept images 