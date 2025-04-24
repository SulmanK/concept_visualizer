# TaskStatusBar Component

## Overview

The `TaskStatusBar` component displays the current status of background tasks in a persistent, user-friendly status bar. It provides real-time updates on task progress, supports cancelation, and adapts its appearance based on the task status.

## Component Details

- **File Path**: `frontend/my-app/src/components/TaskStatusBar.tsx`
- **Type**: React Functional Component

## Features

- Real-time display of active task status
- Progress visualization with animated indicators
- Task cancelation capability
- Different appearances based on task status (pending, processing, completed, failed)
- Automatic dismissal after completion
- Persistent across page navigation

## State and Context

This component primarily relies on the `TaskContext` to access information about the current active task. It displays:

- Task type (e.g., "Generating concept", "Refining concept")
- Current status (pending, processing, completed, failed)
- Time elapsed since task started
- Cancel button for interruptible tasks

## Usage Example

The component is typically included once in the application layout to provide a consistent status display:

```tsx
import { TaskStatusBar } from "../components/TaskStatusBar";
import { MainLayout } from "../components/layout/MainLayout";

const App = () => {
  return (
    <>
      <MainLayout>
        {/* Application content */}
        <Routes>
          <Route path="/" element={<LandingPage />} />
          {/* Other routes */}
        </Routes>
      </MainLayout>

      {/* The TaskStatusBar is outside the main layout so it can be fixed at the bottom */}
      <TaskStatusBar />
    </>
  );
};
```

## Animation and Transitions

The component uses CSS transitions and animations to:

- Slide in when a task becomes active
- Show progress with animated indicators
- Change color based on task status
- Slide out when dismissed

## Related Components and Hooks

- [`Spinner`](./ui/Spinner.md) - Used for loading indicators
- [`Button`](./ui/Button.md) - Used for the cancel button
- `useTaskContext` - Hook providing task information
- `useTaskSubscription` - Hook for subscribing to task updates
