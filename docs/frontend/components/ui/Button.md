# Button Component

The `Button` component provides a standardized button element for user interactions throughout the application.

## Overview

This component wraps Material-UI's Button component with consistent styling, variants, and accessibility features. It simplifies implementing buttons with a consistent look and feel across the application.

## Usage

```tsx
import { Button } from 'components/ui/Button';

// Basic usage
<Button onClick={handleClick}>
  Click Me
</Button>

// Primary variant with icon
<Button
  variant="primary"
  startIcon={<SaveIcon />}
  onClick={handleSave}
>
  Save Changes
</Button>

// Outlined secondary button with loading state
<Button
  variant="secondary"
  color="error"
  loading={isSubmitting}
  onClick={handleDelete}
>
  Delete Item
</Button>
```

## Props

| Prop        | Type                                                                      | Default     | Description                           |
| ----------- | ------------------------------------------------------------------------- | ----------- | ------------------------------------- |
| `children`  | `React.ReactNode`                                                         | -           | Button content                        |
| `variant`   | `'primary' \| 'secondary' \| 'text'`                                      | `'primary'` | Button style variant                  |
| `color`     | `'primary' \| 'secondary' \| 'success' \| 'error' \| 'info' \| 'warning'` | `'primary'` | Button color                          |
| `size`      | `'small' \| 'medium' \| 'large'`                                          | `'medium'`  | Button size                           |
| `fullWidth` | `boolean`                                                                 | `false`     | Whether button should take full width |
| `disabled`  | `boolean`                                                                 | `false`     | Whether button is disabled            |
| `loading`   | `boolean`                                                                 | `false`     | Shows loading spinner when true       |
| `startIcon` | `React.ReactNode`                                                         | -           | Icon to display before text           |
| `endIcon`   | `React.ReactNode`                                                         | -           | Icon to display after text            |
| `onClick`   | `(e: React.MouseEvent<HTMLButtonElement>) => void`                        | -           | Click handler                         |
| `type`      | `'button' \| 'submit' \| 'reset'`                                         | `'button'`  | HTML button type                      |
| `className` | `string`                                                                  | `''`        | Additional CSS class to apply         |
| `sx`        | `SxProps<Theme>`                                                          | `{}`        | MUI system props for styling          |

## Implementation Details

```tsx
import React from "react";
import {
  Button as MuiButton,
  ButtonProps as MuiButtonProps,
  CircularProgress,
} from "@mui/material";
import { SxProps, Theme } from "@mui/material/styles";

export interface ButtonProps extends Omit<MuiButtonProps, "variant" | "color"> {
  variant?: "primary" | "secondary" | "text";
  color?: "primary" | "secondary" | "success" | "error" | "info" | "warning";
  loading?: boolean;
  startIcon?: React.ReactNode;
  endIcon?: React.ReactNode;
  fullWidth?: boolean;
  size?: "small" | "medium" | "large";
  className?: string;
  sx?: SxProps<Theme>;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  type?: "button" | "submit" | "reset";
}

export function Button({
  children,
  variant = "primary",
  color = "primary",
  loading = false,
  disabled = false,
  startIcon,
  endIcon,
  fullWidth = false,
  size = "medium",
  className = "",
  sx = {},
  onClick,
  type = "button",
  ...rest
}: ButtonProps) {
  // Map our custom variants to MUI variants
  const muiVariant =
    variant === "primary"
      ? "contained"
      : variant === "secondary"
      ? "outlined"
      : "text";

  return (
    <MuiButton
      variant={muiVariant}
      color={color}
      disabled={disabled || loading}
      startIcon={loading ? undefined : startIcon}
      endIcon={loading ? undefined : endIcon}
      fullWidth={fullWidth}
      size={size}
      className={className}
      sx={sx}
      onClick={onClick}
      type={type}
      {...rest}
    >
      {loading ? (
        <>
          <CircularProgress
            size={size === "small" ? 16 : size === "large" ? 24 : 20}
            color="inherit"
            sx={{ mr: children ? 1 : 0 }}
          />
          {children}
        </>
      ) : (
        children
      )}
    </MuiButton>
  );
}
```

## Features

- **Consistent Styling**: Follows the application's design system
- **Multiple Variants**: Primary (filled), secondary (outlined), and text variants
- **Color Options**: Supports all Material-UI theme colors
- **Loading State**: Built-in loading indicator
- **Icon Support**: Options for icons before or after text
- **Responsive Width**: Can take full width of container
- **Size Options**: Small, medium, and large sizes
- **Accessible**: Follows accessibility best practices

## Usage Patterns

### Primary Action Button

```tsx
<Button variant="primary" color="primary" onClick={handleSubmit} type="submit">
  Submit Form
</Button>
```

### Secondary Action Button

```tsx
<Button variant="secondary" color="primary" onClick={handleCancel}>
  Cancel
</Button>
```

### Dangerous Action Button

```tsx
<Button
  variant="primary"
  color="error"
  onClick={handleDelete}
  startIcon={<DeleteIcon />}
>
  Delete Permanently
</Button>
```

### Loading Button

```tsx
<Button
  variant="primary"
  loading={isSubmitting}
  onClick={handleSubmit}
  disabled={!isValid}
>
  {isSubmitting ? "Saving..." : "Save Changes"}
</Button>
```

### Icon Button

```tsx
<Button variant="text" startIcon={<AddIcon />} onClick={handleAddItem}>
  Add Item
</Button>
```

### Full Width Button

```tsx
<Button variant="primary" fullWidth onClick={handleContinue} size="large">
  Continue to Checkout
</Button>
```

## Best Practices

1. Use primary variant for the main action in a form or view
2. Use secondary variant for secondary actions
3. Use text variant for less prominent actions
4. Add loading state for operations that take time to complete
5. Use color appropriately - error for destructive actions, success for positive outcomes
6. Keep button text concise and action-oriented (e.g., "Save" rather than "Save the form")
7. Include icons when they add clarity to the action
8. Group related buttons together with consistent styling
9. Ensure sufficient contrast between button color and text for accessibility
10. Use appropriate button sizes based on importance and context
