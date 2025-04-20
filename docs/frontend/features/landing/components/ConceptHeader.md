# ConceptHeader

The ConceptHeader component serves as the hero section for the landing page, providing a visually engaging introduction to the application.

## Overview

This component creates an impactful first impression, with a headline, tagline, and visual elements that communicate the core value proposition of the concept visualization tool.

## Component Structure

```tsx
const ConceptHeader: React.FC = () => {
  return (
    <header className="concept-header">
      <div className="header-content">
        <h1 className="main-heading">
          Visualize Your <span className="highlight">Brand Concepts</span>
        </h1>
        
        <p className="tagline">
          Transform your brand ideas into visual concepts with AI-powered design generation
        </p>
        
        <div className="cta-container">
          <Button 
            variant="primary"
            size="large"
            onClick={() => {
              document.getElementById('concept-form')?.scrollIntoView({ 
                behavior: 'smooth' 
              });
            }}
          >
            Start Creating
          </Button>
          
          <Button
            variant="secondary"
            size="large"
            as="a"
            href="/examples"
          >
            View Examples
          </Button>
        </div>
      </div>
      
      <div className="header-visual">
        <OptimizedImage 
          src="/assets/hero-image.webp"
          alt="Visual representation of brand concept generation"
          width={600}
          height={400}
          priority={true}
        />
      </div>
    </header>
  );
};
```

## Features

- **Engaging Headline**: Clear, concise value proposition
- **Visual Element**: Illustrative image that reinforces the concept
- **Call-to-Action Buttons**: Direct users to take immediate action
- **Responsive Design**: Adapts to different screen sizes
- **Smooth Scrolling**: Scrolls to the concept form when the CTA is clicked

## Dependencies

- `Button`: Button component for call-to-action buttons
- `OptimizedImage`: Optimized image component for the hero visual

## Props

This component does not accept any props as it's designed to be self-contained.

## Styling

The component uses modern web styling techniques:

- **Grid Layout**: For responsive alignment of content and visual
- **Typography Hierarchy**: Clear visual hierarchy with distinct heading and body text styles
- **Color Highlights**: Strategic use of accent colors to emphasize key terms
- **Responsive Breakpoints**: Adjusts layout for mobile, tablet, and desktop views

## Related Components

- [Button](../../../../components/ui/Button.md)
- [OptimizedImage](../../../../components/ui/OptimizedImage.md)
- [LandingPage](../LandingPage.md)

## Accessibility

- Semantic HTML structure with proper heading hierarchy
- Sufficient color contrast for text readability
- Alternative text for images
- Keyboard-accessible navigation for CTAs

## Usage

This component is typically used at the top of the landing page to create an impactful first impression:

```tsx
const LandingPage: React.FC = () => {
  return (
    <MainLayout>
      <ConceptHeader />
      {/* Other sections */}
    </MainLayout>
  );
};
```

## Performance Considerations

- Uses `priority={true}` on the hero image to ensure it loads early
- Optimized asset loading with WebP format
- Minimal JavaScript for interactive elements 