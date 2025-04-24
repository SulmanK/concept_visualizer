import React, { TextareaHTMLAttributes, useState } from "react";
import { usePrefersReducedMotion } from "../../hooks";

export interface TextAreaProps
  extends TextareaHTMLAttributes<HTMLTextAreaElement> {
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

  /**
   * Whether to apply focus animation
   * @default true
   */
  animated?: boolean;
}

/**
 * TextArea component for forms
 */
export const TextArea: React.FC<TextAreaProps> = ({
  label,
  helperText,
  error,
  fullWidth = false,
  className = "",
  id,
  rows = 4,
  animated = true,
  onFocus,
  onBlur,
  ...props
}) => {
  const [isFocused, setIsFocused] = useState(false);
  const prefersReducedMotion = usePrefersReducedMotion();

  // Generate a unique ID if not provided
  const textareaId =
    id || `textarea-${Math.random().toString(36).substr(2, 9)}`;

  // Base textarea classes
  const textareaBaseClasses =
    "w-full px-4 py-3 rounded-lg border focus:outline-none resize-y";

  // Focus ring classes
  const focusRingClasses =
    "focus:ring-2 focus:ring-primary/30 focus:border-primary";

  // Error classes
  const textareaErrorClasses = error
    ? "border-red-300 focus:border-red-500 focus:ring-red-200"
    : "border-indigo-200";

  // Transition classes for animation
  const transitionClasses =
    animated && !prefersReducedMotion ? "transition-all duration-200" : "";

  // Animation classes for the textarea and border
  const animationClasses =
    animated && !prefersReducedMotion && isFocused
      ? "scale-[1.01] border-indigo-400"
      : "";

  // Combine all textarea classes
  const textareaClasses =
    `${textareaBaseClasses} ${focusRingClasses} ${textareaErrorClasses} ${transitionClasses} ${animationClasses} ${className}`.trim();

  // Label animation
  const labelClasses =
    animated && !prefersReducedMotion
      ? `block text-sm font-medium text-indigo-700 mb-2 transition-all duration-200 ${
          isFocused ? "text-indigo-600 translate-x-1" : ""
        }`
      : "block text-sm font-medium text-indigo-700 mb-2";

  // Handle focus event
  const handleFocus = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    setIsFocused(true);
    if (onFocus) onFocus(e);
  };

  // Handle blur event
  const handleBlur = (e: React.FocusEvent<HTMLTextAreaElement>) => {
    setIsFocused(false);
    if (onBlur) onBlur(e);
  };

  return (
    <div className={fullWidth ? "w-full" : ""}>
      {label && (
        <label htmlFor={textareaId} className={labelClasses}>
          {label}
        </label>
      )}

      <textarea
        id={textareaId}
        className={textareaClasses}
        rows={rows}
        aria-invalid={Boolean(error)}
        aria-describedby={
          error
            ? `${textareaId}-error`
            : helperText
            ? `${textareaId}-helper`
            : undefined
        }
        onFocus={handleFocus}
        onBlur={handleBlur}
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

export default TextArea;
