import { useState, useEffect } from 'react';

/**
 * Hook that detects if the user has requested reduced motion in their OS settings
 * This is important for accessibility to respect user preferences
 * 
 * @returns boolean indicating if the user prefers reduced motion
 */
export const usePrefersReducedMotion = (): boolean => {
  // Default to false (animations enabled) if the query isn't supported
  const [prefersReducedMotion, setPrefersReducedMotion] = useState<boolean>(false);
  
  useEffect(() => {
    // Check if the browser supports this feature
    const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    
    // Set the initial value
    setPrefersReducedMotion(mediaQuery.matches);
    
    // Define a handler for changes to the preference
    const handleChange = (event: MediaQueryListEvent) => {
      setPrefersReducedMotion(event.matches);
    };
    
    // Add the event listener (with compatibility check for older browsers)
    if (mediaQuery.addEventListener) {
      mediaQuery.addEventListener('change', handleChange);
    } else {
      // For older browsers
      mediaQuery.addListener(handleChange);
    }
    
    // Cleanup function
    return () => {
      if (mediaQuery.removeEventListener) {
        mediaQuery.removeEventListener('change', handleChange);
      } else {
        // For older browsers
        mediaQuery.removeListener(handleChange);
      }
    };
  }, []);
  
  return prefersReducedMotion;
};

export default usePrefersReducedMotion; 