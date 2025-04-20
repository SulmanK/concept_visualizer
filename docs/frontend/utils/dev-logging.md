# Development Logging Utilities

The `dev-logging.ts` module provides utility functions for conditional logging based on the environment. It creates wrapper functions that only log in development mode, keeping the production console clean while still maintaining helpful logging during development.

## Core Features

- Environment-aware logging (only logs in development mode)
- Preserves console output format and coloring
- Consistent API with standard console methods
- Always logs errors regardless of environment

## Available Functions

| Function | Description |
|----------|-------------|
| `devLog(...args)` | Logs to console only in development mode (wrapper for `console.log`) |
| `devWarn(...args)` | Logs warnings to console only in development mode (wrapper for `console.warn`) |
| `devDebug(...args)` | Logs debug information to console only in development mode (wrapper for `console.debug`) |
| `devInfo(...args)` | Logs info to console only in development mode (wrapper for `console.info`) |
| `logError(...args)` | Always logs errors to console regardless of environment (wrapper for `console.error`) |

## Usage Examples

### Basic Logging

```typescript
import { devLog, devWarn, logError } from '../utils/dev-logging';

function processData(data) {
  // Only logs in development mode
  devLog('Processing data:', data);
  
  try {
    // Process data...
    if (someCondition) {
      // Only logs in development mode
      devWarn('Unusual condition detected:', someCondition);
    }
    
    return processedData;
  } catch (error) {
    // Always logs, even in production
    logError('Error processing data:', error);
    throw error;
  }
}
```

### Component Debugging

```tsx
import React, { useEffect } from 'react';
import { devLog } from '../utils/dev-logging';

const DebugComponent = ({ data }) => {
  useEffect(() => {
    // Only logs in development mode
    devLog('Component mounted with data:', data);
    
    return () => {
      devLog('Component will unmount');
    };
  }, [data]);
  
  return <div>{/* Component content */}</div>;
};
```

## Implementation Details

The module uses Vite's `import.meta.env.DEV` environment variable to determine if the application is running in development mode:

```typescript
// Check if we're in development mode
const isDev = import.meta.env.DEV === true;

export function devLog(...args: any[]): void {
  if (isDev) {
    console.log(...args);
  }
}
```

## Best Practices

1. **Use for Development-Only Logging**: Use these utilities for logs that should only appear during development
2. **Use `logError` for Critical Errors**: Always use `logError` for important errors that should be logged in production
3. **Provide Context**: Include descriptive messages and relevant data with your log calls
4. **Clean Up**: Remove or convert unnecessary debug logging before shipping to production
5. **Performance**: Avoid expensive operations in log arguments as they still execute in production 