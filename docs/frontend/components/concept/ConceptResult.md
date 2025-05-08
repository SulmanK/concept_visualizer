# ConceptResult Component

## Overview

The `ConceptResult` component displays the results of a concept generation request, including the generated image, color palette variations, and associated metadata. It provides options for viewing, refining, downloading, and exporting the concept.

## Component Details

- **File Path**: `frontend/my-app/src/components/concept/ConceptResult.tsx`
- **Type**: React Functional Component

## Props

| Prop              | Type                                                                               | Required | Default     | Description                          |
| ----------------- | ---------------------------------------------------------------------------------- | -------- | ----------- | ------------------------------------ |
| `concept`         | `GenerationResponse`                                                               | Yes      | -           | Generated concept data               |
| `onRefineRequest` | `() => void`                                                                       | No       | `undefined` | Handler for refinement request       |
| `onDownload`      | `() => void`                                                                       | No       | `undefined` | Handler for downloading the image    |
| `onColorSelect`   | `(color: string) => void`                                                          | No       | `undefined` | Handler for selecting a color        |
| `variations`      | `Array<{name: string, colors: string[], image_url: string, description?: string}>` | No       | `[]`        | Color palette variations with images |
| `onExport`        | `(conceptId: string) => void`                                                      | No       | `undefined` | Handler for exporting the concept    |
| `selectedColor`   | `string \| null`                                                                   | No       | `null`      | The currently selected color         |
| `onViewDetails`   | `() => void`                                                                       | No       | `undefined` | Handler for viewing concept details  |

## Features

- Displays generated concept image with error handling
- Shows color palette with detailed color codes
- Supports selecting different color palette variations
- Allows downloading the image
- Provides options for refinement and export
- Displays variation name and description when selected
- Handles missing concept data gracefully
- Supports color selection for palette exploration

## Usage Example

```tsx
import { ConceptResult } from "../components/concept/ConceptResult";
import { useNavigate } from "react-router-dom";
import { useConceptDetail } from "../../hooks/useConceptQueries";

const ConceptDetailPage = ({ conceptId }) => {
  const navigate = useNavigate();
  const { data: concept, isLoading } = useConceptDetail(conceptId);
  const [selectedColor, setSelectedColor] = useState(null);

  const handleRefineRequest = () => {
    navigate(`/refine/${conceptId}`);
  };

  const handleDownload = () => {
    // Custom download logic if needed
    // Otherwise component handles download automatically
  };

  const handleExport = (conceptId) => {
    navigate(`/export/${conceptId}`);
  };

  const handleViewDetails = () => {
    navigate(`/concept/${conceptId}/details`);
  };

  if (isLoading) return <div>Loading...</div>;

  return (
    <ConceptResult
      concept={concept}
      onRefineRequest={handleRefineRequest}
      onDownload={handleDownload}
      onColorSelect={setSelectedColor}
      variations={concept?.variations}
      onExport={() => handleExport(conceptId)}
      selectedColor={selectedColor}
      onViewDetails={handleViewDetails}
    />
  );
};
```

## Component Structure

The component is structured into several sections:

1. **Main Image Display**: Shows the current concept image (original or selected variation)
2. **Variation Selector**: Allows switching between different color palette variations
3. **Color Palette Display**: Shows the colors in the current palette
4. **Action Buttons**: Download, Refine, Export, and View Details options
5. **Metadata**: Displays information about the concept generation

## Implementation Details

- Uses a responsive grid layout for desktop and mobile views
- Implements error handling for image loading
- Provides fallback for missing images
- Formats dates and filenames automatically
- Handles both array-based and object-based color palettes

## Related Components

- [`ColorPalette`](../ui/ColorPalette.md) - Used to display the color palette
- [`Button`](../ui/Button.md) - Used for action buttons
