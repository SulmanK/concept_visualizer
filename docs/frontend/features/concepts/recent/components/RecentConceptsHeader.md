# RecentConceptsHeader

The RecentConceptsHeader component provides controls for sorting, filtering, and managing concepts within the Recent Concepts page.

## Overview

This component renders a header section with interactive controls that allow users to sort and filter their concept list. It also provides buttons for creating new concepts and potentially other bulk actions.

## Component Structure

```tsx
interface RecentConceptsHeaderProps {
  onSortChange: (sort: SortOrder) => void;
  currentSort: SortOrder;
  onFilterChange?: (filters: ConceptFilters) => void;
  currentFilters?: ConceptFilters;
  totalConcepts?: number;
}

const RecentConceptsHeader: React.FC<RecentConceptsHeaderProps> = ({
  onSortChange,
  currentSort,
  onFilterChange,
  currentFilters = {},
  totalConcepts = 0,
}) => {
  return (
    <div className="recent-concepts-header">
      <div className="header-left">
        <h1>Your Concepts</h1>
        {totalConcepts > 0 && (
          <span className="concept-count">{totalConcepts} concepts</span>
        )}
      </div>
      
      <div className="header-controls">
        <div className="sort-controls">
          <label htmlFor="sort-select">Sort by:</label>
          <Select
            id="sort-select"
            value={currentSort}
            onChange={(e) => onSortChange(e.target.value as SortOrder)}
            options={[
              { value: 'newest', label: 'Newest first' },
              { value: 'oldest', label: 'Oldest first' },
              { value: 'name', label: 'Name (A-Z)' },
              { value: 'name-desc', label: 'Name (Z-A)' },
            ]}
          />
        </div>
        
        {onFilterChange && (
          <FilterControls 
            filters={currentFilters}
            onChange={onFilterChange}
          />
        )}
        
        <Button 
          variant="primary"
          icon="plus"
          onClick={() => window.location.href = '/concepts/new'}
        >
          New Concept
        </Button>
      </div>
    </div>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `onSortChange` | `(sort: SortOrder) => void` | Yes | - | Callback when sorting option changes |
| `currentSort` | `SortOrder` | Yes | - | Current sort order value |
| `onFilterChange` | `(filters: ConceptFilters) => void` | No | - | Callback when filters change |
| `currentFilters` | `ConceptFilters` | No | `{}` | Current applied filters |
| `totalConcepts` | `number` | No | 0 | Total number of concepts (for displaying count) |

## Types

```tsx
type SortOrder = 'newest' | 'oldest' | 'name' | 'name-desc';

interface ConceptFilters {
  status?: ConceptStatus[];
  tags?: string[];
  dateRange?: {
    start: Date;
    end: Date;
  };
}

type ConceptStatus = 'draft' | 'complete' | 'in-progress';
```

## Features

- **Sorting Controls**: Allow sorting by date, name, or other attributes
- **Filtering Options**: Filter concepts by status, tags, or date range
- **Create Button**: Quick access to creating new concepts
- **Count Display**: Shows the total number of concepts matching current filters

## Dependencies

- `Select`: Dropdown component for selecting sort options
- `Button`: Standard button component
- `FilterControls`: Component for managing filters (if implemented)

## Related Components

- [ConceptList](./ConceptList.md)
- [RecentConceptsPage](../RecentConceptsPage.md)

## Usage Example

```tsx
const RecentConceptsPage = () => {
  const [sortOrder, setSortOrder] = useState<SortOrder>('newest');
  const [filters, setFilters] = useState<ConceptFilters>({});
  
  // Data fetching with filters and sorting
  const { data } = useConceptQueries.useRecentConcepts({
    sortOrder,
    ...filters,
  });
  
  return (
    <div className="recent-concepts-page">
      <RecentConceptsHeader
        onSortChange={setSortOrder}
        currentSort={sortOrder}
        onFilterChange={setFilters}
        currentFilters={filters}
        totalConcepts={data?.totalItems}
      />
      
      {/* ... rest of the page */}
    </div>
  );
};
```

## Accessibility

- Sort select input has proper labeling
- Interactive elements have appropriate ARIA attributes
- Focus management follows best practices 