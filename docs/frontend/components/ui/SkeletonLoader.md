# SkeletonLoader Component

## Overview

The `SkeletonLoader` component provides placeholder loading states for various UI elements. It helps improve perceived performance by showing content outlines while actual data is being loaded, preventing layout shifts and giving users visual feedback.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/SkeletonLoader.tsx`
- **Type**: React Functional Component

## Props

| Prop          | Type                                      | Required | Default      | Description                             |
|---------------|-------------------------------------------|----------|-------------|-----------------------------------------|
| `type`        | `SkeletonType`                            | No       | `'text'`     | Type of skeleton (text, circle, etc.)    |
| `width`       | `string`                                  | No       | Type-based   | Width of the skeleton                    |
| `height`      | `string`                                  | No       | Type-based   | Height of the skeleton                   |
| `lines`       | `number`                                  | No       | `1`          | Number of lines for text skeleton        |
| `lineHeight`  | `'sm' \| 'md' \| 'lg'`                   | No       | `'md'`       | Line height for text skeleton            |
| `borderRadius`| `string`                                  | No       | Type-based   | Border radius for the skeleton           |
| `className`   | `string`                                  | No       | `''`         | Additional CSS classes                   |
| `style`       | `React.CSSProperties`                     | No       | `undefined`  | Additional inline styles                 |

## Skeleton Types

The component supports several preset skeleton types:

- **`text`**: For text content (paragraphs, headings, etc.)
- **`circle`**: For circular elements (avatars, icons, etc.)
- **`rectangle`**: For rectangular content blocks
- **`card`**: For card components with header, content and footer sections
- **`image`**: For image placeholders
- **`button`**: For button placeholders

## Features

- **Animated Pulse Effect**: Subtle animation to indicate loading state
- **Multiple Text Lines**: Support for multi-line text skeletons with varying widths
- **Responsive Sizing**: Default dimensions based on type with customizable overrides
- **Card Layout**: Special rendering for card skeletons with content structure
- **Accessibility**: Proper ARIA attributes for screen readers
- **Theming**: Uses application color scheme for consistent appearance

## Usage Examples

### Basic Usage

```tsx
import { SkeletonLoader } from '../components/ui/SkeletonLoader';

// Simple text loading placeholder
<SkeletonLoader type="text" lines={3} />

// Avatar placeholder
<SkeletonLoader type="circle" width="64px" height="64px" />

// Button placeholder
<SkeletonLoader type="button" width="120px" />
```

### Complex Example

```tsx
import { SkeletonLoader } from '../components/ui/SkeletonLoader';

const LoadingProfileCard = () => {
  return (
    <div className="bg-white p-4 rounded-lg shadow">
      <div className="flex items-center mb-4">
        {/* Avatar skeleton */}
        <SkeletonLoader type="circle" width="60px" height="60px" />
        
        <div className="ml-4 flex-1">
          {/* Name skeleton */}
          <SkeletonLoader type="text" lineHeight="lg" width="70%" />
          {/* Title skeleton */}
          <SkeletonLoader type="text" lineHeight="sm" width="50%" className="mt-2" />
        </div>
      </div>
      
      {/* Bio skeleton */}
      <SkeletonLoader type="text" lines={3} className="mb-4" />
      
      {/* Stats skeleton */}
      <div className="flex justify-between">
        <SkeletonLoader type="rectangle" width="30%" height="40px" />
        <SkeletonLoader type="rectangle" width="30%" height="40px" />
        <SkeletonLoader type="rectangle" width="30%" height="40px" />
      </div>
    </div>
  );
};
```

## Implementation Details

- Uses Tailwind's `animate-pulse` for the loading animation
- Leverages CSS gradients for a subtle shimmer effect
- Automatically determines reasonable defaults based on the skeleton type
- Uses screen reader text to indicate loading state for accessibility
- Multi-line text skeletons have decreasing width for each line for a natural look

## Accessibility

- Includes `role="status"` for proper ARIA role
- Provides descriptive `aria-label` attributes based on type
- Includes visually hidden text for screen readers via `sr-only` class 