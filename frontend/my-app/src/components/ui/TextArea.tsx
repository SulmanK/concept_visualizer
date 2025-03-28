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
  
  const textareaClasses = [
    'input',
    'resize-y',
    error ? 'border-accent-500 focus:border-accent-500 focus:ring-accent-500' : '',
    fullWidth ? 'w-full' : '',
    className
  ].join(' ').trim();
  
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={textareaId} className="label">
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
        <p id={`${textareaId}-error`} className="mt-1 text-sm text-accent-600">
          {error}
        </p>
      )}
      
      {!error && helperText && (
        <p id={`${textareaId}-helper`} className="helper-text">
          {helperText}
        </p>
      )}
    </div>
  );
}; 