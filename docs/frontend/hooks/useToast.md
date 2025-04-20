# useToast Hook

The `useToast` hook provides a convenient way to display toast notifications in the application.

## Usage

```tsx
import { useToast } from 'hooks/useToast';

function MyComponent() {
  const { showToast } = useToast();
  
  const handleClick = () => {
    showToast({
      message: 'Operation successful!',
      type: 'success',
      duration: 3000
    });
  };
  
  return <button onClick={handleClick}>Show Toast</button>;
}
```

## API

### Return Values

| Value | Type | Description |
|-------|------|-------------|
| `showToast` | `(options: ToastOptions) => void` | Function to display a toast notification |
| `hideToast` | `(id?: string) => void` | Function to hide a specific toast or all toasts if no ID is provided |
| `hideAllToasts` | `() => void` | Function to hide all toast notifications |

### ToastOptions

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `message` | `string` | - | The message to display in the toast |
| `type` | `'info' \| 'success' \| 'warning' \| 'error'` | `'info'` | The type of toast notification |
| `duration` | `number` | `5000` | Duration in milliseconds before the toast automatically dismisses |
| `id` | `string` | Auto-generated | Unique identifier for the toast |
| `position` | `'top-right' \| 'top-left' \| 'bottom-right' \| 'bottom-left'` | `'top-right'` | Position of the toast on the screen |

## Examples

### Success Toast

```tsx
showToast({
  message: 'Concept created successfully!',
  type: 'success'
});
```

### Error Toast

```tsx
showToast({
  message: 'Failed to save concept. Please try again.',
  type: 'error',
  duration: 7000 // Show for longer duration
});
```

### Warning Toast with Custom Position

```tsx
showToast({
  message: 'You are approaching your API rate limit',
  type: 'warning',
  position: 'bottom-left'
});
```

## Implementation Details

The `useToast` hook uses the global toast context to manage toast notifications. It ensures that:

- Multiple toasts can be displayed simultaneously
- Toasts are automatically dismissed after their duration
- Toasts can be manually dismissed
- Each toast has a unique identifier 