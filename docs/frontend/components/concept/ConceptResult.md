# ConceptResult Component

## Overview

The `ConceptResult` component displays the results of a concept generation request, including the generated image, color palette, and associated metadata. It provides options for viewing, saving, and refining the concept.

## Component Details

- **File Path**: `frontend/my-app/src/components/concept/ConceptResult.tsx`
- **Type**: React Functional Component

## Props

| Prop             | Type                  | Required | Default      | Description                                      |
|------------------|----------------------|----------|--------------|--------------------------------------------------|
| `concept`        | `ConceptWithPalettes` | Yes      | -            | Generated concept data with palettes             |
| `isLoading`      | `boolean`            | No       | `false`      | Whether the concept is still loading             |
| `error`          | `string \| null`     | No       | `null`       | Error message if generation failed               |
| `onRefinement`   | `() => void`         | No       | `undefined`  | Handler for refinement request                   |
| `onSave`         | `() => void`         | No       | `undefined`  | Handler for saving the concept                   |
| `onExport`       | `() => void`         | No       | `undefined`  | Handler for exporting the concept                |
| `className`      | `string`             | No       | `''`         | Additional CSS classes                           |

## Features

- Displays generated concept image with optimized loading
- Shows color palette with detailed color codes
- Displays generation metadata (resolution, creation date, etc.)
- Offers refinement and export buttons
- Responsive design with different layouts for mobile and desktop
- Appropriate loading and error states

## Usage Example

```tsx
import { ConceptResult } from '../components/concept/ConceptResult';

const GenerationPage = () => {
  const { data: concept, isLoading, error } = useConceptQuery(conceptId);
  
  const handleRefinement = () => {
    navigate(`/refine/${conceptId}`);
  };
  
  const handleSave = async () => {
    await saveConcept(conceptId);
    showToast('Concept saved successfully!');
  };
  
  const handleExport = () => {
    navigate(`/export/${conceptId}`);
  };
  
  return (
    <ConceptResult
      concept={concept}
      isLoading={isLoading}
      error={error}
      onRefinement={handleRefinement}
      onSave={handleSave}
      onExport={handleExport}
      className="mt-8"
    />
  );
};
```

## Related Components

- [`ConceptImage`](./ConceptImage.md) - Used to display the concept image
- [`ColorPalette`](../ui/ColorPalette.md) - Used to display the color palette
- [`Button`](../ui/Button.md) - Used for action buttons
- [`LoadingIndicator`](../ui/LoadingIndicator.md) - Displays loading state
- [`ErrorMessage`](../ui/ErrorMessage.md) - Displays error messages 