import React, { useState } from 'react';
import { Card } from './Card';

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
   */
  images?: string[];
  
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
  onEdit?: () => void;
  
  /**
   * Handler for view details button click
   */
  onViewDetails?: () => void;
}

/**
 * Card component for displaying concept previews
 */
export const ConceptCard: React.FC<ConceptCardProps> = ({
  title,
  description,
  colorVariations,
  images,
  gradient = { from: 'blue-400', to: 'indigo-500' },
  initials,
  onEdit,
  onViewDetails,
}) => {
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);
  
  // Ensure we have at least one variation
  const hasVariations = colorVariations && colorVariations.length > 0;
  const colors = hasVariations ? colorVariations[selectedVariationIndex] : [];
  
  // Get the main color from the current variation
  const mainColor = colors.length > 0 ? colors[0] : '#4F46E5';
  
  // Handle color variation selection
  const handleVariationSelect = (index: number) => {
    if (index >= 0 && index < colorVariations.length) {
      setSelectedVariationIndex(index);
    }
  };
  
  return (
    <div className="overflow-hidden rounded-lg shadow-modern border border-indigo-100 bg-white/90 backdrop-blur-sm hover-lift hover:shadow-modern-hover transition-all duration-300 scale-in">
      {/* Header with image or gradient + initials */}
      <div 
        className={`h-40 p-4 flex items-center justify-center`}
        style={{ 
          background: images && images[selectedVariationIndex] 
            ? 'transparent' 
            : `linear-gradient(to right, var(--tw-gradient-from-${gradient.from}), var(--tw-gradient-to-${gradient.to}))`
        }}
      >
        {images && images[selectedVariationIndex] ? (
          <img 
            src={images[selectedVariationIndex]} 
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
      <div className="p-4">
        <h4 className="font-semibold text-indigo-900">{title}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
        
        {/* Color palettes */}
        {hasVariations && (
          <div className="mt-3 flex space-x-2">
            {colorVariations.map((variation, index) => (
              <button 
                key={`${variation[0]}-${index}`}
                onClick={() => handleVariationSelect(index)}
                className={`inline-block w-6 h-6 rounded-full transition-all duration-300 ${
                  selectedVariationIndex === index ? 'ring-2 ring-indigo-500 ring-offset-2' : 'hover-scale'
                }`}
                style={{ backgroundColor: variation[0] || '#4F46E5' }}
                title={`Color Palette ${index + 1}`}
              />
            ))}
          </div>
        )}
        
        {/* Actions */}
        <div className="mt-4 flex justify-between">
          {onEdit && (
            <button 
              className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
              onClick={onEdit}
            >
              Edit
            </button>
          )}
          
          {onViewDetails && (
            <button 
              className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
              onClick={onViewDetails}
            >
              View Details
            </button>
          )}
        </div>
      </div>
    </div>
  );
}; 