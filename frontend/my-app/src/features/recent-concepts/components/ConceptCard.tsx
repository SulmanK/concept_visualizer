import React from 'react';
import { Link } from 'react-router-dom';
import { ColorPalette } from '../../../components/ui/ColorPalette';
import { ConceptCardProps } from '../types';

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
 * Card component that displays a single concept
 */
export const ConceptCard: React.FC<ConceptCardProps> = ({ concept }) => {
  // Get main color for concept (use first color or default to indigo)
  const mainColor = concept.color_variations && 
                  concept.color_variations.length > 0 && 
                  concept.color_variations[0].colors ? 
                  concept.color_variations[0].colors[0] : 
                  '#4F46E5';
  
  const initials = getConceptInitials(concept.logo_description || '');
  
  return (
    <Link 
      to={`/concepts/${concept.id}`}
      className="block hover-lift hover:no-underline"
    >
      <div className="flex flex-col bg-indigo-50/90 rounded-lg overflow-hidden shadow-sm border border-indigo-100 h-full transition-all duration-300 hover:shadow-md">
        <div 
          className="h-48 flex items-center justify-center"
          style={{ background: mainColor }}
        >
          <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center font-bold text-xl" style={{ color: mainColor }}>
            {initials}
          </div>
        </div>
        
        <div className="p-5 flex-grow">
          <h3 className="font-semibold text-dark-900 mb-2">
            {concept.title || (concept.logo_description ? concept.logo_description.substring(0, 40) + '...' : 'Untitled Concept')}
          </h3>
          
          <p className="text-sm text-dark-600 line-clamp-2 mb-4">
            {concept.description || concept.logo_description || 'No description available'}
          </p>
          
          {concept.color_variations && concept.color_variations.length > 0 && concept.color_variations[0].colors && (
            <ColorPalette 
              colors={concept.color_variations[0].colors.slice(0, 5)} 
              small
            />
          )}
          
          <div className="flex justify-between mt-4 pt-4 border-t border-dark-100">
            <span className="text-indigo-600 text-sm font-medium">View Details</span>
            <span className="text-indigo-600 text-sm font-medium">Edit</span>
          </div>
        </div>
      </div>
    </Link>
  );
}; 