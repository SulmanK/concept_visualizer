import React, { Component, ErrorInfo, ReactNode } from "react";
import { ErrorMessage } from "./ErrorMessage";

interface ErrorBoundaryProps {
  /**
   * Child components to be rendered inside the error boundary
   */
  children: ReactNode;

  /**
   * Custom fallback component to render when an error occurs
   * If not provided, will use the default ErrorMessage component
   */
  fallback?: ReactNode;

  /**
   * Whether to retry loading the component that crashed
   * @default true
   */
  canRetry?: boolean;

  /**
   * Custom error message to display
   * @default "Something went wrong in this component"
   */
  errorMessage?: string;

  /**
   * Callback function to be called when an error is caught
   */
  onError?: (error: Error, errorInfo: ErrorInfo) => void;
}

interface ErrorBoundaryState {
  /**
   * Whether an error has been caught
   */
  hasError: boolean;

  /**
   * The error that was caught
   */
  error: Error | null;

  /**
   * Additional information about the error
   */
  errorInfo: ErrorInfo | null;
}

/**
 * Component that catches JavaScript errors anywhere in its child component tree,
 * displays a fallback UI, and logs the errors.
 *
 * Usage:
 * ```jsx
 * <ErrorBoundary>
 *   <ComponentThatMightThrow />
 * </ErrorBoundary>
 * ```
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  /**
   * Update state so the next render will show the fallback UI
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  /**
   * Log the error to an error reporting service
   */
  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    this.setState({ errorInfo });

    // Call the onError callback if provided
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log the error to the console
    console.error("Error caught by ErrorBoundary:", error, errorInfo);
  }

  /**
   * Reset the error boundary state to try again
   */
  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    const { hasError, error, errorInfo } = this.state;
    const {
      children,
      fallback,
      canRetry = true,
      errorMessage = "Something went wrong in this component",
    } = this.props;

    // If there's no error, render the children
    if (!hasError) {
      return children;
    }

    // If custom fallback is provided, render it
    if (fallback) {
      return fallback;
    }

    // Get the component stack from the error info
    const componentStack = errorInfo?.componentStack || "";

    // Format the stack for display as details
    const errorDetails =
      error?.stack || error?.message || "No error details available";

    // Otherwise, render our default error message
    return (
      <div className="p-4 rounded-lg shadow-sm">
        <ErrorMessage
          message={errorMessage}
          details={`${errorDetails}\n\nComponent stack: ${componentStack}`}
          type="client"
          onRetry={canRetry ? this.handleRetry : undefined}
        />
      </div>
    );
  }
}

export default ErrorBoundary;
