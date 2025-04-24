# Toast Component

## Overview

The `Toast` component displays short-lived notification messages to users. It supports different notification types (success, error, info, warning), auto-dismissal with a visual progress indicator, and manual dismissal via a close button.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/Toast.tsx`
- **Type**: React Functional Component

## Props

| Prop              | Type                   | Required | Default     | Description                                                        |
| ----------------- | ---------------------- | -------- | ----------- | ------------------------------------------------------------------ |
| `id`              | `string`               | Yes      | -           | Unique identifier for the toast                                    |
| `type`            | `ToastType`            | Yes      | -           | Type of toast: 'success' \| 'error' \| 'info' \| 'warning'         |
| `message`         | `string`               | Yes      | -           | Content of the toast notification                                  |
| `onDismiss`       | `(id: string) => void` | No       | `undefined` | Function called when toast is dismissed                            |
| `duration`        | `number`               | No       | `5000`      | Time in milliseconds before auto-dismissal (0 for no auto-dismiss) |
| `showCloseButton` | `boolean`              | No       | `true`      | Whether to show the close button                                   |

## Features

- **Visual Styling by Type**: Each toast type has distinct colors and icons
- **Auto-dismissal**: Toasts automatically dismiss after a specified duration
- **Progress Indicator**: Visual countdown showing time remaining before dismissal
- **Animations**: Smooth entry and exit animations
- **Accessibility**: Proper ARIA attributes for screen readers
- **Manual Dismissal**: Close button for user-controlled dismissal

## Usage Example

```tsx
import { Toast } from "../components/ui/Toast";
import { useState } from "react";

const NotificationExample = () => {
  const [isVisible, setIsVisible] = useState(true);

  const handleDismiss = (id: string) => {
    console.log(`Toast ${id} dismissed`);
    setIsVisible(false);
  };

  return (
    <div>
      {isVisible && (
        <Toast
          id="success-notification-1"
          type="success"
          message="Your changes have been saved successfully!"
          onDismiss={handleDismiss}
          duration={3000}
        />
      )}

      <button onClick={() => setIsVisible(true)}>Show Toast Again</button>
    </div>
  );
};
```

## Type Definitions

```typescript
export type ToastType = "success" | "error" | "info" | "warning";

export interface ToastProps {
  id: string;
  type: ToastType;
  message: string;
  onDismiss?: (id: string) => void;
  duration?: number;
  showCloseButton?: boolean;
}
```

## Visual Appearance

Each toast type has a distinct visual appearance:

- **Success**: Green background with checkmark icon
- **Error**: Red background with X icon
- **Warning**: Yellow background with exclamation icon
- **Info**: Indigo background with information icon

## Related Components

- [`ToastContainer`](./ToastContainer.md) - Container for managing multiple toasts
- [`useToast`](../../hooks/useToast.md) - Hook for creating and managing toasts
