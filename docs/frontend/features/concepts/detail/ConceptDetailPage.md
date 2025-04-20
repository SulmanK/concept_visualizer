# ConceptDetailPage Component

## Overview

The `ConceptDetailPage` component displays detailed information about a generated concept including the image, color palette, metadata, and provides options for refining, exporting, and viewing different color variations of the concept.

## Component Details

- **File Path**: `frontend/my-app/src/features/concepts/detail/ConceptDetailPage.tsx`
- **Type**: React Functional Component

## Features

- **Concept Image Display**: Shows the main concept image with optimized loading
- **Color Palette Visualization**: Displays the concept's color palette with color codes
- **Color Variations**: Shows and allows selection between different color variations of the concept
- **Refinement**: Provides a direct link to refine the concept further
- **Export Options**: Offers export functionality with various format and size options
- **Enhanced Preview**: Includes zoomable/pannable image preview functionality
- **Error Handling**: Gracefully handles loading errors and not-found states
- **Loading States**: Shows skeleton loaders during data fetching

## Implementation Details

### Data Fetching

The component uses a custom hook `useConceptDetailWithLogging` which wraps the main `useConceptDetail` hook to add logging and debugging information. The hook fetches:

- Concept metadata
- Image URL
- Color palette information
- Color variations (if any)

### State Management

Several state variables manage the component's behavior:

- `selectedVariation`: Tracks the currently selected color variation
- `error`: Manages error state for failed requests or missing concepts
- `showExport`: Controls visibility of export options panel

### URL Parameter Handling

The component reads and updates URL parameters to reflect the current state:

- `colorId`: Identifies which color variation is currently selected
- `showExport`: Boolean parameter to control export panel visibility

## Usage Example

The component is typically accessed via a route like:

```tsx
// In route configuration
<Route path="/concepts/:conceptId" element={<ConceptDetailPage />} />

// Navigating to the page
navigate(`/concepts/${conceptId}`);

// With color variation
navigate(`/concepts/${conceptId}?colorId=${variationId}`);

// With export panel open
navigate(`/concepts/${conceptId}?showExport=true`);
```

## Related Components

- [`EnhancedImagePreview`](./components/EnhancedImagePreview.md) - Modal for zooming and panning concept images
- [`ExportOptions`](./components/ExportOptions.md) - Component for exporting concepts in different formats
- [`ColorPalette`](../../../components/ui/ColorPalette.md) - Displays color palette information
- [`OptimizedImage`](../../../components/ui/OptimizedImage.md) - Optimized image loading component

## Hooks and Services

- `useConceptDetail` - Fetches concept data from the API
- `useAuth` - Provides user authentication information
- `eventService` - Emits events for application-wide notifications

## User Flow

1. User navigates to a concept detail page via URL or from recent concepts
2. The component loads the concept data and displays the image with color palette
3. User can view different color variations using the palette selector
4. User can refine the concept by clicking the "Refine This Concept" button
5. User can export the concept in different formats by triggering the export panel

## Accessibility

- Proper heading structure for screen readers
- Alt text for images
- ARIA attributes for interactive elements
- Keyboard navigation support

## Performance Considerations

- Lazy loading for EnhancedImagePreview component
- Optimized image loading with OptimizedImage component
- Error boundaries to prevent cascading failures 