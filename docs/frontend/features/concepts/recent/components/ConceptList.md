# ConceptList

The ConceptList component displays a grid of concept cards, representing the user's concepts in a visually appealing layout.

## Overview

This component provides a responsive grid layout for displaying concept thumbnail cards. It handles the organization of multiple concept items into a visually coherent collection with consistent spacing and alignment.

## Component Structure

```tsx
interface ConceptListProps {
  concepts: Concept[];
  onConceptSelect?: (conceptId: string) => void;
  emptyStateMessage?: string;
  columns?: 2 | 3 | 4;
  className?: string;
}

const ConceptList: React.FC<ConceptListProps> = ({
  concepts,
  onConceptSelect,
  emptyStateMessage = "No concepts found",
  columns = 3,
  className,
}) => {
  if (concepts.length === 0) {
    return (
      <div className="empty-state">
        <p>{emptyStateMessage}</p>
      </div>
    );
  }
  
  return (
    <div className={`concept-grid columns-${columns} ${className || ''}`}>
      {concepts.map((concept) => (
        <ConceptCard
          key={concept.id}
          concept={concept}
          onClick={() => onConceptSelect?.(concept.id)}
        />
      ))}
    </div>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `concepts` | `Concept[]` | Yes | - | Array of concept objects to display |
| `onConceptSelect` | `(conceptId: string) => void` | No | - | Callback when a concept is selected |
| `emptyStateMessage` | `string` | No | "No concepts found" | Message to display when no concepts are available |
| `columns` | `2 \| 3 \| 4` | No | 3 | Number of columns to display in the grid |
| `className` | `string` | No | - | Additional CSS class for styling |

## Features

- **Responsive Grid Layout**: Adjusts layout based on screen size and column prop
- **Empty State Handling**: Displays a user-friendly message when no concepts are available
- **Selection Handling**: Provides callbacks for concept selection
- **Customizable Styling**: Accepts custom CSS classes

## Dependencies

- `ConceptCard`: Individual card component for displaying a concept
- `Concept`: Type definition for concept data structure

## Related Components

- [ConceptCard](../../../components/ui/ConceptCard.md)
- [RecentConceptsPage](../RecentConceptsPage.md)

## Usage Example

```tsx
import { ConceptList } from './ConceptList';
import { useRouter } from 'next/router';

const MyConceptsSection = () => {
  const router = useRouter();
  const { data } = useConceptQueries.useRecentConcepts();
  
  const handleConceptSelect = (conceptId: string) => {
    router.push(`/concepts/${conceptId}`);
  };
  
  return (
    <section className="my-concepts-section">
      <h2>My Concepts</h2>
      <ConceptList 
        concepts={data?.items || []}
        onConceptSelect={handleConceptSelect}
        columns={4}
        emptyStateMessage="You haven't created any concepts yet"
      />
    </section>
  );
};
```

## Styling

The component uses CSS Grid for layout with responsive breakpoints. The number of columns can be controlled through the `columns` prop, which applies appropriate CSS classes. 