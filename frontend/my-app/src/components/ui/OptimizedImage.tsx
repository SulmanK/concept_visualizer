import { useState, useEffect, useRef } from 'react';

interface OptimizedImageProps {
  /**
   * Source URL of the image
   */
  src: string | undefined;
  
  /**
   * Alternative text for the image
   */
  alt: string;
  
  /**
   * Whether to lazy load the image
   * @default true
   */
  lazy?: boolean;
  
  /**
   * Width of the image element
   */
  width?: string | number;
  
  /**
   * Height of the image element
   */
  height?: string | number;
  
  /**
   * CSS class names for styling
   */
  className?: string;
  
  /**
   * Object fit property
   * @default "contain"
   */
  objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down';
  
  /**
   * Blur hash or placeholder to use while loading
   */
  placeholder?: string;
  
  /**
   * Background color to show while loading
   */
  backgroundColor?: string;
  
  /**
   * Additional props
   */
  [x: string]: any;
}

/**
 * OptimizedImage component that handles lazy loading, placeholders, and error states
 */
export const OptimizedImage: React.FC<OptimizedImageProps> = ({
  src = '/placeholder-image.png',
  alt,
  lazy = true,
  width,
  height,
  className = '',
  objectFit = 'contain',
  placeholder,
  backgroundColor = '#f3f4f6',
  ...rest
}) => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [error, setError] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const [currentSrc, setCurrentSrc] = useState<string | null>(lazy ? null : (src || '/placeholder-image.png'));
  
  // Set up intersection observer for lazy loading
  useEffect(() => {
    if (!lazy || !imgRef.current) return;
    
    observerRef.current = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        setCurrentSrc(src || '/placeholder-image.png');
        observerRef.current?.disconnect();
      }
    }, {
      rootMargin: '200px 0px', // Load images when they're 200px from viewport
      threshold: 0.01
    });
    
    observerRef.current.observe(imgRef.current);
    
    return () => {
      observerRef.current?.disconnect();
    };
  }, [src, lazy]);
  
  // Update current source if src prop changes
  useEffect(() => {
    if (!lazy || isLoaded) {
      setCurrentSrc(src || '/placeholder-image.png');
    }
  }, [src, lazy, isLoaded]);
  
  // Handle image load event
  const handleLoad = () => {
    setIsLoaded(true);
    setError(false);
  };
  
  // Handle image error event
  const handleError = () => {
    setError(true);
    console.error(`Failed to load image: ${src}`);
  };
  
  // Style object for the image
  const imageStyle: React.CSSProperties = {
    opacity: isLoaded ? 1 : 0,
    transition: 'opacity 0.3s ease-in-out',
    objectFit,
    width: width ? (typeof width === 'number' ? `${width}px` : width) : 'auto',
    height: height ? (typeof height === 'number' ? `${height}px` : height) : 'auto',
    maxWidth: '100%',
    maxHeight: '100%',
    margin: 'auto',
    display: 'block',
  };
  
  // Style for the container
  const containerStyle: React.CSSProperties = {
    position: 'relative',
    width: width ? (typeof width === 'number' ? `${width}px` : width) : 'auto',
    height: height ? (typeof height === 'number' ? `${height}px` : height) : 'auto',
    backgroundColor,
    overflow: 'hidden',
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  };
  
  // If there's an error, show a fallback
  if (error) {
    return (
      <div
        style={{
          ...containerStyle,
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          fontSize: '14px',
          color: '#6b7280',
          padding: '1rem'
        }}
        className={className}
        {...rest}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          style={{ marginBottom: '0.5rem' }}
        >
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        Failed to load image
      </div>
    );
  }
  
  return (
    <div style={containerStyle} className={className} {...rest}>
      {/* Placeholder or loading indicator */}
      {!isLoaded && (
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '100%',
            height: '100%',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            backgroundColor
          }}
        >
          {placeholder ? (
            <img
              src={placeholder}
              alt="Loading placeholder"
              style={{
                objectFit,
                width: '100%',
                height: '100%'
              }}
            />
          ) : (
            <div className="animate-pulse rounded-full h-8 w-8 border-t-2 border-b-2 border-indigo-500"></div>
          )}
        </div>
      )}
      
      {/* Actual image */}
      <img
        ref={imgRef}
        src={currentSrc || undefined}
        alt={alt}
        style={imageStyle}
        loading={lazy ? 'lazy' : undefined}
        onLoad={handleLoad}
        onError={handleError}
      />
    </div>
  );
};

export default OptimizedImage; 