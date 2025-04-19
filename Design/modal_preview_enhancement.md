# Image Preview Enhancement Design Document

## Problem Statement
The current image preview functionality in the `ExportOptions` component uses a custom-built modal with basic styling. While functional, it lacks advanced features such as zooming, panning, and smooth transitions that would provide a better user experience. Using a specialized image viewer library would be more efficient both from a development and performance perspective.

## Requirements

1. Implement a modern image preview functionality with:
   - Zooming capabilities
   - Panning/dragging
   - Smooth transitions and animations
   - Support for different image formats (PNG, JPG, SVG)
   - Responsive design
   - Keyboard navigation

2. Maintain compatibility with the existing image export workflow:
   - Preview should work with blob URLs
   - Modal should close properly and clean up resources

3. Keep consistent styling with the rest of the application

## Library Selection

After evaluating several options, we recommend using **Material UI (MUI)** components for the following reasons:

1. **Already in the project**: The application already uses MUI v7.0.2, compatible with React 19
2. **Feature-rich**: MUI has excellent modal and image handling components
3. **Consistent styling**: Will maintain the same design language as the rest of the application
4. **Well-maintained**: Regular updates and excellent documentation
5. **TypeScript support**: Full TypeScript definitions
6. **Accessibility**: Strong focus on accessibility standards

Instead of adding a new dependency, we'll leverage existing MUI components:
- `Modal` for the dialog container
- `IconButton` for controls
- `Fade` and `Zoom` for transitions
- Custom zoom and pan functionality using React hooks

Other libraries considered:
- react-image-lightbox: Compatibility issues with React 19
- react-viewer: More complex, larger bundle size
- react-image-gallery: Focus on galleries rather than single image viewing
- react-modal-image: Compatibility issues with newer React versions

## Implementation Plan

### 1. No New Dependencies Required

Since we're using existing MUI components, no additional dependencies are needed.

### 2. Update ExportOptions Component

Replace the current custom `PreviewModal` with MUI components:

1. Import the necessary MUI components
2. Create a new `EnhancedImagePreview` component
3. Implement zoom and pan functionality with React hooks
4. Ensure proper resource cleanup

### 3. Styling Customization

Use MUI's styling system to match our application's design language:
- Use the theme's color palette
- Add appropriate transitions
- Ensure consistent spacing

### 4. Testing

1. Test with different image formats (PNG, JPG, SVG)
2. Verify zoom and pan functionality
3. Test keyboard navigation
4. Ensure responsive behavior
5. Test resource cleanup on modal close

## Code Changes

### Component Updates

The main changes will be in the `ExportOptions.tsx` file:

1. Remove the custom `PreviewModal` component
2. Create a new `EnhancedImagePreview` component using MUI
3. Implement zoom/pan functionality with hooks
4. Update resource cleanup logic

### CSS Changes

- Leverage MUI's styling system
- Add custom styles for the zoom/pan functionality
- Create appropriate transitions for smoother UX

## Implementation Example

Here's a sketch of the proposed implementation:

```tsx
import { Modal, IconButton, Box, Paper } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import CloseIcon from '@mui/icons-material/Close';
import { useState, useRef, useEffect } from 'react';

interface EnhancedImagePreviewProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  format: string;
}

const EnhancedImagePreview: React.FC<EnhancedImagePreviewProps> = ({
  isOpen,
  onClose,
  imageUrl,
  format
}) => {
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  // Pan and zoom implementation...
  
  return (
    <Modal
      open={isOpen}
      onClose={onClose}
      closeAfterTransition
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '90%',
        maxWidth: 1000,
        bgcolor: 'background.paper',
        boxShadow: 24,
        p: 2,
        outline: 'none',
      }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <h3>Preview ({format.toUpperCase()})</h3>
          <Box>
            <IconButton onClick={() => setScale(s => Math.max(0.5, s - 0.5))}>
              <ZoomOutIcon />
            </IconButton>
            <IconButton onClick={() => setScale(s => Math.min(3, s + 0.5))}>
              <ZoomInIcon />
            </IconButton>
            <IconButton onClick={onClose}>
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
        
        <Box
          sx={{
            overflow: 'hidden',
            position: 'relative',
            height: '70vh',
            bgcolor: 'grey.100',
          }}
          // Pan handlers...
        >
          <Box
            component="img"
            src={imageUrl}
            alt="Preview"
            sx={{
              position: 'absolute',
              transform: `translate(${position.x}px, ${position.y}px) scale(${scale})`,
              maxWidth: '100%',
              maxHeight: '100%',
              transition: isDragging ? 'none' : 'transform 0.2s',
              transformOrigin: 'center',
            }}
          />
        </Box>
      </Box>
    </Modal>
  );
};
```

## Potential Risks

1. **Performance**: Complex pan/zoom operations may affect performance
2. **Browser compatibility**: Ensuring transforms work consistently across browsers
3. **Resource management**: Ensure no memory leaks with blob URL handling

## Success Metrics

1. Improved UX for previewing images (user feedback)
2. No performance regression in the export functionality
3. Maintained or improved accessibility

## Timeline

1. Component implementation: 2 hours
2. Adding zoom/pan functionality: 2 hours
3. Testing and bug fixes: 1 hour

Total estimated time: 5 hours 