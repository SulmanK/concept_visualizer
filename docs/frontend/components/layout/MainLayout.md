# MainLayout Component

The `MainLayout` component is a foundational layout wrapper that applies consistent structure to all pages, including the header, footer, and main content area.

## Overview

MainLayout provides a consistent layout structure across the application. It wraps the main content with a header and footer, handles spacing to accommodate the fixed header, and ensures the footer appears at the bottom of the viewport even when content is minimal.

## Usage

```tsx
import { MainLayout } from "components/layout/MainLayout";

function App() {
  return (
    <MainLayout>
      {/* Route components or page content */}
      <HomePage />
    </MainLayout>
  );
}
```

```tsx
// Using with React Router
import { Routes, Route } from "react-router-dom";
import { MainLayout } from "components/layout/MainLayout";

function App() {
  return (
    <MainLayout>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/concepts" element={<ConceptsPage />} />
        {/* Additional routes */}
      </Routes>
    </MainLayout>
  );
}
```

## Props

| Prop                | Type                                            | Default | Description                                                                  |
| ------------------- | ----------------------------------------------- | ------- | ---------------------------------------------------------------------------- |
| `children`          | `React.ReactNode`                               | -       | The main content to render within the layout                                 |
| `headerTransparent` | `boolean`                                       | `false` | Whether the header should be transparent (used for pages with hero sections) |
| `maxWidth`          | `'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl' \| false` | `'lg'`  | Maximum width of the content container                                       |
| `disableFooter`     | `boolean`                                       | `false` | Whether to hide the footer                                                   |

## Implementation Details

```tsx
import React from "react";
import { Container, Box, useTheme } from "@mui/material";
import { Header } from "./Header";
import { Footer } from "./Footer";

interface MainLayoutProps {
  children: React.ReactNode;
  headerTransparent?: boolean;
  maxWidth?: "xs" | "sm" | "md" | "lg" | "xl" | false;
  disableFooter?: boolean;
}

export function MainLayout({
  children,
  headerTransparent = false,
  maxWidth = "lg",
  disableFooter = false,
}: MainLayoutProps) {
  const theme = useTheme();

  return (
    <Box
      sx={{
        display: "flex",
        flexDirection: "column",
        minHeight: "100vh",
        backgroundColor: theme.palette.background.default,
      }}
    >
      {/* Header */}
      <Header transparent={headerTransparent} />

      {/* Main Content */}
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          // Add padding to account for fixed header height
          pt: headerTransparent ? 0 : theme.spacing(8),
          // Add responsive padding on smaller screens
          [theme.breakpoints.down("sm")]: {
            pt: headerTransparent ? 0 : theme.spacing(7),
          },
        }}
      >
        <Container maxWidth={maxWidth} sx={{ py: 4 }}>
          {children}
        </Container>
      </Box>

      {/* Footer */}
      {!disableFooter && <Footer />}
    </Box>
  );
}
```

## Features

- **Consistent Layout**: Applies the same header and footer to every page
- **Flexible Content Width**: Configurable maximum width for content container
- **Responsive Behavior**: Adapts to different screen sizes
- **Full Viewport Height**: Ensures the layout takes up at least the full viewport height
- **Transparent Header Option**: Allows for hero sections with transparent header overlay
- **Optional Footer**: Can hide the footer when needed (e.g., for specific pages)

## Layout Structure

The component creates the following DOM structure:

```
<Box> (flex container, min-height: 100vh)
  <Header />
  <Box component="main"> (flex-grow: 1)
    <Container maxWidth={maxWidth}>
      {children}
    </Container>
  </Box>
  <Footer /> (optional)
</Box>
```

This structure ensures:

1. The header is always at the top of the page
2. The main content takes up all available vertical space
3. The footer is always at the bottom, even when the content is shorter than the viewport
4. The content is properly centered and constrained to a maximum width for readability

## Best Practices

1. **Use consistently**: Apply MainLayout to all pages that should share the same structure
2. **Transparent header**: Use `headerTransparent={true}` for pages with hero sections at the top
3. **Content width**: Choose appropriate `maxWidth` based on the content type (e.g., `md` for forms, `lg` for content-heavy pages)

## Examples

### Standard Page

```tsx
function StandardPage() {
  return (
    <MainLayout>
      <Typography variant="h4">Standard Page</Typography>
      <Typography variant="body1">
        This page uses the standard layout with header and footer.
      </Typography>
    </MainLayout>
  );
}
```

### Landing Page with Hero Section

```tsx
function LandingPage() {
  return (
    <MainLayout headerTransparent maxWidth={false} disableFooter={false}>
      <HeroSection />
      <FeaturesSection />
      <TestimonialsSection />
      <CallToActionSection />
    </MainLayout>
  );
}
```

### Form Page with Narrower Content

```tsx
function FormPage() {
  return (
    <MainLayout maxWidth="sm">
      <Typography variant="h4">Contact Us</Typography>
      <ContactForm />
    </MainLayout>
  );
}
```
