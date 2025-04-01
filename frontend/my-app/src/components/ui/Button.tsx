import React from 'react';

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
  ...props
}) => {
  const baseClasses = 'inline-flex items-center justify-center font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed';
  
  const variantClasses = {
    primary: 'bg-gradient-to-r from-primary to-primary-dark text-white shadow-modern hover:shadow-modern-hover hover:brightness-105',
    secondary: 'bg-gradient-to-r from-secondary to-secondary-dark text-white shadow-modern hover:shadow-modern-hover hover:brightness-105',
    outline: 'border border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50 hover:text-primary-dark',
    ghost: 'text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50',
  };
  
  const sizeClasses = {
    sm: 'text-xs px-2.5 py-1',
    md: 'text-sm px-4 py-2',
    lg: 'text-base px-6 py-3',
  };
  
  const roundedClasses = pill ? 'rounded-full' : 'rounded-lg';
  
  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${roundedClasses} ${className}`;
  
  return (
    <button
      type={type}
      className={buttonClasses}
      {...props}
    >
      {children}
    </button>
  );
}; 