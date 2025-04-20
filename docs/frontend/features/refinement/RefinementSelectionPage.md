# RefinementSelectionPage

The RefinementSelectionPage component allows users to select which concept(s) they want to refine from their collection.

## Overview

This page serves as an intermediary step in the refinement workflow, allowing users to browse and select concepts for refinement. It displays a grid of the user's concepts with options to filter, sort, and select concepts for the refinement process.

## Component Structure

```tsx
const RefinementSelectionPage: React.FC = () => {
  const router = useRouter();
  const [selectedConceptIds, setSelectedConceptIds] = useState<string[]>([]);
  const [sortOrder, setSortOrder] = useState<SortOrder>('newest');
  const [searchTerm, setSearchTerm] = useState<string>('');
  
  const { data: concepts, isLoading } = useConceptQueries.useRecentConcepts({
    sortOrder,
    searchTerm,
    limit: 20,
  });
  
  const handleConceptSelect = useCallback((conceptId: string) => {
    setSelectedConceptIds((prev) => {
      // For single selection, replace the array
      // For multi-selection, would toggle the selection
      return [conceptId];
    });
  }, []);
  
  const handleProceedToRefinement = useCallback(() => {
    if (selectedConceptIds.length === 0) {
      // Show error or warning
      return;
    }
    
    // Navigate to refinement page with the selected concept
    router.push(`/concepts/${selectedConceptIds[0]}/refine`);
  }, [selectedConceptIds, router]);
  
  return (
    <MainLayout>
      <header className="refinement-selection-header">
        <h1>Select a Concept to Refine</h1>
        <p>Choose a concept to refine and improve based on additional feedback</p>
      </header>
      
      <div className="selection-controls">
        <div className="search-bar">
          <Input
            type="search"
            placeholder="Search concepts..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            icon="search"
          />
        </div>
        
        <div className="sort-control">
          <label htmlFor="sort-select">Sort by:</label>
          <Select
            id="sort-select"
            value={sortOrder}
            onChange={(e) => setSortOrder(e.target.value as SortOrder)}
            options={[
              { value: 'newest', label: 'Newest first' },
              { value: 'oldest', label: 'Oldest first' },
              { value: 'name', label: 'Name (A-Z)' },
              { value: 'name-desc', label: 'Name (Z-A)' },
            ]}
          />
        </div>
      </div>
      
      <div className="concepts-grid">
        {isLoading ? (
          <LoadingIndicator />
        ) : concepts?.items.length === 0 ? (
          <div className="empty-state">
            <p>No concepts found. Try adjusting your search or creating a new concept.</p>
            <Button
              variant="primary"
              onClick={() => router.push('/concepts/new')}
            >
              Create New Concept
            </Button>
          </div>
        ) : (
          concepts?.items.map((concept) => (
            <ConceptCard
              key={concept.id}
              concept={concept}
              isSelected={selectedConceptIds.includes(concept.id)}
              onClick={() => handleConceptSelect(concept.id)}
              selectable
            />
          ))
        )}
      </div>
      
      <div className="action-bar">
        <Button
          variant="secondary"
          onClick={() => router.back()}
        >
          Cancel
        </Button>
        
        <Button
          variant="primary"
          onClick={handleProceedToRefinement}
          disabled={selectedConceptIds.length === 0}
        >
          Proceed to Refinement
        </Button>
      </div>
    </MainLayout>
  );
};
```

## Features

- **Concept Selection**: Allow users to select concept(s) for refinement
- **Search Functionality**: Search through concepts by name or description
- **Sorting Options**: Sort concepts by different criteria (date, name)
- **Visual Selection**: Visual indication of selected concepts
- **Empty State Handling**: Proper handling when no concepts are available
- **Action Controls**: Proceed to refinement or cancel the workflow

## Dependencies

- `ConceptCard`: Component for displaying and selecting concepts
- `Input`: Text input component for search functionality
- `Select`: Dropdown component for sorting options
- `Button`: Button component for actions
- `LoadingIndicator`: Component for loading state
- `useConceptQueries`: Hooks for fetching concept data
- `useRouter`: Router hook for navigation

## Props

This component does not accept any props as it's a top-level page component.

## Types

```tsx
type SortOrder = 'newest' | 'oldest' | 'name' | 'name-desc';
```

## State Management

- Local state for selected concepts, sort order, and search term
- React Query for data fetching
- Loading and empty states handled appropriately

## Related Components

- [ConceptCard](../../../components/ui/ConceptCard.md)
- [RefinementPage](./RefinementPage.md)

## Usage

This page is typically accessed when a user wants to refine one of their existing concepts:

```tsx
<Route path="/concepts/refine" element={<RefinementSelectionPage />} />
```

Users can navigate to this page from various points in the application:

```tsx
// From a dashboard or concepts list
<Button
  onClick={() => router.push('/concepts/refine')}
>
  Refine a Concept
</Button>
```

## Accessibility

- Form inputs have proper labels
- Interactive elements have appropriate ARIA attributes
- Loading and empty states are properly communicated
- Keyboard navigation for selection and actions 