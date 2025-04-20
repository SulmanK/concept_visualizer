# TextArea Component

## Overview

The `TextArea` component provides a customizable, accessible textarea input for forms with support for labels, helper text, error messages, and animations. It's designed to match the application's design system and provide consistent user experience.

## Component Details

- **File Path**: `frontend/my-app/src/components/ui/TextArea.tsx`
- **Type**: React Functional Component

## Props

| Prop        | Type                                      | Required | Default     | Description                             |
|-------------|-------------------------------------------|----------|-------------|-----------------------------------------|
| `label`     | `string`                                  | No       | `undefined` | Label text for the textarea             |
| `helperText`| `string`                                  | No       | `undefined` | Helper text displayed below the textarea|
| `error`     | `string`                                  | No       | `undefined` | Error message to display                |
| `fullWidth` | `boolean`                                 | No       | `false`     | Whether the textarea takes full width   |
| `animated`  | `boolean`                                 | No       | `true`      | Whether to apply focus animations       |
| `rows`      | `number`                                  | No       | `4`         | Number of visible rows                  |
| `id`        | `string`                                  | No       | Auto-generated | ID for the textarea element          |
| `className` | `string`                                  | No       | `''`        | Additional CSS classes                  |
| `...props`  | `TextareaHTMLAttributes<HTMLTextAreaElement>` | No  | -           | All standard textarea HTML attributes   |

## State

- `isFocused`: Tracks the focus state of the textarea for animation purposes

## Features

- Accessible design with proper ARIA attributes
- Focus animations with support for reduced motion preferences
- Error state styling and messaging
- Helper text support
- Customizable appearance through className prop
- Auto-generated IDs for accessibility if not provided

## Usage Example

```tsx
import { TextArea } from '../components/ui/TextArea';
import { useState } from 'react';

const FeedbackForm = () => {
  const [feedback, setFeedback] = useState('');
  const [error, setError] = useState<string | undefined>(undefined);
  
  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    setFeedback(value);
    
    if (value.length > 0 && value.length < 10) {
      setError('Feedback must be at least 10 characters long');
    } else {
      setError(undefined);
    }
  };
  
  return (
    <form>
      <TextArea
        label="Your Feedback"
        helperText="Please provide detailed feedback to help us improve"
        error={error}
        value={feedback}
        onChange={handleChange}
        fullWidth
        rows={6}
        placeholder="Tell us what you think..."
        required
      />
      <button type="submit" disabled={!!error}>Submit</button>
    </form>
  );
};
```

## Accessibility

- Uses proper label association with the textarea through htmlFor/id
- Provides error feedback through aria-invalid and aria-describedby
- Respects user preferences for reduced motion
- Ensures proper color contrast for text elements

## Related Components

- [`Input`](./Input.md) - Similar component for single-line text input
- [`ErrorMessage`](./ErrorMessage.md) - Used for displaying errors elsewhere 