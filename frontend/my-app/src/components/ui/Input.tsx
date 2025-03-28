import React, { InputHTMLAttributes } from 'react';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  /**
   * Input label
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
   * Full width input
   */
  fullWidth?: boolean;
  
  /**
   * Icon to display at start of input
   */
  startIcon?: React.ReactNode;
  
  /**
   * Icon to display at end of input
   */
  endIcon?: React.ReactNode;
}

/**
 * Input component for forms
 */
export const Input: React.FC<InputProps> = ({
  label,
  helperText,
  error,
  fullWidth = false,
  className = '',
  startIcon,
  endIcon,
  id,
  ...props
}) => {
  // Generate a unique ID if not provided
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  const inputClasses = [
    'input',
    error ? 'border-accent-500 focus:border-accent-500 focus:ring-accent-500' : '',
    startIcon ? 'pl-10' : '',
    endIcon ? 'pr-10' : '',
    fullWidth ? 'w-full' : '',
    className
  ].join(' ').trim();
  
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={inputId} className="label">
          {label}
        </label>
      )}
      
      <div className="relative">
        {startIcon && (
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            {startIcon}
          </div>
        )}
        
        <input
          id={inputId}
          className={inputClasses}
          aria-invalid={error ? 'true' : 'false'}
          aria-describedby={
            error 
              ? `${inputId}-error` 
              : helperText 
                ? `${inputId}-helper` 
                : undefined
          }
          {...props}
        />
        
        {endIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {endIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-sm text-accent-600">
          {error}
        </p>
      )}
      
      {!error && helperText && (
        <p id={`${inputId}-helper`} className="helper-text">
          {helperText}
        </p>
      )}
    </div>
  );
}; 