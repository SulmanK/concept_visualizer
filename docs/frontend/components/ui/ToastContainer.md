# ToastContainer Component

## Overview

The `ToastContainer` component manages and displays multiple toast notifications in a consistent layout. It handles positioning toasts on the screen and provides a centralized interface for displaying notifications throughout the application.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/ToastContainer.tsx`
- **Type**: React Functional Component

## Props

| Prop        | Type                          | Required | Default        | Description                                      |
|-------------|-------------------------------|----------|----------------|--------------------------------------------------|
| `toasts`    | `ToastData[]`                 | Yes      | -              | Array of toast notifications to display           |
| `position`  | `string`                      | No       | `'bottom-right'`| Position of the toast container on screen        |
| `onDismiss` | `(id: string) => void`        | Yes      | -              | Function to call when a toast is dismissed       |

## Supported Positions

- `top-right`: Toasts appear from the top-right corner
- `top-left`: Toasts appear from the top-left corner
- `bottom-right`: Toasts appear from the bottom-right corner
- `bottom-left`: Toasts appear from the bottom-left corner
- `top-center`: Toasts appear from the top-center
- `bottom-center`: Toasts appear from the bottom-center

## Type Definitions

```typescript
export interface ToastData {
  /**
   * Unique ID for the toast
   */
  id: string;
  
  /**
   * Toast type/severity
   */
  type: ToastType; // 'success' | 'error' | 'info' | 'warning'
  
  /**
   * Message to display
   */
  message: string;
  
  /**
   * Auto dismiss timeout in milliseconds
   * Set to 0 to prevent auto-dismissal
   */
  duration?: number;
}

export interface ToastContainerProps {
  toasts: ToastData[];
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'top-center' | 'bottom-center';
  onDismiss: (id: string) => void;
}
```

## Features

- **Flexible Positioning**: Position toasts in various locations on the screen
- **Stacking Order**: Arranges multiple toasts in a stack with appropriate spacing
- **Direction Control**: Automatically stacks toasts upward or downward based on position
- **Animation Support**: Preserves entrance/exit animations from child Toast components
- **Responsive Design**: Adapts to screen size while maintaining readability

## Usage Example

```tsx
import { ToastContainer } from '../components/ui/ToastContainer';
import { useState } from 'react';

const NotificationSystem = () => {
  const [toasts, setToasts] = useState([
    {
      id: 'toast-1',
      type: 'success',
      message: 'Operation completed successfully',
      duration: 5000
    },
    {
      id: 'toast-2',
      type: 'info',
      message: 'New updates are available',
      duration: 8000
    }
  ]);
  
  const handleDismiss = (id: string) => {
    setToasts(toasts.filter(toast => toast.id !== id));
  };
  
  const addToast = (type, message) => {
    const newToast = {
      id: `toast-${Date.now()}`,
      type,
      message,
      duration: 5000
    };
    setToasts([...toasts, newToast]);
  };
  
  return (
    <div>
      <button onClick={() => addToast('success', 'Item created!')}>
        Show Success Toast
      </button>
      <button onClick={() => addToast('error', 'Operation failed')}>
        Show Error Toast
      </button>
      
      <ToastContainer
        toasts={toasts}
        position="top-right"
        onDismiss={handleDismiss}
      />
    </div>
  );
};
```

## Implementation Notes

- The component uses fixed positioning to ensure toasts appear above other content
- Z-index is set high (50) to ensure visibility above most UI elements
- Spacing between toasts is managed with Tailwind's space utilities
- Top positions stack downward from top, bottom positions stack upward from bottom

## Related Components

- [`Toast`](./Toast.md) - Individual toast notification component
- [`useToast`](../../hooks/useToast.md) - Hook for creating and managing toasts
- [`ApiToastListener`](./ApiToastListener.md) - Component that listens for API events and shows toasts 