import React from 'react';
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
   */
  colors: string[];
  
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
  colors,
  gradient = { from: 'blue-400', to: 'indigo-500' },
  initials,
  onEdit,
  onViewDetails,
}) => {
  return (
    <div className="overflow-hidden rounded-lg shadow-modern border border-indigo-100 bg-white/90 backdrop-blur-sm hover-lift hover:shadow-modern-hover transition-all duration-300 scale-in">
      {/* Gradient header with initials */}
      <div className={`h-40 bg-gradient-to-r from-${gradient.from} to-${gradient.to} p-4 flex items-center justify-center`}>
        <div className="w-20 h-20 bg-white rounded-full flex items-center justify-center font-bold text-indigo-600 text-xl shadow-lg">
          {initials}
        </div>
      </div>
      
      {/* Content area */}
      <div className="p-4">
        <h4 className="font-semibold text-indigo-900">{title}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
        
        {/* Color palette */}
        <div className="mt-3 flex space-x-2">
          {colors.map((color, index) => (
            <span 
              key={`${color}-${index}`}
              className="inline-block w-6 h-6 rounded-full hover-scale" 
              style={{ backgroundColor: color }}
              title={color}
            />
          ))}
        </div>
        
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