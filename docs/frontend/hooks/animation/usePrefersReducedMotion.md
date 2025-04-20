# usePrefersReducedMotion Hook

The `usePrefersReducedMotion` hook detects if the user has indicated a preference for reduced motion in their operating system or browser settings.

## Overview

This accessibility-focused hook helps create more inclusive user experiences by respecting the user's motion preferences. It allows developers to provide alternative animations or disable animations completely for users who may experience discomfort or health issues from motion effects.

## Usage

```tsx
import { usePrefersReducedMotion } from 'hooks/animation/usePrefersReducedMotion';

function AnimatedComponent() {
  const prefersReducedMotion = usePrefersReducedMotion();
  
  const animationStyle = prefersReducedMotion
    ? {} // No animation
    : { transition: 'transform 0.3s ease', transform: 'scale(1.1)' };
  
  return (
    <div 
      className="animated-element"
      style={animationStyle}
    >
      Content
    </div>
  );
}
```

## API

### Parameters

This hook doesn't accept any parameters.

### Return Value

| Type | Description |
|------|-------------|
| `boolean` | `true` if the user prefers reduced motion, `false` otherwise |

## Example: Conditional Animation Component

```tsx
import { usePrefersReducedMotion } from 'hooks/animation/usePrefersReducedMotion';

function FadeIn({ children }) {
  const prefersReducedMotion = usePrefersReducedMotion();
  
  const className = prefersReducedMotion
    ? 'content'
    : 'content fade-in-animation';
  
  return <div className={className}>{children}</div>;
}
```

## Example: With CSS Variables

```tsx
import { usePrefersReducedMotion } from 'hooks/animation/usePrefersReducedMotion';

function AnimationRoot() {
  const prefersReducedMotion = usePrefersReducedMotion();
  
  // Set CSS variables based on motion preference
  const cssVariables = {
    '--transition-duration': prefersReducedMotion ? '0s' : '0.3s',
    '--animation-distance': prefersReducedMotion ? '0px' : '20px',
  };
  
  return (
    <div style={cssVariables} className="app-root">
      {/* Child components can use these CSS variables */}
    </div>
  );
}
```

## Implementation Details

The hook uses:

1. `window.matchMedia` to check the `prefers-reduced-motion` CSS media query
2. An event listener to detect changes to the user's preference
3. `useState` to store and update the current preference

If the browser doesn't support the `prefers-reduced-motion` media query, the hook defaults to `false` (assuming animations are acceptable).

## Best Practices

- Use this hook to conditionally apply animations based on user preference
- Provide static alternatives that communicate the same information
- Never completely remove important functionality or information
- Consider using subtle transitions even for reduced motion (opacity changes are often acceptable)

## Browser Support

The `prefers-reduced-motion` media query is supported in:
- Chrome 74+
- Firefox 63+
- Safari 10.1+
- Edge 79+

For browsers that don't support this feature, the hook defaults to allowing animations.

## Related Hooks

- [useAnimatedMount](./useAnimatedMount.md)
- [useAnimatedValue](./useAnimatedValue.md) 