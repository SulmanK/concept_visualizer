# RecentConceptsSection

The RecentConceptsSection component displays a preview of the user's most recently created concepts on the landing page.

## Overview

This component provides quick access to the user's recent work, allowing them to resume previous concept creation sessions or view their latest outputs. It serves as both a convenience feature and a showcase of the user's work.

## Component Structure

```tsx
interface RecentConceptsSectionProps {
  concepts: Concept[];
  maxDisplay?: number;
  showViewAllLink?: boolean;
}

const RecentConceptsSection: React.FC<RecentConceptsSectionProps> = ({
  concepts,
  maxDisplay = 3,
  showViewAllLink = true,
}) => {
  // Show only up to maxDisplay concepts
  const displayConcepts = concepts.slice(0, maxDisplay);
  
  if (displayConcepts.length === 0) {
    return null; // Don't render if no concepts
  }
  
  return (
    <section className="recent-concepts-section">
      <div className="section-header">
        <h2 className="section-title">Your Recent Concepts</h2>
        
        {showViewAllLink && concepts.length > maxDisplay && (
          <Link href="/concepts/recent" className="view-all-link">
            View All Concepts
            <Icon name="arrow-right" size="small" />
          </Link>
        )}
      </div>
      
      <div className="recent-concepts-grid">
        {displayConcepts.map((concept) => (
          <ConceptCard
            key={concept.id}
            concept={concept}
            onClick={() => window.location.href = `/concepts/${concept.id}`}
          />
        ))}
      </div>
    </section>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `concepts` | `Concept[]` | Yes | - | Array of concept objects to display |
| `maxDisplay` | `number` | No | 3 | Maximum number of concepts to display |
| `showViewAllLink` | `boolean` | No | true | Whether to show the "View All" link |

## Features

- **Recent Concepts Preview**: Shows thumbnails of the user's most recent concepts
- **Adaptive Display**: Shows only up to a configurable maximum number of concepts
- **Quick Navigation**: Allows users to quickly access their recent work
- **View All Link**: Optional link to the full concepts page when more concepts exist

## Dependencies

- `ConceptCard`: Component for displaying individual concept previews
- `Link`: Navigation component for the "View All" link
- `Icon`: Icon component for the arrow icon in the link

## Types

```tsx
interface Concept {
  id: string;
  title: string;
  createdAt: string;
  thumbnailUrl: string;
  status: 'draft' | 'complete' | 'in-progress';
  // Other concept properties
}
```

## Styling

- **Grid Layout**: Responsive grid for concept cards
- **Section Header**: Styled header with title and optional link
- **Card Hover Effects**: Visual feedback on card interaction

## Related Components

- [ConceptCard](../../../../components/ui/ConceptCard.md)
- [LandingPage](../LandingPage.md)

## Accessibility

- Semantic HTML structure with proper heading hierarchy
- Keyboard navigation support for links and cards
- Appropriate ARIA attributes for interactive elements

## Usage

This component is typically used on the landing page to show the user's recent work:

```tsx
const LandingPage: React.FC = () => {
  const { data: recentConcepts } = useConceptQueries.useRecentConcepts({
    limit: 3,
    sortOrder: 'newest'
  });
  
  return (
    <MainLayout>
      {/* Other sections */}
      {recentConcepts?.items.length > 0 && (
        <RecentConceptsSection 
          concepts={recentConcepts.items}
          maxDisplay={3}
        />
      )}
    </MainLayout>
  );
};
```

## Conditional Rendering

The component automatically handles these edge cases:
- Returns `null` if no concepts are available (prevents rendering empty sections)
- Hides the "View All" link if there aren't more concepts than the display limit
- Limits display to the specified maximum number of concepts 