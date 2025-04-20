# Styles

This directory contains global styles, variables, animations, and theme configurations for the Concept Visualizer application.

## Directory Structure

The styles are organized into the following files:

- **Global styles**: Application-wide styles and CSS resets
- **Variables**: SCSS variables for colors, spacing, fonts, etc.
- **Animations**: Reusable animations and transitions
- **Theme**: Theme configuration for styled components or MUI

## Key Features

- **Responsive Design**: Mobile-first approach with breakpoints for different screen sizes
- **Consistent Colors**: Predefined color palette for brand consistency
- **Typography System**: Standardized font sizes, weights, and line heights
- **Spacing System**: Consistent spacing variables for margins and padding
- **Animation Library**: Reusable animations for interactive elements

## Usage

### Importing Styles

```typescript
// Global styles are imported in the main App component
import './styles/global.scss';

// For specific component styles
import './styles/components/Button.scss';
```

### Theme Variables

The application uses CSS variables for theming, allowing for easy dark/light mode switching and consistent styling across components:

```css
:root {
  --primary-color: #3a86ff;
  --secondary-color: #ff006e;
  --background-color: #ffffff;
  --text-color: #333333;
  
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  --font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 24px;
}

/* Dark mode theme */
@media (prefers-color-scheme: dark) {
  :root {
    --background-color: #121212;
    --text-color: #f5f5f5;
  }
}
```

### Animations

The application includes several reusable animations:

```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fade-in {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes slideIn {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.slide-in {
  animation: slideIn 0.4s ease-out;
}
```

## Best Practices

1. **Use Variables**: Always use the predefined variables for colors, spacing, and typography
2. **Mobile-First**: Start with mobile styles and use media queries for larger screens
3. **Component Encapsulation**: Keep component styles scoped to prevent leakage
4. **Consistent Naming**: Follow BEM (Block Element Modifier) naming convention
5. **Performance**: Minimize nested selectors and avoid expensive CSS properties 