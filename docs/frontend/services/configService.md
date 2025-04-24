# Configuration Service

The Configuration Service provides functionality for fetching and managing application configuration values from the backend. It handles storage bucket names, feature flags, and other global application settings.

## Key Features

- Fetches application configuration from the backend
- Provides fallback default values if API fails
- Singleton pattern to ensure consistent configuration across the app
- Typed interfaces for configuration objects
- React hooks for easy integration with components

## Core Interfaces

```typescript
// Storage bucket configuration interface
interface StorageBucketsConfig {
  concept: string;
  palette: string;
}

// Complete configuration interface
interface AppConfig {
  storage: StorageBucketsConfig;
  maxUploadSize: number;
  supportedFileTypes: string[];
  features: {
    refinement: boolean;
    palette: boolean;
    export: boolean;
  };
  limits: {
    maxConcepts: number;
    maxPalettes: number;
  };
}
```

## Key Functions

| Function              | Description                                                                  |
| --------------------- | ---------------------------------------------------------------------------- |
| `fetchConfig()`       | Asynchronously fetches configuration from the backend API                    |
| `getConfig()`         | Returns the current configuration, falling back to defaults if needed        |
| `getBucketName(type)` | Returns the bucket name for a specific storage type ('concept' or 'palette') |

## React Hooks

### useConfig

```typescript
const { config, loading, error } = useConfig();
```

A custom React hook that provides the application configuration with loading and error states. This is the recommended way to access configuration in React components.

## Usage Example

```tsx
import { useConfig } from "../services/configService";

const FeatureFlagExample = () => {
  const { config, loading } = useConfig();

  if (loading) return <div>Loading configuration...</div>;

  return (
    <div>
      {config.features.refinement && <button>Refine Concept</button>}

      <p>Maximum upload size: {config.maxUploadSize / (1024 * 1024)}MB</p>
      <p>Supported file types: {config.supportedFileTypes.join(", ")}</p>
    </div>
  );
};
```

## Notes

- For React components, prefer using the `useConfigQuery` hook from `src/hooks/useConfigQuery.ts` for React Query integration
- The service initializes configuration on module load to ensure it's available early in the application lifecycle
