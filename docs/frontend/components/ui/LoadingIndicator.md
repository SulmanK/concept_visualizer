# LoadingIndicator Component

The `LoadingIndicator` component provides a standardized loading animation that visually indicates to users that content is being loaded or an operation is in progress.

## Overview

This component creates a consistent visual indicator for loading states across the application. It wraps Material-UI's CircularProgress component with application-specific styling and provides additional options for customization.

## Usage

```tsx
import { LoadingIndicator } from 'components/ui/LoadingIndicator';

// Basic usage
<LoadingIndicator />

// Custom size and color
<LoadingIndicator size={40} color="secondary" />

// With text label
<LoadingIndicator label="Loading data..." />

// Centered in container
<LoadingIndicator center />
```

## Props

| Prop        | Type                                       | Default           | Description                                        |
| ----------- | ------------------------------------------ | ----------------- | -------------------------------------------------- |
| `size`      | `number \| 'small' \| 'medium' \| 'large'` | `'medium'`        | Size of the loading indicator                      |
| `color`     | `'primary' \| 'secondary' \| 'inherit'`    | `'primary'`       | Color of the loading indicator                     |
| `label`     | `string`                                   | `''`              | Text to display below the indicator                |
| `center`    | `boolean`                                  | `false`           | Whether to center the indicator in its container   |
| `thickness` | `number`                                   | `3.6`             | Thickness of the circular progress                 |
| `variant`   | `'indeterminate' \| 'determinate'`         | `'indeterminate'` | Type of progress indicator                         |
| `value`     | `number`                                   | `0`               | Progress value (0-100) when variant is determinate |
| `className` | `string`                                   | `''`              | Additional CSS class to apply                      |
| `sx`        | `SxProps<Theme>`                           | `{}`              | MUI system props for additional styling            |

## Implementation Details

```tsx
import React from "react";
import { Box, CircularProgress, Typography } from "@mui/material";
import { SxProps, Theme } from "@mui/material/styles";

interface LoadingIndicatorProps {
  size?: number | "small" | "medium" | "large";
  color?: "primary" | "secondary" | "inherit";
  label?: string;
  center?: boolean;
  thickness?: number;
  variant?: "indeterminate" | "determinate";
  value?: number;
  className?: string;
  sx?: SxProps<Theme>;
}

export function LoadingIndicator({
  size = "medium",
  color = "primary",
  label = "",
  center = false,
  thickness = 3.6,
  variant = "indeterminate",
  value = 0,
  className = "",
  sx = {},
}: LoadingIndicatorProps) {
  // Convert named sizes to pixel values
  const sizeInPixels = (): number => {
    if (typeof size === "number") return size;
    switch (size) {
      case "small":
        return 24;
      case "large":
        return 48;
      case "medium":
      default:
        return 36;
    }
  };

  return (
    <Box
      className={className}
      sx={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: center ? "center" : "flex-start",
        ...(center && {
          position: "absolute",
          top: "50%",
          left: "50%",
          transform: "translate(-50%, -50%)",
        }),
        ...sx,
      }}
    >
      <CircularProgress
        size={sizeInPixels()}
        color={color}
        thickness={thickness}
        variant={variant}
        value={value}
      />
      {label && (
        <Typography variant="body2" color="textSecondary" sx={{ mt: 1 }}>
          {label}
        </Typography>
      )}
    </Box>
  );
}
```

## Features

- **Consistent Styling**: Follows the application's design system
- **Size Options**: Predefined sizes (small, medium, large) or custom pixel values
- **Color Variants**: Primary, secondary, or inherit colors
- **Text Labels**: Optional descriptive text
- **Centering Option**: Can be automatically centered in its container
- **Progress Tracking**: Supports both indeterminate and determinate progress
- **Customizable**: Visual aspects like thickness can be adjusted
- **Accessible**: Properly communicates loading state to screen readers

## Usage Patterns

### Basic Page Loading

```tsx
function PageContent() {
  const { data, isLoading } = useQuery(["data"], fetchData);

  if (isLoading) {
    return <LoadingIndicator center label="Loading content..." />;
  }

  return <div>{/* Render data */}</div>;
}
```

### Inline Loading

```tsx
<Box sx={{ display: "flex", alignItems: "center" }}>
  <Typography variant="body1">Loading search results</Typography>
  <LoadingIndicator size="small" sx={{ ml: 1 }} />
</Box>
```

### Determinate Progress

```tsx
function FileUpload() {
  const [progress, setProgress] = useState(0);

  // Upload logic that updates progress

  return (
    <Box sx={{ textAlign: "center" }}>
      <LoadingIndicator
        variant="determinate"
        value={progress}
        label={`Uploading... ${progress}%`}
      />
    </Box>
  );
}
```

### Loading Button Alternative

```tsx
<Box sx={{ position: "relative" }}>
  <Button
    variant="primary"
    disabled={isSubmitting}
    sx={{ opacity: isSubmitting ? 0.7 : 1 }}
  >
    Submit
  </Button>
  {isSubmitting && (
    <LoadingIndicator
      size="small"
      color="inherit"
      sx={{
        position: "absolute",
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      }}
    />
  )}
</Box>
```

### Section Loading

```tsx
<Card>
  <CardHeader title="Recent Activities" />
  <CardContent>
    {isLoading ? (
      <Box
        sx={{
          height: 200,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
        }}
      >
        <LoadingIndicator label="Loading activities..." />
      </Box>
    ) : (
      <ActivityList activities={activities} />
    )}
  </CardContent>
</Card>
```

## Best Practices

1. Use loading indicators for operations that take longer than 300ms
2. Include descriptive labels for longer operations to inform users what's happening
3. Use appropriate sizes based on context (small for inline, medium/large for main content)
4. For determinate operations, use the determinate variant to show progress
5. Position the indicator in the same location where content will appear
6. Consider using skeleton loaders for content that has a known structure
7. Ensure loading states are properly communicated to screen readers
