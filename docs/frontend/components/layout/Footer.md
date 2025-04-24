# Footer Component

The `Footer` component displays the application footer with links, legal information, and branding.

## Overview

The footer appears at the bottom of every page in the application and provides secondary navigation, copyright information, and additional links. It maintains a consistent appearance across all pages.

## Usage

```tsx
import { Footer } from "components/layout/Footer";

function App() {
  return (
    <div className="app">
      <Header />
      <main>{/* Page content */}</main>
      <Footer />
    </div>
  );
}
```

## Props

| Prop        | Type     | Default | Description                                 |
| ----------- | -------- | ------- | ------------------------------------------- |
| `className` | `string` | `''`    | Additional CSS class to apply to the footer |

## Implementation Details

```tsx
import React from "react";
import { Box, Container, Typography, Link, Grid } from "@mui/material";
import { styled } from "@mui/material/styles";

const StyledFooter = styled("footer")(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(6, 0),
  marginTop: "auto", // Pushes footer to bottom when page content is short
  borderTop: `1px solid ${theme.palette.divider}`,
}));

export function Footer({ className = "" }: { className?: string }) {
  const currentYear = new Date().getFullYear();

  return (
    <StyledFooter className={className}>
      <Container maxWidth="lg">
        <Grid container spacing={4} justifyContent="space-between">
          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="textPrimary" gutterBottom>
              Concept Visualizer
            </Typography>
            <Typography variant="body2" color="textSecondary">
              Generate visual concepts with AI-powered technology
            </Typography>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="textPrimary" gutterBottom>
              Quick Links
            </Typography>
            <Box component="ul" sx={{ p: 0, listStyle: "none" }}>
              <li>
                <Link href="/" color="inherit">
                  Home
                </Link>
              </li>
              <li>
                <Link href="/concepts" color="inherit">
                  My Concepts
                </Link>
              </li>
              <li>
                <Link href="/help" color="inherit">
                  Help Center
                </Link>
              </li>
            </Box>
          </Grid>

          <Grid item xs={12} sm={4}>
            <Typography variant="h6" color="textPrimary" gutterBottom>
              Legal
            </Typography>
            <Box component="ul" sx={{ p: 0, listStyle: "none" }}>
              <li>
                <Link href="/privacy" color="inherit">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" color="inherit">
                  Terms of Service
                </Link>
              </li>
            </Box>
          </Grid>
        </Grid>

        <Box mt={5}>
          <Typography variant="body2" color="textSecondary" align="center">
            © {currentYear} Concept Visualizer. All rights reserved.
          </Typography>
        </Box>
      </Container>
    </StyledFooter>
  );
}
```

## Features

- Responsive design that adapts to different screen sizes
- Organized link sections for easy navigation
- Automatically updates the copyright year
- Uses Material-UI components for consistent styling
- Sticky footer that stays at the bottom even with minimal page content

## Accessibility

The Footer component is designed with accessibility in mind:

- Proper heading hierarchy for screen readers
- Semantic HTML elements
- Sufficient color contrast for text readability
- Proper link labeling for navigation

## Customization

The Footer can be customized through:

1. **CSS overrides**: Using the `className` prop
2. **Theme customization**: Changing the Material-UI theme variables
3. **Component extension**: Creating a wrapped version with additional links or content
