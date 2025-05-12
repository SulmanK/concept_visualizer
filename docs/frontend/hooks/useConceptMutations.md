# useConceptMutations Hooks

The `useConceptMutations` module provides a collection of React Query mutation hooks for creating and refining concepts.

## Overview

These hooks handle state management and API interactions for mutations that modify concept data. They initiate asynchronous tasks for concept generation and refinement, with built-in loading, error handling, and integration with the task tracking system.

## Available Hooks

### `useGenerateConceptMutation`

Creates a new concept based on user input by initiating a backend task.

#### Usage

```tsx
import { useGenerateConceptMutation } from "hooks/useConceptMutations";

function ConceptForm() {
  const [formData, setFormData] = useState({
    logo_description: "",
    theme_description: "",
  });

  const { mutate, isPending, error } = useGenerateConceptMutation();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate(formData, {
      onSuccess: (data) => {
        // data contains the task information
        console.log(`Task initiated with ID: ${data.task_id || data.id}`);
      },
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={isPending}>
        {isPending ? "Creating..." : "Create Concept"}
      </button>
      {error && <ErrorMessage error={error} />}
    </form>
  );
}
```

#### Parameters

The `mutate` function accepts:

| Parameter | Type            | Required | Description                  |
| --------- | --------------- | -------- | ---------------------------- |
| `data`    | `PromptRequest` | Yes      | Concept creation data        |
| `options` | `MutateOptions` | No       | React Query mutation options |

```tsx
interface PromptRequest {
  logo_description: string; // Description of the logo
  theme_description: string; // Description of the brand theme
}
```

#### Return Value

The hook returns a React Query mutation result with the following properties:

| Property      | Type                                                                      | Description                              |
| ------------- | ------------------------------------------------------------------------- | ---------------------------------------- |
| `mutate`      | `(data: PromptRequest, options?: MutateOptions) => void`                  | Function to trigger the mutation         |
| `mutateAsync` | `(data: PromptRequest, options?: MutateOptions) => Promise<TaskResponse>` | Async version of mutate                  |
| `isPending`   | `boolean`                                                                 | `true` while the mutation is in progress |
| `isSuccess`   | `boolean`                                                                 | `true` if the mutation succeeded         |
| `isError`     | `boolean`                                                                 | `true` if the mutation failed            |
| `error`       | `Error \| null`                                                           | Error object if the mutation failed      |
| `data`        | `TaskResponse \| undefined`                                               | Response data if successful              |

```tsx
interface TaskResponse {
  id: string; // Task ID
  task_id?: string; // Alternative task ID field (depends on API)
  status: "pending" | "processing" | "completed" | "failed"; // Status of the task
  type: "generate_concept" | "refine_concept"; // Type of task
  result_id?: string; // ID of the result once completed
  error_message?: string; // Error message if task failed
  created_at: string; // Creation timestamp
  updated_at: string; // Last update timestamp
}
```

### `useRefineConceptMutation`

Refines an existing concept based on additional feedback by initiating a backend task.

#### Usage

```tsx
import { useRefineConceptMutation } from "hooks/useConceptMutations";

function RefinementForm({ originalImageUrl }) {
  const [refinementData, setRefinementData] = useState({
    refinement_prompt: "",
    preserve_aspects: [],
  });

  const { mutate, isPending } = useRefineConceptMutation();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({
      original_image_url: originalImageUrl,
      ...refinementData,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={isPending}>
        {isPending ? "Refining..." : "Refine Concept"}
      </button>
    </form>
  );
}
```

#### Parameters

The `mutate` function accepts:

| Parameter | Type                | Required | Description                  |
| --------- | ------------------- | -------- | ---------------------------- |
| `data`    | `RefinementRequest` | Yes      | Refinement data              |
| `options` | `MutateOptions`     | No       | React Query mutation options |

```tsx
interface RefinementRequest {
  original_image_url: string; // URL of the original image to refine
  logo_description?: string; // Optional updated logo description
  theme_description?: string; // Optional updated theme description
  refinement_prompt: string; // Specific refinement instructions
  preserve_aspects: string[]; // Elements to preserve in the refinement
}
```

#### Return Value

Similar to `useGenerateConceptMutation`, this hook returns a standard React Query mutation result with a `TaskResponse` as the success data type.

## Implementation Details

These hooks are built with React Query for data mutations and integrate with several system components:

- **Task Context**: Both hooks update the task context to track the background processing
- **Rate Limit Management**: Mutations decrement rate limits via `useRateLimitsDecrement`
- **Error Handling**: Specialized error handling for network and rate limit issues
- **Network Status**: Checks online status before initiating API calls
- **Query Cache Management**: Cleans up the mutation cache after completion

## Related Hooks

- [useConceptQueries](./useConceptQueries.md) - For fetching concept data
- [useTask](./useTask.md) - For tracking and updating task status
- [useRateLimits](./useRateLimits.md) - For managing API rate limits
