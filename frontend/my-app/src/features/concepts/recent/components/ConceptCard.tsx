import React, { useState, useEffect, useMemo } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ColorPalette } from '../../../../components/ui/ColorPalette';
import { ConceptData } from '../../../../services/supabaseClient';

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

interface ConceptCardProps {
  concept: ConceptData;
  /** Prevents default navigation on card click */
  preventNavigation?: boolean;
  /** Callback when a specific color variation is clicked */
  onColorClick?: (variationId: string) => void;
  /** Callback when the Edit button is clicked */
  onEdit?: (conceptId: string, variationId?: string | null) => void;
  /** Callback when the View Details button is clicked */
  onViewDetails?: (conceptId: string, variationId?: string | null) => void;
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

/**
 * Card component that displays a single concept
 */
export const ConceptCard: React.FC<ConceptCardProps> = ({ 
  concept, 
  preventNavigation = false,
  onColorClick,
  onEdit,
  onViewDetails
}) => {
  const navigate = useNavigate();
  
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(-1); // -1 means original image
  
  // Debug logging for concept variations
  useEffect(() => {
    if (concept.color_variations && concept.color_variations.length > 0) {
      console.log('ConceptCard - Available variations:', 
        concept.color_variations.map((v, i) => ({
          index: i,
          id: v.id,
          name: v.palette_name,
          firstColor: v.colors[0],
          hasImage: !!v.image_url
        }))
      );
    }
    
    // Add debug logging for the images array too
    const baseImageUrl = concept.image_url || concept.base_image_url;
    console.log('ConceptCard - Base image URL:', baseImageUrl);
    
    // Log all variation image URLs
    if (concept.color_variations) {
      console.log('ConceptCard - Variation image URLs:', 
        concept.color_variations.map(v => v.image_url).filter(Boolean)
      );
    }
  }, [concept.color_variations, concept.image_url, concept.base_image_url]);
  
  // Get current color variation or null if original is selected
  const currentVariation = selectedVariationIndex >= 0 && concept.color_variations && concept.color_variations.length > 0 
    ? concept.color_variations?.[selectedVariationIndex] 
    : null;
  
  // Get main color for concept (use selected variation or default to indigo)
  // This is used for the color buttons, but not for the background anymore
  const mainColor = currentVariation && currentVariation.colors && currentVariation.colors.length > 0
    ? currentVariation.colors[0]
    : '#4F46E5';
  
  const initials = getConceptInitials(concept.logo_description || '');
  
  // Handle color palette click - switch between variations
  const handlePaletteClick = (e: React.MouseEvent, index: number) => {
    e.preventDefault(); // Prevent navigation when clicking on color circles
    e.stopPropagation(); // Prevent the card click from triggering

    console.log('Palette click:', { 
      currentIndex: selectedVariationIndex, 
      newIndex: index, 
      isOriginal: index === -1 
    });

    // Update the selected variation index (local state only)
    setSelectedVariationIndex(index);
    
    // If onColorClick is provided and it's a variation (not original)
    // This is optional - only if you need immediate parent notification on color change
    if (onColorClick && concept.color_variations && index >= 0 && index < concept.color_variations.length) {
      const variationId = concept.color_variations[index].id;
      if (variationId) {
        console.log('Calling onColorClick with variation ID:', variationId);
        onColorClick(variationId);
      }
    }
  };
  
  // Get variation ID from selected index
  const getVariationId = (index: number): string | null => {
    if (index < 0 || !concept.color_variations || concept.color_variations.length === 0) {
      return null;
    }
    
    if (index < concept.color_variations.length) {
      return concept.color_variations[index]?.id || null;
    }
    
    return null;
  };
  
  // Handle edit button click
  const handleEdit = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Get variation ID from selected index
    const variationId = getVariationId(selectedVariationIndex);
    
    console.log('[ConceptCard] Edit clicked:', { 
      conceptId: concept.id, 
      selectedIndex: selectedVariationIndex, 
      mappedVariationId: variationId
    });
    
    // Send the variation ID to the parent handler if provided
    if (onEdit) {
      onEdit(concept.id, variationId);
    } else {
      // If no callback provided, navigate to refine page with selected variation
      if (variationId) {
        navigate(`/refine/${concept.id}?colorId=${variationId}`);
      } else {
        // Navigate to refine with original
        navigate(`/refine/${concept.id}`);
      }
    }
  };
  
  // Handle view details button click
  const handleViewDetails = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    // Get variation ID from selected index
    const variationId = getVariationId(selectedVariationIndex);
    
    console.log('[ConceptCard] View details clicked:', { 
      conceptId: concept.id, 
      selectedIndex: selectedVariationIndex, 
      mappedVariationId: variationId 
    });
    
    // Send the variation ID to the parent handler if provided  
    if (onViewDetails) {
      onViewDetails(concept.id, variationId);
    } else {
      // If no callback provided, navigate to concept details page with selected variation
      if (variationId) {
        navigate(`/concepts/${concept.id}?colorId=${variationId}`);
      } else {
        // Navigate to details with original
        navigate(`/concepts/${concept.id}`);
      }
    }
  };
  
  // Get the current image URL based on selection using memoization for performance
  // If we're showing the original (-1), use the concept's original image URL
  // Otherwise get the image URL from the selected variation
  const currentImageUrl = useMemo(() => {
    // Default to the original/base image URL
    let urlToUse = concept.image_url || concept.base_image_url;
    
    console.log(`[DEBUG] ConceptCard image selection:`, {
      conceptId: concept.id,
      selectedVariationIndex,
      hasVariations: Boolean(concept.color_variations && concept.color_variations.length > 0),
      variationsCount: concept.color_variations?.length || 0,
      baseImageUrl: concept.base_image_url,
      imageUrl: concept.image_url
    });
    
    if (selectedVariationIndex >= 0 && 
        concept.color_variations && 
        selectedVariationIndex < concept.color_variations.length) {
      // Get the variation at the exact index
      const variation = concept.color_variations[selectedVariationIndex];
      console.log(`[DEBUG] Selected variation:`, {
        index: selectedVariationIndex,
        variationId: variation?.id,
        variationName: variation?.palette_name,
        hasImage: Boolean(variation?.image_url)
      });
      
      if (variation && variation.image_url) {
        urlToUse = variation.image_url;
        console.log(`ConceptCard: Using variation ${selectedVariationIndex} image:`, urlToUse);
      } else {
        console.log(`ConceptCard: Variation ${selectedVariationIndex} has no image, using original:`, urlToUse);
      }
    } else {
      console.log(`ConceptCard: Using original image (index ${selectedVariationIndex}):`, urlToUse);
    }
    
    console.log(`[DEBUG] Final image URL selected: ${urlToUse?.substring(0, 50)}${urlToUse && urlToUse.length > 50 ? '...' : ''}`);
    
    return urlToUse || '/placeholder-image.png'; // Fallback if no URL available
  }, [concept, selectedVariationIndex]); // Recalculate only when these dependencies change
  
  // Use a consistent neutral background color
  const neutralBackgroundColor = '#f0f0f5';
  
  // Create the card content
  const cardContent = (
    <div className="flex flex-col bg-indigo-50/90 rounded-lg overflow-hidden shadow-sm border border-indigo-100 h-full transition-all duration-300 hover:shadow-md">
      {/* Image container with fixed height */}
      <div 
        className="h-48 flex items-center justify-center overflow-hidden"
        style={{ background: neutralBackgroundColor }}
      >
        <img
          src={currentImageUrl}
          alt={concept.logo_description}
          className="w-full h-full object-contain"
        />
      </div>
      
      <div className="p-5 flex-grow flex flex-col">
        {/* Title container with fixed height */}
        <div className="h-16 mb-2">
          <h3 className="font-semibold text-dark-900 line-clamp-2">
            {concept.logo_description ? 
              (concept.logo_description.length > 40 ? 
                concept.logo_description.substring(0, 40) + '...' : 
                concept.logo_description) : 
              'Untitled Concept'}
          </h3>
        </div>
        
        {/* Description with fixed height and clamp */}
        <div className="h-12 mb-4">
          <p className="text-sm text-dark-600 line-clamp-2">
            {concept.logo_description || 'No description available'}
          </p>
        </div>
        
        {/* Color variations */}
        <div className="mt-auto mb-3">
          {concept.color_variations && concept.color_variations.length > 0 && (
            <div className="flex space-x-2">
              {/* Original color option */}
              <button 
                onClick={(e) => handlePaletteClick(e, -1)}
                className={`w-6 h-6 rounded-full border border-gray-300 transition-all duration-300 flex items-center justify-center ${
                  selectedVariationIndex === -1 ? 'ring-2 ring-indigo-500 ring-offset-2' : ''
                }`}
                style={{ background: 'white' }}
                title="Original Image"
                aria-label="View original image"
              >
                <span className="text-xs">O</span>
              </button>
              
              {/* Color variations */}
              {concept.color_variations?.map((variation, index) => {
                const color = variation.colors && variation.colors.length > 0 ? variation.colors[0] : '#4F46E5';
                const isLight = isLightColor(color);
                
                return (
                  <button 
                    key={variation.id || `var-${index}`}
                    onClick={(e) => handlePaletteClick(e, index)}
                    className={`w-6 h-6 rounded-full transition-all duration-300 ${
                      selectedVariationIndex === index ? 'ring-2 ring-indigo-500 ring-offset-2' : ''
                    } ${isLight ? 'border-2 border-gray-400' : ''}`}
                    style={{ backgroundColor: color }}
                    title={variation.palette_name || `Color Palette ${index + 1}`}
                    aria-label={`View ${variation.palette_name || `Color Palette ${index + 1}`}`}
                  />
                );
              })}
            </div>
          )}
        </div>
        
        {/* Action buttons with consistent position */}
        <div className="flex justify-between pt-4 border-t border-dark-100">
          <button 
            onClick={handleEdit}
            className="text-indigo-600 text-sm font-medium hover:text-indigo-800 transition-colors"
          >
            Refine
          </button>
          <button 
            onClick={handleViewDetails}
            className="text-indigo-600 text-sm font-medium hover:text-indigo-800 transition-colors"
          >
            View Details
          </button>
        </div>
      </div>
    </div>
  );
  
  // If preventNavigation is true, just return the card content directly
  if (preventNavigation) {
    return cardContent;
  }
  
  // Otherwise render the card without a Link wrapper, since we now have buttons
  return cardContent;
}; 