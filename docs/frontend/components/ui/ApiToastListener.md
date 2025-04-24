# ApiToastListener Component

## Overview

The `ApiToastListener` component is a utility component that listens for API events from the application's event service and displays toast notifications in response to those events. It's a non-visual component that connects the API layer with the toast notification system.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/ApiToastListener.tsx`
- **Type**: React Functional Component

## Features

- **API Event Subscription**: Listens to events emitted by the application's event service
- **Toast Creation**: Creates appropriate toast notifications based on event types
- **Error Handling**: Formats error messages for display in toast notifications
- **Success Notifications**: Shows success messages for completed operations
- **Warning Messages**: Displays warnings for potential issues
- **Rate Limit Alerts**: Special handling for API rate limit notifications

## Usage Example

The component is typically included once at a high level in the application component tree:

```tsx
import { ApiToastListener } from "../components/ui/ApiToastListener";
import { ToastContainer } from "../components/ui/ToastContainer";

const App = () => {
  return (
    <>
      {/* Rest of your app */}
      <div className="app-container">
        <Router>{/* Routes and other components */}</Router>
      </div>

      {/* Toast system components */}
      <ApiToastListener />
      <ToastContainer position="bottom-right" />
    </>
  );
};
```

## Event Handling

The component listens for several types of API events:

- **API Errors**: Displays error messages from failed API calls
- **API Successes**: Shows success messages for completed operations
- **Rate Limit Warnings**: Notifies when API rate limits are approaching
- **Rate Limit Exceeded**: Alerts when rate limits have been exceeded
- **Network Status Changes**: Notifies when network connectivity changes

## Implementation Details

- Uses the `useToast` hook to create toast notifications
- Subscribes to the application's event service on mount
- Unsubscribes from events on unmount to prevent memory leaks
- Formats and categorizes messages based on event type
- Customizes notification duration based on message importance

## Related Components and Services

- [`Toast`](./Toast.md) - Individual toast notification component
- [`ToastContainer`](./ToastContainer.md) - Container for managing multiple toasts
- [`useToast`](../../hooks/useToast.md) - Hook for creating toast notifications
- `eventService` - Service for application-wide event communication
