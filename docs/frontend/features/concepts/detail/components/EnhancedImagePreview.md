# EnhancedImagePreview Component

## Overview

The `EnhancedImagePreview` component provides an advanced image viewer with zoom and pan functionality. It displays images in a modal dialog with controls for zooming in, zooming out, and resetting the view, allowing users to examine concept images in detail.

## Component Details

- **File Path**: `frontend/my-app/src/features/concepts/detail/components/EnhancedImagePreview.tsx`
- **Type**: React Functional Component

## Props

| Prop        | Type       | Required | Description                                      |
|-------------|------------|----------|--------------------------------------------------|
| `isOpen`    | `boolean`  | Yes      | Controls whether the modal is open or closed     |
| `onClose`   | `() => void` | Yes    | Function to call when the modal is closed        |
| `imageUrl`  | `string`   | Yes      | URL of the image to display                      |
| `format`    | `string`   | Yes      | Format of the image (e.g., 'png', 'jpg')         |

## Features

- **Interactive Zoom**: Users can zoom in and out using buttons or mouse wheel
- **Pan Functionality**: Users can drag to pan the image when zoomed in
- **Reset View**: One-click reset to default zoom and position
- **Responsive Design**: Works well on different screen sizes
- **Keyboard Controls**: Support for keyboard navigation and controls
- **Format Indication**: Shows the image format in the preview title

## Implementation Details

### State Management

The component uses several state variables to manage user interactions:

- `scale`: Tracks the current zoom level (default: 1)
- `position`: Tracks the current pan position as x/y coordinates
- `isDragging`: Boolean flag for when the user is actively dragging
- `dragStart`: Coordinates where dragging began for calculating movement

### User Interactions

- **Zoom In/Out**: Via dedicated buttons or mouse wheel
- **Panning**: Click and drag to move the image when zoomed in
- **Reset**: Button to reset zoom level and position
- **Close**: Button to close the modal

### Animation and Transitions

- Smooth transitions when zooming (unless actively dragging)
- Reset state after modal close for a clean experience next time

## Usage Example

```tsx
import { useState } from 'react';
import EnhancedImagePreview from './components/EnhancedImagePreview';

const ImageDisplay = ({ imageUrl }) => {
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);
  
  return (
    <div>
      <img 
        src={imageUrl} 
        alt="Concept preview" 
        onClick={() => setIsPreviewOpen(true)}
        className="cursor-pointer"
      />
      
      <EnhancedImagePreview
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
        imageUrl={imageUrl}
        format="png"
      />
    </div>
  );
};
```

## UI Components

The component uses Material UI components for the interface:

- `Modal`: For the dialog container
- `Box`: For layout structure
- `Typography`: For text elements
- `IconButton`: For control buttons

## Accessibility

- Modal properly manages focus when open
- ARIA attributes for screen readers
- Keyboard navigation support
- Visual feedback for interactive elements

## Related Components

- [`ConceptDetailPage`](../ConceptDetailPage.md) - Uses this component for image previews
- [`ExportOptions`](./ExportOptions.md) - Can trigger this component to preview exports 