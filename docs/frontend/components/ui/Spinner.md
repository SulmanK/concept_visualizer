# Spinner Component

The `Spinner` component provides a lightweight, customizable loading animation primarily used for inline or smaller loading indicators throughout the application.

## Overview

This component offers a simplified alternative to the LoadingIndicator component, optimized for smaller UI elements and inline loading states. It uses CSS animations for efficiency and provides various customization options.

## Usage

```tsx
import { Spinner } from 'components/ui/Spinner';

// Basic usage
<Spinner />

// Custom size and color
<Spinner size={20} color="secondary" />

// With different variant
<Spinner variant="dots" />

// Inside a button
<Button disabled={isLoading}>
  {isLoading ? <Spinner size={16} color="inherit" /> : null}
  Submit
</Button>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `number` | `24` | Size of the spinner in pixels |
| `color` | `'primary' \| 'secondary' \| 'success' \| 'error' \| 'warning' \| 'info' \| 'inherit'` | `'primary'` | Color of the spinner |
| `variant` | `'circular' \| 'dots' \| 'pulse'` | `'circular'` | Style variant of the spinner |
| `thickness` | `number` | `2` | Thickness of the spinner (for circular variant) |
| `className` | `string` | `''` | Additional CSS class to apply |
| `sx` | `SxProps<Theme>` | `{}` | MUI system props for additional styling |

## Implementation Details

```tsx
import React from 'react';
import { Box } from '@mui/material';
import { useTheme } from '@mui/material/styles';
import { SxProps, Theme } from '@mui/material/styles';

interface SpinnerProps {
  size?: number;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info' | 'inherit';
  variant?: 'circular' | 'dots' | 'pulse';
  thickness?: number;
  className?: string;
  sx?: SxProps<Theme>;
}

export function Spinner({
  size = 24,
  color = 'primary',
  variant = 'circular',
  thickness = 2,
  className = '',
  sx = {},
}: SpinnerProps) {
  const theme = useTheme();
  
  // Get the color from theme or use directly if 'inherit'
  const spinnerColor = color === 'inherit' 
    ? 'currentColor' 
    : theme.palette[color].main;
  
  // Render different spinner variants
  const renderSpinner = () => {
    switch (variant) {
      case 'dots':
        return (
          <Box
            className={`spinner-dots ${className}`}
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '4px',
              width: size,
              height: size / 2,
              ...sx,
            }}
          >
            {[0, 1, 2].map((i) => (
              <Box
                key={i}
                sx={{
                  width: size / 6,
                  height: size / 6,
                  borderRadius: '50%',
                  backgroundColor: spinnerColor,
                  animation: 'spinner-dots 1.4s infinite ease-in-out',
                  animationDelay: `${i * 0.16}s`,
                  '@keyframes spinner-dots': {
                    '0%, 80%, 100%': {
                      transform: 'scale(0)',
                    },
                    '40%': {
                      transform: 'scale(1)',
                    },
                  },
                }}
              />
            ))}
          </Box>
        );
        
      case 'pulse':
        return (
          <Box
            className={`spinner-pulse ${className}`}
            sx={{
              width: size,
              height: size,
              borderRadius: '50%',
              backgroundColor: spinnerColor,
              animation: 'spinner-pulse 1.2s infinite cubic-bezier(0.4, 0, 0.2, 1)',
              opacity: 0.7,
              '@keyframes spinner-pulse': {
                '0%': {
                  transform: 'scale(0.8)',
                  opacity: 0.7,
                },
                '50%': {
                  transform: 'scale(1)',
                  opacity: 0.5,
                },
                '100%': {
                  transform: 'scale(0.8)',
                  opacity: 0.7,
                },
              },
              ...sx,
            }}
          />
        );
        
      case 'circular':
      default:
        return (
          <Box
            className={`spinner-circular ${className}`}
            sx={{
              width: size,
              height: size,
              borderRadius: '50%',
              border: `${thickness}px solid ${theme.palette.grey[200]}`,
              borderTopColor: spinnerColor,
              animation: 'spinner-circular 0.8s linear infinite',
              '@keyframes spinner-circular': {
                '0%': {
                  transform: 'rotate(0deg)',
                },
                '100%': {
                  transform: 'rotate(360deg)',
                },
              },
              ...sx,
            }}
          />
        );
    }
  };
  
  return renderSpinner();
}
```

## Features

- **Lightweight**: Uses CSS animations for better performance
- **Multiple Variants**: Supports circular, dots, and pulse animation styles
- **Theme Integration**: Uses theme colors for consistent styling
- **Customizable**: Adjustable size, thickness, and color
- **Adaptive**: Works well in various contexts (inline, buttons, etc.)
- **Size Efficient**: Optimized for smaller UI elements
- **Performance**: Minimal impact on UI responsiveness

## Usage Patterns

### Inline Text Loading

```tsx
<Typography variant="body1">
  Loading results 
  <Spinner size={14} variant="dots" sx={{ display: 'inline-block', ml: 1 }} />
</Typography>
```

### Button Loading State

```tsx
<Button 
  variant="primary" 
  disabled={isSubmitting}
  sx={{ minWidth: 120 }}
>
  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
    {isSubmitting && <Spinner size={16} color="inherit" />}
    {isSubmitting ? 'Submitting...' : 'Submit'}
  </Box>
</Button>
```

### Icon Replacement

```tsx
<IconButton 
  disabled={isRefreshing}
  onClick={handleRefresh}
  aria-label="Refresh data"
>
  {isRefreshing ? <Spinner size={18} color="inherit" /> : <RefreshIcon />}
</IconButton>
```

### Minimal Loading State

```tsx
<Card>
  <CardHeader 
    title="Recent Activity"
    action={
      isLoading ? <Spinner size={20} /> : (
        <IconButton onClick={handleRefresh}>
          <RefreshIcon />
        </IconButton>
      )
    }
  />
  <CardContent>
    {/* Content */}
  </CardContent>
</Card>
```

### Multiple Spinner Styles

```tsx
function LoadingStateDemo() {
  return (
    <Box sx={{ display: 'flex', gap: 4, alignItems: 'center' }}>
      <Box sx={{ textAlign: 'center' }}>
        <Spinner variant="circular" />
        <Typography variant="caption">Circular</Typography>
      </Box>
      <Box sx={{ textAlign: 'center' }}>
        <Spinner variant="dots" />
        <Typography variant="caption">Dots</Typography>
      </Box>
      <Box sx={{ textAlign: 'center' }}>
        <Spinner variant="pulse" />
        <Typography variant="caption">Pulse</Typography>
      </Box>
    </Box>
  );
}
```

## Best Practices

1. Use the Spinner component for smaller, inline loading states
2. Choose the appropriate variant based on the context and available space
3. For primary page or section loading, consider using the LoadingIndicator component instead
4. Match the spinner color with associated interactive elements
5. Keep spinners small when used inline with text to avoid disrupting reading flow
6. Use the same loading indicator consistently for similar operations
7. For buttons, use the built-in Button loading state if possible, or ensure consistent placement
8. Avoid using too many spinners simultaneously as it can be visually distracting 