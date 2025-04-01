import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { ColorPalette } from '../../../../components/ui/ColorPalette';
import { ConceptData } from '../../../../services/supabaseClient';

interface ConceptCardProps {
  concept: ConceptData;
  /** Prevents default navigation on card click */
  preventNavigation?: boolean;
  /** Callback when a specific color variation is clicked */
  onColorClick?: (variationId: string) => void;
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
  onColorClick 
}) => {
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);
  
  // Get current color variation or default to first one
  const hasVariations = concept.color_variations && concept.color_variations.length > 0;
  const currentVariation = hasVariations ? concept.color_variations?.[selectedVariationIndex] : null;
  
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

    if (hasVariations && index < (concept.color_variations?.length || 0)) {
      setSelectedVariationIndex(index);
      
      // If onColorClick is provided, call it with the variation ID
      if (onColorClick && concept.color_variations) {
        onColorClick(concept.color_variations[index].id);
      }
    }
  };
  
  // Get the current image URL based on selection
  const currentImageUrl = currentVariation?.image_url || concept.base_image_url;
  
  // Use a consistent neutral background color
  const neutralBackgroundColor = '#f0f0f5';
  
  // Create the card content
  const cardContent = (
    <div className="flex flex-col bg-indigo-50/90 rounded-lg overflow-hidden shadow-sm border border-indigo-100 h-full transition-all duration-300 hover:shadow-md">
      <div 
        className="h-48 flex items-center justify-center"
        style={{ background: neutralBackgroundColor }}
      >
        {/* Show the selected variation image or base image */}
        <img
          src={currentImageUrl}
          alt={concept.logo_description}
          className="w-full h-full object-contain"
        />
      </div>
      
      <div className="p-5 flex-grow">
        <h3 className="font-semibold text-dark-900 mb-2">
          {concept.title || (concept.logo_description ? concept.logo_description.substring(0, 40) + '...' : 'Untitled Concept')}
        </h3>
        
        <p className="text-sm text-dark-600 line-clamp-2 mb-4">
          {concept.logo_description || 'No description available'}
        </p>
        
        {hasVariations && (
          <div className="mt-3 mb-3">
            <div className="flex space-x-2">
              {concept.color_variations?.map((variation, index) => (
                <button 
                  key={index}
                  onClick={(e) => handlePaletteClick(e, index)}
                  className={`w-6 h-6 rounded-full transition-all duration-300 ${
                    selectedVariationIndex === index ? 'ring-2 ring-indigo-500 ring-offset-2' : ''
                  }`}
                  style={{ backgroundColor: variation.colors[0] || '#4F46E5' }}
                  title={`${onColorClick ? 'Refine' : 'View'} ${variation.palette_name || `Color Palette ${index + 1}`}`}
                />
              ))}
            </div>
          </div>
        )}
        
        <div className="flex justify-between mt-4 pt-4 border-t border-dark-100">
          <span className="text-indigo-600 text-sm font-medium">View Details</span>
          <span className="text-indigo-600 text-sm font-medium">Edit</span>
        </div>
      </div>
    </div>
  );
  
  // If preventNavigation is true, just return the card content directly
  if (preventNavigation) {
    return cardContent;
  }
  
  // Otherwise wrap it in a Link for navigation
  return (
    <Link 
      to={`/concepts/${concept.id}`}
      className="block hover-lift hover:no-underline"
    >
      {cardContent}
    </Link>
  );
}; 