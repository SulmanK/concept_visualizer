# ConceptImage Component

## Overview

The `ConceptImage` component is a wrapper for displaying concept-related images with error handling and loading state management. It builds upon the `OptimizedImage` component and provides a standardized way to handle missing images or loading failures.

## Component Details

- **File Path**: `frontend/my-app/src/components/concept/ConceptImage.tsx`
- **Type**: React Functional Component

## Props

| Prop        | Type      | Required | Default | Description                                     |
|-------------|-----------|----------|---------|-------------------------------------------------|
| `path`      | `string`  | No       | -       | Legacy path to the image (for backward compatibility) |
| `url`       | `string`  | No       | -       | URL of the image (preferred over path)          |
| `isPalette` | `boolean` | No       | `false` | Whether the image is a color palette            |
| `alt`       | `string`  | Yes      | -       | Alt text for the image for accessibility        |
| `className` | `string`  | No       | -       | Additional CSS classes                          |
| `lazy`      | `boolean` | No       | `true`  | Whether to lazy-load the image                  |

## State

- `error`: Tracks image loading errors

## Features

- Error handling for missing or failed images
- Fallback displays when images fail to load
- Support for lazy loading
- Backward compatibility with older path-based usage

## Usage Example

```tsx
import ConceptImage from '../components/concept/ConceptImage';

const ConceptDisplay = ({ concept }) => {
  return (
    <div className="concept-container">
      <ConceptImage 
        url={concept.imageUrl}
        alt={`Generated concept for ${concept.title}`}
        className="rounded-lg shadow-md w-full"
      />
      <div className="palette-container mt-4">
        <ConceptImage 
          url={concept.paletteUrl}
          isPalette={true}
          alt="Color palette for this concept"
          className="w-full h-12"
        />
      </div>
    </div>
  );
};
```

## Related Components

- [`OptimizedImage`](../ui/OptimizedImage.md) - Base component used for image display 