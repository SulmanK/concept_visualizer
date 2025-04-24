import { useState, useEffect, useRef } from "react";
import usePrefersReducedMotion from "./usePrefersReducedMotion";

export type AnimationState = "entering" | "entered" | "exiting" | "exited";

export interface AnimatedMountOptions {
  /**
   * Initial mount state
   * @default 'exited'
   */
  initialState?: AnimationState;

  /**
   * Duration of the enter animation in ms
   * @default 300
   */
  enterDuration?: number;

  /**
   * Duration of the exit animation in ms
   * @default 300
   */
  exitDuration?: number;

  /**
   * Whether the component should be mounted initially
   * @default false
   */
  initialMount?: boolean;

  /**
   * Callback when the entering animation starts
   */
  onEntering?: () => void;

  /**
   * Callback when the entering animation completes
   */
  onEntered?: () => void;

  /**
   * Callback when the exiting animation starts
   */
  onExiting?: () => void;

  /**
   * Callback when the exiting animation completes
   */
  onExited?: () => void;
}

/**
 * Hook for animating component mounting and unmounting
 *
 * @param isVisible - Whether the component should be visible
 * @param options - Animation options
 * @returns Object containing animationState, isMounted, and ref to attach to the animated element
 */
export const useAnimatedMount = (
  isVisible: boolean,
  options: AnimatedMountOptions = {},
) => {
  const {
    initialState = "exited",
    enterDuration = 300,
    exitDuration = 300,
    initialMount = false,
    onEntering,
    onEntered,
    onExiting,
    onExited,
  } = options;

  const prefersReducedMotion = usePrefersReducedMotion();
  const [animationState, setAnimationState] = useState<AnimationState>(
    initialMount ? "entered" : initialState,
  );
  const [isMounted, setIsMounted] = useState<boolean>(
    initialMount || isVisible,
  );
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Clear any existing timeouts on unmount
  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  useEffect(() => {
    // If user prefers reduced motion, skip animations
    if (prefersReducedMotion) {
      setIsMounted(isVisible);
      setAnimationState(isVisible ? "entered" : "exited");
      return;
    }

    if (isVisible) {
      // Component should become visible
      setIsMounted(true);

      // Clear any exit timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      // Start enter animation
      setAnimationState("entering");
      if (onEntering) onEntering();

      // Schedule entered state
      timeoutRef.current = setTimeout(() => {
        setAnimationState("entered");
        if (onEntered) onEntered();
        timeoutRef.current = null;
      }, enterDuration);
    } else if (isMounted) {
      // Component is mounted but should hide

      // Clear any enter timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }

      // Start exit animation
      setAnimationState("exiting");
      if (onExiting) onExiting();

      // Schedule unmounting
      timeoutRef.current = setTimeout(() => {
        setAnimationState("exited");
        setIsMounted(false);
        if (onExited) onExited();
        timeoutRef.current = null;
      }, exitDuration);
    }
  }, [
    isVisible,
    isMounted,
    enterDuration,
    exitDuration,
    prefersReducedMotion,
    onEntering,
    onEntered,
    onExiting,
    onExited,
  ]);

  return {
    animationState,
    isMounted,
  };
};

export default useAnimatedMount;
