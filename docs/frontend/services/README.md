# Services

The `services` directory contains modules that handle communication with external APIs and provide shared functionality across the application. These services encapsulate data access logic and abstract away the details of API communication.

## Overview

The service layer acts as an intermediary between the UI components and external data sources. Each service is responsible for a specific domain of functionality and provides a clean API for the rest of the application to use.

## Service Modules

| Service | Purpose | Key Responsibilities |
|---------|---------|----------------------|
| [apiClient](./apiClient.md) | Core HTTP client | API requests, error handling, authentication, interceptors |
| [supabaseClient](./supabaseClient.md) | Supabase API client | Authentication, real-time subscriptions, storage |
| [conceptService](./conceptService.md) | Concept operations | Generate concepts, refine concepts, fetch concept details |
| [rateLimitService](./rateLimitService.md) | Rate limit management | Fetch rate limits, handle rate limiting, format limits |
| [configService](./configService.md) | App configuration | Fetch and manage application configuration |
| [eventService](./eventService.md) | Event management | Application-wide event bus, event subscriptions |

## Design Principles

The service layer follows these principles:

1. **Separation of concerns**: Each service handles a specific domain of functionality
2. **Abstraction**: Services hide implementation details from consuming components
3. **Error handling**: Centralized error processing and transformation
4. **Type safety**: Strongly typed interfaces for request/response data
5. **Reusability**: Common functionality shared across the application

## Usage Pattern

Services are typically imported directly where needed:

```tsx
// Example of using a service
import { generateConcept } from '../services/conceptService';
import { useErrorHandling } from '../hooks/useErrorHandling';

function ConceptGenerator() {
  const { handleError } = useErrorHandling();
  
  const handleSubmit = async (formData) => {
    try {
      const result = await generateConcept({
        logoDescription: formData.logoDescription,
        themeDescription: formData.themeDescription
      });
      
      // Handle successful result
      console.log('Generated concept:', result);
    } catch (error) {
      // Handle error
      handleError(error);
    }
  };
  
  // Component JSX...
}
```

## API Client Architecture

The core of the service layer is the `apiClient`, which:

1. Handles HTTP requests using Axios
2. Manages authentication headers
3. Processes API responses
4. Standardizes error handling
5. Implements retry logic
6. Tracks rate limits

Other service modules typically build on top of the `apiClient` to provide domain-specific functionality.

## Related

- [hooks](../hooks/README.md) - Custom hooks that often use services for data access
- [contexts](../contexts/README.md) - Context providers that wrap services for global state
- [types](../types/README.md) - Type definitions used by services 