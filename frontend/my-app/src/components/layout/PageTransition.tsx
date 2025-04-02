import React, { useEffect, useState, useRef, useLayoutEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { AnimatedTransition } from '../ui';

interface PageTransitionProps {
  /**
   * The component/page to render
   */
  children: React.ReactNode;
  
  /**
   * Type of animation to use for transitions
   * @default 'fade'
   */
  transitionType?: 'fade' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right';
  
  /**
   * Duration of the enter animation in ms
   * @default 300
   */
  enterDuration?: number;
  
  /**
   * Duration of the exit animation in ms
   * @default 250
   */
  exitDuration?: number;
}

/**
 * Component that adds animated transitions between page changes with pre-loading
 * and smooth transitions to prevent flash of content
 */
export const PageTransition: React.FC<PageTransitionProps> = ({ 
  children, 
  transitionType = 'fade',
  enterDuration = 300,
  exitDuration = 250
}) => {
  const location = useLocation();
  const [displayLocation, setDisplayLocation] = useState(location);
  const [transitionStage, setTransitionStage] = useState<'fadeIn' | 'fadeOut'>('fadeIn');
  const [isInitialRender, setIsInitialRender] = useState(true);
  const [isContentReady, setIsContentReady] = useState(false);
  const previousChildren = useRef<React.ReactNode>(null);
  const contentRef = useRef<HTMLDivElement>(null);
  const [currentChildren, setCurrentChildren] = useState<React.ReactNode>(children);
  
  // Handle initial render using useLayoutEffect to prevent flash
  useLayoutEffect(() => {
    if (isInitialRender) {
      // Hide content immediately
      if (contentRef.current) {
        contentRef.current.style.opacity = '0';
      }
      
      // Wait for next frame to ensure content is hidden
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          setIsInitialRender(false);
          setIsContentReady(true);
        });
      });
    }
  }, [isInitialRender]);
  
  useEffect(() => {
    if (location.pathname !== displayLocation.pathname) {
      // Store current children before location changes
      previousChildren.current = currentChildren;
      
      // Start exit animation but don't update children yet
      setIsContentReady(false);
      setTransitionStage('fadeOut');
      
      // Wait for exit animation to complete before changing displayLocation
      const timeout = setTimeout(() => {
        setDisplayLocation(location);
        // Only after exit animation completes, update the current children
        setCurrentChildren(children);
        
        // Now prepare to fade in the new content
        requestAnimationFrame(() => {
          setIsContentReady(true);
          setTransitionStage('fadeIn');
        });
      }, exitDuration);
      
      return () => clearTimeout(timeout);
    } else {
      // Update current children when not transitioning
      setCurrentChildren(children);
    }
  }, [location, displayLocation.pathname, exitDuration, children]);
  
  return (
    <div 
      ref={contentRef}
      className="page-transition-container"
      style={{
        opacity: 0,
        visibility: isContentReady ? 'visible' : 'hidden',
        transition: `opacity ${enterDuration}ms ease-out, visibility ${enterDuration}ms ease-out`
      }}
    >
      <AnimatedTransition
        show={transitionStage === 'fadeIn' && isContentReady}
        type={transitionType}
        enterDuration={enterDuration}
        exitDuration={exitDuration}
        className="h-full w-full"
        style={{ 
          contain: 'content',
          visibility: isContentReady ? 'visible' : 'hidden'
        }}
        onEntered={() => {
          if (contentRef.current) {
            contentRef.current.style.opacity = '1';
          }
        }}
      >
        <div key={displayLocation.pathname} className="h-full w-full">
          {/* Only render the appropriate content based on transition stage */}
          {transitionStage === 'fadeOut' && previousChildren.current}
          {transitionStage === 'fadeIn' && currentChildren}
        </div>
      </AnimatedTransition>
    </div>
  );
};

export default PageTransition; 