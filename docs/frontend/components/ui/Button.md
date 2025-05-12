# Button Component

The `Button` component provides a standardized button element for user interactions throughout the application.

## Overview

This component is a custom Tailwind CSS-based button with consistent styling, variants, and accessibility features. It simplifies implementing buttons with a consistent look and feel across the application, including hover animations and reduced motion support.

## Usage

```tsx
import { Button } from 'components/ui/Button';

// Basic usage
<Button onClick={handleClick}>
  Click Me
</Button>

// Primary variant
<Button variant="primary" onClick={handleClick}>
  Primary Action
</Button>

// Secondary variant
<Button variant="secondary" onClick={handleCancel}>
  Secondary Action
</Button>

// Outline variant
<Button variant="outline" onClick={handleCancel}>
  Outlined Button
</Button>

// Pill-shaped button (fully rounded)
<Button pill onClick={handleAction}>
  Pill Button
</Button>
```

## Props

| Prop        | Type                                               | Default     | Description                           |
| ----------- | -------------------------------------------------- | ----------- | ------------------------------------- |
| `children`  | `React.ReactNode`                                  | -           | Button content                        |
| `variant`   | `'primary' \| 'secondary' \| 'outline' \| 'ghost'` | `'primary'` | Button style variant                  |
| `size`      | `'sm' \| 'md' \| 'lg'`                             | `'md'`      | Button size                           |
| `pill`      | `boolean`                                          | `false`     | Whether to use fully rounded corners  |
| `animated`  | `boolean`                                          | `true`      | Whether to use hover/press animations |
| `className` | `string`                                           | `''`        | Additional CSS class to apply         |
| `type`      | `'button' \| 'submit' \| 'reset'`                  | `'button'`  | HTML button type                      |
| `disabled`  | `boolean`                                          | `false`     | Whether button is disabled            |
| `onClick`   | `(e: React.MouseEvent<HTMLButtonElement>) => void` | -           | Click handler                         |

## Implementation Details

```tsx
import React, { useState } from "react";
import { usePrefersReducedMotion } from "../../hooks";

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button variant
   */
  variant?: "primary" | "secondary" | "outline" | "ghost";

  /**
   * Button size
   */
  size?: "sm" | "md" | "lg";

  /**
   * Whether to use a pill shape (fully rounded)
   */
  pill?: boolean;

  /**
   * Button type attribute
   */
  type?: "button" | "submit" | "reset";

  /**
   * Additional class names
   */
  className?: string;

  /**
   * Button children
   */
  children: React.ReactNode;

  /**
   * Whether to add subtle hover animation
   * @default true
   */
  animated?: boolean;
}

/**
 * Button component with different variants and sizes
 */
export const Button: React.FC<ButtonProps> = ({
  variant = "primary",
  size = "md",
  pill = false,
  type = "button",
  className = "",
  children,
  animated = true,
  onClick,
  ...props
}) => {
  const [isPressed, setIsPressed] = useState(false);
  const prefersReducedMotion = usePrefersReducedMotion();

  // Base classes for all buttons
  const baseClasses =
    "inline-flex items-center justify-center font-medium focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-2 disabled:opacity-60 disabled:cursor-not-allowed";

  // Transition classes (skip if reduced motion is preferred)
  const transitionClasses = prefersReducedMotion
    ? ""
    : "transition-all duration-200";

  // Define variant-specific classes
  const variantClasses = {
    primary:
      "bg-gradient-to-r from-primary to-primary-dark text-white shadow-modern hover:shadow-modern-hover hover:brightness-105",
    secondary:
      "bg-gradient-to-r from-secondary to-secondary-dark text-white shadow-modern hover:shadow-modern-hover hover:brightness-105",
    outline:
      "border border-indigo-300 text-indigo-700 bg-white hover:bg-indigo-50 hover:text-primary-dark",
    ghost: "text-indigo-600 hover:text-indigo-800 hover:bg-indigo-50",
  };

  // Size classes
  const sizeClasses = {
    sm: "text-xs px-2.5 py-1",
    md: "text-sm px-4 py-2",
    lg: "text-base px-6 py-3",
  };

  // Border radius based on pill prop
  const roundedClasses = pill ? "rounded-full" : "rounded-lg";

  // Animation classes for pressed state
  const animationClasses =
    animated && !prefersReducedMotion
      ? isPressed
        ? "transform scale-95"
        : "transform scale-100 hover:scale-[1.02]"
      : "";

  // Combine all classes
  const buttonClasses = `${baseClasses} ${transitionClasses} ${variantClasses[variant]} ${sizeClasses[size]} ${roundedClasses} ${animationClasses} ${className}`;

  // Handle click with animation
  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    if (animated && !prefersReducedMotion && !props.disabled) {
      setIsPressed(true);

      // Reset the pressed state after animation
      setTimeout(() => {
        setIsPressed(false);
      }, 150);
    }

    // Call the original onClick handler
    if (onClick) {
      onClick(e);
    }
  };

  return (
    <button
      type={type}
      className={buttonClasses}
      onClick={handleClick}
      {...props}
    >
      {children}
    </button>
  );
};
```

## Features

- **Tailwind CSS Styling**: Uses Tailwind utility classes for consistent styling
- **Multiple Variants**: Primary, secondary, outline, and ghost variants
- **Motion Sensitivity**: Respects user motion preferences
- **Animations**: Subtle scale animations on hover and click
- **Gradient Backgrounds**: Primary and secondary variants use gradient backgrounds
- **Size Options**: Small, medium, and large sizes
- **Shape Options**: Standard rounded or pill shape
- **Accessible**: Includes focus rings and respects disabled state
- **Modern Shadow**: Custom shadow effects for depth

## Usage Patterns

### Primary Action Button

```tsx
<Button variant="primary" onClick={handleSubmit} type="submit">
  Submit Form
</Button>
```

### Secondary Action Button

```tsx
<Button variant="secondary" onClick={handleCancel}>
  Cancel
</Button>
```

### Outline Button

```tsx
<Button variant="outline" onClick={handleReset}>
  Reset Form
</Button>
```

### Ghost Button

```tsx
<Button variant="ghost" onClick={handleSkip}>
  Skip this step
</Button>
```

### Pill-Shaped Button

```tsx
<Button variant="primary" pill onClick={handleAction}>
  Action Button
</Button>
```

### Different Sizes

```tsx
<>
  <Button variant="primary" size="sm">
    Small
  </Button>
  <Button variant="primary" size="md">
    Medium
  </Button>
  <Button variant="primary" size="lg">
    Large
  </Button>
</>
```

### Disabled Button

```tsx
<Button variant="primary" disabled>
  Can't Click Me
</Button>
```

## Best Practices

1. Use primary variant for the main action in a form or view
2. Use secondary variant for secondary actions
3. Use outline or ghost variants for less prominent actions
4. Consider using pill shape for action buttons that should stand out
5. Use appropriate button sizes based on importance and context
6. Keep button text concise and action-oriented
7. Ensure sufficient contrast between button color and text for accessibility
8. Group related buttons together with consistent styling
9. Leverage the className prop to add custom styles when needed
10. Set the animated prop to false for utility buttons that don't need animation
