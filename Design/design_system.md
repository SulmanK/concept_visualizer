# Concept Visualizer Design System

This document outlines the design system for the Concept Visualizer application, providing guidelines for consistent implementation across the application.

## 🎨 Colors

### Primary Color Palette

| Color Name | Hex Code | Usage |
|------------|----------|-------|
| Primary | `#8B5CF6` | Main brand color, buttons, active states |
| Primary Dark | `#7C3AED` | Hover states, gradient ends |
| Secondary | `#C084FC` | Accents, alternative actions |
| Secondary Dark | `#A855F7` | Secondary hover states |
| Accent | `#F5F3FF` | Backgrounds, subtle highlights |

### Neutral Colors

| Color Name | Tailwind Class | Usage |
|------------|----------------|-------|
| White | `white` | Card backgrounds, text on dark backgrounds |
| Gray 50 | `gray-50` | Page backgrounds |
| Gray 100-200 | `gray-100` to `gray-200` | Subtle borders, dividers |
| Gray 400-500 | `gray-400` to `gray-500` | Placeholders, disabled states |
| Gray 700-800 | `gray-700` to `gray-800` | Secondary text |
| Gray 900 | `gray-900` | Primary text |

### Semantic Colors

| Color Name | Tailwind Class | Usage |
|------------|----------------|-------|
| Success | `green-500` | Success messages, confirmations |
| Warning | `amber-500` | Warnings, cautionary actions |
| Error | `red-500` | Error states, destructive actions |
| Info | `blue-500` | Informational elements |

## 🔤 Typography

### Font Family

The primary font is **Montserrat**, with fallbacks to system fonts:

```css
font-family: 'Montserrat', system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
```

### Font Sizes

| Element | Size | Weight | Class |
|---------|------|--------|-------|
| H1 | 2.25rem (36px) | Bold (700) | `text-4xl font-bold` |
| H2 | 1.875rem (30px) | Bold (700) | `text-3xl font-bold` |
| H3 | 1.5rem (24px) | Semibold (600) | `text-2xl font-semibold` |
| H4 | 1.25rem (20px) | Semibold (600) | `text-xl font-semibold` |
| Body | 1rem (16px) | Regular (400) | `text-base` |
| Small | 0.875rem (14px) | Regular (400) | `text-sm` |
| Extra Small | 0.75rem (12px) | Regular (400) | `text-xs` |

## 🧩 Components

### Buttons

#### Button Variants

| Variant | Description | Classes |
|---------|-------------|---------|
| Primary | Main call to action | `bg-gradient-to-r from-primary to-primary-dark text-white shadow-modern hover:shadow-modern-hover` |
| Secondary | Alternative actions | `bg-gradient-to-r from-secondary to-secondary-dark text-white shadow-modern hover:shadow-modern-hover` |
| Outline | Less prominent actions | `border-2 border-primary/50 bg-white/80 hover:bg-white text-primary shadow-sm hover:shadow-modern` |
| Ghost | Subtle actions | `hover:bg-violet-50 text-violet-700 hover:text-primary` |

#### Button Sizes

| Size | Description | Classes |
|------|-------------|---------|
| Small | Compact buttons | `h-9 px-4 text-sm` |
| Medium | Default size | `h-12 px-6 py-2` |
| Large | Prominent buttons | `h-14 px-8 text-lg` |

#### Button States

| State | Description | Classes |
|-------|-------------|---------|
| Default | Normal state | *(base classes)* |
| Hover | Mouse over | `hover:shadow-modern-hover` |
| Focus | Keyboard focus | `focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2` |
| Disabled | Inactive | `opacity-40 pointer-events-none` |
| Loading | Processing action | Include spinner element |

### Cards

```html
<div class="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-violet-100 overflow-hidden">
  <!-- Card content -->
</div>
```

### Inputs

```html
<div>
  <label for="input-id" class="block text-sm font-medium text-gray-700 mb-2">
    Label
  </label>
  <input 
    type="text" 
    id="input-id" 
    class="w-full px-4 py-2 rounded-lg border border-gray-300 focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all duration-200"
    placeholder="Placeholder text"
  />
  <p class="mt-1 text-sm text-gray-500">Helper text goes here</p>
</div>
```

### Navigation

```html
<nav class="flex space-x-4">
  <a href="#" class="px-4 py-2 rounded-lg text-sm font-semibold bg-gradient-to-r from-primary to-primary-dark text-white shadow-modern">
    Active Link
  </a>
  <a href="#" class="px-4 py-2 rounded-lg text-sm font-semibold text-violet-700 hover:bg-violet-50 hover:text-primary-dark transition-colors">
    Inactive Link
  </a>
</nav>
```

## 🎭 Effects & Animation

### Shadows

| Shadow | Classes | Usage |
|--------|---------|-------|
| Modern | `shadow-modern` | Cards, buttons, interactive elements |
| Modern Hover | `shadow-modern-hover` | Hover states for interactive elements |

### Gradients

| Gradient | Classes | Usage |
|----------|---------|-------|
| Primary Gradient | `bg-gradient-to-r from-primary to-primary-dark` | Primary buttons, prominent UI elements |
| Secondary Gradient | `bg-gradient-to-r from-secondary to-secondary-dark` | Secondary buttons, accents |
| Page Gradient | `bg-gradient-to-br from-violet-50 to-indigo-100` | Page backgrounds |

### Transitions

All interactive elements should have smooth transitions:

```css
transition-all duration-200
```

## 📱 Responsive Design

The application follows a mobile-first approach with these breakpoints:

| Breakpoint | Screen Width | Tailwind Prefix |
|------------|--------------|----------------|
| Mobile | Default | (none) |
| Small | 640px | `sm:` |
| Medium | 768px | `md:` |
| Large | 1024px | `lg:` |
| Extra Large | 1280px | `xl:` |
| 2X Large | 1536px | `2xl:` |

## 🧪 Theme Variations

The design system supports multiple theme variations:

1. **Modern Gradient Violet** (Default) - Purple/violet theme
2. **Modern Gradient Indigo** - Blue/indigo theme
3. **Dark Mode Pro** - Dark theme with violet accents
4. **Modern Gradient Teal** - Teal/cyan theme
5. **Modern Gradient Sunset** - Orange/purple theme

Implementation of theme variations can be achieved through:

1. CSS custom properties (variables)
2. Tailwind CSS theme configuration
3. Theme switcher component

## ♿ Accessibility

- Ensure color contrast meets WCAG AA standards (4.5:1 for normal text)
- Use semantic HTML elements
- Include proper ARIA attributes where necessary
- Ensure keyboard navigation works for all interactive elements
- Support reduced motion preferences

## 🛠️ Implementation

1. Use the Tailwind CSS configuration to set up the color palette and typography
2. Create reusable component classes with `@apply` directives
3. Implement responsive layouts using Tailwind's responsive prefixes
4. Use the example code in this document as a reference for component implementation

## 📚 Resources

- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Design Mockups](/Design/theme_variations/)
- [Component Examples](/Design/component_mockups/)
- [Design Concepts](/Design/design_concepts.md) 