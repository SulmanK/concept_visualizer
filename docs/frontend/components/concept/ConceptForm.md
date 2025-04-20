# ConceptForm Component

## Overview

The `ConceptForm` component provides a user interface for submitting concept generation requests. It handles form validation, submission, and displays appropriate loading states and error messages.

## Component Details

- **File Path**: `frontend/my-app/src/components/concept/ConceptForm.tsx`
- **Type**: React Functional Component

## Props

| Prop             | Type                                       | Required | Default                                   | Description                                      |
|------------------|--------------------------------------------|---------|--------------------------------------------|--------------------------------------------------|
| `onSubmit`       | `(logoDescription: string, themeDescription: string) => void` | Yes     | -                                          | Handler for form submission                      |
| `status`         | `FormStatus` (`'idle'` \| `'submitting'` \| `'success'` \| `'error'`) | Yes     | -                                          | Form submission status                           |
| `error`          | `string \| null`                           | No      | `undefined`                                | Error message from submission                    |
| `onReset`        | `() => void`                               | No      | `undefined`                                | Reset form and results                           |
| `isProcessing`   | `boolean`                                  | No      | `false`                                    | Whether concept generation is being processed asynchronously |
| `processingMessage` | `string`                                | No      | `'Processing your concept generation request...'` | Message to display during processing         |

## State

- `logoDescription`: Stores the logo description input value
- `themeDescription`: Stores the theme description input value 
- `validationError`: Stores form validation error messages

## Features

- Form validation with detailed error messages
- Rate limit error detection and specialized display
- Integration with task context for global state management
- Loading indicators for processing states
- Reset functionality on task completion

## Usage Example

```tsx
import { ConceptForm } from '../components/concept/ConceptForm';
import { FormStatus } from '../types';

const ExamplePage = () => {
  const [status, setStatus] = useState<FormStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  
  const handleSubmit = async (logoDescription: string, themeDescription: string) => {
    setStatus('submitting');
    try {
      await generateConcept(logoDescription, themeDescription);
      setStatus('success');
    } catch (err) {
      setError(err.message);
      setStatus('error');
    }
  };
  
  const handleReset = () => {
    setStatus('idle');
    setError(null);
  };
  
  return (
    <ConceptForm
      onSubmit={handleSubmit}
      status={status}
      error={error}
      onReset={handleReset}
    />
  );
};
```

## Related Components

- [`TextArea`](../ui/TextArea.md) - Used for multi-line text input
- [`Input`](../ui/Input.md) - Used for single-line text input
- [`Button`](../ui/Button.md) - Used for form submission
- [`LoadingIndicator`](../ui/LoadingIndicator.md) - Displays loading state
- [`ErrorMessage`](../ui/ErrorMessage.md) - Displays error messages 