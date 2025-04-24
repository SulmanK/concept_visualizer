# useAnimatedMount Hook

The `useAnimatedMount` hook provides a way to smoothly animate components when they mount and unmount from the DOM.

## Overview

This hook helps create smooth transitions for components entering and exiting the UI. It's particularly useful for modals, tooltips, notifications, and other components that appear and disappear dynamically.

## Usage

```tsx
import { useAnimatedMount } from "hooks/animation/useAnimatedMount";

function MyAnimatedComponent({ isVisible }) {
  const { shouldRender, animationClass } = useAnimatedMount(isVisible);

  if (!shouldRender) {
    return null;
  }

  return (
    <div className={`my-component ${animationClass}`}>
      Content that will animate in and out
    </div>
  );
}
```

## API

### Parameters

| Parameter   | Type                   | Required | Default   | Description                             |
| ----------- | ---------------------- | -------- | --------- | --------------------------------------- |
| `isVisible` | `boolean`              | Yes      | -         | Whether the component should be visible |
| `options`   | `AnimatedMountOptions` | No       | See below | Configuration options for the animation |

### Options

```tsx
interface AnimatedMountOptions {
  enterDuration?: number; // Duration of enter animation in ms
  exitDuration?: number; // Duration of exit animation in ms
  enterClass?: string; // CSS class for enter animation
  exitClass?: string; // CSS class for exit animation
  baseClass?: string; // Base CSS class always applied
  enteringClass?: string; // CSS class during enter animation
  exitingClass?: string; // CSS class during exit animation
}
```

Default options:

```tsx
{
  enterDuration: 300,
  exitDuration: 300,
  enterClass: 'enter',
  exitClass: 'exit',
  baseClass: 'animated',
  enteringClass: 'entering',
  exitingClass: 'exiting'
}
```

### Return Values

| Value            | Type                                               | Description                                                            |
| ---------------- | -------------------------------------------------- | ---------------------------------------------------------------------- |
| `shouldRender`   | `boolean`                                          | Whether the component should be rendered at all (handles DOM presence) |
| `animationClass` | `string`                                           | The current animation CSS class to apply to the component              |
| `stage`          | `'entering' \| 'entered' \| 'exiting' \| 'exited'` | The current animation stage                                            |

## Example with CSS

```tsx
// Component
import { useAnimatedMount } from 'hooks/animation/useAnimatedMount';

function FadeInCard({ isVisible, children }) {
  const { shouldRender, animationClass } = useAnimatedMount(isVisible, {
    baseClass: 'fade-card',
    enterClass: 'fade-in',
    exitClass: 'fade-out',
  });

  if (!shouldRender) {
    return null;
  }

  return (
    <div className={animationClass}>
      {children}
    </div>
  );
}

// CSS
.fade-card {
  opacity: 0;
  transition: opacity 300ms ease-in-out;
}

.fade-card.fade-in {
  opacity: 1;
}

.fade-card.fade-out {
  opacity: 0;
}
```

## Implementation Details

The hook uses React's `useEffect` to track when the component should start or stop rendering based on the `isVisible` prop. The general flow is:

1. When `isVisible` changes to `true`:

   - Sets `shouldRender` to `true`
   - Applies entering animation classes
   - After enter duration, updates to entered state

2. When `isVisible` changes to `false`:
   - Applies exiting animation classes
   - After exit duration, sets `shouldRender` to `false`
   - Component is removed from the DOM

This approach ensures that animations have time to complete before components are actually removed from the DOM.

## Related Hooks

- [useAnimatedValue](./useAnimatedValue.md)
- [usePrefersReducedMotion](./usePrefersReducedMotion.md)
