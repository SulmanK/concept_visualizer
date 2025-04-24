# Theme Configuration

The `theme.tsx` file defines the global theming for the application using Material-UI's theming system. It establishes a consistent design language across the application including colors, typography, spacing, and component styles.

## Overview

The theme file creates and exports a custom theme that extends Material-UI's default theme. This theme is then provided to the entire application via the `ThemeProvider` in the `App` component.

## Implementation

```tsx
import { createTheme, responsiveFontSizes } from "@mui/material/styles";

// Define custom color palette
const palette = {
  primary: {
    main: "#2563EB",
    light: "#60A5FA",
    dark: "#1E40AF",
    contrastText: "#FFFFFF",
  },
  secondary: {
    main: "#10B981",
    light: "#34D399",
    dark: "#059669",
    contrastText: "#FFFFFF",
  },
  error: {
    main: "#EF4444",
    light: "#F87171",
    dark: "#B91C1C",
  },
  warning: {
    main: "#F59E0B",
    light: "#FBBF24",
    dark: "#D97706",
  },
  info: {
    main: "#3B82F6",
    light: "#60A5FA",
    dark: "#2563EB",
  },
  success: {
    main: "#10B981",
    light: "#34D399",
    dark: "#059669",
  },
  background: {
    default: "#F9FAFB",
    paper: "#FFFFFF",
  },
  text: {
    primary: "#1F2937",
    secondary: "#6B7280",
    disabled: "#9CA3AF",
  },
};

// Define custom typography
const typography = {
  fontFamily: [
    "Inter",
    "-apple-system",
    "BlinkMacSystemFont",
    '"Segoe UI"',
    "Roboto",
    '"Helvetica Neue"',
    "Arial",
    "sans-serif",
  ].join(","),
  h1: {
    fontWeight: 700,
    fontSize: "2.5rem",
  },
  h2: {
    fontWeight: 600,
    fontSize: "2rem",
  },
  h3: {
    fontWeight: 600,
    fontSize: "1.75rem",
  },
  h4: {
    fontWeight: 600,
    fontSize: "1.5rem",
  },
  h5: {
    fontWeight: 600,
    fontSize: "1.25rem",
  },
  h6: {
    fontWeight: 600,
    fontSize: "1rem",
  },
  subtitle1: {
    fontSize: "1rem",
    fontWeight: 500,
  },
  subtitle2: {
    fontSize: "0.875rem",
    fontWeight: 500,
  },
  body1: {
    fontSize: "1rem",
  },
  body2: {
    fontSize: "0.875rem",
  },
  button: {
    textTransform: "none",
    fontWeight: 600,
  },
};

// Create the base theme
let theme = createTheme({
  palette,
  typography,
  shape: {
    borderRadius: 8,
  },
  spacing: 8,
});

// Component overrides
theme = createTheme(theme, {
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          padding: `${theme.spacing(1)} ${theme.spacing(2)}`,
          boxShadow: "none",
          "&:hover": {
            boxShadow: "none",
          },
        },
        contained: {
          "&:hover": {
            boxShadow: "none",
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: `0 1px 3px 0 rgba(0, 0, 0, 0.1)`,
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          "& .MuiOutlinedInput-root": {
            "& fieldset": {
              borderColor: "#E5E7EB",
            },
            "&:hover fieldset": {
              borderColor: theme.palette.primary.main,
            },
          },
        },
      },
    },
  },
});

// Enable responsive font sizes
theme = responsiveFontSizes(theme);

export { theme };
```

## Key Features

### Color Palette

The theme defines a consistent color palette for the application, including:

- **Primary Colors**: Main brand colors used for primary actions and highlighting important UI elements
- **Secondary Colors**: Used for secondary actions and complementary UI elements
- **Feedback Colors**: Error, warning, info, and success colors for status feedback
- **Background Colors**: Colors for different background surfaces
- **Text Colors**: Different text colors for various contexts and emphasis levels

### Typography

The theme establishes a consistent typography system:

- **Font Family**: Primary and fallback fonts for the application
- **Headings**: Styles for h1-h6 elements with appropriate sizing and weights
- **Body Text**: Styles for body text with different sizes
- **Other Text Elements**: Styles for buttons, captions, and other specialized text elements

### Component Customization

The theme customizes Material-UI components to match the application's design:

- **Buttons**: Custom padding, no elevation shadow, custom hover effects
- **Cards**: Subtle shadow effect
- **Text Fields**: Custom border colors and hover states

### Responsive Design

The theme uses `responsiveFontSizes` to automatically adjust font sizes based on screen size, ensuring text is readable across different devices.

## Usage

To use the theme in components:

```tsx
import { useTheme } from "@mui/material/styles";

function MyComponent() {
  const theme = useTheme();

  return (
    <div
      style={{
        color: theme.palette.primary.main,
        padding: theme.spacing(2),
        fontFamily: theme.typography.fontFamily,
      }}
    >
      Themed component
    </div>
  );
}
```
