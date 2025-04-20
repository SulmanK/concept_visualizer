# RefinementHeader

The RefinementHeader component provides contextual information and navigation options at the top of the refinement page.

## Overview

This component serves as the header section for the refinement page, displaying the concept title, version information, and providing navigation options. It helps users understand which concept they are refining and keeps track of the version history.

## Component Structure

```tsx
interface RefinementHeaderProps {
  conceptTitle: string;
  versionNumber: number;
  onBackClick?: () => void;
}

const RefinementHeader: React.FC<RefinementHeaderProps> = ({
  conceptTitle,
  versionNumber,
  onBackClick,
}) => {
  return (
    <header className="refinement-header">
      <div className="header-content">
        <div className="title-container">
          {onBackClick && (
            <button 
              className="back-button"
              onClick={onBackClick}
              aria-label="Go back"
            >
              <Icon name="arrow-left" />
            </button>
          )}
          
          <div className="title-info">
            <h1 className="concept-title">{conceptTitle}</h1>
            <div className="version-badge">
              Version {versionNumber}
            </div>
          </div>
        </div>
        
        <div className="header-actions">
          <Link href={`/concepts/${conceptTitle.toLowerCase().replace(/\s+/g, '-')}`} className="view-details-link">
            View Details
          </Link>
        </div>
      </div>
      
      <div className="refinement-description">
        <p>
          Refine your concept by providing additional feedback and specific change requests. 
          Your refinements will be used to generate an improved version while preserving 
          elements you specify.
        </p>
      </div>
    </header>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `conceptTitle` | `string` | Yes | - | Title of the concept being refined |
| `versionNumber` | `number` | Yes | - | Current version number of the concept |
| `onBackClick` | `() => void` | No | - | Callback when back button is clicked |

## Features

- **Concept Title**: Clearly displays the title of the concept being refined
- **Version Badge**: Shows the current version number
- **Back Navigation**: Optional back button for navigation
- **Detail Link**: Link to view the full concept details
- **Descriptive Text**: Brief explanation of the refinement process

## Dependencies

- `Icon`: Icon component for the back arrow
- `Link`: Link component for navigation

## Styling

- **Prominent Title**: Clear visual hierarchy with the concept title
- **Version Indicator**: Visually distinct badge for version number
- **Responsive Layout**: Adapts to different screen sizes
- **Consistent Styling**: Follows the application's design system

## Related Components

- [RefinementPage](../RefinementPage.md)
- [RefinementForm](./RefinementForm.md)

## Accessibility

- Back button has proper aria-label
- Semantic HTML structure with proper heading hierarchy
- Sufficient color contrast for all text elements
- Keyboard navigation support

## Usage Example

```tsx
const RefinementPage: React.FC = () => {
  const router = useRouter();
  const { data: concept } = useConceptQueries.useConceptById('concept-123');
  
  const handleBackClick = useCallback(() => {
    router.back();
  }, [router]);
  
  if (!concept) {
    return <LoadingIndicator />;
  }
  
  return (
    <div className="refinement-page">
      <RefinementHeader
        conceptTitle={concept.title}
        versionNumber={concept.version}
        onBackClick={handleBackClick}
      />
      
      {/* Rest of refinement page content */}
    </div>
  );
};
```

## Behavior

- Back button navigates to the previous page in the browser history
- Version badge updates automatically when the concept version changes
- Detail link navigates to the concept detail page 