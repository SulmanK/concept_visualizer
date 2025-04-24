import React from "react";

export type LoadingIndicatorSize = "small" | "medium" | "large";

export interface LoadingIndicatorProps {
  /**
   * Size of the loading indicator
   * @default 'medium'
   */
  size?: LoadingIndicatorSize;

  /**
   * Custom CSS class for the container
   */
  className?: string;

  /**
   * Show text label alongside spinner
   * @default false
   */
  showLabel?: boolean;

  /**
   * Custom label text
   * @default 'Loading...'
   */
  labelText?: string;

  /**
   * Color theme for the spinner
   * @default 'primary'
   */
  variant?: "primary" | "light" | "dark";
}

/**
 * Loading indicator component that displays a spinner with optional label
 */
export const LoadingIndicator: React.FC<LoadingIndicatorProps> = ({
  size = "medium",
  className = "",
  showLabel = false,
  labelText = "Loading...",
  variant = "primary",
}) => {
  // Size mapping for spinner dimensions
  const sizeClasses = {
    small: "h-4 w-4",
    medium: "h-8 w-8",
    large: "h-12 w-12",
  };

  // Color variants
  const colorClasses = {
    primary: "text-indigo-600",
    light: "text-white",
    dark: "text-gray-800",
  };

  // Text size mapping based on spinner size
  const textSizeClasses = {
    small: "text-xs",
    medium: "text-sm",
    large: "text-base",
  };

  return (
    <div className={`flex items-center justify-center ${className}`}>
      <div className="flex flex-col items-center gap-2">
        <svg
          className={`animate-spin ${sizeClasses[size]} ${colorClasses[variant]}`}
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
          data-testid="loading-spinner"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          ></circle>
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          ></path>
        </svg>

        {showLabel && (
          <span
            className={`${textSizeClasses[size]} font-medium ${colorClasses[variant]}`}
          >
            {labelText}
          </span>
        )}
      </div>
    </div>
  );
};

export default LoadingIndicator;
