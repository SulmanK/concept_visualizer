# useConceptQueries Hooks

The `useConceptQueries` module provides a collection of React Query hooks for fetching concept data from the API.

## Overview

These hooks handle data fetching, caching, and state management for concept-related API requests. They provide a standardized way to access concept data throughout the application, with built-in loading, error, and success states.

## Available Hooks

### `useRecentConcepts`

Fetches a list of the user's recent concepts.

#### Usage

```tsx
import { useRecentConcepts } from "hooks/useConceptQueries";
import { useUserId } from "hooks/useAuth";

function RecentConceptsList() {
  const userId = useUserId();
  const { data, isLoading, error } = useRecentConcepts(userId, 10);

  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;

  return (
    <div>
      {data?.map((concept) => (
        <ConceptCard key={concept.id} concept={concept} />
      ))}
    </div>
  );
}
```

#### Parameters

| Parameter | Type                  | Required | Default | Description                   |
| --------- | --------------------- | -------- | ------- | ----------------------------- |
| `userId`  | `string \| undefined` | Yes      | -       | User ID to fetch concepts for |
| `limit`   | `number`              | No       | 10      | Number of concepts to fetch   |

#### Return Value

The hook returns a React Query result object with the following properties:

| Property     | Type                                 | Description                                                      |
| ------------ | ------------------------------------ | ---------------------------------------------------------------- |
| `data`       | `ConceptData[] \| undefined`         | Array of concept data if successful                              |
| `isLoading`  | `boolean`                            | `true` during initial load                                       |
| `isFetching` | `boolean`                            | `true` during any loading state (including background refreshes) |
| `error`      | `Error \| null`                      | Error object if the request failed                               |
| `refetch`    | `() => Promise<QueryObserverResult>` | Function to manually refetch data                                |

```tsx
interface ConceptData {
  id: string;
  user_id: string;
  logo_description: string;
  theme_description: string;
  image_path: string;
  image_url: string;
  created_at: string;
  color_variations?: ColorVariationData[];
  storage_path?: string;
}

interface ColorVariationData {
  id: string;
  concept_id: string;
  palette_name: string;
  colors: string[];
  description?: string;
  image_path: string;
  image_url: string;
  created_at: string;
  storage_path?: string;
}
```

### `useConceptDetail`

Fetches a single concept by its ID.

#### Usage

```tsx
import { useConceptDetail } from "hooks/useConceptQueries";
import { useUserId } from "hooks/useAuth";

function ConceptDetail({ conceptId }) {
  const userId = useUserId();
  const {
    data: concept,
    isLoading,
    error,
  } = useConceptDetail(conceptId, userId);

  if (isLoading) return <LoadingIndicator />;
  if (error) return <ErrorMessage error={error} />;
  if (!concept) return <NotFoundMessage />;

  return (
    <div>
      <h1>Concept Detail</h1>
      <img src={concept.image_url} alt="Concept" />
      <p>Logo Description: {concept.logo_description}</p>
      <p>Theme Description: {concept.theme_description}</p>

      {/* Color variations */}
      {concept.color_variations && concept.color_variations.length > 0 && (
        <div>
          <h2>Color Variations</h2>
          {concept.color_variations.map((variation) => (
            <div key={variation.id}>
              <p>{variation.palette_name}</p>
              <img src={variation.image_url} alt={variation.palette_name} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

#### Parameters

| Parameter   | Type                  | Required | Default | Description                |
| ----------- | --------------------- | -------- | ------- | -------------------------- |
| `conceptId` | `string \| undefined` | Yes      | -       | ID of the concept to fetch |
| `userId`    | `string \| undefined` | Yes      | -       | User ID for authentication |

#### Return Value

The hook returns a React Query result object with the following properties:

| Property     | Type                                 | Description                        |
| ------------ | ------------------------------------ | ---------------------------------- |
| `data`       | `ConceptData \| null \| undefined`   | Concept data if successful         |
| `isLoading`  | `boolean`                            | `true` during initial load         |
| `isFetching` | `boolean`                            | `true` during any loading state    |
| `error`      | `Error \| null`                      | Error object if the request failed |
| `refetch`    | `() => Promise<QueryObserverResult>` | Function to manually refetch data  |

## Implementation Details

These hooks are built with React Query for data fetching and state management. Key aspects include:

- **API Integration**: Hooks use `fetchRecentConceptsFromApi` and `fetchConceptDetailFromApi` from the concept service
- **Automatic Caching**: Results are cached with a stale time of 1 minute to minimize API requests
- **Background Refreshing**: Data is refreshed in the background when windows are refocused
- **Error Handling**: Specialized error handling through the `useErrorHandling` hook
- **Type Safety**: Fully typed parameters and return values
- **Conditional Fetching**: Queries only run when required parameters are available (`enabled` option)

## Related Hooks

- [useGenerateConceptMutation](./useConceptMutations.md) - For creating concepts
- [useRefineConceptMutation](./useConceptMutations.md) - For refining concepts
- [useAuth](./useAuth.md) - For getting the current user ID
