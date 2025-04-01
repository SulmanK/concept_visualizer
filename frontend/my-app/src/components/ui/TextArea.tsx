import React, { TextareaHTMLAttributes } from 'react';

export interface TextAreaProps extends TextareaHTMLAttributes<HTMLTextAreaElement> {
  /**
   * TextArea label
   */
  label?: string;
  
  /**
   * Helper text
   */
  helperText?: string;
  
  /**
   * Error message
   */
  error?: string;
  
  /**
   * Full width textarea
   */
  fullWidth?: boolean;
}

/**
 * TextArea component for forms
 */
export const TextArea: React.FC<TextAreaProps> = ({
  label,
  helperText,
  error,
  fullWidth = false,
  className = '',
  id,
  rows = 4,
  ...props
}) => {
  // Generate a unique ID if not provided
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  
  const textareaBaseClasses = 'w-full px-4 py-3 rounded-lg border focus:ring-2 focus:outline-none transition-all duration-200 resize-y';
  const textareaErrorClasses = error 
    ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
    : 'border-indigo-200 focus:border-primary focus:ring-primary/30';
  
  const textareaClasses = `${textareaBaseClasses} ${textareaErrorClasses} ${className}`.trim();
  
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={textareaId} className="block text-sm font-medium text-indigo-700 mb-2">
          {label}
        </label>
      )}
      
      <textarea
        id={textareaId}
        className={textareaClasses}
        rows={rows}
        aria-invalid={error ? 'true' : 'false'}
        aria-describedby={
          error 
            ? `${textareaId}-error` 
            : helperText 
              ? `${textareaId}-helper` 
              : undefined
        }
        {...props}
      />
      
      {error && (
        <p id={`${textareaId}-error`} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
      
      {!error && helperText && (
        <p id={`${textareaId}-helper`} className="mt-2 text-xs text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
}; 