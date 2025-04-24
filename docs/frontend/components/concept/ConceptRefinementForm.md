# ConceptRefinementForm Component

## Overview

The `ConceptRefinementForm` component provides a user interface for refining existing concept designs. It allows users to submit feedback and refinement instructions for an existing generated concept to improve or modify it.

## Component Details

- **File Path**: `frontend/my-app/src/components/concept/ConceptRefinementForm.tsx`
- **Type**: React Functional Component

## Props

| Prop                | Type                                 | Required | Default                                   | Description                                    |
| ------------------- | ------------------------------------ | -------- | ----------------------------------------- | ---------------------------------------------- |
| `onSubmit`          | `(refinementPrompt: string) => void` | Yes      | -                                         | Handler for form submission                    |
| `status`            | `FormStatus`                         | Yes      | -                                         | Form submission status                         |
| `error`             | `string \| null`                     | No       | `undefined`                               | Error message from submission                  |
| `onReset`           | `() => void`                         | No       | `undefined`                               | Reset form and results                         |
| `isProcessing`      | `boolean`                            | No       | `false`                                   | Whether the refinement is being processed      |
| `processingMessage` | `string`                             | No       | `'Processing your refinement request...'` | Message to display during processing           |
| `initialPrompt`     | `string`                             | No       | `''`                                      | Initial refinement prompt to populate the form |

## State

- `refinementPrompt`: Stores the refinement instructions input value
- `validationError`: Stores form validation error messages

## Features

- Form validation with detailed error messages
- Rate limit error detection and specialized display
- Integration with task context for global state management
- Loading indicators for processing states
- Reset functionality on task completion
- Suggested refinement prompts to help users

## Usage Example

```tsx
import { ConceptRefinementForm } from "../components/concept/ConceptRefinementForm";
import { FormStatus } from "../types";

const RefinementPage = ({ conceptId }) => {
  const [status, setStatus] = useState<FormStatus>("idle");
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (refinementPrompt: string) => {
    setStatus("submitting");
    try {
      await refineConcept(conceptId, refinementPrompt);
      setStatus("success");
    } catch (err) {
      setError(err.message);
      setStatus("error");
    }
  };

  const handleReset = () => {
    setStatus("idle");
    setError(null);
  };

  return (
    <ConceptRefinementForm
      onSubmit={handleSubmit}
      status={status}
      error={error}
      onReset={handleReset}
      initialPrompt="Make the colors more vibrant"
    />
  );
};
```

## Related Components

- [`TextArea`](../ui/TextArea.md) - Used for refinement instructions input
- [`Button`](../ui/Button.md) - Used for form submission
- [`LoadingIndicator`](../ui/LoadingIndicator.md) - Displays loading state
- [`ErrorMessage`](../ui/ErrorMessage.md) - Displays error messages
