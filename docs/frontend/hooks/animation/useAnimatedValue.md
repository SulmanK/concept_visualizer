# useAnimatedValue Hook

The `useAnimatedValue` hook provides a way to animate numerical values over time, useful for creating smooth transitions for numbers, sizes, positions, and other numeric properties.

## Overview

This hook helps create smooth transitions between different numeric values, enabling fluid animations for counters, progress indicators, and other components that display changing numbers or measurements.

## Usage

```tsx
import { useAnimatedValue } from 'hooks/animation/useAnimatedValue';

function Counter({ value }) {
  const animatedValue = useAnimatedValue(value);
  
  return <div>{Math.round(animatedValue)}</div>;
}
```

## API

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `targetValue` | `number` | Yes | - | The target value to animate to |
| `options` | `AnimatedValueOptions` | No | See below | Configuration options for the animation |

### Options

```tsx
interface AnimatedValueOptions {
  duration?: number;      // Duration of animation in ms
  easing?: (t: number) => number;  // Easing function
  immediate?: boolean;    // Skip animation and set value immediately
  precision?: number;     // Number of decimal places to round to
}
```

Default options:

```tsx
{
  duration: 300,
  easing: t => t,  // Linear easing
  immediate: false,
  precision: 2
}
```

### Return Value

The hook returns a single value:

| Type | Description |
|------|-------------|
| `number` | The current animated value |

## Example: Animated Progress Bar

```tsx
import { useAnimatedValue } from 'hooks/animation/useAnimatedValue';

function ProgressBar({ percent }) {
  const animatedPercent = useAnimatedValue(percent, {
    duration: 500,
    easing: t => t * t,  // Quadratic easing
  });
  
  return (
    <div className="progress-container">
      <div 
        className="progress-bar"
        style={{ width: `${animatedPercent}%` }}
      />
      <div className="progress-text">
        {Math.round(animatedPercent)}%
      </div>
    </div>
  );
}
```

## Example: Animated Counter with Formatting

```tsx
import { useAnimatedValue } from 'hooks/animation/useAnimatedValue';

function AnimatedCounter({ value, prefix = '', suffix = '' }) {
  const animatedValue = useAnimatedValue(value, {
    duration: 800,
    precision: 0
  });
  
  return (
    <span className="counter">
      {prefix}{Math.round(animatedValue)}{suffix}
    </span>
  );
}

// Usage
<AnimatedCounter value={1250} prefix="$" />  // Shows "$1250"
```

## Implementation Details

The hook uses:

1. `useState` to track the current animated value
2. `useRef` to store the previous value and animation frame ID
3. `useEffect` to start and manage animations when the target value changes

The animation works by:
- Calculating the difference between the previous and target values
- Using `requestAnimationFrame` to perform the animation
- Applying the provided easing function to create natural motion
- Cleaning up any in-progress animations when the component unmounts

## Accessibility

For users who prefer reduced motion, this hook should be used in conjunction with the `usePrefersReducedMotion` hook to disable animations when appropriate:

```tsx
import { useAnimatedValue } from 'hooks/animation/useAnimatedValue';
import { usePrefersReducedMotion } from 'hooks/animation/usePrefersReducedMotion';

function AccessibleCounter({ value }) {
  const prefersReducedMotion = usePrefersReducedMotion();
  const animatedValue = useAnimatedValue(value, {
    immediate: prefersReducedMotion
  });
  
  return <div>{Math.round(animatedValue)}</div>;
}
```

## Related Hooks

- [useAnimatedMount](./useAnimatedMount.md)
- [usePrefersReducedMotion](./usePrefersReducedMotion.md) 