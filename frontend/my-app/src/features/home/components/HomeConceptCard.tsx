import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import { ConceptData } from '../../../services/supabaseClient';

interface HomeConceptCardProps {
  concept: ConceptData;
  onEdit: () => void;
  onViewDetails: () => void;
}

/**
 * Concept initials generator
 * 
 * @param description The concept description
 * @returns Two-letter initials extracted from the description
 */
const getConceptInitials = (description: string): string => {
  const words = description.trim().split(/\s+/);
  
  if (words.length === 0) return 'CV';
  if (words.length === 1) return words[0].substring(0, 2).toUpperCase();
  
  return (words[0][0] + words[1][0]).toUpperCase();
};

/**
 * Card component that displays a single concept for the home page
 */
export const HomeConceptCard: React.FC<HomeConceptCardProps> = ({ 
  concept,
  onEdit,
  onViewDetails
}) => {
  // Add debug logging for this specific concept
  useEffect(() => {
    console.log(`HomeConceptCard for "${concept.logo_description}" (ID: ${concept.id.substring(0, 8)}...)`, { 
      id: concept.id,
      base_image_path: concept.base_image_path,
      base_image_url: concept.base_image_url,
      variations_count: concept.color_variations?.length || 0,
    });
    
    // If we have color variations, log details for debugging
    if (concept.color_variations && concept.color_variations.length > 0) {
      console.log(`Color variations for concept ${concept.id.substring(0, 8)}...`);
      concept.color_variations.forEach((variation, index) => {
        console.log(`  Variation ${index+1}: ${variation.palette_name}`, {
          image_path: variation.image_path,
          image_url: variation.image_url,
          colors_count: variation.colors?.length || 0
        });
      });
    }
  }, [concept]);

  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);
  
  // State to track image loading status
  const [imageLoaded, setImageLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  
  // Get current color variation or default to first one
  const hasVariations = concept.color_variations && concept.color_variations.length > 0;
  const currentVariation = hasVariations ? concept.color_variations?.[selectedVariationIndex] : null;
  
  // Get main color for concept (use selected variation or default to indigo)
  // This is used for the color buttons and fallback initials, but not for the background
  const mainColor = currentVariation && currentVariation.colors && currentVariation.colors.length > 0
    ? currentVariation.colors[0]
    : '#4F46E5';
  
  const initials = getConceptInitials(concept.logo_description || '');
  
  // Handle color palette click - switch between variations
  const handlePaletteClick = (index: number, e: React.MouseEvent) => {
    e.preventDefault(); // Prevent navigation when clicking on color circles
    if (hasVariations && index < (concept.color_variations?.length || 0)) {
      setSelectedVariationIndex(index);
      setImageLoaded(false); // Reset image loaded state when switching variations
      setImageError(false);  // Reset error state
      console.log(`Switched to variation ${index} for concept ${concept.id.substring(0, 8)}...`);
    }
  };
  
  // Get the current image URL based on selection
  const currentImageUrl = currentVariation?.image_url || concept.base_image_url;
  
  // Use a consistent neutral background color
  const neutralBackgroundColor = '#f0f0f5';
  
  const handleImageLoad = () => {
    console.log(`✅ Image loaded successfully for ${concept.logo_description}: ${currentImageUrl}`);
    setImageLoaded(true);
    setImageError(false);
  };
  
  const handleImageError = () => {
    console.error(`❌ Failed to load image for ${concept.logo_description}: ${currentImageUrl}`);
    console.error(`   Original path: ${currentVariation?.image_path || concept.base_image_path}`);
    setImageError(true);
    setImageLoaded(false);
  };
  
  return (
    <div className="flex flex-col bg-indigo-50/90 rounded-lg overflow-hidden shadow-sm border border-indigo-100 h-full transition-all duration-300 hover:shadow-md">
      <div 
        className="h-48 flex items-center justify-center"
        style={{ background: neutralBackgroundColor }}
      >
        {imageError || !currentImageUrl ? (
          // Show initials if image fails to load or no URL is provided
          <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center font-bold text-xl" style={{ color: mainColor }}>
            {initials}
          </div>
        ) : (
          // Show the selected variation image if available
          <img
            src={currentImageUrl}
            alt={concept.logo_description}
            className="w-full h-full object-contain"
            onLoad={handleImageLoad}
            onError={handleImageError}
            crossOrigin="anonymous" // Add CORS attribute to help with cross-origin image loading
          />
        )}
      </div>
      
      <div className="p-5 flex-grow">
        <h3 className="font-semibold text-dark-900 mb-2">
          {concept.logo_description ? 
            (concept.logo_description.length > 25 ? concept.logo_description.substring(0, 25) + '...' : concept.logo_description) : 
            'Untitled Concept'}
        </h3>
        
        <p className="text-sm text-dark-600 line-clamp-2 mb-4">
          {concept.theme_description || 'No description available'}
        </p>
        
        {hasVariations && (
          <div className="mt-3 mb-3">
            <div className="flex space-x-2">
              {concept.color_variations?.map((variation, index) => (
                <button 
                  key={index}
                  onClick={(e) => handlePaletteClick(index, e)}
                  className={`w-6 h-6 rounded-full transition-all duration-300 ${
                    selectedVariationIndex === index ? 'ring-2 ring-indigo-500 ring-offset-2' : ''
                  }`}
                  style={{ backgroundColor: variation.colors[0] || '#4F46E5' }}
                  title={`${variation.palette_name || `Color Palette ${index + 1}`}`}
                />
              ))}
            </div>
          </div>
        )}
        
        <div className="flex justify-between mt-4 pt-4 border-t border-dark-100">
          <button
            onClick={onViewDetails}
            className="text-indigo-600 text-sm font-medium hover:text-indigo-800 transition-colors"
          >
            View Details
          </button>
          <button
            onClick={onEdit}
            className="text-indigo-600 text-sm font-medium hover:text-indigo-800 transition-colors"
          >
            Edit
          </button>
        </div>
      </div>
    </div>
  );
}; 