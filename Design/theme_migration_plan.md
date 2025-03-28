# Modern Gradient Indigo Theme Migration Plan

This document outlines the specific steps to migrate the current Modern Gradient Violet theme to the desired Modern Gradient Indigo theme based on the `modern-gradient-indigo.html` design mockup.

## Color Palette Updates

### Tailwind Configuration

Update `tailwind.config.js` with the following color scheme:

```js
colors: {
  primary: '#4F46E5',
  'primary-dark': '#4338CA',
  secondary: '#818CF8',
  'secondary-dark': '#6366F1',
  accent: '#EEF2FF',
  'accent-foreground': '#312E81',
},
```

### Gradient Definitions

Add the following gradient definitions:

```js
backgroundImage: {
  'gradient-primary': 'linear-gradient(135deg, #4F46E5 0%, #4338CA 100%)',
  'gradient-secondary': 'linear-gradient(135deg, #818CF8 0%, #6366F1 100%)',
  'gradient-page': 'linear-gradient(135deg, #EEF2FF 0%, #C7D2FE 100%)',
},
```

### Shadow Definitions

Update shadow definitions to use the indigo color:

```js
boxShadow: {
  'modern': '0 10px 30px -5px rgba(79, 70, 229, 0.2)',
  'modern-hover': '0 20px 40px -5px rgba(79, 70, 229, 0.3)',
},
```

## Component Style Updates

### Button Component

Update the Button component's CSS classes:

```jsx
// Primary Button
className="inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 h-12 px-6 py-2 bg-gradient-primary text-white shadow-modern hover:shadow-modern-hover"

// Secondary Button
className="inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-secondary focus-visible:ring-offset-2 h-12 px-6 py-2 bg-gradient-secondary text-white shadow-modern hover:shadow-modern-hover"

// Outline Button
className="inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 h-12 px-6 py-2 border-2 border-primary/50 bg-white/80 hover:bg-white text-primary shadow-modern hover:shadow-modern-hover"

// Ghost Button
className="inline-flex items-center justify-center rounded-lg font-semibold transition-all duration-200 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary focus-visible:ring-offset-2 h-12 px-6 py-2 hover:bg-indigo-50 text-indigo-700 hover:text-primary"
```

### Card Component

Update the Card component styles:

```jsx
className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 overflow-hidden"
```

### Input Fields

Update input field styles:

```jsx
className="w-full px-4 py-3 rounded-lg border border-indigo-200 focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all duration-200"
```

### Loading Spinner

Update the spinner color:

```jsx
<svg className="h-5 w-5 animate-spin text-primary" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
</svg>
```

### Error Messages

Update error message styling:

```jsx
className="flex items-center p-4 rounded-lg text-sm bg-gradient-to-r from-red-50 to-indigo-50 text-red-600 border border-indigo-100 shadow-lg"
```

## Layout Updates

### Main Layout

Update the main app container:

```jsx
<div className="bg-gradient-to-br from-indigo-50 to-blue-100 min-h-screen font-sans text-gray-800">
  {/* Content */}
</div>
```

### Header

Update the header component:

```jsx
<header className="bg-white/80 backdrop-blur-sm shadow-sm border-b border-indigo-100">
  <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    {/* Header content */}
  </div>
</header>
```

### Typography Updates

Apply gradient text to headings:

```jsx
<h1 className="text-3xl font-bold mb-3 bg-gradient-to-r from-indigo-600 to-blue-500 bg-clip-text text-transparent">
  Concept Visualizer
</h1>
```

Update paragraph text colors:

```jsx
<p className="text-lg text-indigo-600">
  Describe your logo and theme to generate visual concepts.
</p>
```

## Implementation Steps

1. **Update Color Configuration**
   - Modify `tailwind.config.js` with the new color palette
   - Add extended theme properties for gradients and shadows

2. **Update Global Styles**
   - Modify the base CSS file to use the new background gradient
   - Update font definitions to ensure Montserrat is consistently applied

3. **Component Updates**
   - Update Button component variants
   - Update Card component styles
   - Update Input/Form Field components
   - Update LoadingSpinner component colors
   - Update ErrorMessage component styling

4. **Layout Updates**
   - Update MainLayout component background
   - Update Header component styling
   - Apply gradient text styling to headings
   - Update text colors throughout the application

5. **Testing and Verification**
   - Test all component variants in isolation
   - Verify responsive behavior on multiple screen sizes
   - Check for consistent styling across all pages
   - Ensure proper color contrast for accessibility

## CSS Custom Properties (Optional Enhancement)

For easier theme switching in future, consider implementing CSS custom properties:

```css
:root {
  --color-primary: #4F46E5;
  --color-primary-dark: #4338CA;
  --color-secondary: #818CF8;
  --color-secondary-dark: #6366F1;
  --color-accent: #EEF2FF;
  --color-accent-foreground: #312E81;
  
  --gradient-primary: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-dark) 100%);
  --gradient-secondary: linear-gradient(135deg, var(--color-secondary) 0%, var(--color-secondary-dark) 100%);
  --gradient-page: linear-gradient(135deg, var(--color-accent) 0%, #C7D2FE 100%);
  
  --shadow-modern: 0 10px 30px -5px rgba(79, 70, 229, 0.2);
  --shadow-modern-hover: 0 20px 40px -5px rgba(79, 70, 229, 0.3);
}
```

This approach would make future theme changes easier to implement. 