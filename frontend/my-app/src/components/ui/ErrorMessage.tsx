import React from "react";
import { ErrorWithCategory } from "../../hooks/useErrorHandling";
import { formatTimeRemaining } from "../../services/rateLimitService";

export type ErrorType =
  | "validation"
  | "network"
  | "permission"
  | "notFound"
  | "server"
  | "client"
  | "generic"
  | "rateLimit"
  | "auth";

export interface ErrorMessageProps {
  /**
   * Error message to display
   */
  message: string;

  /**
   * Error details (optional) for more technical explanation
   */
  details?: string;

  /**
   * Type of error that affects styling and icon
   * @default 'generic'
   */
  type?: ErrorType;

  /**
   * Custom CSS class name
   */
  className?: string;

  /**
   * Handler for retry button click
   */
  onRetry?: () => void;

  /**
   * Handler for dismiss button click
   */
  onDismiss?: () => void;

  /**
   * Rate limit specific data (only used when type is 'rateLimit')
   */
  rateLimitData?: {
    limit: number;
    current: number;
    period: string;
    resetAfterSeconds: number;
  };

  /**
   * Error code from backend API
   */
  error_code?: string;

  /**
   * Validation errors for specific fields
   */
  validationErrors?: Record<string, string[]>;

  /**
   * HTTP status code
   */
  status?: number;
}

/**
 * Component for displaying error messages with appropriate styling based on error type
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  details,
  type = "generic",
  className = "",
  onRetry,
  onDismiss,
  rateLimitData,
  error_code,
  validationErrors,
  status,
}) => {
  // Map of error types to appropriate styling
  const typeStyles = {
    validation: "bg-orange-50 border-orange-200 text-orange-700",
    network: "bg-blue-50 border-blue-200 text-blue-700",
    permission: "bg-yellow-50 border-yellow-200 text-yellow-700",
    notFound: "bg-purple-50 border-purple-200 text-purple-700",
    server: "bg-red-50 border-red-200 text-red-700",
    client: "bg-orange-50 border-orange-200 text-orange-700",
    generic: "bg-indigo-50 border-indigo-200 text-indigo-700",
    rateLimit: "bg-pink-50 border-pink-200 text-pink-700",
    auth: "bg-amber-50 border-amber-200 text-amber-700",
  };

  // Error icons based on type
  const ErrorIcon = () => {
    switch (type) {
      case "validation":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "network":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M3 4a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 2V5h1v1H5zM3 13a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1v-3zm2 2v-1h1v1H5zM13 4a1 1 0 00-1 1v3a1 1 0 001 1h3a1 1 0 001-1V5a1 1 0 00-1-1h-3zm1 2v1h1V6h-1zM13 13a1 1 0 00-1 1v3a1 1 0 001 1h3a1 1 0 001-1v-3a1 1 0 00-1-1h-3zm1 2v1h1v-1h-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "permission":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "rateLimit":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "auth":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "notFound":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "server":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      case "client":
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zm-1 4a1 1 0 00-1 1v3a1 1 0 102 0v-3a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        );
      default:
        return (
          <svg
            xmlns="http://www.w3.org/2000/svg"
            className="h-5 w-5"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
        );
    }
  };

  // Special error types
  const isRateLimit = type === "rateLimit" && rateLimitData;
  const isValidation =
    type === "validation" &&
    validationErrors &&
    Object.keys(validationErrors).length > 0;

  // Get action advice based on error type
  const getActionAdvice = () => {
    switch (type) {
      case "network":
        return "Please check your internet connection and try again.";
      case "validation":
        return "Please review the form fields and correct any errors.";
      case "permission":
        return "You may need to request access to this resource.";
      case "notFound":
        return "The requested resource could not be found. It may have been moved or deleted.";
      case "server":
        return "Our servers are experiencing issues. Please try again later.";
      case "auth":
        return "Your session may have expired. Please sign in again.";
      case "client":
        return "There was an issue with your request. Please try again with valid parameters.";
      case "rateLimit":
        return rateLimitData && rateLimitData.resetAfterSeconds > 0
          ? `Please try again next month when the usage limits reset.`
          : "You've reached your usage limit for this month. Please try again next month.";
      default:
        return "If this issue persists, please contact support.";
    }
  };

  // Format time with countdown for rate limit errors
  const formatRateLimitTime = (seconds: number) => {
    if (seconds <= 0) return "less than a minute";

    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;

    if (minutes === 0) {
      return `${remainingSeconds} second${remainingSeconds !== 1 ? "s" : ""}`;
    } else if (remainingSeconds === 0) {
      return `${minutes} minute${minutes !== 1 ? "s" : ""}`;
    } else {
      return `${minutes}m ${remainingSeconds}s`;
    }
  };

  return (
    <div
      className={`flex items-start p-4 rounded-lg border ${typeStyles[type]} ${className}`}
      role="alert"
      aria-live="assertive"
      data-testid="error-message"
    >
      <div className="flex-shrink-0 mr-3">
        <ErrorIcon />
      </div>

      <div className="flex-1">
        <div className="flex justify-between items-start">
          <h3 className="text-sm font-medium">{message}</h3>
          {(error_code || status) && (
            <span className="text-xs opacity-70 bg-white/30 px-1.5 py-0.5 rounded ml-2">
              {error_code ? `Code: ${error_code}` : `${status}`}
            </span>
          )}
        </div>

        {details && <p className="mt-1 text-xs opacity-80">{details}</p>}

        {/* Validation errors */}
        {isValidation && (
          <div className="mt-2 text-xs space-y-1">
            {Object.entries(validationErrors).map(([field, errors]) => (
              <div key={field} className="bg-white bg-opacity-50 p-2 rounded">
                <span className="font-medium">{field}: </span>
                <span>{Array.isArray(errors) ? errors[0] : errors}</span>
              </div>
            ))}
          </div>
        )}

        {/* Action advice based on error type */}
        <p className="mt-2 text-xs">{getActionAdvice()}</p>

        {/* Rate limit specific information */}
        {isRateLimit && (
          <div className="mt-3 bg-white bg-opacity-50 p-3 rounded-md">
            <div className="text-xs font-medium mb-2">
              API Usage Limit Reached
            </div>
            <div className="flex justify-between text-xs mb-1">
              <span>Current usage:</span>
              <span className="font-medium">
                {rateLimitData.current}/{rateLimitData.limit} per{" "}
                {rateLimitData.period}
              </span>
            </div>
            <div className="flex justify-between text-xs">
              <span>Reset:</span>
              <span className="font-medium">
                At the beginning of next month
              </span>
            </div>

            <div className="w-full bg-gray-200 rounded-full h-1.5 my-2">
              <div
                className="bg-pink-700 h-1.5 rounded-full"
                style={{
                  width: `${Math.min(
                    100,
                    (rateLimitData.current / rateLimitData.limit) * 100,
                  )}%`,
                }}
              ></div>
            </div>
          </div>
        )}

        {/* Authentication errors */}
        {type === "auth" && (
          <div className="mt-3">
            <button
              className="px-3 py-1 text-xs bg-amber-100 text-amber-700 rounded hover:bg-amber-200 transition-colors"
              onClick={() => {
                // Dispatch a sign-in event
                document.dispatchEvent(new CustomEvent("sign-in-required"));
              }}
            >
              Sign in again
            </button>
          </div>
        )}

        {/* Action buttons */}
        {(onRetry || onDismiss) && (
          <div className="mt-3 flex gap-2">
            {onRetry && !isRateLimit && (
              <button
                onClick={onRetry}
                className="text-xs font-medium hover:underline"
                data-testid="error-retry-button"
              >
                Try Again
              </button>
            )}

            {onDismiss && (
              <button
                onClick={onDismiss}
                className="text-xs hover:underline opacity-80"
                data-testid="error-dismiss-button"
              >
                Dismiss
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

/**
 * Creates an ErrorMessage component preconfigured for rate limit errors
 */
export const RateLimitErrorMessage: React.FC<
  Omit<ErrorMessageProps, "type" | "rateLimitData" | "message"> & {
    error: ErrorWithCategory;
  }
> = ({ error, ...props }) => {
  // Add a check to ensure we have rate limit data
  if (!error.limit || !error.resetAfterSeconds) {
    console.warn(
      "RateLimitErrorMessage received an error without rate limit data",
      error,
    );
  }

  return (
    <ErrorMessage
      type="rateLimit"
      message={error.message}
      details={error.details}
      rateLimitData={{
        limit: error.limit || 0,
        current: error.current || 0,
        period: error.period || "unknown",
        resetAfterSeconds: error.resetAfterSeconds || 0,
      }}
      {...props}
    />
  );
};

/**
 * Creates an ErrorMessage component preconfigured for validation errors
 */
export const ValidationErrorMessage: React.FC<
  Omit<ErrorMessageProps, "type" | "validationErrors" | "message"> & {
    error: ErrorWithCategory & { validationErrors?: Record<string, string[]> };
  }
> = ({ error, ...props }) => {
  return (
    <ErrorMessage
      type="validation"
      message={error.message}
      details={error.details}
      validationErrors={error.validationErrors}
      {...props}
    />
  );
};

export default ErrorMessage;
