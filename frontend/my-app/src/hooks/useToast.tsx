import { useContext, createContext } from "react";
import { ToastType } from "../components/ui/Toast";

export interface ToastContextProps {
  /**
   * Show a success toast notification
   */
  showSuccess: (message: string, duration?: number) => string;

  /**
   * Show an error toast notification
   */
  showError: (message: string, duration?: number) => string;

  /**
   * Show an info toast notification
   */
  showInfo: (message: string, duration?: number) => string;

  /**
   * Show a warning toast notification
   */
  showWarning: (message: string, duration?: number) => string;

  /**
   * Show a custom toast notification
   */
  showToast: (type: ToastType, message: string, duration?: number) => string;

  /**
   * Dismiss a specific toast by ID
   */
  dismissToast: (id: string) => void;

  /**
   * Dismiss all currently displayed toasts
   */
  dismissAll: () => void;
}

/**
 * Context for toast notifications
 */
export const ToastContext = createContext<ToastContextProps | undefined>(
  undefined,
);

/**
 * Custom hook for using the Toast context
 * @returns Context object with toast functions
 * @throws Error if used outside of ToastProvider
 */
export const useToast = (): ToastContextProps => {
  const context = useContext(ToastContext);

  if (context === undefined) {
    throw new Error("useToast must be used within a ToastProvider");
  }

  return context;
};

export default useToast;
