import { useState, useEffect, useRef } from "react";
import usePrefersReducedMotion from "./usePrefersReducedMotion";

export interface AnimatedValueOptions {
  /**
   * Duration of the animation in ms
   * @default 300
   */
  duration?: number;

  /**
   * Easing function for the animation
   * @default 'easeOutCubic'
   */
  easing?: "linear" | "easeInCubic" | "easeOutCubic" | "easeInOutCubic";

  /**
   * Delay before starting animation in ms
   * @default 0
   */
  delay?: number;

  /**
   * Callback when animation completes
   */
  onComplete?: () => void;
}

// Easing functions
const easingFunctions = {
  linear: (t: number) => t,
  easeInCubic: (t: number) => t * t * t,
  easeOutCubic: (t: number) => 1 - Math.pow(1 - t, 3),
  easeInOutCubic: (t: number) =>
    t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2,
};

/**
 * Hook that animates a value from start to end
 *
 * @param startValue - Starting value
 * @param endValue - Ending value
 * @param isActive - Whether the animation should be active
 * @param options - Animation options
 * @returns The current animated value
 */
export const useAnimatedValue = (
  startValue: number,
  endValue: number,
  isActive: boolean = true,
  options: AnimatedValueOptions = {},
): number => {
  const {
    duration = 300,
    easing = "easeOutCubic",
    delay = 0,
    onComplete,
  } = options;

  const [value, setValue] = useState<number>(startValue);
  const animationRef = useRef<number | null>(null);
  const startTimeRef = useRef<number | null>(null);
  const valueRangeRef = useRef<{ start: number; end: number }>({
    start: startValue,
    end: endValue,
  });
  const prefersReducedMotion = usePrefersReducedMotion();

  // Skip animation if user prefers reduced motion
  if (prefersReducedMotion && value !== endValue) {
    setValue(endValue);
  }

  useEffect(() => {
    // If animation is not active or user prefers reduced motion, set value to end immediately
    if (!isActive || prefersReducedMotion) {
      setValue(endValue);
      return;
    }

    // Store the range for this animation
    valueRangeRef.current = { start: value, end: endValue };

    // If the values are the same, no need to animate
    if (value === endValue) {
      return;
    }

    let delayTimeout: NodeJS.Timeout | null = null;

    const startAnimation = () => {
      // Clean up existing animation
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
      }

      const easingFunction = easingFunctions[easing];

      const animateValue = (timestamp: number) => {
        // Set the start time on first run
        if (startTimeRef.current === null) {
          startTimeRef.current = timestamp;
        }

        // Calculate elapsed time
        const elapsed = timestamp - startTimeRef.current;

        // Calculate progress (0 to 1)
        const progress = Math.min(elapsed / duration, 1);

        // Apply easing function
        const easedProgress = easingFunction(progress);

        // Calculate current value
        const currentValue =
          valueRangeRef.current.start +
          (valueRangeRef.current.end - valueRangeRef.current.start) *
            easedProgress;

        // Update state with current value
        setValue(currentValue);

        // Continue animation if not complete
        if (progress < 1) {
          animationRef.current = requestAnimationFrame(animateValue);
        } else {
          // Animation complete
          setValue(valueRangeRef.current.end);
          startTimeRef.current = null;
          animationRef.current = null;

          if (onComplete) {
            onComplete();
          }
        }
      };

      // Start the animation loop
      animationRef.current = requestAnimationFrame(animateValue);
    };

    // Apply delay if specified
    if (delay > 0) {
      delayTimeout = setTimeout(startAnimation, delay);
    } else {
      startAnimation();
    }

    // Clean up animation on unmount or when dependencies change
    return () => {
      if (animationRef.current !== null) {
        cancelAnimationFrame(animationRef.current);
        animationRef.current = null;
      }

      if (delayTimeout !== null) {
        clearTimeout(delayTimeout);
      }
    };
  }, [
    endValue,
    isActive,
    duration,
    easing,
    delay,
    onComplete,
    prefersReducedMotion,
    value,
  ]);

  return value;
};

export default useAnimatedValue;
