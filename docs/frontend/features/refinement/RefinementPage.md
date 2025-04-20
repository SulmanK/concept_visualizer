# RefinementPage

The RefinementPage component provides an interface for users to refine and iterate on existing concept visualizations.

## Overview

This page allows users to provide additional feedback and refine their concepts after initial generation. Users can make adjustments to their original prompt, view side-by-side comparisons with previous versions, and generate refined versions of their concepts.

## Component Structure

```tsx
interface RefinementPageProps {
  conceptId: string;
}

const RefinementPage: React.FC<RefinementPageProps> = ({ conceptId }) => {
  const { data: concept, isLoading: isLoadingConcept } = useConceptQueries.useConceptById(conceptId);
  const { mutate: refine, isPending: isRefining } = useConceptMutations.useRefineConcept();
  
  const [refinementFormData, setRefinementFormData] = useState<RefinementFormData>({
    additionalFeedback: '',
    preserveElements: [],
    changeRequests: [],
  });
  
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();
    
    if (!concept) return;
    
    refine({
      conceptId: concept.id,
      ...refinementFormData,
    }, {
      onSuccess: (refinedConcept) => {
        // Handle success - maybe show comparison view
      },
    });
  }, [concept, refinementFormData, refine]);
  
  if (isLoadingConcept) {
    return <LoadingIndicator />;
  }
  
  if (!concept) {
    return <ErrorMessage message="Concept not found" />;
  }
  
  return (
    <MainLayout>
      <RefinementHeader 
        conceptTitle={concept.title}
        versionNumber={concept.version}
      />
      
      <div className="refinement-container">
        <div className="left-panel">
          <ConceptImage 
            imageUrl={concept.imageUrl}
            altText={`${concept.title} - Version ${concept.version}`}
          />
        </div>
        
        <div className="right-panel">
          <RefinementForm
            formData={refinementFormData}
            onChange={setRefinementFormData}
            onSubmit={handleSubmit}
            isSubmitting={isRefining}
            originalPrompt={concept.prompt}
          />
        </div>
      </div>
      
      {concept.previousVersions && concept.previousVersions.length > 0 && (
        <ComparisonView
          currentVersion={concept}
          previousVersions={concept.previousVersions}
        />
      )}
      
      <RefinementActions
        onSave={() => {/* Save functionality */}}
        onExport={() => {/* Export functionality */}}
        onDiscard={() => {/* Discard functionality */}}
      />
    </MainLayout>
  );
};
```

## Features

- **Interactive Form**: Form for providing refinement feedback
- **Side-by-Side Comparison**: View current concept alongside previous versions
- **Preservation Controls**: Specify elements to preserve in refinement
- **Change Requests**: Specific instructions for changes to make
- **Version Tracking**: Visual indication of concept version
- **Action Controls**: Save, export, or discard refinements

## Props

| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| `conceptId` | `string` | Yes | - | ID of the concept to refine |

## Types

```tsx
interface RefinementFormData {
  additionalFeedback: string;
  preserveElements: string[];
  changeRequests: string[];
}

interface ConceptVersion {
  id: string;
  version: number;
  imageUrl: string;
  prompt: string;
  createdAt: string;
  // Other properties
}
```

## Dependencies

- `ConceptImage`: Component for displaying the concept image
- `RefinementForm`: Form component for refinement inputs
- `RefinementHeader`: Header with title and version information
- `ComparisonView`: Component for comparing versions
- `RefinementActions`: Action buttons for refinement workflow
- `useConceptQueries`: Hooks for fetching concept data
- `useConceptMutations`: Hooks for concept refinement mutations

## State Management

- Local state for refinement form data
- React Query for API data fetching and mutations
- Loading and error states handled appropriately

## Related Components

- [RefinementForm](./components/RefinementForm.md)
- [RefinementHeader](./components/RefinementHeader.md)
- [ComparisonView](./components/ComparisonView.md)
- [RefinementActions](./components/RefinementActions.md)
- [RefinementSelectionPage](./RefinementSelectionPage.md)

## Usage

This page is typically accessed after concept generation when a user wants to refine their concept:

```tsx
<Route path="/concepts/:conceptId/refine" element={<RefinementPage />} />
```

The component would extract the `conceptId` from route parameters:

```tsx
const RefinementPageWrapper: React.FC = () => {
  const { conceptId } = useParams<{ conceptId: string }>();
  
  if (!conceptId) {
    return <Navigate to="/concepts" />;
  }
  
  return <RefinementPage conceptId={conceptId} />;
};
```

## Accessibility

- Form inputs have proper labels and error states
- Loading and error states are properly communicated
- Keyboard navigation for all interactive elements
- Sufficient color contrast for text readability 