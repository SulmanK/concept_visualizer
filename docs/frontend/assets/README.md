# Assets

This directory contains static assets used throughout the application, such as images, icons, logos, and other media files.

## Directory Structure

The assets directory is organized by asset type to maintain clarity and ease of management:

```
assets/
├── images/        # Image files (png, jpg, webp)
├── icons/         # Icon files (svg)
├── logos/         # Application and brand logos
└── animations/    # Animation files (lottie, gif)
```

## Usage Guidelines

### Images

Images should be optimized for web use with appropriate compression and dimensions. For responsive images, different sizes should be provided and loaded using the `OptimizedImage` component.

```tsx
import { OptimizedImage } from "components/ui/OptimizedImage";
import placeholderImage from "assets/images/placeholder.jpg";

function MyComponent() {
  return (
    <OptimizedImage
      src={placeholderImage}
      alt="Placeholder image"
      width={400}
      height={300}
    />
  );
}
```

### Icons

SVG icons are preferred for scalability and customization. Icons should be imported and used with the appropriate wrapper component to ensure consistent styling and accessibility.

```tsx
import { ReactComponent as StarIcon } from "assets/icons/star.svg";
import { Icon } from "components/ui/Icon";

function MyComponent() {
  return (
    <Icon>
      <StarIcon />
    </Icon>
  );
}
```

### Logos

Application logos should be available in multiple formats and sizes to accommodate different use cases (header, favicon, splash screen, etc.).

```tsx
import logoFull from "assets/logos/logo-full.svg";
import logoSmall from "assets/logos/logo-small.svg";

function Header({ isCompact }) {
  return (
    <header>
      <img src={isCompact ? logoSmall : logoFull} alt="Application logo" />
    </header>
  );
}
```

### Animations

Animation files should be lightweight and used sparingly to enhance the user experience without impacting performance.

```tsx
import { Player } from "@lottiefiles/react-lottie-player";
import loadingAnimation from "assets/animations/loading.json";

function LoadingIndicator() {
  return (
    <Player
      autoplay
      loop
      src={loadingAnimation}
      style={{ height: "100px", width: "100px" }}
    />
  );
}
```

## Best Practices

1. **Optimization**: All assets should be optimized for web use to minimize file size and improve loading performance.
2. **Naming Conventions**: Use descriptive, kebab-case names for all asset files (e.g., `concept-placeholder.png`, `arrow-right.svg`).
3. **Static Imports**: Prefer static imports for assets used in components, allowing Webpack to handle optimization and bundling.
4. **Accessibility**: Ensure all assets have appropriate alternative text or ARIA attributes when used in the UI.
5. **Responsiveness**: Provide multiple sizes or formats for images used in responsive layouts.

## Managing Assets

When adding new assets to the project:

1. Place the asset in the appropriate subdirectory based on its type
2. Optimize the asset for web use using appropriate tools
3. Use descriptive naming conventions
4. Update this documentation if adding a new category of assets

## External Assets

For assets loaded from external sources (APIs, CDNs), handle loading states and errors appropriately:

```tsx
function ExternalImage({ src, alt, ...props }) {
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  return (
    <div className="image-container">
      {isLoading && <LoadingIndicator />}
      {error && <ErrorMessage error={error} />}
      <img
        src={src}
        alt={alt}
        onLoad={() => setIsLoading(false)}
        onError={(e) => {
          setIsLoading(false);
          setError(new Error("Failed to load image"));
        }}
        {...props}
      />
    </div>
  );
}
```
