# Logger Utility

The `logger.ts` module provides a flexible logging utility that conditionally logs based on the environment. It helps maintain clean console outputs in production while providing comprehensive logging during development.

## Core Features

- Environment-aware logging (development vs. production)
- Multiple logging levels (debug, info, warn, error)
- Production-safe logging (suppresses debug and info logs in production)
- Consistent logging interface

## Logger Interface

```typescript
interface Logger {
  debug: (message: string, ...args: any[]) => void;
  info: (message: string, ...args: any[]) => void;
  warn: (message: string, ...args: any[]) => void;
  error: (message: string, ...args: any[]) => void;
}
```

## Available Functions

| Function         | Development | Production    | Description                                  |
| ---------------- | ----------- | ------------- | -------------------------------------------- |
| `logger.debug()` | ✅ Enabled  | ❌ Suppressed | Log debug information                        |
| `logger.info()`  | ✅ Enabled  | ❌ Suppressed | Log informational messages                   |
| `logger.warn()`  | ✅ Enabled  | ✅ Enabled    | Log warnings                                 |
| `logger.error()` | ✅ Enabled  | ✅ Enabled    | Log errors                                   |
| `logDev()`       | ✅ Enabled  | ❌ Suppressed | Helper function for development-only logging |

## Usage Examples

### Basic Logging

```typescript
import { logger } from "../utils/logger";

function processData(data) {
  // Only shown in development
  logger.debug("Processing data:", data);

  try {
    // Processing logic...

    // Only shown in development
    logger.info("Data processed successfully");

    return processedData;
  } catch (error) {
    // Shown in both development and production
    logger.error("Failed to process data:", error);

    // Shown in both development and production
    logger.warn("Falling back to default data");

    return defaultData;
  }
}
```

### Development-Only Logging

```typescript
import { logDev } from "../utils/logger";

function complexCalculation(input) {
  // This will only appear in development builds
  logDev("Starting calculation with input:", input);

  // Calculation steps...

  // Logs intermediate values in development only
  logDev("Intermediate result:", intermediateResult);

  return finalResult;
}
```

## Implementation Details

The logger implementation switches between two different logger instances based on the environment:

```typescript
// Check if we're in development mode
const isDev = import.meta.env.DEV === true;

/**
 * Production logger - suppresses debug and info logs
 */
const productionLogger: Logger = {
  debug: () => {},
  info: () => {},
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};

/**
 * Development logger - shows all logs
 */
const developmentLogger: Logger = {
  debug: console.debug.bind(console),
  info: console.info.bind(console),
  warn: console.warn.bind(console),
  error: console.error.bind(console),
};

/**
 * Logger instance based on environment
 */
export const logger: Logger = isDev ? developmentLogger : productionLogger;
```

## Best Practices

1. **Use Appropriate Log Levels**:

   - `debug`: For detailed debugging information
   - `info`: For general information about application flow
   - `warn`: For non-critical issues that don't stop execution
   - `error`: For critical issues that might cause failures

2. **Structured Logging**: Include relevant context with log messages

3. **Be Concise**: Keep log messages clear and to the point

4. **Performance**: Avoid expensive operations in log arguments in production
