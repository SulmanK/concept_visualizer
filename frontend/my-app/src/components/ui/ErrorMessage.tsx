import React from 'react';
import { ErrorWithCategory } from '../../hooks/useErrorHandling';
import { formatTimeRemaining } from '../../services/rateLimitService';

export type ErrorType = 'validation' | 'network' | 'permission' | 'notFound' | 'server' | 'generic' | 'rateLimit';

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
}

/**
 * Component for displaying error messages with appropriate styling based on error type
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  details,
  type = 'generic',
  className = '',
  onRetry,
  onDismiss,
  rateLimitData,
}) => {
  // Map of error types to appropriate styling
  const typeStyles = {
    validation: 'bg-orange-50 border-orange-200 text-orange-700',
    network: 'bg-blue-50 border-blue-200 text-blue-700',
    permission: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    notFound: 'bg-purple-50 border-purple-200 text-purple-700',
    server: 'bg-red-50 border-red-200 text-red-700',
    generic: 'bg-indigo-50 border-indigo-200 text-indigo-700',
    rateLimit: 'bg-pink-50 border-pink-200 text-pink-700',
  };
  
  // Error icons based on type
  const ErrorIcon = () => {
    switch (type) {
      case 'validation':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      case 'network':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 2V5h1v1H5zM3 13a1 1 0 011-1h3a1 1 0 011 1v3a1 1 0 01-1 1H4a1 1 0 01-1-1v-3zm2 2v-1h1v1H5zM13 4a1 1 0 00-1 1v3a1 1 0 001 1h3a1 1 0 001-1V5a1 1 0 00-1-1h-3zm1 2v1h1V6h-1zM13 13a1 1 0 00-1 1v3a1 1 0 001 1h3a1 1 0 001-1v-3a1 1 0 00-1-1h-3zm1 2v1h1v-1h-1z" clipRule="evenodd" />
          </svg>
        );
      case 'permission':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z" clipRule="evenodd" />
          </svg>
        );
      case 'rateLimit':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z" clipRule="evenodd" />
          </svg>
        );
      case 'server':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
          </svg>
        );
      default:
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
          </svg>
        );
    }
  };

  // If this is a rate limit error, show detailed information
  const isRateLimit = type === 'rateLimit' && rateLimitData;

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
        <h3 className="text-sm font-medium">{message}</h3>
        {details && <p className="mt-1 text-xs opacity-80">{details}</p>}
        
        {isRateLimit && (
          <div className="mt-3 bg-white bg-opacity-50 p-3 rounded-md">
            <div className="text-xs font-medium mb-2">API Usage Limit Reached</div>
            <div className="flex justify-between text-xs mb-1">
              <span>Current usage:</span>
              <span className="font-medium">{rateLimitData.current}/{rateLimitData.limit} per {rateLimitData.period}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span>Reset in:</span>
              <span className="font-medium">{formatTimeRemaining(rateLimitData.resetAfterSeconds)}</span>
            </div>
            
            <div className="mt-2 text-xs">
              <a href="/pricing" className="text-pink-700 hover:underline font-medium">
                Upgrade your plan
              </a>
              {' '}for higher usage limits
            </div>
          </div>
        )}
        
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
export const RateLimitErrorMessage: React.FC<Omit<ErrorMessageProps, 'type' | 'rateLimitData' | 'message'> & { error: ErrorWithCategory }> = ({
  error,
  ...props
}) => {
  return (
    <ErrorMessage
      type="rateLimit"
      message={error.message}
      details={error.details}
      rateLimitData={{
        limit: error.limit || 0,
        current: error.current || 0,
        period: error.period || 'unknown',
        resetAfterSeconds: error.resetAfterSeconds || 0
      }}
      {...props}
    />
  );
};

export default ErrorMessage; 