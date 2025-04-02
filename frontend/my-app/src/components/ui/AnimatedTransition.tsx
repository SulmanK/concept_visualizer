import React, { ReactNode, CSSProperties } from 'react';
import { useAnimatedMount, AnimationState } from '../../hooks';

export type TransitionType = 'fade' | 'slide-up' | 'slide-down' | 'slide-left' | 'slide-right' | 'scale' | 'none';

export interface AnimatedTransitionProps {
  /**
   * Whether the component is visible
   */
  show: boolean;
  
  /**
   * Content to display
   */
  children: ReactNode;
  
  /**
   * Type of animation
   * @default 'fade'
   */
  type?: TransitionType;
  
  /**
   * Duration of enter animation in ms
   * @default 300
   */
  enterDuration?: number;
  
  /**
   * Duration of exit animation in ms
   * @default 300
   */
  exitDuration?: number;
  
  /**
   * Delay before animation starts in ms
   * @default 0
   */
  delay?: number;
  
  /**
   * Whether to mount the component initially without animation
   * @default false
   */
  initialMount?: boolean;
  
  /**
   * Custom CSS classes to add to the container
   */
  className?: string;
  
  /**
   * Custom styles to add to the container
   */
  style?: CSSProperties;
  
  /**
   * Custom CSS classes for different animation states
   */
  stateClasses?: Partial<Record<AnimationState, string>>;
  
  /**
   * Custom styles for different animation states
   */
  stateStyles?: Partial<Record<AnimationState, CSSProperties>>;
  
  /**
   * Function called when the component is fully entered
   */
  onEntered?: () => void;
  
  /**
   * Function called when the component is fully exited
   */
  onExited?: () => void;
}

/**
 * Component for animating elements entering and exiting the DOM
 */
export const AnimatedTransition: React.FC<AnimatedTransitionProps> = ({
  show,
  children,
  type = 'fade',
  enterDuration = 300,
  exitDuration = 300,
  delay = 0,
  initialMount = false,
  className = '',
  style = {},
  stateClasses = {},
  stateStyles = {},
  onEntered,
  onExited
}) => {
  const { animationState, isMounted } = useAnimatedMount(show, {
    enterDuration,
    exitDuration,
    initialMount,
    onEntered,
    onExited
  });
  
  if (!isMounted) {
    return null;
  }
  
  // Default transition styles based on animation type
  const getDefaultStateStyles = (): Record<AnimationState, CSSProperties> => {
    const transitionProperty = 'all';
    const transitionTimingFunction = 'cubic-bezier(0.4, 0, 0.2, 1)';
    
    // Base styles with transition properties
    const baseStyle: CSSProperties = {
      transitionProperty,
      transitionTimingFunction,
    };
    
    // Enter duration for entering state
    const enterStyle: CSSProperties = {
      ...baseStyle,
      transitionDuration: `${enterDuration}ms`,
      transitionDelay: `${delay}ms`,
    };
    
    // Exit duration for exiting state
    const exitStyle: CSSProperties = {
      ...baseStyle,
      transitionDuration: `${exitDuration}ms`,
      transitionDelay: '0ms',
    };
    
    // Default styles for each animation type
    switch (type) {
      case 'fade':
        return {
          entering: { ...enterStyle, opacity: 0 },
          entered: { ...enterStyle, opacity: 1 },
          exiting: { ...exitStyle, opacity: 0 },
          exited: { ...exitStyle, opacity: 0 },
        };
        
      case 'slide-up':
        return {
          entering: { ...enterStyle, opacity: 0, transform: 'translateY(20px)' },
          entered: { ...enterStyle, opacity: 1, transform: 'translateY(0)' },
          exiting: { ...exitStyle, opacity: 0, transform: 'translateY(20px)' },
          exited: { ...exitStyle, opacity: 0, transform: 'translateY(20px)' },
        };
        
      case 'slide-down':
        return {
          entering: { ...enterStyle, opacity: 0, transform: 'translateY(-20px)' },
          entered: { ...enterStyle, opacity: 1, transform: 'translateY(0)' },
          exiting: { ...exitStyle, opacity: 0, transform: 'translateY(-20px)' },
          exited: { ...exitStyle, opacity: 0, transform: 'translateY(-20px)' },
        };
        
      case 'slide-left':
        return {
          entering: { ...enterStyle, opacity: 0, transform: 'translateX(20px)' },
          entered: { ...enterStyle, opacity: 1, transform: 'translateX(0)' },
          exiting: { ...exitStyle, opacity: 0, transform: 'translateX(20px)' },
          exited: { ...exitStyle, opacity: 0, transform: 'translateX(20px)' },
        };
        
      case 'slide-right':
        return {
          entering: { ...enterStyle, opacity: 0, transform: 'translateX(-20px)' },
          entered: { ...enterStyle, opacity: 1, transform: 'translateX(0)' },
          exiting: { ...exitStyle, opacity: 0, transform: 'translateX(-20px)' },
          exited: { ...exitStyle, opacity: 0, transform: 'translateX(-20px)' },
        };
        
      case 'scale':
        return {
          entering: { ...enterStyle, opacity: 0, transform: 'scale(0.95)' },
          entered: { ...enterStyle, opacity: 1, transform: 'scale(1)' },
          exiting: { ...exitStyle, opacity: 0, transform: 'scale(0.95)' },
          exited: { ...exitStyle, opacity: 0, transform: 'scale(0.95)' },
        };
        
      case 'none':
        return {
          entering: {},
          entered: {},
          exiting: {},
          exited: {},
        };
        
      default:
        return {
          entering: { ...enterStyle, opacity: 0 },
          entered: { ...enterStyle, opacity: 1 },
          exiting: { ...exitStyle, opacity: 0 },
          exited: { ...exitStyle, opacity: 0 },
        };
    }
  };
  
  const defaultStateStyles = getDefaultStateStyles();
  const currentStateStyle = {
    ...defaultStateStyles[animationState],
    ...stateStyles[animationState]
  };
  
  // Get class name based on current state
  const stateClassName = stateClasses[animationState] || '';
  
  return (
    <div
      className={`animated-transition ${stateClassName} ${className}`}
      style={{
        ...style,
        ...currentStateStyle
      }}
    >
      {children}
    </div>
  );
};

export default AnimatedTransition; 