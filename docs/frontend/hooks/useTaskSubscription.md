# useTaskSubscription

The `useTaskSubscription` hook provides real-time updates for background tasks using Supabase Realtime. It enables components to receive instant notifications when task status changes, without constant polling.

## Overview

While the `useTaskStatusQuery` hook handles periodic polling for task updates, this hook leverages WebSockets through Supabase Realtime to receive push notifications when a task's status changes. This approach provides more immediate feedback and reduces unnecessary network requests.

## Usage

```tsx
import { useTaskSubscription } from '../hooks/useTaskSubscription';

function TaskMonitor({ taskId }) {
  const { 
    taskData, 
    error, 
    status 
  } = useTaskSubscription(taskId);
  
  // Handle connection status
  if (status === 'TIMED_OUT' || status === 'CHANNEL_ERROR') {
    return <div>Connection issue - falling back to polling</div>;
  }
  
  // Handle error state
  if (error) {
    return <ErrorMessage error={error} />;
  }
  
  // Handle loading/no data state
  if (!taskData) {
    return <LoadingIndicator />;
  }
  
  // Render task details
  return (
    <div>
      <h2>Task: {taskData.name}</h2>
      <p>Status: {taskData.status}</p>
      {taskData.progress && <ProgressBar value={taskData.progress} />}
      {taskData.message && <p>{taskData.message}</p>}
      {taskData.status === 'completed' && (
        <div className="result">
          <h3>Result:</h3>
          <pre>{JSON.stringify(taskData.result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
```

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `taskId` | `string \| null` | Yes | The ID of the task to subscribe to |

## Return Value

The hook returns an object with the following properties:

| Property | Type | Description |
|----------|------|-------------|
| `taskData` | `TaskResponse \| null` | The latest task data from real-time updates |
| `error` | `Error \| null` | Error from subscription or initial fetch |
| `status` | `string \| null` | Current subscription status |

## Subscription Flow

The hook follows this sequence:

1. **Initial Data Load**: Fetches the current task state using `useTaskStatusQuery` when first mounted
2. **Channel Setup**: Creates a Supabase Realtime channel specific to the task
3. **Subscription**: Listens for PostgreSQL changes (specifically UPDATEs) to the task record
4. **Real-time Updates**: Updates local state and React Query cache when new data arrives
5. **Connection Monitoring**: Tracks connection state and reports errors
6. **Cleanup**: Properly unsubscribes when the component unmounts or taskId changes

## Connection Status Values

The `status` field can contain the following values:

| Status | Description |
|--------|-------------|
| `null` | Initial state, no subscription active |
| `'SUBSCRIBED'` | Successfully subscribed and listening for updates |
| `'TIMED_OUT'` | Subscription request timed out |
| `'CHANNEL_ERROR'` | Error occurred in the channel |
| `'error'` | General subscription error |
| `'disconnected'` | Connection to Supabase Realtime was lost |

## Error Handling

The hook handles various error scenarios:

- **Initial Fetch Failure**: If the initial API call fails, the error is captured and returned
- **Subscription Errors**: Connection issues or channel errors are captured and exposed
- **Timeouts**: If subscription times out, an appropriate error is set

## Implementation Details

- Uses Supabase Realtime `channel` API to subscribe to database changes
- Targets the `tasks` table with a filter for the specific task ID
- Updates both local state and React Query cache for consistency
- Extensive logging for debugging connection issues
- Proper cleanup to prevent memory leaks and unnecessary connections

## Related

- `useTaskQueries` - Companion hook for standard task API access
- `supabaseClient` - Underlying Supabase client that provides Realtime functionality
- `TaskContext` - Often used alongside this hook for application-wide task tracking 