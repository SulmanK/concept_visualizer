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
   */
  onViewDetails?: () => void;
  
  /**
   * Text to display on the edit button (default: "Edit")
   */
  editButtonText?: string;
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
}) => {
  // State to track the selected color variation
  const [selectedVariationIndex, setSelectedVariationIndex] = useState(0);
  
  // Ensure we have at least one variation
  const hasVariations = colorVariations && colorVariations.length > 0;
  const colors = hasVariations ? colorVariations[selectedVariationIndex - (includeOriginal && selectedVariationIndex > 0 ? 1 : 0)] : [];
  
  // Get the main color from the current variation
  const mainColor = colors.length > 0 ? colors[0] : '#4F46E5';
  
  // Handle color variation selection
  const handleVariationSelect = (index: number) => {
    setSelectedVariationIndex(index);
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
          {hasVariations && colorVariations.map((variation, index) => (
            <button 
              key={`${variation[0]}-${index}`}
              onClick={() => handleVariationSelect(includeOriginal ? index + 1 : index)}
              className={`inline-block w-6 h-6 rounded-full transition-all duration-300 ${
                selectedVariationIndex === (includeOriginal ? index + 1 : index) 
                  ? 'ring-2 ring-indigo-500 ring-offset-2' 
                  : 'hover-scale'
              }`}
              style={{ backgroundColor: variation[0] || '#4F46E5' }}
              title={`Color Palette ${index + 1}`}
            />
          ))}
        </div>
        
        {/* Actions */}
        <div className="mt-4 flex justify-between">
          {onEdit && (
            <button 
              className="text-sm font-medium text-indigo-600 hover:text-indigo-800 transition-colors"
              onClick={() => onEdit(selectedVariationIndex)}
            >
              {editButtonText}
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