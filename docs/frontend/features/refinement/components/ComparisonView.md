# ComparisonView

The ComparisonView component displays a side-by-side comparison of the current concept version with previous versions, allowing users to see the evolution of their concept through the refinement process.

## Overview

This component helps users understand how their concept has changed over time by showing the current version alongside previous iterations. It provides visual comparison tools and allows users to navigate through the version history.

## Component Structure

```tsx
interface ComparisonViewProps {
  currentVersion: ConceptVersion;
  previousVersions: ConceptVersion[];
}

const ComparisonView: React.FC<ComparisonViewProps> = ({
  currentVersion,
  previousVersions,
}) => {
  const [selectedVersionIndex, setSelectedVersionIndex] = useState<number>(0);
  const selectedVersion = previousVersions[selectedVersionIndex];
  
  return (
    <section className="comparison-view">
      <h2 className="section-title">Version Comparison</h2>
      
      <div className="version-selector">
        <label htmlFor="version-select">Compare with:</label>
        <Select
          id="version-select"
          value={String(selectedVersionIndex)}
          onChange={(e) => setSelectedVersionIndex(Number(e.target.value))}
          options={previousVersions.map((version, index) => ({
            value: String(index),
            label: `Version ${version.version} (${new Date(version.createdAt).toLocaleDateString()})`,
          }))}
        />
      </div>
      
      <div className="comparison-container">
        <div className="version-card">
          <h3>Previous Version {selectedVersion.version}</h3>
          <div className="image-container">
            <OptimizedImage
              src={selectedVersion.imageUrl}
              alt={`Version ${selectedVersion.version}`}
              width={400}
              height={300}
            />
          </div>
          <div className="prompt-container">
            <h4>Original Prompt:</h4>
            <p>{selectedVersion.prompt}</p>
          </div>
        </div>
        
        <div className="version-card current">
          <h3>Current Version {currentVersion.version}</h3>
          <div className="image-container">
            <OptimizedImage
              src={currentVersion.imageUrl}
              alt={`Version ${currentVersion.version} (current)`}
              width={400}
              height={300}
            />
          </div>
          <div className="prompt-container">
            <h4>Refined Prompt:</h4>
            <p>{currentVersion.prompt}</p>
          </div>
        </div>
      </div>
      
      <div className="comparison-controls">
        <Button
          variant="secondary"
          disabled={selectedVersionIndex === 0}
          onClick={() => setSelectedVersionIndex(prev => Math.max(0, prev - 1))}
        >
          Previous Version
        </Button>
        
        <Button
          variant="secondary"
          disabled={selectedVersionIndex === previousVersions.length - 1}
          onClick={() => setSelectedVersionIndex(prev => Math.min(previousVersions.length - 1, prev + 1))}
        >
          Next Version
        </Button>
      </div>
    </section>
  );
};
```

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `currentVersion` | `ConceptVersion` | Yes | - | The current version of the concept |
| `previousVersions` | `ConceptVersion[]` | Yes | - | Array of previous concept versions |

## Types

```tsx
interface ConceptVersion {
  id: string;
  version: number;
  imageUrl: string;
  prompt: string;
  createdAt: string;
  // Other properties
}
```

## Features

- **Side-by-Side Comparison**: Visual comparison of current and selected previous versions
- **Version Selection**: Dropdown to select which previous version to compare
- **Version Navigation**: Buttons to navigate through version history
- **Prompt Comparison**: Shows the prompts for both versions to understand textual changes
- **Responsive Layout**: Adapts to different screen sizes

## Dependencies

- `OptimizedImage`: Component for displaying concept images
- `Select`: Dropdown component for version selection
- `Button`: Button component for navigation controls

## State Management

- Local state for selected version index
- Props for version data

## Related Components

- [RefinementPage](../RefinementPage.md)
- [RefinementForm](./RefinementForm.md)

## Accessibility

- Proper labeling for interactive elements
- Keyboard navigation for version selection
- Descriptive alt text for images
- Semantic HTML structure

## Usage Example

```tsx
const RefinementPageContent: React.FC = () => {
  const { data: concept } = useConceptQueries.useConceptById('concept-123');
  
  if (!concept || !concept.previousVersions?.length) {
    return null;
  }
  
  return (
    <div className="refinement-page-content">
      {/* Other content */}
      <ComparisonView
        currentVersion={concept}
        previousVersions={concept.previousVersions}
      />
    </div>
  );
};
```

## Styling

- Clear visual distinction between current and previous versions
- Consistent card styling for each version
- Responsive grid layout for comparison view
- Visual indicators for version numbers 