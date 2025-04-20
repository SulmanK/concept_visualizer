# String Utilities

The `stringUtils.ts` module provides utility functions for common string manipulation operations used throughout the application. These functions help maintain consistency in string formatting and handling.

## Core Features

- String case transformations
- Truncation with proper ellipsis
- String format conversions
- Graceful handling of null or undefined inputs

## Available Functions

### capitalizeFirstLetter

```typescript
capitalizeFirstLetter(str: string): string
```

Capitalizes the first letter of a string.

| Parameter | Type | Description |
|-----------|------|-------------|
| `str` | string | The string to capitalize |

**Returns:** The string with the first letter capitalized

### truncateString

```typescript
truncateString(str: string, maxLength: number): string
```

Truncates a string to a specified length and adds an ellipsis if truncated.

| Parameter | Type | Description |
|-----------|------|-------------|
| `str` | string | The string to truncate |
| `maxLength` | number | The maximum length of the string |

**Returns:** The truncated string with ellipsis if needed

### toKebabCase

```typescript
toKebabCase(str: string): string
```

Formats a string to kebab-case (lowercase with hyphens between words).

| Parameter | Type | Description |
|-----------|------|-------------|
| `str` | string | The string to format |

**Returns:** The kebab-case formatted string

## Usage Examples

### Capitalizing Text

```typescript
import { capitalizeFirstLetter } from '../utils/stringUtils';

// Basic usage
const name = 'john';
const capitalizedName = capitalizeFirstLetter(name); // "John"

// In a component
const LabelDisplay = ({ label }) => {
  return <span>{capitalizeFirstLetter(label)}</span>;
};
```

### Truncating Long Text

```typescript
import { truncateString } from '../utils/stringUtils';

const longDescription = "This is a very long description that needs to be truncated for display purposes.";
const truncated = truncateString(longDescription, 20); // "This is a very long..."

// In a component
const DescriptionPreview = ({ description, maxLength = 50 }) => {
  return <p>{truncateString(description, maxLength)}</p>;
};
```

### Converting to Kebab Case

```typescript
import { toKebabCase } from '../utils/stringUtils';

const title = "My Cool Component";
const idAttribute = toKebabCase(title); // "my-cool-component"

// In a component
const GenerateId = ({ text }) => {
  const id = toKebabCase(text);
  return <div id={id}>{text}</div>;
};
```

## Implementation Details

Each function in this module:

1. **Handles edge cases** - Null/undefined inputs return the input without error
2. **Is pure** - No side effects, returns a new string rather than modifying the input
3. **Is type-safe** - Fully typed with TypeScript
4. **Is performant** - Uses built-in string methods for optimal performance

## Best Practices

- Use these utilities instead of implementing the same logic repeatedly
- For localization concerns, consider using a proper i18n library instead
- When working with very large strings, be mindful of performance implications 