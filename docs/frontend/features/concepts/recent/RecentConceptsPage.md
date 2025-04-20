# RecentConceptsPage

The RecentConceptsPage component displays a list of the user's recently created concepts, providing a gallery view with filtering and sorting options.

## Overview

This page serves as a dashboard for users to browse, manage, and revisit their previously generated concepts. It provides a visual grid of concept cards with thumbnail previews and essential metadata.

## Features

- **Gallery View**: Display concepts in a responsive grid layout
- **Sorting**: Sort concepts by creation date, name, or other attributes
- **Filtering**: Filter concepts by status, tags, or other properties
- **Pagination**: Navigate through large collections of concepts
- **Quick Actions**: Access common actions directly from the concept cards

## Component Structure

```tsx
const RecentConceptsPage: React.FC = () => {
  // State management for sorting, filtering, pagination
  const [sortOrder, setSortOrder] = useState<SortOrder>('newest');
  const [currentPage, setCurrentPage] = useState(1);
  
  // Data fetching with React Query
  const { data, isLoading, error } = useConceptQueries.useRecentConcepts({
    sortOrder,
    page: currentPage,
    limit: CONCEPTS_PER_PAGE
  });
  
  return (
    <MainLayout>
      <PageHeader title="Your Recent Concepts" />
      <RecentConceptsHeader 
        onSortChange={setSortOrder}
        currentSort={sortOrder}
      />
      
      {/* Error and loading states handled by this component */}
      <QueryResultHandler
        isLoading={isLoading}
        error={error}
        data={data}
        loadingComponent={<ConceptListSkeleton />}
        errorComponent={<ErrorMessage />}
      >
        {(conceptsData) => (
          <>
            <ConceptList concepts={conceptsData.items} />
            <Pagination 
              currentPage={currentPage}
              totalPages={conceptsData.totalPages}
              onPageChange={setCurrentPage}
            />
          </>
        )}
      </QueryResultHandler>
    </MainLayout>
  );
};
```

## Dependencies

- `ConceptList`: Renders the grid of concept cards
- `RecentConceptsHeader`: Contains sorting and filtering controls
- `QueryResultHandler`: Handles loading, error, and data states
- `Pagination`: Provides pagination controls
- `MainLayout`: Standard page layout with header, footer, and main content area

## Props

This component does not accept any props as it's a top-level page component.

## State Management

- Local state for UI controls (sorting, filtering, pagination)
- Remote state managed with React Query hooks from `useConceptQueries`

## Related Components

- [ConceptList](./components/ConceptList.md)
- [RecentConceptsHeader](./components/RecentConceptsHeader.md)

## Usage

This page is typically accessed via the main navigation or from the dashboard. It's rendered as part of the main application routes:

```tsx
<Route path="/concepts/recent" element={<RecentConceptsPage />} />
``` 