# ConceptRefinementForm Component

## Overview

The `ConceptRefinementForm` component provides a user interface for refining existing concept designs. It allows users to submit feedback and refinement instructions for an existing generated concept, including options to preserve specific aspects of the original design.

## Component Details

- **File Path**: `frontend/my-app/src/components/concept/ConceptRefinementForm.tsx`
- **Type**: React Functional Component

## Props

| Prop                      | Type                                                                                                               | Required | Default                                             | Description                                   |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------ | -------- | --------------------------------------------------- | --------------------------------------------- |
| `originalImageUrl`        | `string`                                                                                                           | Yes      | -                                                   | URL of the image to be refined                |
| `onSubmit`                | `(refinementPrompt: string, logoDescription: string, themeDescription: string, preserveAspects: string[]) => void` | Yes      | -                                                   | Handler for form submission                   |
| `status`                  | `FormStatus`                                                                                                       | Yes      | -                                                   | Form submission status                        |
| `error`                   | `string \| null`                                                                                                   | No       | `undefined`                                         | Error message from submission                 |
| `onCancel`                | `() => void`                                                                                                       | No       | `undefined`                                         | Cancel refinement handler                     |
| `initialLogoDescription`  | `string`                                                                                                           | No       | `''`                                                | Initial logo description                      |
| `initialThemeDescription` | `string`                                                                                                           | No       | `''`                                                | Initial theme description                     |
| `refinementPlaceholder`   | `string`                                                                                                           | No       | `'Describe how you want to refine this concept...'` | Custom placeholder text for refinement prompt |
| `defaultPreserveAspects`  | `string[]`                                                                                                         | No       | `[]`                                                | Default preserve aspects to pre-select        |
| `isColorVariation`        | `boolean`                                                                                                          | No       | `false`                                             | Whether refining a color variation            |
| `colorInfo`               | `{colors: string[], name: string}`                                                                                 | No       | `undefined`                                         | Color information for the current variation   |
| `isProcessing`            | `boolean`                                                                                                          | No       | `false`                                             | Whether the refinement is being processed     |
| `processingMessage`       | `string`                                                                                                           | No       | `'Processing your refinement request...'`           | Message to display during processing          |

## State

- `refinementPrompt`: Stores the refinement instructions input value
- `logoDescription`: Stores the logo description input value
- `themeDescription`: Stores the theme description input value
- `preserveAspects`: Stores selected aspects to preserve from the original concept
- `validationError`: Stores form validation error messages

## Features

- Form validation with error messages for required fields
- Support for preserving specific aspects of the original design
- Integration with task context for global state management
- Task-based processing with progress indicators
- Automatic form reset when task is cleared
- Displays original image for reference
- Supports color variation refinement
- Handles concurrent task management

## Integration with Task Context

The component integrates with the global task management system:

- Uses `useTaskContext` to access task state
- Detects if other tasks are in progress
- Provides appropriate messaging for task status
- Automatically resets the form when a task is completed
- Uses `useOnTaskCleared` for cleanup operations

## Usage Example

```tsx
import { ConceptRefinementForm } from "../components/concept/ConceptRefinementForm";
import { FormStatus } from "../types";
import { useRefineConceptMutation } from "../../hooks/useConceptMutations";

const RefinementPage = ({ conceptId, originalImageUrl }) => {
  const [status, setStatus] = useState<FormStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  // Use the mutation hook for refinement
  const { mutateAsync: refineConcept, isLoading } = useRefineConceptMutation();

  const handleSubmit = async (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[],
  ) => {
    setStatus("submitting");
    try {
      await refineConcept({
        originalImageUrl,
        refinementPrompt,
        logoDescription,
        themeDescription,
        preserveAspects,
      });
      setStatus("success");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  };

  const handleCancel = () => {
    // Navigation logic
  };

  return (
    <ConceptRefinementForm
      originalImageUrl={originalImageUrl}
      onSubmit={handleSubmit}
      status={status}
      error={error}
      onCancel={handleCancel}
      initialLogoDescription="Modern tech logo"
      initialThemeDescription="Blue professional theme"
      defaultPreserveAspects={["layout", "style"]}
      isProcessing={isLoading}
    />
  );
};
```

## Component Structure

The form is structured into several sections:

1. **Original Image Display**: Shows the image being refined
2. **Refinement Prompt**: Text area for specific refinement instructions
3. **Description Fields**: Text areas for updating logo and theme descriptions
4. **Preserve Aspects**: Checkboxes for selecting aspects to preserve
5. **Action Buttons**: Submit and Cancel buttons
6. **Processing Indicator**: Shows task progress and status messages

## Related Components

- [`TextArea`](../ui/TextArea.md) - Used for text input fields
- [`Button`](../ui/Button.md) - Used for form submission and cancel actions
- [`Card`](../ui/Card.md) - Used for layout structure
- [`Spinner`](../ui/Spinner.md) - Used for loading indicators
