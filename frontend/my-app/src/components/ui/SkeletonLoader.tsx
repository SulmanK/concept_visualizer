import React from 'react';

export type SkeletonType = 'text' | 'circle' | 'rectangle' | 'card' | 'image' | 'button';

export interface SkeletonLoaderProps {
  /**
   * Type of skeleton loader
   * @default 'text'
   */
  type?: SkeletonType;
  
  /**
   * Width of the skeleton
   * For text, could be '100%', '75%', etc.
   * For fixed dimensions, could be in pixels like '50px'
   */
  width?: string;
  
  /**
   * Height of the skeleton (applicable for non-text types)
   */
  height?: string;
  
  /**
   * Number of lines for text skeleton
   * @default 1
   */
  lines?: number;
  
  /**
   * Line height for text skeleton
   * @default 'md'
   */
  lineHeight?: 'sm' | 'md' | 'lg';
  
  /**
   * Border radius for the skeleton
   * @default depends on type
   */
  borderRadius?: string;
  
  /**
   * Custom CSS class
   */
  className?: string;
  
  /**
   * CSS properties for finer control
   */
  style?: React.CSSProperties;
}

/**
 * Skeleton loader component for content placeholders during loading
 */
export const SkeletonLoader: React.FC<SkeletonLoaderProps> = ({
  type = 'text',
  width,
  height,
  lines = 1,
  lineHeight = 'md',
  borderRadius,
  className = '',
  style,
}) => {
  // Common animation class
  const animationClass = 'animate-pulse bg-gradient-to-r from-indigo-100/70 to-indigo-200/70';
  
  // Line height mapping
  const lineHeightClasses = {
    sm: 'h-3',
    md: 'h-4',
    lg: 'h-6',
  };
  
  // Default width based on type
  const defaultWidth = (() => {
    switch (type) {
      case 'text': return '100%';
      case 'circle': return '48px';
      case 'rectangle': return '100%';
      case 'card': return '100%';
      case 'image': return '100%';
      case 'button': return '120px';
      default: return '100%';
    }
  })();
  
  // Default height based on type
  const defaultHeight = (() => {
    switch (type) {
      case 'text': return lineHeightClasses[lineHeight];
      case 'circle': return '48px';
      case 'rectangle': return '100px';
      case 'card': return '200px';
      case 'image': return '200px';
      case 'button': return '40px';
      default: return 'h-4';
    }
  })();
  
  // Default border radius based on type
  const defaultBorderRadius = (() => {
    switch (type) {
      case 'text': return 'rounded';
      case 'circle': return 'rounded-full';
      case 'rectangle': return 'rounded-md';
      case 'card': return 'rounded-lg';
      case 'image': return 'rounded-md';
      case 'button': return 'rounded-md';
      default: return 'rounded';
    }
  })();
  
  // Generate multiple lines for text skeleton
  if (type === 'text' && lines > 1) {
    return (
      <div className={`flex flex-col space-y-2 ${className}`} role="status" aria-label="Loading content">
        {Array.from({ length: lines }).map((_, index) => (
          <div
            key={index}
            className={`${animationClass} ${borderRadius || defaultBorderRadius} ${defaultHeight}`}
            style={{
              width: index === lines - 1 ? '75%' : width || defaultWidth,
              ...style,
            }}
          />
        ))}
        <span className="sr-only">Loading...</span>
      </div>
    );
  }
  
  // Special rendering for card skeleton
  if (type === 'card') {
    return (
      <div 
        className={`${className} overflow-hidden`} 
        style={{ width: width || defaultWidth, height: height || defaultHeight, ...style }}
        role="status"
        aria-label="Loading card"
      >
        <div className={`${animationClass} ${borderRadius || defaultBorderRadius} h-full w-full`}>
          {/* Card header */}
          <div className="h-1/3 w-full bg-indigo-100/80" />
          <div className="p-4">
            {/* Card title */}
            <div className="h-5 bg-indigo-100/80 rounded mb-4 w-3/4" />
            {/* Card content */}
            <div className="space-y-2">
              <div className="h-3 bg-indigo-100/80 rounded w-full" />
              <div className="h-3 bg-indigo-100/80 rounded w-full" />
              <div className="h-3 bg-indigo-100/80 rounded w-5/6" />
            </div>
            {/* Card footer */}
            <div className="mt-4 flex justify-between">
              <div className="h-6 bg-indigo-100/80 rounded w-1/4" />
              <div className="h-6 bg-indigo-100/80 rounded w-1/4" />
            </div>
          </div>
        </div>
        <span className="sr-only">Loading card...</span>
      </div>
    );
  }
  
  // Standard skeleton for other types
  return (
    <div
      className={`${animationClass} ${borderRadius || defaultBorderRadius} ${className}`}
      style={{
        width: width || defaultWidth,
        height: height || defaultHeight,
        ...style,
      }}
      role="status"
      aria-label="Loading"
    >
      <span className="sr-only">Loading...</span>
    </div>
  );
};

export default SkeletonLoader; 