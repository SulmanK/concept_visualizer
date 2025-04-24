# useConceptMutations Hooks

The `useConceptMutations` module provides a collection of React Query mutation hooks for creating, updating, and managing concepts.

## Overview

These hooks handle state management and API interactions for mutations that modify concept data. They provide a standardized way to create and update concepts, with built-in loading, error, and success states.

## Available Hooks

### `useCreateConcept`

Creates a new concept based on user input.

#### Usage

```tsx
import { useConceptMutations } from "hooks/useConceptMutations";

function ConceptForm() {
  const [formData, setFormData] = useState({
    logoDescription: "",
    themeDescription: "",
  });

  const { mutate, isPending, error } = useConceptMutations.useCreateConcept();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate(formData, {
      onSuccess: (data) => {
        // Navigate to the new concept detail page
        router.push(`/concepts/${data.conceptId}`);
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

| Parameter | Type                   | Required | Description                  |
| --------- | ---------------------- | -------- | ---------------------------- |
| `data`    | `CreateConceptRequest` | Yes      | Concept creation data        |
| `options` | `MutateOptions`        | No       | React Query mutation options |

```tsx
interface CreateConceptRequest {
  logoDescription: string; // Description of the logo
  themeDescription: string; // Description of the brand theme
  name?: string; // Optional concept name (auto-generated if not provided)
  tags?: string[]; // Optional tags for the concept
}
```

#### Return Value

The hook returns a React Query mutation result with the following properties:

| Property      | Type                                                                                      | Description                              |
| ------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------- |
| `mutate`      | `(data: CreateConceptRequest, options?: MutateOptions) => void`                           | Function to trigger the mutation         |
| `mutateAsync` | `(data: CreateConceptRequest, options?: MutateOptions) => Promise<CreateConceptResponse>` | Async version of mutate                  |
| `isPending`   | `boolean`                                                                                 | `true` while the mutation is in progress |
| `isSuccess`   | `boolean`                                                                                 | `true` if the mutation succeeded         |
| `isError`     | `boolean`                                                                                 | `true` if the mutation failed            |
| `error`       | `Error \| null`                                                                           | Error object if the mutation failed      |
| `data`        | `CreateConceptResponse \| undefined`                                                      | Response data if successful              |

```tsx
interface CreateConceptResponse {
  conceptId: string; // ID of the created concept
  status: "pending" | "processing" | "complete"; // Status of the creation process
  taskId?: string; // ID of the associated background task, if applicable
}
```

### `useRefineConcept`

Refines an existing concept based on additional feedback.

#### Usage

```tsx
import { useConceptMutations } from "hooks/useConceptMutations";

function RefinementForm({ conceptId }) {
  const [refinementData, setRefinementData] = useState({
    additionalFeedback: "",
    preserveElements: [],
    changeRequests: [],
  });

  const { mutate, isPending } = useConceptMutations.useRefineConcept();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({
      conceptId,
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

| Parameter | Type                   | Required | Description                  |
| --------- | ---------------------- | -------- | ---------------------------- |
| `data`    | `RefineConceptRequest` | Yes      | Refinement data              |
| `options` | `MutateOptions`        | No       | React Query mutation options |

```tsx
interface RefineConceptRequest {
  conceptId: string; // ID of the concept to refine
  additionalFeedback: string; // Additional feedback/instructions for refinement
  preserveElements: string[]; // Elements to preserve in the refinement
  changeRequests: string[]; // Specific change requests
}
```

#### Return Value

Similar to `useCreateConcept`, but with a slightly different response type:

```tsx
interface RefineConceptResponse {
  conceptId: string; // ID of the refined concept (same as input)
  newVersionId: string; // ID of the new version created
  status: "pending" | "processing" | "complete"; // Status of the refinement process
  taskId?: string; // ID of the associated background task, if applicable
}
```

### `useDeleteConcept`

Deletes a concept.

#### Usage

```tsx
import { useConceptMutations } from "hooks/useConceptMutations";

function DeleteConceptButton({ conceptId }) {
  const { mutate, isPending } = useConceptMutations.useDeleteConcept();

  const handleDelete = () => {
    if (window.confirm("Are you sure you want to delete this concept?")) {
      mutate(conceptId, {
        onSuccess: () => {
          // Navigate back to concepts list
          router.push("/concepts");
        },
      });
    }
  };

  return (
    <button
      onClick={handleDelete}
      disabled={isPending}
      className="delete-button"
    >
      {isPending ? "Deleting..." : "Delete Concept"}
    </button>
  );
}
```

#### Parameters

The `mutate` function accepts:

| Parameter   | Type            | Required | Description                  |
| ----------- | --------------- | -------- | ---------------------------- |
| `conceptId` | `string`        | Yes      | ID of the concept to delete  |
| `options`   | `MutateOptions` | No       | React Query mutation options |

#### Return Value

Standard React Query mutation result with a simple success response:

```tsx
interface DeleteConceptResponse {
  success: boolean; // Whether the deletion was successful
  message?: string; // Optional message about the deletion
}
```

### `useUpdateConcept`

Updates concept metadata such as name, tags, or description.

#### Usage

```tsx
import { useConceptMutations } from "hooks/useConceptMutations";

function EditConceptForm({ concept }) {
  const [formData, setFormData] = useState({
    name: concept.name,
    tags: concept.tags,
  });

  const { mutate, isPending } = useConceptMutations.useUpdateConcept();

  const handleSubmit = (e) => {
    e.preventDefault();
    mutate({
      conceptId: concept.id,
      ...formData,
    });
  };

  return (
    <form onSubmit={handleSubmit}>
      {/* Form fields */}
      <button type="submit" disabled={isPending}>
        {isPending ? "Saving..." : "Save Changes"}
      </button>
    </form>
  );
}
```

#### Parameters

The `mutate` function accepts:

| Parameter | Type                   | Required | Description                  |
| --------- | ---------------------- | -------- | ---------------------------- |
| `data`    | `UpdateConceptRequest` | Yes      | Update data                  |
| `options` | `MutateOptions`        | No       | React Query mutation options |

```tsx
interface UpdateConceptRequest {
  conceptId: string; // ID of the concept to update
  name?: string; // New name for the concept
  tags?: string[]; // New tags for the concept
  description?: string; // New description for the concept
  favorite?: boolean; // Whether the concept is favorited
}
```

## Implementation Details

These hooks are built with React Query for data mutations. Key aspects include:

- **Optimistic Updates**: Some mutations use optimistic updates to provide immediate UI feedback
- **Cache Invalidation**: Successful mutations invalidate related queries to ensure data consistency
- **Error Handling**: Mutations capture and expose errors for UI handling
- **Loading States**: Mutations track loading state with `isPending`
- **Retry Logic**: Failed mutations can be automatically retried

## Related Hooks

- [useConceptQueries](./useConceptQueries.md) - For fetching concept data
- [useExportImageMutation](./useExportImageMutation.md) - For exporting concept images
