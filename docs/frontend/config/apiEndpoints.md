# API Endpoints Configuration

## Overview

The `apiEndpoints.ts` file contains constants for all API endpoints used throughout the application. It centralizes URL paths and provides named references to ensure consistency in API calls.

## File Details

- **File Path**: `frontend/my-app/src/config/apiEndpoints.ts`
- **Type**: TypeScript Configuration File

## Constants

### Polling Interval

```typescript
export const DEFAULT_POLLING_INTERVAL = 2000; // 2 seconds
```

This constant defines the default interval in milliseconds for polling operations (e.g., task status checks).

### Task Status Constants

```typescript
export const TASK_STATUS = {
  /** Base path for task endpoints */
  BASE_PATH: 'tasks',
  /** Task is waiting to be processed */
  PENDING: 'pending',
  /** Task is currently being processed */
  PROCESSING: 'processing',
  /** Task has been completed successfully */
  COMPLETED: 'completed',
  /** Task has failed */
  FAILED: 'failed',
  /** Task has been canceled */
  CANCELED: 'canceled'
};
```

These constants define the possible task statuses and the base path for task-related endpoints.

### API Endpoints Object

```typescript
export const API_ENDPOINTS = {
  GENERATE_CONCEPT: 'concepts/generate-with-palettes',
  REFINE_CONCEPT: 'concepts/refine',
  TASK_STATUS_BY_ID: (taskId: string) => `${TASK_STATUS.BASE_PATH}/${taskId}`,
  TASK_CANCEL: (taskId: string) => `${TASK_STATUS.BASE_PATH}/${taskId}/cancel`,
  EXPORT_IMAGE: 'export/process',
  RECENT_CONCEPTS: 'storage/recent',
  CONCEPT_DETAIL: (id: string) => `storage/concept/${id}`,
  RATE_LIMITS: 'health/rate-limits-status'
};
```

This object contains endpoint paths for various API operations. Some entries are simple strings, while others are functions that generate paths based on parameters (e.g., `taskId`).

## Usage

```typescript
import { API_ENDPOINTS, DEFAULT_POLLING_INTERVAL } from '../config/apiEndpoints';
import { apiClient } from '../services/apiClient';

// Using a simple endpoint
const fetchRecentConcepts = async () => {
  const response = await apiClient.get(API_ENDPOINTS.RECENT_CONCEPTS);
  return response.data;
};

// Using a parameterized endpoint
const fetchTaskStatus = async (taskId: string) => {
  const response = await apiClient.get(API_ENDPOINTS.TASK_STATUS_BY_ID(taskId));
  return response.data;
};

// Using the polling interval
const pollTaskStatus = (taskId: string, callback: (status: any) => void) => {
  const interval = setInterval(async () => {
    const status = await fetchTaskStatus(taskId);
    callback(status);
    
    if (status.status === TASK_STATUS.COMPLETED || status.status === TASK_STATUS.FAILED) {
      clearInterval(interval);
    }
  }, DEFAULT_POLLING_INTERVAL);
  
  return () => clearInterval(interval);
};
```

## Best Practices

1. **Always use these constants** instead of hardcoding paths in components or services
2. **Make endpoint URLs descriptive** to clearly indicate their purpose
3. **Use functions for parameterized endpoints** to ensure consistent formatting
4. **Export constants individually** to allow for selective imports
5. **Add JSDoc comments** to explain the purpose and usage of each endpoint 