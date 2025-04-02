import React, { useState } from 'react';
import { usePrefersReducedMotion } from '../../hooks';

export interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button variant
   */
  variant?: 'primary' | 'secondary' | 'outline' | 'ghost';
  
  /**
   * Button size
   */
  size?: 'sm' | 'md' | 'lg';
  
  /**
   * Whether to use a pill shape (fully rounded)
   */
  pill?: boolean;
  
  /**
   * Button type attribute
   */
  type?: 'button' | 'submit' | 'reset';
  
  /**
   * Additional class names
   */
  className?: string;
  
  /**
   * Button children
   */
  children: React.ReactNode;
  
  /**
   * Whether to add subtle hover animation
   * @default true
   */
  animated?: boolean;
}

/**
 * Button component with different variants and sizes
 */
export const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'md',
  pill = false,
  type = 'button',
  className = '',
  children,
  animated = true,
  onClick,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const prefersReducedMotion = usePrefersReducedMotion();
  
  // Base classes for all buttons
  const baseClasses = 'inline-flex items-center justify-center font-medium focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed';
  
  // Transition classes (skip if reduced motion is preferred)
  const transitionClasses = prefersReducedMotion ? '' : 'transition-all duration-200';
  
  // Define variant-specific classes
  const variantClasses = {
    primary: 'bg-gradient-to-r from-primary to-primary-dark text-white shadow-modern hover:shadow-modern-hover hover:brightness-105',
    secondary: 'bg-gradient-to-r from-secondary to-secondary-dark text-white shadow-modern hover:shadow-modern-hover hover:brightness-105',
    outline: 'border border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50 hover:text-primary-dark',
    ghost: 'text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50',
  };
  
  // Size classes
  const sizeClasses = {
    sm: 'text-xs px-2.5 py-1',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-6 py-3',
  };
  
  // Border radius based on pill prop
  const roundedClasses = pill ? 'rounded-full' : 'rounded-lg';
  
  // Animation classes for pressed state
  const animationClasses = animated && !prefersReducedMotion
    ? isPressed
      ? 'transform scale-95' 
      : 'transform scale-100 hover:scale-[1.02]'
    : '';
  
  // Combine all classes
  const buttonClasses = `${baseClasses} ${transitionClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${roundedClasses} ${animationClasses} ${className}`;
  
  // Handle click with animation
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (animated && !prefersReducedMotion && !props.disabled) {
      setIsPressed(true);
      
      // Reset the pressed state after animation
      setTimeout(() => {
        setIsPressed(false);
      }, 150);
    }
    
    // Call the original onClick handler
    if (onClick) {
      onClick(e);
    }
  };
  
  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  );
}; 