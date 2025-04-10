import React, { useState, useEffect } from 'react';
import { Card } from './Card';
import { getSignedImageUrl } from '../../services/supabaseClient';

/**
 * Helper function to determine if a color is light
 * @param hexColor - Hex color string
 * @returns boolean - True if color is light
 */
const isLightColor = (hexColor: string): boolean => {
  // Default to false for non-hex colors
  if (!hexColor || !hexColor.startsWith('#')) {
    return false;
  }

  // Convert hex to RGB
  let r = 0, g = 0, b = 0;
  if (hexColor.length === 7) {
    r = parseInt(hexColor.substring(1, 3), 16);
    g = parseInt(hexColor.substring(3, 5), 16);
    b = parseInt(hexColor.substring(5, 7), 16);
  } else if (hexColor.length === 4) {
    r = parseInt(hexColor.substring(1, 2), 16) * 17;
    g = parseInt(hexColor.substring(2, 3), 16) * 17;
    b = parseInt(hexColor.substring(3, 4), 16) * 17;
  }

  // Calculate perceived brightness (YIQ formula)
  const yiq = ((r * 299) + (g * 587) + (b * 114)) / 1000;
  return yiq >= 200; // Higher threshold to catch very light colors
}

// Helper function to process image URLs and handle signed URLs
const processImageUrl = (imageUrl: string | undefined | null): string => {
  if (!imageUrl || typeof imageUrl !== 'string') {
    console.log('ConceptCard: Image URL is empty, undefined, or not a string', imageUrl);
    return '';
  }
  
  // Log the original image URL for debugging
  console.log(`ConceptCard: Processing image URL: ${imageUrl.substring(0, 50)}${imageUrl.length > 50 ? '...' : ''}`);
  
  // If it's already a signed URL or a complete URL, return it directly
  if (imageUrl.includes('/object/sign/') && imageUrl.includes('token=')) {
    // Check for double signing
    if (imageUrl.indexOf('/object/sign/') !== imageUrl.lastIndexOf('/object/sign/')) {
      console.log('ConceptCard: Found doubly-signed URL, using original format');
      // For double-signed URLs, just return the URL as is since getSignedImageUrl will handle this
    }
    console.log('ConceptCard: URL is already signed, using as-is');
    return imageUrl;
  }
  
  // If it's a full URL but not signed yet
  if (imageUrl.startsWith('http')) {
    // Try to extract the path
    if (imageUrl.includes('/storage/v1/object/public/')) {
      const bucketTypes = ['concept-images', 'palette-images'];
      for (const bucket of bucketTypes) {
        if (imageUrl.includes(`/${bucket}/`)) {
          const pathParts = imageUrl.split(`/${bucket}/`);
          if (pathParts.length > 1) {
            const path = pathParts[1].split('?')[0];
            console.log(`ConceptCard: Extracted path from URL: ${path}, using ${bucket.includes('palette') ? 'palette' : 'concept'} bucket`);
            return getSignedImageUrl(path, bucket.includes('palette') ? 'palette' : 'concept');
          }
        }
      }
    }
    console.log('ConceptCard: Using full URL directly');
    return imageUrl;
  }
  
  // For simple paths, assume it's a concept image path
  console.log(`ConceptCard: Treating as simple path, getting signed URL`);
  return getSignedImageUrl(imageUrl, 'concept');
}

export interface ConceptCardProps {
  /**
   * Concept title/name
   */
  title: string;
  
  /**
   * Concept description
   */
  description: string;
  
  /**
   * Colors to display in the palette
   * Each element represents a color variation with an array of colors
   */
  colorVariations: string[][];
  
  /**
   * Images for each color variation, if available
   * If includeOriginal is true, the first image is considered the original
   */
  images?: string[];
  
  /**
   * Whether to include the original image as a variation option
   * If true, the first image in the images array is the original
   */
  includeOriginal?: boolean;
  
  /**
   * Gradient colors for the header (from and to)
   */
  gradient?: {
    from: string;
    to: string;
  };
  
  /**
   * Initials to display in the centered circle
   */
  initials: string;
  
  /**
   * Handler for edit button click
   */
  onEdit?: (index: number) => void;
  
  /**
   * Handler for view details button click
   * @param index The selected variation index
   */
  onViewDetails?: (index: number) => void;
  
  /**
   * Text to display on the edit button (default: "Edit")
   */
  editButtonText?: string;
  
  /**
   * Direct image URL for sample concepts
   * This bypasses the Supabase storage processing
   */
  sampleImageUrl?: string;
  
  /**
   * Optional color variation data including IDs
   * This is used to map UI indices to backend variation IDs
   */
  colorData?: Array<{
    id: string;
    colors: string[];
  }>;
}

/**
 * Card component for displaying concept previews
 */
export const ConceptCard: React.FC<ConceptCardProps> = ({
  title,
  description,
  colorVariations,
  images,
  includeOriginal = false,
  gradient = { from: 'blue-400', to: 'indigo-500' },
  initials,
  onEdit,
  onViewDetails,
  editButtonText = "Edit",
  sampleImageUrl,
  colorData
}) => {
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);

  // Add debug useEffect to track variation changes
  useEffect(() => {
    console.log(`ConceptCard ${title} - Selected variation changed to: ${selectedVariationIndex}`);
    console.log(`ConceptCard ${title} - Available images:`, images);
    
    // If we have images, log which one would be selected
    if (images && images.length > 0) {
      // Calculate the actual image index based on selection and includeOriginal flag
      let actualImageIndex;
      
      if (includeOriginal) {
        if (selectedVariationIndex === 0) {
          actualImageIndex = 0; // Original image
        } else {
          // For non-original selections, adjust the index to get the correct image
          // If includeOriginal is true, colorVariation index 0 maps to image index 1, 
          // colorVariation index 1 maps to image index 2, etc.
          actualImageIndex = selectedVariationIndex;
        }
      } else {
        // If we don't include original, the mapping is direct
        actualImageIndex = selectedVariationIndex;
      }
      
      if (actualImageIndex >= 0 && actualImageIndex < images.length) {
        console.log(`ConceptCard ${title} - Selected image at index ${actualImageIndex}:`, 
                   images[actualImageIndex].substring(0, 30) + '...');
      }
    }
  }, [selectedVariationIndex, images, title, includeOriginal]);
  
  // Log props for debugging
  console.log(`ConceptCard ${title} - Props:`, {
    includeOriginal,
    hasImages: images ? true : false,
    imagesCount: images?.length || 0,
    variationsCount: colorVariations?.length || 0
  });
  
  // Ensure we have at least one variation
  const hasVariations = colorVariations && Array.isArray(colorVariations) && colorVariations.length > 0;
  
  // Get the color array for the currently selected variation
  // Adjust index if we're including original (where index 0 is original, 1+ are variations)
  let colorIndex;
  if (includeOriginal && selectedVariationIndex > 0) {
    colorIndex = selectedVariationIndex - 1; // Adjust index for colorVariations array
  } else if (!includeOriginal) {
    colorIndex = selectedVariationIndex; // Direct mapping
  } else {
    colorIndex = 0; // Default to first variation if original is selected
  }
  
  const colors = hasVariations && colorIndex >= 0 && colorIndex < colorVariations.length
    ? colorVariations[colorIndex]
    : [];
  
  // Get the main color from the current variation
  const mainColor = colors && colors.length > 0 ? colors[0] : '#4F46E5';
  
  // Handle color variation selection
  const handleVariationSelect = (index: number) => {
    console.log(`ConceptCard ${title} - Selected variation index: ${index}`);
    setSelectedVariationIndex(index);
  };
  
  // Get the processed image URL for the current selected variation
  const currentImageUrl = (() => {
    // If sample image URL is provided, use it directly
    if (sampleImageUrl) {
      console.log(`ConceptCard: ${title} - Using sample image URL: ${sampleImageUrl}`);
      return sampleImageUrl;
    }
    
    // Debug what images are available
    console.log(`ConceptCard: ${title} - Selected variation: ${selectedVariationIndex}`);
    console.log(`ConceptCard: ${title} - Has images array: ${images ? 'yes' : 'no'}, length: ${images?.length || 0}`);
    console.log(`ConceptCard: ${title} - includeOriginal: ${includeOriginal}`);
    
    // Log each image URL for debugging
    if (images && images.length > 0) {
      console.log(`ConceptCard: ${title} - Available images:`, 
        images.map((url, i) => `[${i}]: ${typeof url === 'string' ? url.substring(0, 30) + '...' : 'not a string'}`));
    }
    
    // If no images are available, return undefined
    if (!images || images.length === 0) {
      console.log(`ConceptCard: ${title} - No images available`);
      return undefined;
    }
    
    // FIX: Calculate the actual image index based on selected variation index
    // Simplified mapping to ensure consistent behavior
    let imageIndex = selectedVariationIndex;
    
    // Safety check to make sure index is valid
    if (imageIndex < 0 || imageIndex >= images.length) {
      console.log(`ConceptCard: ${title} - Invalid index ${imageIndex}, using first image`);
      return processImageUrl(images[0]);
    }
    
    // Get and process the URL for the selected variation
    const rawUrl = images[imageIndex];
    
    // Check if rawUrl is a string before calling substring
    if (typeof rawUrl === 'string') {
      console.log(`ConceptCard: ${title} - Raw URL for index ${imageIndex}: ${rawUrl.substring(0, 30)}${rawUrl.length > 30 ? '...' : ''}`);
    } else {
      console.log(`ConceptCard: ${title} - Raw URL for index ${imageIndex} is not a string:`, rawUrl);
      // Return undefined if the URL is not a string (will show default initials instead)
      return undefined;
    }
    
    return processImageUrl(rawUrl);
  })();
  
  return (
    <div className="overflow-hidden rounded-lg shadow-modern border border-indigo-100 bg-white/90 backdrop-blur-sm hover-lift hover:shadow-modern-hover transition-all duration-300 scale-in h-full flex flex-col">
      {/* Header with image or gradient + initials */}
      <div 
        className={`h-40 p-4 flex items-center justify-center`}
        style={{ 
          background: currentImageUrl 
            ? 'transparent' 
            : `linear-gradient(to right, var(--tw-gradient-from-${gradient.from}), var(--tw-gradient-to-${gradient.to}))`
        }}
      >
        {currentImageUrl ? (
          <img 
            src={currentImageUrl} 
            alt={title}
            className="w-full h-full object-contain"
          />
        ) : (
          <div 
            className="w-20 h-20 bg-white rounded-full flex items-center justify-center font-bold text-xl shadow-lg"
            style={{ color: mainColor }}
          >
            {initials}
          </div>
        )}
      </div>
      
      {/* Content area */}
      <div className="p-4 flex-grow flex flex-col">
        <h4 className="font-semibold text-indigo-900">{title}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
        
        {/* Color palettes */}
        <div className="mt-3 flex space-x-2">
          {/* Original option if available */}
          {includeOriginal && (
            <button 
              onClick={() => handleVariationSelect(0)}
              className={`inline-block w-6 h-6 rounded-full border border-gray-300 flex items-center justify-center transition-all duration-300 ${
                selectedVariationIndex === 0 ? 'ring-2 ring-indigo-500 ring-offset-2' : 'hover-scale'
              }`}
              style={{ background: 'white' }}
              title="Original"
            >
              <span className="text-xs">O</span>
            </button>
          )}
          
          {/* Color variations */}
          {hasVariations && Array.isArray(colorVariations) && colorVariations.map((colorSet, variationIndex) => {
            // Adjust the index to account for the original option
            const displayIndex = includeOriginal ? variationIndex + 1 : variationIndex;
            
            // Get the primary color (first color in the set)
            const primaryColor = Array.isArray(colorSet) && colorSet.length > 0
              ? colorSet[0] 
              : '#4F46E5';
            
            return (
              <button 
                key={`variation-${variationIndex}`}
                onClick={() => handleVariationSelect(displayIndex)}
                className={`inline-block w-6 h-6 rounded-full flex items-center justify-center transition-all duration-300 ${
                  selectedVariationIndex === displayIndex ? 'ring-2 ring-indigo-500 ring-offset-2' : 'hover-scale'
                }`}
                style={{ backgroundColor: primaryColor, color: isLightColor(primaryColor) ? '#1E293B' : 'white' }}
                title={`Color variation ${variationIndex + 1}`}
              >
                <span className="text-xs">{variationIndex + 1}</span>
              </button>
            );
          })}
        </div>

        {/* Spacer to push buttons to bottom */}
        <div className="flex-grow"></div>
        
        {/* Action buttons */}
        <div className="mt-4 flex justify-between">
          {onEdit && (
            <button 
              onClick={() => {
                // If colorData is available, use it to map indices to variation IDs
                if (colorData && Array.isArray(colorData) && selectedVariationIndex > 0) {
                  // Convert UI index to colorData index
                  const colorIndex = includeOriginal ? selectedVariationIndex - 1 : selectedVariationIndex;
                  
                  // Get the variation ID if available
                  if (colorIndex >= 0 && colorIndex < colorData.length) {
                    const variationId = colorData[colorIndex]?.id;
                    console.log(`ConceptCard edit: mapped variation index ${selectedVariationIndex} to ID ${variationId}`);
                  } else {
                    console.log(`ConceptCard edit: could not map variation index ${selectedVariationIndex} (color index ${colorIndex}) - out of range of colorData (length: ${colorData.length})`);
                  }
                }
                
                // Always call the original handler with the index for backwards compatibility
                onEdit(selectedVariationIndex);
              }}
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              {editButtonText}
            </button>
          )}
          
          {onViewDetails && (
            <button 
              onClick={() => {
                // If colorData is available, use it to map indices to variation IDs
                if (colorData && Array.isArray(colorData) && selectedVariationIndex > 0) {
                  // Convert UI index to colorData index
                  const colorIndex = includeOriginal ? selectedVariationIndex - 1 : selectedVariationIndex;
                  
                  // Get the variation ID if available
                  if (colorIndex >= 0 && colorIndex < colorData.length) {
                    const variationId = colorData[colorIndex]?.id;
                    console.log(`ConceptCard view details: mapped variation index ${selectedVariationIndex} to ID ${variationId}`);
                  } else {
                    console.log(`ConceptCard view details: could not map variation index ${selectedVariationIndex} (color index ${colorIndex}) - out of range of colorData (length: ${colorData.length})`);
                  }
                }
                
                // Always call the original handler with the index for backwards compatibility
                onViewDetails(selectedVariationIndex);
              }}
              className="text-indigo-600 hover:text-indigo-800 text-sm font-medium flex items-center"
            >
              <span className="mr-1">View Details</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConceptCard; 