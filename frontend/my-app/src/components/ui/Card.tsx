import React, { HTMLAttributes } from 'react';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /**
   * Card variant
   */
  variant?: 'default' | 'gradient' | 'elevated';
  
  /**
   * Header content
   */
  header?: React.ReactNode;
  
  /**
   * Footer content
   */
  footer?: React.ReactNode;
  
  /**
   * Add extra padding to the card
   */
  padded?: boolean;
  
  /**
   * Card is in loading state
   */
  isLoading?: boolean;
}

/**
 * Card component for containing content
 */
export const Card: React.FC<CardProps> = ({
  variant = 'default',
  header,
  footer,
  padded = true,
  isLoading = false,
  className = '',
  children,
  ...props
}) => {
  const baseClasses = {
    default: 'card',
    gradient: 'card-gradient',
    elevated: 'card bg-white border-none shadow-lg',
  };
  
  const cardClass = [
    baseClasses[variant],
    className
  ].join(' ').trim();
  
  const contentClass = padded ? 'p-4 sm:p-6' : '';
  
  const headerClass = 'px-4 py-3 sm:px-6 border-b border-dark-200 bg-dark-50';
  
  const footerClass = 'px-4 py-3 sm:px-6 border-t border-dark-200 bg-dark-50';
  
  return (
    <div className={cardClass} {...props}>
      {header && <div className={headerClass}>{header}</div>}
      
      <div className={contentClass}>
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          children
        )}
      </div>
      
      {footer && <div className={footerClass}>{footer}</div>}
    </div>
  );
}; 