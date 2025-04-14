import React, { useState, useEffect, useMemo } from 'react';
import { Card } from './Card';
import { getSignedImageUrl } from '../../services/supabaseClient';
import { ConceptData, ColorVariationData } from '../../services/supabaseClient';
import { Link } from 'react-router-dom';

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

/**
 * Concept initials generator
 * 
 * @param description The concept description
 * @returns Two-letter initials extracted from the description
 */
const getConceptInitials = (description: string): string => {
  const words = description.split(' ');
  if (words.length === 1) {
    return words[0].substring(0, 2).toUpperCase();
  }
  return (words[0][0] + words[1][0]).toUpperCase();
};

export interface ConceptCardProps {
  /**
   * Either provide a complete ConceptData object
   */
  concept?: ConceptData;

  /**
   * Or provide individual properties
   */
  
  /**
   * Concept title/name
   */
  title?: string;
  
  /**
   * Concept description
   */
  description?: string;
  
  /**
   * Colors to display in the palette
   * Each element represents a color variation with an array of colors
   */
  colorVariations?: string[][];
  
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
  initials?: string;
  
  /**
   * Handler for edit button click
   * Either version can be provided: simple index or with concept/variation IDs
   */
  onEdit?: ((index: number) => void) | ((conceptId: string, variationId?: string | null) => void);
  
  /**
   * Handler for view details button click
   * Either version can be provided: simple index or with concept/variation IDs
   */
  onViewDetails?: ((index: number) => void) | ((conceptId: string, variationId?: string | null) => void);
  
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

  /** Prevents default navigation on card click */
  preventNavigation?: boolean;
  
  /** Callback when a specific color variation is clicked */
  onColorClick?: (variationId: string) => void;
}

/**
 * Card component for displaying concept previews
 */
export const ConceptCard: React.FC<ConceptCardProps> = ({
  concept,
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
  colorData,
  preventNavigation = false,
  onColorClick
}) => {
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);

  // DERIVED PROPS: Set derived values based on whether we're using concept data or direct props
  // These derived variables normalize the two input methods
  
  // Get the final title
  const finalTitle = concept?.logo_description || title || "Concept";
  
  // Get the final description
  const finalDescription = concept?.theme_description || description || "";
  
  // Get the final initials
  const finalInitials = initials || (concept ? getConceptInitials(concept.logo_description || "") : "CV");
  
  // Get the final color variations
  const finalColorVariations = useMemo(() => {
    if (concept?.color_variations && concept.color_variations.length > 0) {
      return concept.color_variations.map(variation => variation.colors);
    }
    return colorVariations || [];
  }, [concept, colorVariations]);

  // Get the final images array
  const finalImages = useMemo(() => {
    if (concept) {
      if (concept.color_variations && concept.color_variations.length > 0) {
        // If we have variations, collect all image URLs
        const baseImage = concept.image_url || concept.base_image_url;
        const variationImages = concept.color_variations.map(v => v.image_url).filter(Boolean);
        
        // If we have a base image, put it first
        return baseImage ? [baseImage, ...variationImages] : variationImages;
      } else if (concept.image_url) {
        // Just the base image if no variations
        return [concept.image_url];
      }
    }
    return images || [];
  }, [concept, images]);

  // Add debug useEffect to track variation changes
  useEffect(() => {
    console.log(`ConceptCard - Selected variation changed to: ${selectedVariationIndex}`);
    console.log(`ConceptCard - Available images:`, finalImages);
    
    // Update image URL based on the new selection
    // If includeOriginal is true, index 0 represents the original image
    if (includeOriginal && selectedVariationIndex === 0) {
      // Original image selected
      console.log('ConceptCard - Original image selected');
    } else if (concept?.color_variations) {
      // Get the actual color variation index (accounting for the Original option)
      const variationIndex = includeOriginal ? selectedVariationIndex - 1 : selectedVariationIndex;
      
      // Log the selected variation details
      if (variationIndex >= 0 && variationIndex < concept.color_variations.length) {
        const variation = concept.color_variations[variationIndex];
        console.log(`ConceptCard - Selected variation: ${variation.id}, palette: ${variation.palette_name}`);
      }
    }
    
    // If we have images, log which one would be selected
    if (finalImages && finalImages.length > 0) {
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
      
      if (actualImageIndex >= 0 && actualImageIndex < finalImages.length) {
        console.log(`ConceptCard - Selected image at index ${actualImageIndex}:`, 
                   finalImages[actualImageIndex].substring(0, 30) + '...');
      }
    }
  }, [selectedVariationIndex, concept, finalImages, includeOriginal]);
  
  // Log props for debugging
  useEffect(() => {
    console.log(`ConceptCard - Props:`, {
      hasConceptObj: concept ? true : false,
      title: finalTitle,
    includeOriginal,
      hasImages: finalImages ? true : false,
      imagesCount: finalImages?.length || 0,
      variationsCount: finalColorVariations?.length || 0
  });
  }, [concept, finalTitle, includeOriginal, finalImages, finalColorVariations]);
  
  // Ensure we have at least one variation
  const hasVariations = finalColorVariations && Array.isArray(finalColorVariations) && finalColorVariations.length > 0;
  
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
  
  const colors = hasVariations && colorIndex >= 0 && colorIndex < finalColorVariations.length
    ? finalColorVariations[colorIndex]
    : [];
  
  // Get the main color from the current variation
  const mainColor = colors && colors.length > 0 ? colors[0] : '#4F46E5';
  
  // Handle color variation selection
  const handleVariationSelect = (index: number, e?: React.MouseEvent) => {
    if (e) {
      e.preventDefault(); // Prevent navigation when clicking on color circles
      e.stopPropagation(); // Prevent the card click from triggering
    }
    
    console.log(`ConceptCard - Selected variation index: ${index}`);
    setSelectedVariationIndex(index);
    
    // If onColorClick is provided and we have a concept object
    if (onColorClick && concept?.color_variations && index >= 0 && index < concept.color_variations.length) {
      const variationId = concept.color_variations[index].id;
      if (variationId) {
        console.log('Calling onColorClick with variation ID:', variationId);
        onColorClick(variationId);
      }
    }
  };
  
  // Get the processed image URL for the current selected variation
  const currentImageUrl = useMemo(() => {
    // If sample image URL is provided, use it directly
    if (sampleImageUrl) {
      console.log(`ConceptCard - Using sample image URL: ${sampleImageUrl}`);
      return sampleImageUrl;
    }
    
    // If we have a concept, use its image logic
    if (concept) {
      // If includeOriginal is true and index is 0, or we're at index 0 without includeOriginal
      // or we have no color variations, use the original image
      if ((includeOriginal && selectedVariationIndex === 0) || 
          selectedVariationIndex === 0 || 
          !concept.color_variations || 
          concept.color_variations.length === 0) {
        const baseUrl = concept.image_url || concept.base_image_url;
        console.log(`ConceptCard - Using concept original image: ${baseUrl?.substring(0, 50)}...`);
        return baseUrl || '/placeholder-image.png';
      }
      
      // For color variations, adjust the index if includeOriginal is true
      const variationIndex = includeOriginal ? selectedVariationIndex - 1 : selectedVariationIndex;
      
      // Otherwise, find the right variation image
      if (concept.color_variations && variationIndex >= 0 && variationIndex < concept.color_variations.length) {
        const variationImage = concept.color_variations[variationIndex].image_url;
        console.log(`ConceptCard - Using variation image: ${variationImage?.substring(0, 50)}...`);
        return variationImage || concept.image_url || '/placeholder-image.png';
      }
    }
    
    // Otherwise use the original logic for direct props
    console.log(`ConceptCard - Selected variation: ${selectedVariationIndex}`);
    console.log(`ConceptCard - Has images array: ${finalImages ? 'yes' : 'no'}, length: ${finalImages?.length || 0}`);
    console.log(`ConceptCard - includeOriginal: ${includeOriginal}`);
    
    // If we don't have images, return empty string
    if (!finalImages || finalImages.length === 0) {
      console.log('ConceptCard - No images available');
      return '';
    }
    
    // Calculate which image to use based on the selected variation
    // Selection logic depends on whether we're including original or not
    let imageIndex = 0;
    
    if (includeOriginal) {
      // If includeOriginal is true, index 0 represents the original image
      // and variation indices start at 1
      imageIndex = selectedVariationIndex;
    } else {
      // If includeOriginal is false, variations start at index 0
      imageIndex = selectedVariationIndex;
    }
    
    // Ensure the index is within bounds
    if (imageIndex >= 0 && imageIndex < finalImages.length) {
      // Process the image URL to handle Supabase storage paths
      const rawUrl = finalImages[imageIndex];
      console.log(`ConceptCard - Using image at index ${imageIndex}:`, rawUrl?.substring(0, 50));
      return processImageUrl(rawUrl);
    }
    
    // Fallback to the first image if index is out of bounds
    console.log('ConceptCard - Index out of bounds, using first image as fallback');
    return processImageUrl(finalImages[0]);
  }, [sampleImageUrl, concept, selectedVariationIndex, finalImages, includeOriginal]);

  // Get the logo URL for the central small card - updating to use the current selected variation
  const logoImageUrl = useMemo(() => {
    // If we have a concept with color variations
    if (concept?.color_variations && concept.color_variations.length > 0) {
      // For the original/default variation
      if ((includeOriginal && selectedVariationIndex === 0) || selectedVariationIndex === 0) {
        // Use logo_url if available, otherwise the original image
        return concept.logo_url || concept.image_url;
      }
      
      // For other variations, calculate the proper index
      const variationIndex = includeOriginal ? selectedVariationIndex - 1 : selectedVariationIndex;
      
      // If we have a valid variation index
      if (variationIndex >= 0 && variationIndex < concept.color_variations.length) {
        // Use that variation's image
        return concept.color_variations[variationIndex].image_url || concept.logo_url || concept.image_url;
      }
    }
    
    // Fallbacks for cases without variations
    // If we have a logo_url directly on the concept, use that
    if (concept?.logo_url) {
      return concept.logo_url;
    }
    
    // Check for icon_url
    if (concept?.icon_url) {
      return concept.icon_url;
    }
    
    // For sample cards
    if (sampleImageUrl) {
      return sampleImageUrl; 
    }
    
    // If we have a concept with just an image
    if (concept?.image_url) {
      return concept.image_url;
    }
    
    // Use direct props - check for multiple images
    if (finalImages && finalImages.length > 0) {
      const imageIndex = includeOriginal 
        ? selectedVariationIndex 
        : selectedVariationIndex;
      
      if (imageIndex >= 0 && imageIndex < finalImages.length) {
        return processImageUrl(finalImages[imageIndex]);
      }
      
      // Fallback to first image
      return processImageUrl(finalImages[0]);
    }
    
    return null; // No image available, will show initials instead
  }, [concept, sampleImageUrl, finalImages, includeOriginal, selectedVariationIndex]);

  // Handle edit button click with proper typing for the callback
  const handleEdit = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!onEdit) return;

    if (concept) {
      // Get variation ID from selected index
      const variationId = selectedVariationIndex >= 0 && 
                        concept.color_variations && 
                        selectedVariationIndex < concept.color_variations.length
                            ? concept.color_variations[selectedVariationIndex].id
                            : null;

      console.log('[ConceptCard] Edit clicked:', { 
        conceptId: concept.id, 
        selectedIndex: selectedVariationIndex, 
        variationId
      });
      
      // Call with concept ID style params
      (onEdit as (conceptId: string, variationId?: string | null) => void)(concept.id, variationId);
    } else {
      // Call with index style params
      (onEdit as (index: number) => void)(selectedVariationIndex);
    }
  };

  // Handle view details button click with proper typing for the callback
  const handleViewDetails = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (!onViewDetails) return;

    if (concept) {
      // Get variation ID from selected index
      const variationId = selectedVariationIndex >= 0 && 
                        concept.color_variations && 
                        selectedVariationIndex < concept.color_variations.length
                            ? concept.color_variations[selectedVariationIndex].id
                            : null;

      console.log('[ConceptCard] View details clicked:', { 
        conceptId: concept.id, 
        selectedIndex: selectedVariationIndex, 
        variationId
      });
      
      // Call with concept ID style params
      (onViewDetails as (conceptId: string, variationId?: string | null) => void)(concept.id, variationId);
    } else {
      // Call with index style params
      (onViewDetails as (index: number) => void)(selectedVariationIndex);
    }
  };

  // Handle card click
  const handleCardClick = () => {
    // If prevention is enabled, do nothing
    if (preventNavigation) {
      return;
    }
    
    // Otherwise, trigger view details if handler exists
    if (onViewDetails) {
      handleViewDetails({
        preventDefault: () => {},
        stopPropagation: () => {}
      } as React.MouseEvent);
    }
  };

  // Create the card content
  const cardContent = (
    <div 
      className="concept-card bg-white rounded-xl overflow-hidden shadow-md border border-indigo-100 transition-all duration-300 hover:transform hover:-translate-y-1 hover:shadow-xl"
      style={
        gradient 
          ? { background: 'white' }
          : {}
      }
    >
      <div 
        className="h-32 relative overflow-hidden flex items-center justify-center bg-blue-50"
      >
        {/* Display the initials in the colored background for a cleaner look */}
        <span className="text-5xl font-bold text-indigo-400 opacity-30">{finalInitials}</span>
      </div>
      
      <div className="p-5">
        <div className="-mt-16 mb-4 relative z-10 flex justify-center">
          <div className="w-24 h-24 rounded-lg overflow-hidden border-4 border-white shadow-md bg-white flex items-center justify-center transition-transform duration-300">
            {logoImageUrl ? (
              <img 
                src={logoImageUrl} 
                alt={finalTitle + " logo"} 
                className="object-contain w-full h-full p-1"
                onError={(e) => {
                  console.error('Logo image failed to load:', logoImageUrl);
                  (e.target as HTMLImageElement).src = '/placeholder-image.png';
                }}
          />
        ) : (
              <span className="text-3xl font-bold text-indigo-600">{finalInitials}</span>
            )}
          </div>
      </div>
      
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-800 mb-1">{finalTitle}</h3>
          <p className="text-gray-500 text-sm mb-4">{finalDescription}</p>
        </div>
        
        {/* Color variations */}
        {hasVariations && (
          <div className="flex justify-center items-center space-x-3 mb-4">
          {includeOriginal && (
              <div 
                className="w-6 h-6 rounded-full flex items-center justify-center text-indigo-600 font-bold text-xs bg-indigo-50 border border-gray-200"
                onClick={(e) => handleVariationSelect(0, e)}
              >
                O
              </div>
            )}
            
            {finalColorVariations.map((colorSet, variationIndex) => {
              // Adjust index if we include original variation
              const actualIndex = includeOriginal ? variationIndex + 1 : variationIndex;
              const isSelected = selectedVariationIndex === actualIndex;
              const mainColor = colorSet[0] || '#4F46E5';
              const needsBorder = isLightColor(mainColor);
            
            return (
                <div 
                  key={`${colorSet.join(',')}-${variationIndex}`}
                  className={`w-6 h-6 rounded-full cursor-pointer transition-all duration-200 hover:scale-110 hover:shadow-md ${
                    isSelected 
                      ? 'ring-2 ring-indigo-500 ring-offset-1 scale-110' 
                      : needsBorder 
                        ? 'border border-gray-400'
                        : 'border border-gray-200'
                  }`}
                  style={{ backgroundColor: mainColor }}
                  onClick={(e) => handleVariationSelect(actualIndex, e)}
                />
            );
          })}
        </div>
        )}
        
        {/* Action buttons */}
        <div className="grid grid-cols-2 gap-3">
          {onEdit && (
            <button 
              onClick={handleEdit}
              className="py-2 px-3 border border-gray-300 bg-white rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition shadow-sm"
            >
              {editButtonText}
            </button>
          )}
          
          {onViewDetails && (
            <button 
              onClick={handleViewDetails}
              className="py-2 px-3 bg-indigo-600 rounded-md text-sm font-medium text-white hover:bg-indigo-700 transition shadow-sm"
            >
              View Details
            </button>
          )}
        </div>
      </div>
    </div>
  );

  // Wrap in Card component
  return (
    <Card onClick={handleCardClick} className="h-full">
      {cardContent}
    </Card>
  );
};

export default ConceptCard; 