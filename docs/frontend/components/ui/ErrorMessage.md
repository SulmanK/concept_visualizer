# ErrorMessage Component

The `ErrorMessage` component displays error information to users in a consistent and user-friendly way, providing clear messaging and potential actions to resolve the issue.

## Overview

This component presents error information with appropriate visual styling, messaging, and optional retry functionality. It supports different error types and severities, helping users understand what went wrong and how to proceed.

## Usage

```tsx
import { ErrorMessage } from 'components/ui/ErrorMessage';

// Basic usage with error object
<ErrorMessage error={new Error('Something went wrong')} />

// With retry action
<ErrorMessage
  error={new Error('Failed to load data')}
  onRetry={() => fetchData()}
/>

// With custom message and title
<ErrorMessage
  error={new Error('API_ERROR')}
  title="Unable to Connect"
  message="We couldn't connect to the service. Please check your internet connection."
/>
```

## Props

| Prop        | Type                                          | Default               | Description                                          |
| ----------- | --------------------------------------------- | --------------------- | ---------------------------------------------------- |
| `error`     | `Error \| string \| unknown`                  | -                     | The error object or message to display               |
| `title`     | `string`                                      | `'An error occurred'` | The error title or heading                           |
| `message`   | `string`                                      | -                     | Custom error message (overrides the error's message) |
| `onRetry`   | `() => void`                                  | -                     | Function to call when retry button is clicked        |
| `variant`   | `'default' \| 'inline' \| 'banner' \| 'full'` | `'default'`           | Visual styling variant                               |
| `severity`  | `'error' \| 'warning' \| 'info'`              | `'error'`             | The severity level of the error                      |
| `className` | `string`                                      | `''`                  | Additional CSS class to apply                        |

## Implementation Details

```tsx
import React from "react";
import {
  Box,
  Typography,
  Button,
  Paper,
  Alert,
  AlertTitle,
} from "@mui/material";
import { styled } from "@mui/material/styles";
import ErrorOutlineIcon from "@mui/icons-material/ErrorOutline";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
import InfoOutlinedIcon from "@mui/icons-material/InfoOutlined";
import RefreshIcon from "@mui/icons-material/Refresh";

interface ErrorMessageProps {
  error: Error | string | unknown;
  title?: string;
  message?: string;
  onRetry?: () => void;
  variant?: "default" | "inline" | "banner" | "full";
  severity?: "error" | "warning" | "info";
  className?: string;
}

const ErrorContainer = styled(Paper, {
  shouldForwardProp: (prop) => prop !== "variant",
})<{ variant: string }>(({ theme, variant }) => ({
  padding: variant === "inline" ? theme.spacing(1, 2) : theme.spacing(3),
  display: "flex",
  flexDirection: variant === "inline" ? "row" : "column",
  alignItems: variant === "inline" ? "center" : "flex-start",
  gap: theme.spacing(2),
  borderRadius: variant === "banner" ? 0 : theme.shape.borderRadius,
  width: variant === "full" ? "100%" : "auto",
  backgroundColor:
    variant === "inline"
      ? theme.palette.background.default
      : theme.palette.background.paper,
}));

export function ErrorMessage({
  error,
  title = "An error occurred",
  message,
  onRetry,
  variant = "default",
  severity = "error",
  className = "",
}: ErrorMessageProps) {
  // Extract error message from different error types
  const getErrorMessage = (): string => {
    if (message) return message;

    if (error instanceof Error) {
      return error.message;
    } else if (typeof error === "string") {
      return error;
    } else if (error && typeof error === "object" && "message" in error) {
      return String((error as { message: unknown }).message);
    }

    return "An unexpected error occurred";
  };

  // Get appropriate icon based on severity
  const getIcon = () => {
    switch (severity) {
      case "warning":
        return <WarningAmberIcon color="warning" />;
      case "info":
        return <InfoOutlinedIcon color="info" />;
      case "error":
      default:
        return <ErrorOutlineIcon color="error" />;
    }
  };

  // For inline variant, use Alert component
  if (variant === "inline") {
    return (
      <Alert
        severity={severity}
        className={className}
        action={
          onRetry && (
            <Button
              color="inherit"
              size="small"
              onClick={onRetry}
              startIcon={<RefreshIcon />}
            >
              Retry
            </Button>
          )
        }
      >
        <AlertTitle>{title}</AlertTitle>
        {getErrorMessage()}
      </Alert>
    );
  }

  // For other variants, use custom styling
  return (
    <ErrorContainer variant={variant} className={className}>
      <Box
        sx={{ display: "flex", gap: 1, alignItems: "center", width: "100%" }}
      >
        {getIcon()}
        <Typography
          variant={variant === "full" ? "h5" : "h6"}
          component="h2"
          color={`${severity}.main`}
        >
          {title}
        </Typography>
      </Box>

      <Typography variant="body1" color="text.secondary">
        {getErrorMessage()}
      </Typography>

      {onRetry && (
        <Button
          variant="outlined"
          color={severity}
          onClick={onRetry}
          startIcon={<RefreshIcon />}
          sx={{ mt: 1 }}
        >
          Try Again
        </Button>
      )}
    </ErrorContainer>
  );
}
```

## Variants

### Default

A standard error message box with title, message, and optional retry button.

```tsx
<ErrorMessage
  error={new Error("Could not load user data")}
  onRetry={refetchUserData}
/>
```

### Inline

A compact, inline alert that takes minimal vertical space, suitable for form errors or status updates.

```tsx
<ErrorMessage
  error="Invalid email address"
  variant="inline"
  severity="warning"
/>
```

### Banner

A full-width banner, typically displayed at the top of a page for important errors or notifications.

```tsx
<ErrorMessage
  error="Your session has expired"
  title="Authentication Error"
  variant="banner"
  onRetry={() => handleReauthenticate()}
/>
```

### Full

A prominent error display for critical errors, taking significant space to draw attention.

```tsx
<ErrorMessage
  error={new Error("Server connection lost")}
  title="Connection Error"
  variant="full"
  onRetry={() => window.location.reload()}
/>
```

## Severity Levels

### Error (Default)

Used for critical issues that prevent functionality.

```tsx
<ErrorMessage error="Payment processing failed" severity="error" />
```

### Warning

For non-critical issues that users should be aware of.

```tsx
<ErrorMessage
  error="Some features may be unavailable"
  title="Limited Functionality"
  severity="warning"
/>
```

### Info

For informational messages about errors or issues.

```tsx
<ErrorMessage
  error="Your data was saved locally only"
  title="Offline Mode"
  severity="info"
/>
```

## Error Handling Best Practices

1. **Be Specific**: Provide clear and specific error messages that explain what went wrong.
2. **Offer Solutions**: When possible, suggest actions users can take to resolve the issue.
3. **Use Appropriate Severity**: Match the visual severity to the actual impact of the error.
4. **Provide Retry Options**: For network or transient errors, include retry functionality.
5. **Consistent Styling**: Use consistent error styling throughout the application.
