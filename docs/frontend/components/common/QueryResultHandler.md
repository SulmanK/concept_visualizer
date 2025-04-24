# QueryResultHandler Component

The `QueryResultHandler` is a utility component that provides standardized handling of React Query results, including loading, error, and empty states.

## Overview

This component simplifies working with data fetching by providing a consistent way to handle the different states of a query (loading, error, empty, and success). It reduces boilerplate in components that use React Query.

## Usage

```tsx
import { QueryResultHandler } from "components/common/QueryResultHandler";
import { useQuery } from "@tanstack/react-query";
import { getConceptList } from "services/conceptService";

function ConceptList() {
  const conceptsQuery = useQuery(["concepts"], getConceptList);

  return (
    <QueryResultHandler
      query={conceptsQuery}
      loadingComponent={<ConceptListSkeleton />}
      errorComponent={(error) => <ErrorMessage error={error} />}
      emptyComponent={<EmptyConceptList />}
    >
      {(data) => (
        <div className="concept-list">
          {data.map((concept) => (
            <ConceptCard key={concept.id} concept={concept} />
          ))}
        </div>
      )}
    </QueryResultHandler>
  );
}
```

## Props

| Prop               | Type                                                      | Required | Description                                       |
| ------------------ | --------------------------------------------------------- | -------- | ------------------------------------------------- |
| `query`            | `UseQueryResult<TData, TError>`                           | Yes      | The React Query result object                     |
| `loadingComponent` | `React.ReactNode`                                         | No       | Component to display during loading state         |
| `errorComponent`   | `React.ReactNode \| ((error: TError) => React.ReactNode)` | No       | Component or render function for error state      |
| `emptyComponent`   | `React.ReactNode \| ((data: TData) => React.ReactNode)`   | No       | Component or render function for empty data state |
| `emptyCheck`       | `(data: TData) => boolean`                                | No       | Function to determine if data is considered empty |
| `children`         | `(data: TData) => React.ReactNode`                        | Yes      | Render function for success state with data       |

## Implementation Details

The component evaluates the query state in a specific order:

1. First checks if the query is in a loading state
2. Then checks for errors
3. Then checks if the data is empty (using the provided `emptyCheck` function or a default one)
4. Finally renders the success state with the data

```tsx
import React from "react";
import { UseQueryResult } from "@tanstack/react-query";
import { LoadingIndicator } from "components/ui/LoadingIndicator";
import { ErrorMessage } from "components/ui/ErrorMessage";
import { EmptyState } from "components/ui/EmptyState";

interface QueryResultHandlerProps<TData, TError> {
  query: UseQueryResult<TData, TError>;
  loadingComponent?: React.ReactNode;
  errorComponent?: React.ReactNode | ((error: TError) => React.ReactNode);
  emptyComponent?: React.ReactNode | ((data: TData) => React.ReactNode);
  emptyCheck?: (data: TData) => boolean;
  children: (data: TData) => React.ReactNode;
}

export function QueryResultHandler<TData, TError>({
  query,
  loadingComponent = <LoadingIndicator />,
  errorComponent = (error) => <ErrorMessage error={error as Error} />,
  emptyComponent = <EmptyState message="No data found" />,
  emptyCheck,
  children,
}: QueryResultHandlerProps<TData, TError>) {
  const { isLoading, isError, data, error } = query;

  // Show loading state
  if (isLoading) {
    return <>{loadingComponent}</>;
  }

  // Show error state
  if (isError && error) {
    return (
      <>
        {typeof errorComponent === "function"
          ? errorComponent(error)
          : errorComponent}
      </>
    );
  }

  // Data should exist at this point
  if (!data) {
    return (
      <>
        {typeof emptyComponent === "function"
          ? emptyComponent(null as any)
          : emptyComponent}
      </>
    );
  }

  // Check if data is empty using the provided function or a default check
  const isEmpty = emptyCheck
    ? emptyCheck(data)
    : Array.isArray(data)
    ? data.length === 0
    : Object.keys(data).length === 0;

  // Show empty state
  if (isEmpty) {
    return (
      <>
        {typeof emptyComponent === "function"
          ? emptyComponent(data)
          : emptyComponent}
      </>
    );
  }

  // Show success state with data
  return <>{children(data)}</>;
}
```

## Examples

### Basic Usage with Default Components

```tsx
import { QueryResultHandler } from "components/common/QueryResultHandler";
import { useTasksQuery } from "hooks/useTaskQueries";

function TaskList() {
  const tasksQuery = useTasksQuery();

  return (
    <QueryResultHandler query={tasksQuery}>
      {(tasks) => (
        <ul>
          {tasks.map((task) => (
            <li key={task.id}>{task.name}</li>
          ))}
        </ul>
      )}
    </QueryResultHandler>
  );
}
```

### Custom Components for All States

```tsx
import { QueryResultHandler } from "components/common/QueryResultHandler";
import { useConceptQuery } from "hooks/useConceptQueries";

function ConceptDetail({ conceptId }) {
  const conceptQuery = useConceptQuery(conceptId);

  return (
    <QueryResultHandler
      query={conceptQuery}
      loadingComponent={<ConceptDetailSkeleton />}
      errorComponent={(error) => (
        <ConceptErrorState
          message={error.message}
          onRetry={() => conceptQuery.refetch()}
        />
      )}
      emptyComponent={
        <EmptyConceptDetail message="This concept could not be found" />
      }
    >
      {(concept) => <ConceptDetailView concept={concept} />}
    </QueryResultHandler>
  );
}
```

### Custom Empty Check

```tsx
import { QueryResultHandler } from "components/common/QueryResultHandler";
import { useUserProfileQuery } from "hooks/useUserQueries";

function UserProfile() {
  const profileQuery = useUserProfileQuery();

  return (
    <QueryResultHandler
      query={profileQuery}
      emptyCheck={(profile) => !profile.name || !profile.email}
      emptyComponent={<IncompleteProfileNotice />}
    >
      {(profile) => <ProfileDisplay profile={profile} />}
    </QueryResultHandler>
  );
}
```
