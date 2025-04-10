import React from 'react';
import { LoadingIndicator } from './LoadingIndicator';

export interface SpinnerProps {
  /**
   * Size of the spinner
   * @default "md"
   */
  size?: 'sm' | 'md' | 'lg';
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Spinner component that provides a loading indicator
 * This is a wrapper around LoadingIndicator with a simplified API
 */
export const Spinner: React.FC<SpinnerProps> = ({ 
  size = 'md', 
  className = '' 
}) => {
  // Map the size props to LoadingIndicator sizes
  const sizeMap = {
    'sm': 'small',
    'md': 'medium',
    'lg': 'large',
  };
  
  return (
    <LoadingIndicator 
      size={sizeMap[size]} 
      className={className} 
      variant="primary"
    />
  );
};

export default Spinner; 