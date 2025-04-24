# Input Component

The `Input` component provides a standardized text input field for forms throughout the application, with enhanced features like validation and helper text.

## Overview

This component wraps Material-UI's TextField component, providing consistent styling, validation states, and accessibility features. It supports various input types and includes helpful visual cues for users.

## Usage

```tsx
import { Input } from 'components/ui/Input';

// Basic usage
<Input
  label="Email"
  name="email"
  value={email}
  onChange={handleChange}
/>

// With validation error
<Input
  label="Username"
  name="username"
  value={username}
  onChange={handleChange}
  error={!!errors.username}
  helperText={errors.username}
  required
/>

// Password input with icon
<Input
  label="Password"
  name="password"
  type="password"
  value={password}
  onChange={handleChange}
  endAdornment={<VisibilityIcon />}
/>
```

## Props

| Prop             | Type                                                   | Default    | Description                                |
| ---------------- | ------------------------------------------------------ | ---------- | ------------------------------------------ |
| `name`           | `string`                                               | -          | Input field name (required)                |
| `label`          | `string`                                               | -          | Label text for the input                   |
| `value`          | `string`                                               | `''`       | Current input value                        |
| `onChange`       | `(e: React.ChangeEvent<HTMLInputElement>) => void`     | -          | Handler for value changes                  |
| `type`           | `'text' \| 'password' \| 'email' \| 'number' \| 'tel'` | `'text'`   | HTML input type                            |
| `placeholder`    | `string`                                               | `''`       | Placeholder text when empty                |
| `required`       | `boolean`                                              | `false`    | Whether the field is required              |
| `disabled`       | `boolean`                                              | `false`    | Whether the input is disabled              |
| `error`          | `boolean`                                              | `false`    | Whether the input has an error             |
| `helperText`     | `string`                                               | `''`       | Helper or error text below the input       |
| `fullWidth`      | `boolean`                                              | `true`     | Whether input should take up full width    |
| `size`           | `'small' \| 'medium'`                                  | `'medium'` | Size of the input field                    |
| `startAdornment` | `React.ReactNode`                                      | -          | Icon or element to place at start of input |
| `endAdornment`   | `React.ReactNode`                                      | -          | Icon or element to place at end of input   |
| `multiline`      | `boolean`                                              | `false`    | Whether to render as textarea              |
| `rows`           | `number`                                               | `1`        | Number of rows when multiline              |
| `maxRows`        | `number`                                               | -          | Maximum number of rows when multiline      |
| `autoFocus`      | `boolean`                                              | `false`    | Whether to focus on mount                  |
| `className`      | `string`                                               | `''`       | Additional CSS class to apply              |
| `sx`             | `SxProps<Theme>`                                       | `{}`       | MUI system props for additional styling    |

## Implementation Details

```tsx
import React from "react";
import { TextField, TextFieldProps, InputAdornment } from "@mui/material";
import { SxProps, Theme } from "@mui/material/styles";

interface InputProps extends Omit<TextFieldProps, "variant"> {
  name: string;
  label?: string;
  value?: string;
  onChange?: (e: React.ChangeEvent<HTMLInputElement>) => void;
  type?: "text" | "password" | "email" | "number" | "tel";
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
  fullWidth?: boolean;
  size?: "small" | "medium";
  startAdornment?: React.ReactNode;
  endAdornment?: React.ReactNode;
  multiline?: boolean;
  rows?: number;
  maxRows?: number;
  autoFocus?: boolean;
  className?: string;
  sx?: SxProps<Theme>;
}

export function Input({
  name,
  label,
  value = "",
  onChange,
  type = "text",
  placeholder = "",
  required = false,
  disabled = false,
  error = false,
  helperText = "",
  fullWidth = true,
  size = "medium",
  startAdornment,
  endAdornment,
  multiline = false,
  rows = 1,
  maxRows,
  autoFocus = false,
  className = "",
  sx = {},
  ...rest
}: InputProps) {
  return (
    <TextField
      name={name}
      label={label}
      value={value}
      onChange={onChange}
      type={type}
      placeholder={placeholder}
      required={required}
      disabled={disabled}
      error={error}
      helperText={helperText}
      fullWidth={fullWidth}
      size={size}
      multiline={multiline}
      rows={rows}
      maxRows={maxRows}
      autoFocus={autoFocus}
      className={className}
      variant="outlined"
      InputProps={{
        startAdornment: startAdornment && (
          <InputAdornment position="start">{startAdornment}</InputAdornment>
        ),
        endAdornment: endAdornment && (
          <InputAdornment position="end">{endAdornment}</InputAdornment>
        ),
      }}
      sx={{
        "& .MuiOutlinedInput-root": {
          "&.Mui-focused fieldset": {
            borderColor: (theme) => theme.palette.primary.main,
          },
        },
        ...sx,
      }}
      {...rest}
    />
  );
}
```

## Features

- **Consistent Styling**: Follows the application's design system
- **Validation States**: Visual indicators for errors and required fields
- **Helper Text**: Support for guidance and error messages
- **Flexible Input Types**: Supports various HTML input types
- **Icon Support**: Optional start and end adornments for visual cues
- **Responsive Width**: Full-width by default with option to customize
- **Multiline Support**: Can function as a text area for longer inputs
- **Accessibility**: Proper labeling and focus states

## Usage Patterns

### Basic Form Field

```tsx
<Input
  label="Full Name"
  name="fullName"
  value={formData.fullName}
  onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
  required
/>
```

### Form Field with Validation

```tsx
<Input
  label="Email Address"
  name="email"
  type="email"
  value={formData.email}
  onChange={handleChange}
  error={!!errors.email}
  helperText={errors.email || "We'll never share your email with anyone else."}
  required
/>
```

### Password Field with Visibility Toggle

```tsx
function PasswordField() {
  const [showPassword, setShowPassword] = useState(false);
  const [password, setPassword] = useState("");

  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  return (
    <Input
      label="Password"
      name="password"
      type={showPassword ? "text" : "password"}
      value={password}
      onChange={(e) => setPassword(e.target.value)}
      endAdornment={
        <IconButton
          onClick={togglePasswordVisibility}
          edge="end"
          aria-label={showPassword ? "hide password" : "show password"}
        >
          {showPassword ? <VisibilityOffIcon /> : <VisibilityIcon />}
        </IconButton>
      }
      required
    />
  );
}
```

### Search Field

```tsx
<Input
  placeholder="Search concepts..."
  name="search"
  value={searchQuery}
  onChange={(e) => setSearchQuery(e.target.value)}
  startAdornment={<SearchIcon />}
  endAdornment={
    searchQuery ? (
      <IconButton size="small" onClick={() => setSearchQuery("")}>
        <ClearIcon />
      </IconButton>
    ) : undefined
  }
  size="small"
/>
```

### Multiline Comment Field

```tsx
<Input
  label="Description"
  name="description"
  value={description}
  onChange={(e) => setDescription(e.target.value)}
  multiline
  rows={4}
  maxRows={8}
  placeholder="Enter a detailed description..."
/>
```

## Best Practices

1. Always include a descriptive label for accessibility
2. Use helper text to provide guidance on expected input format
3. Add validation and show error messages for invalid input
4. Use appropriate input types (`email`, `password`, etc.) for built-in validation
5. Keep labels concise and clear about what information is needed
6. Use consistent styling and behavior across all forms in the application
