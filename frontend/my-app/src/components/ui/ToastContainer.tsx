import React from "react";
import Toast, { ToastType } from "./Toast";

export interface ToastData {
  /**
   * Unique ID for the toast
   */
  id: string;

  /**
   * Toast type/severity
   */
  type: ToastType;

  /**
   * Message to display
   */
  message: string;

  /**
   * Auto dismiss timeout in milliseconds
   * Set to 0 to prevent auto-dismissal
   */
  duration?: number;
}

export interface ToastContainerProps {
  /**
   * Array of toast notifications to display
   */
  toasts: ToastData[];

  /**
   * Position of the toast container
   * @default 'bottom-right'
   */
  position?:
    | "top-right"
    | "top-left"
    | "bottom-right"
    | "bottom-left"
    | "top-center"
    | "bottom-center";

  /**
   * Function to call when a toast is dismissed
   */
  onDismiss: (id: string) => void;
}

/**
 * Container for managing and displaying multiple toast notifications
 */
export const ToastContainer: React.FC<ToastContainerProps> = ({
  toasts,
  position = "bottom-right",
  onDismiss,
}) => {
  // Position classes for toast container
  const positionClasses = {
    "top-right": "top-0 right-0",
    "top-left": "top-0 left-0",
    "bottom-right": "bottom-0 right-0",
    "bottom-left": "bottom-0 left-0",
    "top-center": "top-0 left-1/2 transform -translate-x-1/2",
    "bottom-center": "bottom-0 left-1/2 transform -translate-x-1/2",
  };

  // Determine if toasts should stack upward or downward
  const isTopPosition = position.startsWith("top");

  return (
    <div
      className={`fixed z-50 p-4 flex flex-col ${positionClasses[position]} ${
        isTopPosition ? "space-y-3" : "space-y-3 flex-col-reverse"
      }`}
      data-testid="toast-container"
    >
      {toasts.map((toast) => (
        <Toast
          key={toast.id}
          id={toast.id}
          type={toast.type}
          message={toast.message}
          duration={toast.duration}
          onDismiss={onDismiss}
        />
      ))}
    </div>
  );
};

export default ToastContainer;
