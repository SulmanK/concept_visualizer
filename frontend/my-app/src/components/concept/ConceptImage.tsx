import React, { useState } from "react";
import { OptimizedImage } from "../ui/OptimizedImage";

interface ConceptImageProps {
  path?: string;
  url?: string;
  isPalette?: boolean;
  alt: string;
  className?: string;
  lazy?: boolean;
}

/**
 * Component for displaying concept images
 * This is now a simple wrapper around OptimizedImage that handles errors and loading states
 */
const ConceptImage: React.FC<ConceptImageProps> = ({
  path,
  url,
  isPalette = false,
  alt,
  className,
  lazy = true,
}) => {
  const [error, setError] = useState<string | null>(null);

  // Use url if provided, otherwise use path as fallback (for backward compatibility)
  const imageUrl = url || path || "";

  if (!imageUrl) {
    return (
      <div className="image-placeholder text-gray-500 text-sm">
        No image available
      </div>
    );
  }

  if (error) {
    return <div className="image-error text-red-500 text-sm">{error}</div>;
  }

  return (
    <OptimizedImage
      src={imageUrl}
      alt={alt}
      className={className}
      lazy={lazy}
      onError={() => {
        console.error("Error loading image:", imageUrl);
        setError("Failed to load image");
      }}
    />
  );
};

export default ConceptImage;
