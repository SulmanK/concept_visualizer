# Header Component

The `Header` component serves as the main navigation bar at the top of the application, providing access to primary navigation links, user account controls, and branding.

## Overview

The Header is a fixed component that appears on all pages, providing consistent navigation across the application. It includes the application logo, main navigation links, and user-related controls like profile and authentication options.

## Usage

```tsx
import { Header } from "components/layout/Header";

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

| Prop          | Type      | Default | Description                                             |
| ------------- | --------- | ------- | ------------------------------------------------------- |
| `className`   | `string`  | `''`    | Additional CSS class to apply to the header             |
| `transparent` | `boolean` | `false` | Whether the header should have a transparent background |

## Implementation Details

```tsx
import React, { useState } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Box,
  Menu,
  MenuItem,
  Container,
  useScrollTrigger,
  useMediaQuery,
} from "@mui/material";
import { Menu as MenuIcon, AccountCircle } from "@mui/icons-material";
import { useNavigate } from "react-router-dom";
import { useTheme } from "@mui/material/styles";
import { useAuth } from "contexts/AuthContext";
import logoImage from "assets/logos/logo.svg";

interface HeaderProps {
  className?: string;
  transparent?: boolean;
}

export function Header({ className = "", transparent = false }: HeaderProps) {
  const theme = useTheme();
  const navigate = useNavigate();
  const { user, signOut } = useAuth();
  const isMobile = useMediaQuery(theme.breakpoints.down("md"));

  // Change header appearance on scroll
  const scrollTrigger = useScrollTrigger({
    disableHysteresis: true,
    threshold: 50,
  });

  // Mobile menu state
  const [mobileMenuAnchor, setMobileMenuAnchor] = useState<null | HTMLElement>(
    null,
  );
  const isMobileMenuOpen = Boolean(mobileMenuAnchor);

  // User menu state
  const [userMenuAnchor, setUserMenuAnchor] = useState<null | HTMLElement>(
    null,
  );
  const isUserMenuOpen = Boolean(userMenuAnchor);

  // Handle mobile menu
  const handleMobileMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setMobileMenuAnchor(event.currentTarget);
  };

  const handleMobileMenuClose = () => {
    setMobileMenuAnchor(null);
  };

  // Handle user menu
  const handleUserMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setUserMenuAnchor(event.currentTarget);
  };

  const handleUserMenuClose = () => {
    setUserMenuAnchor(null);
  };

  // Navigation handlers
  const navigateTo = (path: string) => {
    navigate(path);
    handleMobileMenuClose();
    handleUserMenuClose();
  };

  const handleSignOut = () => {
    signOut();
    handleUserMenuClose();
    navigate("/");
  };

  return (
    <AppBar
      position="fixed"
      className={className}
      elevation={scrollTrigger || !transparent ? 4 : 0}
      sx={{
        backgroundColor:
          transparent && !scrollTrigger
            ? "transparent"
            : theme.palette.background.paper,
        transition: theme.transitions.create([
          "background-color",
          "box-shadow",
        ]),
      }}
    >
      <Container maxWidth="lg">
        <Toolbar disableGutters>
          {/* Logo */}
          <Box
            sx={{
              display: "flex",
              alignItems: "center",
              flexGrow: { xs: 1, md: 0 },
            }}
          >
            <img
              src={logoImage}
              alt="Concept Visualizer Logo"
              height={40}
              onClick={() => navigateTo("/")}
              style={{ cursor: "pointer" }}
            />
            <Typography
              variant="h6"
              sx={{
                ml: 1,
                display: { xs: "none", sm: "block" },
                color:
                  transparent && !scrollTrigger
                    ? theme.palette.common.white
                    : theme.palette.text.primary,
              }}
            >
              Concept Visualizer
            </Typography>
          </Box>

          {/* Desktop Navigation */}
          {!isMobile && (
            <Box
              sx={{ display: "flex", flexGrow: 1, justifyContent: "center" }}
            >
              <Button
                color="inherit"
                onClick={() => navigateTo("/")}
                sx={{
                  color:
                    transparent && !scrollTrigger
                      ? theme.palette.common.white
                      : theme.palette.text.primary,
                }}
              >
                Home
              </Button>
              <Button
                color="inherit"
                onClick={() => navigateTo("/concepts")}
                sx={{
                  color:
                    transparent && !scrollTrigger
                      ? theme.palette.common.white
                      : theme.palette.text.primary,
                }}
              >
                My Concepts
              </Button>
            </Box>
          )}

          {/* User Actions */}
          <Box sx={{ display: "flex" }}>
            {user ? (
              <>
                <IconButton
                  edge="end"
                  aria-label="account of current user"
                  aria-controls="user-menu"
                  aria-haspopup="true"
                  onClick={handleUserMenuOpen}
                  color="inherit"
                  sx={{
                    color:
                      transparent && !scrollTrigger
                        ? theme.palette.common.white
                        : theme.palette.text.primary,
                  }}
                >
                  <AccountCircle />
                </IconButton>
                <Menu
                  id="user-menu"
                  anchorEl={userMenuAnchor}
                  keepMounted
                  open={isUserMenuOpen}
                  onClose={handleUserMenuClose}
                >
                  <MenuItem onClick={() => navigateTo("/profile")}>
                    Profile
                  </MenuItem>
                  <MenuItem onClick={() => navigateTo("/settings")}>
                    Settings
                  </MenuItem>
                  <MenuItem onClick={handleSignOut}>Sign Out</MenuItem>
                </Menu>
              </>
            ) : (
              <Button
                color="primary"
                variant="contained"
                onClick={() => navigateTo("/login")}
              >
                Sign In
              </Button>
            )}

            {/* Mobile Menu Button */}
            {isMobile && (
              <>
                <IconButton
                  edge="start"
                  color="inherit"
                  aria-label="menu"
                  aria-controls="mobile-menu"
                  aria-haspopup="true"
                  onClick={handleMobileMenuOpen}
                  sx={{
                    ml: 1,
                    color:
                      transparent && !scrollTrigger
                        ? theme.palette.common.white
                        : theme.palette.text.primary,
                  }}
                >
                  <MenuIcon />
                </IconButton>
                <Menu
                  id="mobile-menu"
                  anchorEl={mobileMenuAnchor}
                  keepMounted
                  open={isMobileMenuOpen}
                  onClose={handleMobileMenuClose}
                >
                  <MenuItem onClick={() => navigateTo("/")}>Home</MenuItem>
                  <MenuItem onClick={() => navigateTo("/concepts")}>
                    My Concepts
                  </MenuItem>
                </Menu>
              </>
            )}
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  );
}
```

## Features

- **Responsive Design**: Adapts to different screen sizes, with a hamburger menu for mobile devices
- **Navigation**: Provides access to main application sections
- **User Authentication**: Displays sign-in button or user menu based on authentication state
- **Branding**: Prominently displays application logo and name
- **Transparency Option**: Can be transparent for use on hero sections, gradually becoming opaque on scroll
- **Scroll Behavior**: Changes appearance when scrolling down the page

## Accessibility

- Proper ARIA attributes for interactive elements
- Keyboard navigation support for menus
- Sufficient color contrast for text readability
- Proper alt text for logo image

## Customization

The Header can be customized through:

1. **Props**: Using the `transparent` prop to control background transparency
2. **CSS**: Using the `className` prop to apply custom styles
3. **Theme**: Customizing appearance through the Material-UI theme
4. **Extension**: Creating a wrapped version with additional navigation items
