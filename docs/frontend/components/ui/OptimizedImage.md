# OptimizedImage Component

## Overview

The `OptimizedImage` component is a performance-optimized image wrapper that supports lazy loading, loading indicators, error handling, and placeholders. It's designed to improve the user experience by reducing layout shifts and providing visual feedback during image loading.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/OptimizedImage.tsx`
- **Type**: React Functional Component

## Props

| Prop               | Type                                         | Required | Default               | Description                                       |
|--------------------|----------------------------------------------|----------|------------------------|--------------------------------------------------|
| `src`              | `string \| undefined`                         | Yes      | `'/placeholder-image.png'` | Source URL of the image                           |
| `alt`              | `string`                                      | Yes      | -                      | Alternative text for accessibility                 |
| `lazy`             | `boolean`                                     | No       | `true`                 | Whether to lazy load the image                     |
| `width`            | `string \| number`                            | No       | `'auto'`               | Width of the image element                         |
| `height`           | `string \| number`                            | No       | `'auto'`               | Height of the image element                        |
| `className`        | `string`                                      | No       | `''`                   | CSS class names for styling                        |
| `objectFit`        | `'contain' \| 'cover' \| 'fill' \| 'none' \| 'scale-down'` | No | `'contain'`      | Object fit property                               |
| `placeholder`      | `string`                                      | No       | `undefined`            | Placeholder image to show while loading            |
| `backgroundColor`  | `string`                                      | No       | `'#f3f4f6'`            | Background color while loading                     |
| `...rest`          | `any`                                         | No       | -                      | Additional props passed to container               |

## State

- `isLoaded`: Tracks whether the image has loaded successfully
- `error`: Tracks if there was an error loading the image
- `currentSrc`: The current source URL being displayed (may be null during lazy loading)

## Features

- **Intersection Observer-based Lazy Loading**: Only loads images when they're about to enter the viewport
- **Loading Indicators**: Shows a pulsing animation or custom placeholder while loading
- **Error Handling**: Displays a user-friendly error message when images fail to load
- **Smooth Transitions**: Fades in images when they load to reduce visual jarring
- **Custom Styling**: Supports custom dimensions, object-fit and background colors
- **Reduced Layout Shifts**: Maintains container dimensions during loading to prevent layout shifts

## Usage Example

```tsx
import { OptimizedImage } from '../components/ui/OptimizedImage';

const Gallery = () => {
  return (
    <div className="gallery-grid">
      <OptimizedImage
        src="https://example.com/large-image.jpg"
        alt="Mountain landscape"
        width={400}
        height={300}
        objectFit="cover"
        backgroundColor="#e2e8f0"
      />
      
      <OptimizedImage
        src="https://example.com/another-image.jpg"
        alt="Ocean sunset"
        width="100%"
        height={250}
        placeholder="/low-res-sunset-placeholder.jpg"
        lazy={false} // Load immediately, don't wait for scroll
      />
    </div>
  );
};
```

## Performance Considerations

- The component uses IntersectionObserver to implement efficient lazy loading
- Images are loaded with a 200px margin before they enter the viewport for smoother experiences
- Error states prevent attempts to reload broken images
- Animations are kept minimal to avoid performance issues

## Error Handling

When an image fails to load, the component:
1. Logs an error to the console with the attempted source URL
2. Displays a visual error indicator with an icon and message
3. Sets the error state to prevent further loading attempts

## Related Components

- [`ConceptImage`](../concept/ConceptImage.md) - Higher-level component that uses OptimizedImage for concept images
- [`LoadingIndicator`](./LoadingIndicator.md) - Used elsewhere for loading states 