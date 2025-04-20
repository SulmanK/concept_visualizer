# OfflineStatus Component

## Overview

The `OfflineStatus` component displays a banner notification when a user is offline or experiencing a slow network connection. It helps users understand connectivity issues and provides options to retry the connection.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/OfflineStatus.tsx`
- **Type**: React Functional Component

## Props

| Prop                    | Type                     | Required | Default                      | Description                                      |
|-------------------------|--------------------------|----------|------------------------------|--------------------------------------------------|
| `position`              | `'top' \| 'bottom'`      | No       | `'top'`                     | Position of the banner on screen                 |
| `className`             | `string`                 | No       | `''`                         | Additional CSS classes                           |
| `showRetry`             | `boolean`                | No       | `true`                       | Whether to show a retry connection button        |
| `showConnectionInfo`    | `boolean`                | No       | `false`                      | Whether to show connection type information      |
| `offlineMessage`        | `string`                 | No       | `'You are currently offline'`| Message to display when offline                  |
| `slowConnectionMessage` | `string`                 | No       | `'You are on a slow connection'`| Message when on slow connection               |

## Features

- **Automatic Network Detection**: Uses the `useNetworkStatus` hook to detect network status
- **Offline Duration**: Shows how long the user has been offline (if available)
- **Connection Type**: Optionally displays connection type (WiFi, cellular, etc.)
- **Retry Button**: Allows users to manually trigger a connection check
- **Position Options**: Can be positioned at the top or bottom of the screen
- **Animations**: Smooth entrance and exit animations
- **Visual Differentiation**: Different styling for offline vs. slow connection states
- **Accessibility**: Proper ARIA attributes for screen readers

## Usage Example

```tsx
import { OfflineStatus } from '../components/ui/OfflineStatus';

const AppLayout = ({ children }) => {
  return (
    <div className="app-container">
      {/* The OfflineStatus will automatically appear when needed */}
      <OfflineStatus 
        position="top"
        showConnectionInfo={true}
        offlineMessage="No internet connection available"
      />
      
      <header>...</header>
      <main>{children}</main>
      <footer>...</footer>
    </div>
  );
};
```

## Network Status Information

The component uses the `useNetworkStatus` hook to access the following information:

- `isOnline`: Whether the device has internet connectivity
- `isSlowConnection`: Whether the connection is determined to be slow
- `connectionType`: The type of connection (e.g., 'wifi', '4g', etc.) if available
- `offlineSince`: Timestamp when the connection was lost
- `checkConnection`: Function to manually check connection status

## Styling

- Uses a red background with red border for offline status
- Uses a yellow background with yellow border for slow connection status
- Fixed positioning with high z-index to ensure visibility
- Adaptive styling based on connection status
- Animated transitions for smooth appearance and disappearance

## Related Components and Hooks

- [`useNetworkStatus`](../../hooks/useNetworkStatus.md) - Hook providing network connectivity information 