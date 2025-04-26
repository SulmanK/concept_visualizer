import React, { ReactNode, useState, useCallback } from "react";
import { v4 as uuidv4 } from "uuid";
import ToastContainer, { ToastData } from "../../components/ui/ToastContainer";
import { ToastType } from "../../components/ui/Toast";
import { ToastContext, ToastContextProps } from "../useToast";

export interface ToastProviderProps {
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
   * Default auto-dismiss duration in milliseconds
   * @default 5000 (5 seconds)
   */
  defaultDuration?: number;

  /**
   * Maximum number of toasts to show at once
   * @default 5
   */
  maxToasts?: number;

  /**
   * Children components
   */
  children: ReactNode;
}

/**
 * Provider component for the Toast context
 */
export const ToastProvider: React.FC<ToastProviderProps> = ({
  position = "bottom-right",
  defaultDuration = 5000,
  maxToasts = 5,
  children,
}) => {
  const [toasts, setToasts] = useState<ToastData[]>([]);

  // Show a toast notification with the specified type
  const showToast = useCallback(
    (type: ToastType, message: string, duration = defaultDuration): string => {
      const id = uuidv4();

      setToasts((prevToasts) => {
        // Add new toast to the beginning of the array
        const newToasts = [{ id, type, message, duration }, ...prevToasts];

        // Limit to maxToasts
        return newToasts.slice(0, maxToasts);
      });

      return id;
    },
    [defaultDuration, maxToasts],
  );

  // Helper functions for specific toast types
  const showSuccess = useCallback(
    (message: string, duration?: number) =>
      showToast("success", message, duration),
    [showToast],
  );

  const showError = useCallback(
    (message: string, duration?: number) =>
      showToast("error", message, duration),
    [showToast],
  );

  const showInfo = useCallback(
    (message: string, duration?: number) =>
      showToast("info", message, duration),
    [showToast],
  );

  const showWarning = useCallback(
    (message: string, duration?: number) =>
      showToast("warning", message, duration),
    [showToast],
  );

  // Dismiss a specific toast by ID
  const dismissToast = useCallback((id: string) => {
    setToasts((prevToasts) => prevToasts.filter((toast) => toast.id !== id));
  }, []);

  // Dismiss all toasts
  const dismissAll = useCallback(() => {
    setToasts([]);
  }, []);

  // Context value
  const contextValue: ToastContextProps = {
    showSuccess,
    showError,
    showInfo,
    showWarning,
    showToast,
    dismissToast,
    dismissAll,
  };

  return (
    <ToastContext.Provider value={contextValue}>
      {children}
      {toasts.length > 0 && (
        <ToastContainer
          toasts={toasts}
          position={position}
          onDismiss={dismissToast}
        />
      )}
    </ToastContext.Provider>
  );
};
