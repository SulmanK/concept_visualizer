# Frontend Configuration

## Overview

The `config` directory contains configuration files that define constants and settings used throughout the application. These files provide a centralized place to manage configuration values, making it easier to maintain and modify the application.

## Directory Structure

```
config/
├── apiEndpoints.ts - API endpoint URLs and constants
├── queryKeys.ts - React Query cache keys
└── __tests__/ - Tests for configuration files
```

## Configuration Files

### API Endpoints

The [apiEndpoints.ts](./apiEndpoints.md) file contains constants for all API endpoints used in the application. This ensures consistency in API calls and makes it easier to change endpoint URLs if needed.

### Query Keys

The [queryKeys.ts](./queryKeys.md) file defines the React Query cache keys used throughout the application. This centralized approach to managing query keys ensures consistency and makes it easier to invalidate related queries when data changes.

## Best Practices

When working with configuration files:

1. **Never hardcode values** in components or services that should be in configuration
2. **Use descriptive constants** that explain the purpose of the configuration value
3. **Group related configuration values** together in appropriate files
4. **Add comments** explaining complex configuration values or how they should be used
5. **Add tests** for configuration values to ensure they maintain expected formats
