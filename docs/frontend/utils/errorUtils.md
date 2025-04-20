# Error Utilities

The `errorUtils.ts` module provides standardized error handling utilities across the application. It helps create consistent error handling patterns for asynchronous operations and React Query.

## Core Features

- Standardized error handling for async operations
- Customizable error reporting and logging
- Integration with React Query error handling
- Special handling for rate limit errors
- Toast notification support for user feedback

## Key Functions

### createAsyncErrorHandler

```typescript
const asyncErrorHandler = createAsyncErrorHandler(errorHandler, options);
const result = await asyncErrorHandler(
  () => fetchData(),
  'fetchUserProfile'
);
```

Creates a standardized error handler function for asynchronous operations with the following options:

| Option | Type | Description |
|--------|------|-------------|
| `showToast` | boolean | Whether to show a toast notification on error |
| `defaultErrorMessage` | string | Fallback error message if none is provided |
| `onError` | function | Custom error callback function |
| `context` | string | Context identifier for error logging |

### createQueryErrorHandler

```typescript
const { onQueryError } = createQueryErrorHandler(errorHandler, options);
```

Creates a function to handle errors in React Query mutations with these options:

| Option | Type | Description |
|--------|------|-------------|
| `defaultErrorMessage` | string | Fallback error message if none is provided |
| `showToast` | boolean | Whether to show a toast notification on error |

## Usage Examples

### Handling Async Operations

```typescript
import { useErrorHandling } from '../hooks/useErrorHandling';
import { createAsyncErrorHandler } from '../utils/errorUtils';

const MyComponent = () => {
  const errorHandler = useErrorHandling();
  
  const handleAsyncError = createAsyncErrorHandler(errorHandler, {
    showToast: true,
    defaultErrorMessage: 'Failed to load data',
    context: 'UserProfile'
  });
  
  const fetchUserData = async () => {
    const result = await handleAsyncError(
      () => api.get('/user/profile'),
      'fetchUserProfile'
    );
    
    if (result) {
      // Process the result
    }
  };
  
  return (
    <button onClick={fetchUserData}>Load Profile</button>
  );
};
```

### React Query Error Handling

```typescript
import { useQuery } from '@tanstack/react-query';
import { useErrorHandling } from '../hooks/useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';

const MyDataComponent = () => {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    showToast: true,
    defaultErrorMessage: 'Failed to load data'
  });
  
  const { data, isLoading } = useQuery({
    queryKey: ['userData'],
    queryFn: () => api.get('/user/data'),
    onError: onQueryError
  });
  
  return (
    <div>
      {isLoading ? <LoadingSpinner /> : <UserData data={data} />}
    </div>
  );
};
```

## Special Error Handling

The utilities provide special handling for certain error types:

- **Rate Limit Errors**: Handled with specific user-friendly messages
- **Navigation Errors**: Logged more prominently to help debug routing issues

## Implementation Details

- Uses the `useErrorHandling` hook for centralized error state management
- Logs detailed error information including stack traces in development
- Dispatches custom events for toast notifications
- Extracts user-friendly messages from error objects 