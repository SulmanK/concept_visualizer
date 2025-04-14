import React, { useEffect } from 'react';
import useToast from '../../hooks/useToast';
import { ToastType } from './Toast';

interface ToastDetail {
  title?: string;
  message: string;
  type: ToastType;
  duration?: number;
  isRateLimitError?: boolean;
  rateLimitResetTime?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
}

/**
 * Component that listens for global API toast events and displays them
 * This bridges the gap between non-React code (like apiClient) and React's toast system
 */
const ApiToastListener: React.FC = () => {
  const { showToast, showError, showSuccess, showInfo, showWarning } = useToast();

  useEffect(() => {
    // Function to handle custom toast events
    const handleApiToast = (event: Event) => {
      const customEvent = event as CustomEvent<ToastDetail>;
      const detail = customEvent.detail;

      if (!detail) return;

      // Format the message with title if provided
      const message = detail.title 
        ? `${detail.title}: ${detail.message}` 
        : detail.message;

      // For rate limit errors, use a longer duration and add "Rate Limit: " prefix if not already there
      let formattedMessage = message;
      let duration = detail.duration;
      
      if (detail.isRateLimitError) {
        // Add rate limit specific prefix if not already there
        if (!formattedMessage.toLowerCase().includes('rate limit')) {
          formattedMessage = `Rate Limit: ${formattedMessage}`;
        }
        
        // Use longer duration for rate limit errors
        duration = detail.duration || 8000; // Use 8 seconds for rate limit errors by default
        
        // Handle specific type for rate limit errors
        showWarning(formattedMessage, duration, detail.action);
        return;
      }

      // Use the appropriate toast function based on type
      switch (detail.type) {
        case 'success':
          showSuccess(message, detail.duration);
          break;
        case 'error':
          showError(message, detail.duration);
          break;
        case 'warning':
          showWarning(message, detail.duration);
          break;
        case 'info':
          showInfo(message, detail.duration);
          break;
        default:
          showToast(detail.type || 'info', message, detail.duration);
      }

      // Handle action if provided
      if (detail.action && detail.action.onClick) {
        // We could implement actions here if needed
        // This would require enhancing the Toast component
      }
    };

    // Listen for the custom event
    document.addEventListener('show-api-toast', handleApiToast);

    // Cleanup
    return () => {
      document.removeEventListener('show-api-toast', handleApiToast);
    };
  }, [showToast, showError, showSuccess, showInfo, showWarning]);

  // This is a utility component - it doesn't render anything
  return null;
};

export default ApiToastListener; 