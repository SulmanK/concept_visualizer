# Select Component

The `Select` component provides a standardized dropdown selection field for forms, allowing users to choose from a predefined list of options.

## Overview

This component wraps Material-UI's Select component with consistent styling, validation states, and accessibility features. It simplifies the implementation of dropdown menus throughout the application.

## Usage

```tsx
import { Select } from 'components/ui/Select';

// Basic usage
<Select
  label="Country"
  name="country"
  value={country}
  onChange={handleChange}
  options={[
    { value: 'us', label: 'United States' },
    { value: 'ca', label: 'Canada' },
    { value: 'mx', label: 'Mexico' }
  ]}
/>

// With validation error
<Select
  label="Category"
  name="category"
  value={category}
  onChange={handleChange}
  options={categoryOptions}
  error={!!errors.category}
  helperText={errors.category}
  required
/>

// Multiple selection
<Select
  label="Skills"
  name="skills"
  value={skills}
  onChange={handleChange}
  options={skillOptions}
  multiple
/>
```

## Props

| Prop          | Type                                                               | Default              | Description                                |
| ------------- | ------------------------------------------------------------------ | -------------------- | ------------------------------------------ |
| `name`        | `string`                                                           | -                    | Field name (required)                      |
| `label`       | `string`                                                           | -                    | Label text for the select                  |
| `value`       | `string \| string[] \| number \| number[]`                         | `''`                 | Current selected value(s)                  |
| `onChange`    | `(e: React.ChangeEvent<HTMLInputElement>) => void`                 | -                    | Handler for value changes                  |
| `options`     | `{ value: string \| number; label: string; disabled?: boolean }[]` | `[]`                 | Array of options for the select            |
| `placeholder` | `string`                                                           | `'Select an option'` | Text to display when no option is selected |
| `required`    | `boolean`                                                          | `false`              | Whether the field is required              |
| `disabled`    | `boolean`                                                          | `false`              | Whether the select is disabled             |
| `error`       | `boolean`                                                          | `false`              | Whether the select has an error            |
| `helperText`  | `string`                                                           | `''`                 | Helper or error text below the select      |
| `fullWidth`   | `boolean`                                                          | `true`               | Whether select should take up full width   |
| `size`        | `'small' \| 'medium'`                                              | `'medium'`           | Size of the select field                   |
| `multiple`    | `boolean`                                                          | `false`              | Whether multiple options can be selected   |
| `className`   | `string`                                                           | `''`                 | Additional CSS class to apply              |
| `sx`          | `SxProps<Theme>`                                                   | `{}`                 | MUI system props for additional styling    |

## Implementation Details

```tsx
import React from "react";
import {
  FormControl,
  InputLabel,
  Select as MuiSelect,
  MenuItem,
  FormHelperText,
  SelectChangeEvent,
  SelectProps as MuiSelectProps,
} from "@mui/material";
import { SxProps, Theme } from "@mui/material/styles";

export interface SelectOption {
  value: string | number;
  label: string;
  disabled?: boolean;
}

interface SelectProps extends Omit<MuiSelectProps, "variant"> {
  name: string;
  label?: string;
  value?: string | string[] | number | number[];
  onChange?: (event: SelectChangeEvent<unknown>) => void;
  options: SelectOption[];
  placeholder?: string;
  required?: boolean;
  disabled?: boolean;
  error?: boolean;
  helperText?: string;
  fullWidth?: boolean;
  size?: "small" | "medium";
  multiple?: boolean;
  className?: string;
  sx?: SxProps<Theme>;
}

export function Select({
  name,
  label,
  value = "",
  onChange,
  options = [],
  placeholder = "Select an option",
  required = false,
  disabled = false,
  error = false,
  helperText = "",
  fullWidth = true,
  size = "medium",
  multiple = false,
  className = "",
  sx = {},
  ...rest
}: SelectProps) {
  const labelId = `${name}-label`;
  const displayEmpty = !value || (Array.isArray(value) && value.length === 0);

  return (
    <FormControl
      required={required}
      error={error}
      disabled={disabled}
      fullWidth={fullWidth}
      size={size}
      className={className}
      sx={sx}
    >
      {label && <InputLabel id={labelId}>{label}</InputLabel>}
      <MuiSelect
        labelId={labelId}
        id={name}
        name={name}
        value={value}
        onChange={onChange}
        label={label}
        displayEmpty={displayEmpty}
        multiple={multiple}
        variant="outlined"
        renderValue={(selected) => {
          if (displayEmpty) {
            return <em>{placeholder}</em>;
          }

          if (multiple && Array.isArray(selected)) {
            return selected
              .map(
                (value) =>
                  options.find((opt) => opt.value === value)?.label || value,
              )
              .join(", ");
          }

          const option = options.find((opt) => opt.value === selected);
          return option ? option.label : selected;
        }}
        {...rest}
      >
        {displayEmpty && (
          <MenuItem value="" disabled>
            <em>{placeholder}</em>
          </MenuItem>
        )}
        {options.map((option) => (
          <MenuItem
            key={option.value}
            value={option.value}
            disabled={option.disabled}
          >
            {option.label}
          </MenuItem>
        ))}
      </MuiSelect>
      {helperText && <FormHelperText>{helperText}</FormHelperText>}
    </FormControl>
  );
}
```

## Features

- **Consistent Styling**: Follows the application's design system
- **Validation States**: Visual indicators for errors and required fields
- **Helper Text**: Support for guidance and error messages
- **Multiple Selection**: Support for selecting multiple options
- **Placeholder Text**: Clear indication when no option is selected
- **Disabled Options**: Individual options can be disabled
- **Accessible**: Proper labeling and keyboard navigation
- **Type Support**: Strong TypeScript typing for options and values

## Usage Patterns

### Basic Dropdown

```tsx
<Select
  label="Department"
  name="department"
  value={formData.department}
  onChange={(e) => setFormData({ ...formData, department: e.target.value })}
  options={[
    { value: "engineering", label: "Engineering" },
    { value: "marketing", label: "Marketing" },
    { value: "sales", label: "Sales" },
    { value: "support", label: "Customer Support" },
  ]}
  required
/>
```

### Multiple Selection

```tsx
<Select
  label="Interests"
  name="interests"
  value={formData.interests}
  onChange={(e) => setFormData({ ...formData, interests: e.target.value })}
  options={[
    { value: "tech", label: "Technology" },
    { value: "finance", label: "Finance" },
    { value: "health", label: "Healthcare" },
    { value: "education", label: "Education" },
    { value: "environment", label: "Environment" },
  ]}
  multiple
  helperText="Select all that apply"
/>
```

### With Error State

```tsx
<Select
  label="Priority"
  name="priority"
  value={priority}
  onChange={handlePriorityChange}
  options={[
    { value: "low", label: "Low" },
    { value: "medium", label: "Medium" },
    { value: "high", label: "High" },
    { value: "critical", label: "Critical" },
  ]}
  error={!!errors.priority}
  helperText={errors.priority}
  required
/>
```

### Disabled Options

```tsx
<Select
  label="Subscription Plan"
  name="plan"
  value={plan}
  onChange={handlePlanChange}
  options={[
    { value: "free", label: "Free Tier" },
    { value: "basic", label: "Basic Plan" },
    { value: "premium", label: "Premium Plan" },
    { value: "enterprise", label: "Enterprise Plan", disabled: !isEnterprise },
  ]}
/>
```

### Compact Dropdown

```tsx
<Select
  label="Sort By"
  name="sortBy"
  value={sortBy}
  onChange={handleSortChange}
  options={[
    { value: "name", label: "Name" },
    { value: "date", label: "Date Created" },
    { value: "modified", label: "Last Modified" },
  ]}
  size="small"
/>
```

## Best Practices

1. Always provide clear, descriptive labels for your Select components
2. Group related options together logically
3. Use placeholder text to indicate when no selection has been made
4. Provide helper text to explain the purpose of the selection when needed
5. Use validation and error messages for required selections
6. For long lists, consider adding search functionality or grouping options
7. Test keyboard navigation for accessibility compliance
8. Keep option labels concise and descriptive
