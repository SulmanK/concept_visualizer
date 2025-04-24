# useNetworkStatus

The `useNetworkStatus` hook monitors and manages the application's network connectivity state. It provides detailed information about the current connection status and offers utilities for connection testing and offline detection.

## Overview

This hook combines browser network events with active API health checks to provide a comprehensive view of connectivity. It not only detects when the device goes offline but can also determine when the application server is unreachable even if the device reports being online.

## Usage

```tsx
import { useNetworkStatus } from "../hooks/useNetworkStatus";

function NetworkAwareComponent() {
  const {
    isOnline,
    isSlowConnection,
    connectionType,
    offlineSince,
    checkConnection,
  } = useNetworkStatus({
    notifyOnStatusChange: true,
  });

  const handleRetry = async () => {
    const isConnected = await checkConnection();
    if (isConnected) {
      // Resume normal operation
    } else {
      // Still offline, show offline UI
    }
  };

  // Render offline UI when disconnected
  if (!isOnline) {
    return (
      <div className="offline-container">
        <h2>You're Offline</h2>
        {offlineSince && (
          <p>Disconnected since: {offlineSince.toLocaleTimeString()}</p>
        )}
        <button onClick={handleRetry}>Check Connection</button>
      </div>
    );
  }

  // Render warning for slow connections
  if (isSlowConnection) {
    return (
      <div className="slow-connection-warning">
        <p>
          You're on a slow connection ({connectionType}). Some features may be
          limited.
        </p>
        {/* Main component content */}
      </div>
    );
  }

  // Normal online rendering
  return <div>{/* Main component content */}</div>;
}
```

## Parameters

The hook accepts an optional configuration object with the following properties:

| Parameter              | Type    | Default              | Description                                                     |
| ---------------------- | ------- | -------------------- | --------------------------------------------------------------- |
| `notifyOnStatusChange` | boolean | `true`               | Whether to show toast notifications when network status changes |
| `checkEndpoint`        | string  | `'/health'`          | API endpoint used to test connectivity                          |
| `checkInterval`        | number  | `120000` (2 minutes) | Interval in milliseconds to perform periodic connection checks  |

## Return Value

The hook returns a `NetworkStatus` object with the following properties:

```typescript
interface NetworkStatus {
  // Whether the application is currently online
  isOnline: boolean;

  // Network connection type if available (e.g., '4g', 'wifi')
  connectionType?: string;

  // Whether the browser is on a slow connection (2g, 3g)
  isSlowConnection: boolean;

  // Last time connection status was checked
  lastCheckedAt: Date;

  // Function to manually check connection status
  checkConnection: () => Promise<boolean>;

  // Timestamp when the connection was last lost (if applicable)
  offlineSince?: Date;
}
```

## Features

### Multi-Layer Connectivity Detection

The hook uses multiple strategies to determine connectivity:

1. **Browser Events**: Listens for the browser's native `online` and `offline` events
2. **Active Testing**: Performs HTTP requests to the application's health endpoint to verify actual API connectivity
3. **Connection Quality**: Uses the Network Information API (where available) to detect connection type and quality

### Automatic Notifications

When `notifyOnStatusChange` is enabled, the hook will:

- Show a success toast when connectivity is restored
- Show a warning toast when connectivity is lost

### Connection Quality Detection

On supported browsers, the hook detects and reports:

- **Connection Type**: Reports connection type (e.g., '4g', 'wifi')
- **Slow Connection**: Identifies when the user is on a slow connection (2g, 3g)

### Manual Connection Testing

The `checkConnection` function allows components to:

- Force an immediate connection check
- Get the current connection status as a boolean result
- Use the result to conditionally render UI or retry operations

## Implementation Details

- Uses the browser's `navigator.onLine` property for basic online/offline detection
- Performs HTTP GET requests to the health endpoint to verify API connectivity
- Uses AbortController to implement timeouts for health checks
- Implements the Network Information API for connection quality detection on supported browsers
- Logs connectivity changes to the console for debugging
- Prevents notification spam by only showing toasts when status actually changes

## Browser Compatibility

- The core online/offline detection works in all modern browsers
- Connection quality detection (`connectionType`, `isSlowConnection`) is only available in browsers that support the Network Information API (mainly Chrome-based browsers)
- For browsers without Network Information API support, these values will be `undefined` and `false` respectively

## Related

- `OfflineStatus` component - UI component that displays offline status
- `useToast` hook - Used for displaying notifications
- `apiClient` - Used for health check requests
