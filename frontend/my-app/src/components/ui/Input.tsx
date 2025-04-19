import React, { InputHTMLAttributes, useState } from 'react';
import { usePrefersReducedMotion } from '../../hooks';

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
  
  /**
   * Whether to apply focus animation
   * @default true
   */
  animated?: boolean;
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
  animated = true,
  onFocus,
  onBlur,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const prefersReducedMotion = usePrefersReducedMotion();
  
  // Generate a unique ID if not provided
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  
  // Base input classes
  const inputBaseClasses = 'w-full px-4 py-3 rounded-lg border focus:outline-none';
  
  // Focus ring classes
  const focusRingClasses = 'focus:ring-2 focus:ring-primary/30 focus:border-primary';
  
  // Error classes
  const inputErrorClasses = error 
    ? 'border-red-300 focus:border-red-500 focus:ring-red-200' 
    : 'border-indigo-200';
    
  // Icon adjustment classes
  const inputIconClasses = [
    startIcon ? 'pl-10' : '',
    endIcon ? 'pr-10' : '',
  ].join(' ').trim();
  
  // Transition classes for animation
  const transitionClasses = animated && !prefersReducedMotion
    ? 'transition-all duration-200'
    : '';
  
  // Animation classes for the label and border
  const animationClasses = animated && !prefersReducedMotion && isFocused
    ? 'scale-[1.02] border-indigo-400'
    : '';
  
  // Combine all input classes
  const inputClasses = `${inputBaseClasses} ${focusRingClasses} ${inputErrorClasses} ${inputIconClasses} ${transitionClasses} ${animationClasses} ${className}`.trim();
  
  // Label animation
  const labelClasses = animated && !prefersReducedMotion
    ? `block text-sm font-medium text-indigo-700 mb-2 transition-all duration-200 ${isFocused ? 'text-indigo-600 translate-x-1' : ''}`
    : 'block text-sm font-medium text-indigo-700 mb-2';
    
  // Handle focus event
  const handleFocus = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(true);
    if (onFocus) onFocus(e);
  };
  
  // Handle blur event
  const handleBlur = (e: React.FocusEvent<HTMLInputElement>) => {
    setIsFocused(false);
    if (onBlur) onBlur(e);
  };
  
  return (
    <div className={fullWidth ? 'w-full' : ''}>
      {label && (
        <label htmlFor={inputId} className={labelClasses}>
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
          aria-invalid={Boolean(error)}
          aria-describedby={
            error 
              ? `${inputId}-error` 
              : helperText 
                ? `${inputId}-helper` 
                : undefined
          }
          onFocus={handleFocus}
          onBlur={handleBlur}
          {...props}
        />
        
        {endIcon && (
          <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
            {endIcon}
          </div>
        )}
      </div>
      
      {error && (
        <p id={`${inputId}-error`} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
      
      {!error && helperText && (
        <p id={`${inputId}-helper`} className="mt-2 text-xs text-gray-500">
          {helperText}
        </p>
      )}
    </div>
  );
};

export default Input; 