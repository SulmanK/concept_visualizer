# RateLimitsPanel Component

## Overview

The `RateLimitsPanel` component displays the current API rate limits and usage information in a user-friendly panel. It helps users understand their current usage status and when they'll be able to make additional requests if they've reached their limits.

## Component Details

- **File Path**: `frontend/my-app/src/components/RateLimitsPanel/RateLimitsPanel.tsx`
- **Type**: React Functional Component

## Props

| Prop             | Type                  | Required | Default | Description                                      |
|------------------|----------------------|----------|---------|--------------------------------------------------|
| `rateLimits`     | `RateLimitInfo[]`    | Yes      | -       | Array of rate limit information objects          |
| `isLoading`      | `boolean`            | No       | `false` | Whether rate limit data is loading               |
| `error`          | `string \| null`     | No       | `null`  | Error message if fetching limits failed          |
| `onRefresh`      | `() => void`         | No       | -       | Handler to refresh rate limit data               |
| `className`      | `string`             | No       | `''`    | Additional CSS classes                           |
| `showRefreshButton` | `boolean`         | No       | `true`  | Whether to show the refresh button               |

## Features

- Visual progress bars for each limit type
- Countdown timers for limit resets
- Automatic refresh when limits are about to reset
- User-friendly display of complex rate limit data
- Responsive design that works on mobile and desktop
- Appropriate loading and error states

## Usage Example

```tsx
import { RateLimitsPanel } from '../components/RateLimitsPanel/RateLimitsPanel';
import { useRateLimitsQuery } from '../hooks/useRateLimitsQuery';

const SettingsPage = () => {
  const { 
    data: rateLimits, 
    isLoading, 
    error, 
    refetch 
  } = useRateLimitsQuery();
  
  return (
    <div className="settings-container">
      <h2>API Usage</h2>
      <RateLimitsPanel
        rateLimits={rateLimits || []}
        isLoading={isLoading}
        error={error ? error.message : null}
        onRefresh={refetch}
        className="mt-4"
      />
    </div>
  );
};
```

## Type Definitions

```tsx
interface RateLimitInfo {
  endpoint: string;          // API endpoint name
  limit: number;             // Maximum number of requests allowed
  remaining: number;         // Number of requests remaining
  reset: number;             // Timestamp when the limit resets
  displayName?: string;      // User-friendly name of the endpoint
  description?: string;      // Description of what the endpoint does
}
```

## Related Components

- [`ProgressBar`](../ui/ProgressBar.md) - Used to display usage progress
- [`Card`](../ui/Card.md) - Container for the panel
- [`Button`](../ui/Button.md) - Used for the refresh button
- [`Spinner`](../ui/Spinner.md) - Displays loading state 