import React, { useState, useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'info' | 'warning';

export interface ToastProps {
  /**
   * Unique ID for the toast
   */
  id: string;
  
  /**
   * Toast type/severity that affects styling
   */
  type: ToastType;
  
  /**
   * Message to display
   */
  message: string;
  
  /**
   * Function to call when toast is dismissed
   */
  onDismiss?: (id: string) => void;
  
  /**
   * Auto dismiss timeout in milliseconds
   * @default 5000 (5 seconds)
   */
  duration?: number;
  
  /**
   * Whether to show close button
   * @default true
   */
  showCloseButton?: boolean;
}

/**
 * Toast notification component for showing transient messages
 */
export const Toast: React.FC<ToastProps> = ({
  id,
  type,
  message,
  onDismiss,
  duration = 5000,
  showCloseButton = true,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [progress, setProgress] = useState(100);

  // Toast styling based on type
  const toastStyles = {
    success: 'bg-green-50 border-green-500 text-green-700',
    error: 'bg-red-50 border-red-500 text-red-700',
    info: 'bg-indigo-50 border-indigo-500 text-indigo-700',
    warning: 'bg-yellow-50 border-yellow-500 text-yellow-700',
  };

  // Progress bar styling based on type
  const progressStyles = {
    success: 'bg-green-500',
    error: 'bg-red-500',
    info: 'bg-indigo-500',
    warning: 'bg-yellow-500',
  };

  // Icons for different toast types
  const ToastIcon = () => {
    switch (type) {
      case 'success':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
          </svg>
        );
      case 'error':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
      case 'warning':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  // Handle toast dismissal
  const handleDismiss = () => {
    setIsVisible(false);
    setTimeout(() => {
      if (onDismiss) {
        onDismiss(id);
      }
    }, 300); // Wait for fade out animation
  };

  // Auto-dismiss countdown
  useEffect(() => {
    if (duration > 0) {
      const interval = setInterval(() => {
        setProgress((prevProgress) => {
          const newProgress = prevProgress - (100 / (duration / 100));
          return newProgress <= 0 ? 0 : newProgress;
        });
      }, 100);

      const timeout = setTimeout(() => {
        handleDismiss();
      }, duration);

      return () => {
        clearInterval(interval);
        clearTimeout(timeout);
      };
    }
  }, [duration]);

  return (
    <div
      className={`
        transform transition-all duration-300 ease-in-out
        ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-2 opacity-0 pointer-events-none'}
        max-w-sm w-full shadow-lg rounded-lg pointer-events-auto
        border-l-4 ${toastStyles[type]} overflow-hidden
      `}
      role="alert"
      aria-live="assertive"
      data-testid="toast-notification"
    >
      <div className="relative">
        <div className="flex items-start p-4">
          <div className="flex-shrink-0 mr-3">
            <ToastIcon />
          </div>
          
          <div className="flex-1 pt-0.5">
            <p className="text-sm font-medium">{message}</p>
          </div>
          
          {showCloseButton && (
            <button 
              type="button"
              className="ml-4 flex-shrink-0 text-gray-400 hover:text-gray-500 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded"
              onClick={handleDismiss}
              aria-label="Close"
              data-testid="toast-close-button"
            >
              <svg className="h-4 w-4" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
        
        {/* Progress bar */}
        {duration > 0 && (
          <div 
            className={`h-1 ${progressStyles[type]} transition-all ease-linear duration-100`} 
            style={{ width: `${progress}%` }}
          />
        )}
      </div>
    </div>
  );
};

export default Toast; 