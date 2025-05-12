# Card Component

The `Card` component is a flexible container that displays content with a consistent style, providing a clean and organized visual representation of information.

## Overview

The Card component is a custom Tailwind CSS-based container with modern styling, including backdrop blur, shadows, and hover effects. It provides multiple variants and interactive states to enhance the user experience.

## Usage

```tsx
import { Card } from 'components/ui/Card';

// Basic usage
<Card>
  <h3>Card Title</h3>
  <p>Card content goes here</p>
</Card>

// With header and footer
<Card
  header={<h3 className="font-medium">Card Header</h3>}
  footer={<p className="text-sm text-gray-500">Last updated: 2 days ago</p>}
>
  <p>Card content with header and footer</p>
</Card>

// Gradient variant with hover effect
<Card
  variant="gradient"
  interactive={true}
  hoverEffect="glow"
>
  <h3>Gradient Card</h3>
  <p>Hover over me!</p>
</Card>
```

## Props

| Prop          | Type                                                | Default     | Description                           |
| ------------- | --------------------------------------------------- | ----------- | ------------------------------------- |
| `children`    | `React.ReactNode`                                   | -           | Content to render inside the card     |
| `variant`     | `'default' \| 'gradient' \| 'elevated'`             | `'default'` | Card styling variant                  |
| `header`      | `React.ReactNode`                                   | -           | Optional header content               |
| `footer`      | `React.ReactNode`                                   | -           | Optional footer content               |
| `padded`      | `boolean`                                           | `true`      | Whether to add padding to the content |
| `isLoading`   | `boolean`                                           | `false`     | Shows a loading spinner when true     |
| `interactive` | `boolean`                                           | `true`      | Whether card should be interactive    |
| `hoverEffect` | `'lift' \| 'glow' \| 'border' \| 'scale' \| 'none'` | `'lift'`    | Type of hover animation               |
| `className`   | `string`                                            | `''`        | Additional CSS class to apply         |

## Implementation Details

```tsx
import React, { HTMLAttributes } from "react";
import { usePrefersReducedMotion } from "../../hooks";

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  /**
   * Card variant
   */
  variant?: "default" | "gradient" | "elevated";

  /**
   * Header content
   */
  header?: React.ReactNode;

  /**
   * Footer content
   */
  footer?: React.ReactNode;

  /**
   * Add extra padding to the card
   */
  padded?: boolean;

  /**
   * Card is in loading state
   */
  isLoading?: boolean;

  /**
   * Whether the card should have hover effects
   * @default false
   */
  interactive?: boolean;

  /**
   * Type of hover animation
   * @default 'lift'
   */
  hoverEffect?: "lift" | "glow" | "border" | "scale" | "none";
}

/**
 * Card component for containing content
 */
export const Card: React.FC<CardProps> = ({
  variant = "default",
  header,
  footer,
  padded = true,
  isLoading = false,
  interactive = true,
  hoverEffect = "lift",
  className = "",
  children,
  ...props
}) => {
  const prefersReducedMotion = usePrefersReducedMotion();

  // Base card styles for each variant
  const baseClasses = {
    default:
      "bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 overflow-hidden",
    gradient:
      "bg-gradient-to-br from-indigo-50/90 to-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 overflow-hidden",
    elevated: "bg-white border-none rounded-lg shadow-lg overflow-hidden",
  };

  // Transition classes (skip if reduced motion is preferred)
  const transitionClass = !prefersReducedMotion
    ? "transition-all duration-300"
    : "";

  // Classes for different hover effects when card is interactive
  const getHoverClasses = () => {
    if (!interactive || prefersReducedMotion) return "";

    switch (hoverEffect) {
      case "lift":
        return "hover:translate-y-[-4px] hover:shadow-lg";
      case "glow":
        return "hover:shadow-[0_0_15px_rgba(79,70,229,0.3)]";
      case "border":
        return "hover:border-indigo-300";
      case "scale":
        return "hover:scale-[1.02]";
      case "none":
        return "";
      default:
        return "";
    }
  };

  // Combine all card classes
  const cardClass = `${
    baseClasses[variant]
  } ${transitionClass} ${getHoverClasses()} ${className}`.trim();

  // Content, header and footer classes
  const contentClass = padded ? "p-4 sm:p-6" : "";
  const headerClass =
    "px-4 py-3 sm:px-6 border-b border-indigo-200 bg-indigo-50/50";
  const footerClass =
    "px-4 py-3 sm:px-6 border-t border-indigo-200 bg-indigo-50/50";

  return (
    <div className={cardClass} {...props}>
      {header && <div className={headerClass}>{header}</div>}

      <div className={contentClass}>
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
          </div>
        ) : (
          children
        )}
      </div>

      {footer && <div className={footerClass}>{footer}</div>}
    </div>
  );
};
```

## Features

- **Tailwind CSS**: Built using Tailwind utility classes for modern styling
- **Backdrop Blur**: Subtle blur effect in the background for depth
- **Multiple Variants**: Default, gradient, and elevated styles
- **Interactive States**: Optional hover effects for better user interaction
- **Header & Footer**: Optional dedicated sections for structured content
- **Loading State**: Built-in loading spinner
- **Motion Sensitivity**: Respects user preferences for reduced motion
- **Responsive Design**: Adapts padding based on screen size
- **Modern Shadows**: Custom shadow styling for depth

## Usage Patterns

### Basic Content Card

```tsx
<Card>
  <h2 className="text-xl font-medium mb-2">Card Title</h2>
  <p className="text-gray-600">
    This is a simple content card with default styling.
  </p>
</Card>
```

### Card with Header and Footer

```tsx
<Card
  header={
    <div className="flex justify-between items-center">
      <h3 className="font-medium">Statistics</h3>
      <button className="text-sm text-indigo-600">View All</button>
    </div>
  }
  footer={
    <div className="text-sm text-gray-500 text-right">
      Updated: {new Date().toLocaleDateString()}
    </div>
  }
>
  <div className="py-2">
    <p className="text-2xl font-bold">2,540</p>
    <p className="text-sm text-gray-500">Total users</p>
  </div>
</Card>
```

### Gradient Card with Hover Effect

```tsx
<Card variant="gradient" hoverEffect="glow" onClick={() => handleCardClick()}>
  <div className="text-center py-4">
    <h3 className="text-xl font-medium mb-2">Premium Plan</h3>
    <p className="text-3xl font-bold mb-2">$49/mo</p>
    <p className="text-sm text-gray-600 mb-4">All features, unlimited access</p>
    <button className="bg-indigo-600 text-white px-4 py-2 rounded-lg">
      Upgrade Now
    </button>
  </div>
</Card>
```

### Loading State

```tsx
<Card isLoading={isLoadingData}>
  {data && (
    <div>
      <h3>{data.title}</h3>
      <p>{data.description}</p>
    </div>
  )}
</Card>
```

### Non-Interactive Card

```tsx
<Card interactive={false}>
  <div className="bg-gray-50 p-3 rounded">
    <p className="text-sm text-gray-500">
      This card has no hover effects or interactions.
    </p>
  </div>
</Card>
```

## Best Practices

1. Use appropriate variants based on the card's purpose and importance
2. Keep card content concise and focused on a single topic or action
3. Use the header for titles, actions, or navigation controls
4. Use the footer for metadata, timestamps, or supplementary actions
5. Apply interactive effects only to cards that are clickable or perform actions
6. For cards with dense content, consider setting `padded={false}` and applying custom padding
7. Group related cards with consistent styling and spacing
8. Use the loading state for cards that fetch remote data
