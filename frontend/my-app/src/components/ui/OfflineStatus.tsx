import React, { useState, useEffect } from "react";
import { useNetworkStatus } from "../../hooks/useNetworkStatus";

interface OfflineStatusProps {
  /**
   * Position of the offline status banner
   * @default 'top'
   */
  position?: "top" | "bottom";

  /**
   * Custom styles for the banner
   */
  className?: string;

  /**
   * Whether to show a retry button
   * @default true
   */
  showRetry?: boolean;

  /**
   * Whether to show connection type info
   * @default false
   */
  showConnectionInfo?: boolean;

  /**
   * Custom message to display when offline
   * @default "You are currently offline"
   */
  offlineMessage?: string;

  /**
   * Custom message to display when on a slow connection
   * @default "You are on a slow connection"
   */
  slowConnectionMessage?: string;
}

/**
 * Component that shows a banner when the user is offline or on a slow connection
 */
export const OfflineStatus: React.FC<OfflineStatusProps> = ({
  position = "top",
  className = "",
  showRetry = true,
  showConnectionInfo = false,
  offlineMessage = "You are currently offline",
  slowConnectionMessage = "You are on a slow connection",
}) => {
  const networkStatus = useNetworkStatus({ notifyOnStatusChange: false });
  const {
    isOnline,
    isSlowConnection,
    connectionType,
    checkConnection,
    offlineSince,
  } = networkStatus;

  // Local state for animation and visibility
  const [isVisible, setIsVisible] = useState<boolean>(false);
  const [isAnimating, setIsAnimating] = useState<boolean>(false);

  // Format time offline if available
  const getOfflineDuration = (): string => {
    if (!offlineSince) return "";

    const diffMs = Date.now() - offlineSince.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);

    if (diffHours > 0) {
      return `for ${diffHours}h ${diffMins % 60}m`;
    } else if (diffMins > 0) {
      return `for ${diffMins}m`;
    } else {
      return "just now";
    }
  };

  // Handle retry button click
  const handleRetry = async () => {
    setIsAnimating(true);
    await checkConnection();
    setIsAnimating(false);
  };

  // Update visibility based on network status
  useEffect(() => {
    if (!isOnline) {
      setIsVisible(true);
    } else if (isSlowConnection && showConnectionInfo) {
      setIsVisible(true);
    } else {
      setIsVisible(false);
    }
  }, [isOnline, isSlowConnection, showConnectionInfo]);

  // Don't render if online and not showing connection info
  if (isOnline && !(isSlowConnection && showConnectionInfo)) {
    return null;
  }

  // Position classes
  const positionClasses = {
    top: "top-0 left-0 right-0 border-b",
    bottom: "bottom-0 left-0 right-0 border-t",
  };

  return (
    <div
      className={`
        fixed z-50 flex items-center justify-between px-4 py-2
        transition-all duration-300 ease-in-out
        ${
          !isVisible
            ? "translate-y-[-100%] opacity-0"
            : "translate-y-0 opacity-100"
        }
        ${
          isOnline
            ? "bg-yellow-50 text-yellow-800 border-yellow-200"
            : "bg-red-50 text-red-800 border-red-200"
        }
        ${positionClasses[position]}
        ${className}
      `}
      role="alert"
      aria-live="assertive"
    >
      <div className="flex items-center">
        {isOnline ? (
          // Slow connection icon
          <svg
            className="h-5 w-5 mr-2 text-yellow-500"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
              clipRule="evenodd"
            />
          </svg>
        ) : (
          // Offline icon
          <svg
            className="h-5 w-5 mr-2 text-red-500"
            xmlns="http://www.w3.org/2000/svg"
            viewBox="0 0 20 20"
            fill="currentColor"
          >
            <path
              fillRule="evenodd"
              d="M13.477 14.89A6 6 0 015.11 6.524l8.367 8.368zm1.414-1.414L6.524 5.11a6 6 0 018.367 8.367zM18 10a8 8 0 11-16 0 8 8 0 0116 0z"
              clipRule="evenodd"
            />
          </svg>
        )}
        <span className="text-sm font-medium">
          {isOnline ? slowConnectionMessage : offlineMessage}
          {!isOnline && offlineSince && (
            <span className="ml-1 text-xs opacity-80">
              {getOfflineDuration()}
            </span>
          )}
        </span>
        {showConnectionInfo && connectionType && (
          <span className="ml-2 text-xs bg-white/60 px-1.5 py-0.5 rounded text-gray-700">
            {connectionType}
          </span>
        )}
      </div>

      {showRetry && (
        <button
          onClick={handleRetry}
          disabled={isAnimating}
          className="ml-4 text-xs font-medium bg-white/80 hover:bg-white px-2 py-1 rounded border border-current transition-colors"
        >
          {isAnimating ? (
            <span className="flex items-center">
              <svg
                className="animate-spin h-3 w-3 mr-1"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
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
              Checking...
            </span>
          ) : (
            "Retry"
          )}
        </button>
      )}
    </div>
  );
};

export default OfflineStatus;
