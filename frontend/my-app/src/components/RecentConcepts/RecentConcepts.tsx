/**
 * Component for displaying recently generated concepts
 */

import React from 'react';
import { Link } from 'react-router-dom';
import { useConceptContext } from '../../contexts/ConceptContext';
import { ColorPalette } from '../ui/ColorPalette';

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
 * Component to display a list of recently generated concepts
 */
export const RecentConcepts: React.FC = () => {
  const { recentConcepts, loadingConcepts, errorLoadingConcepts, refreshConcepts } = useConceptContext();
  
  // Log component state on each render for debugging
  console.log('RecentConcepts render state:', { 
    conceptsCount: recentConcepts?.length || 0, 
    loading: loadingConcepts, 
    error: errorLoadingConcepts,
    firstConcept: recentConcepts?.length > 0 ? {
      id: recentConcepts[0].id,
      base_image_url: recentConcepts[0].base_image_url,
      has_variations: (recentConcepts[0].color_variations?.length || 0) > 0
    } : null
  });
  
  // Handle empty state
  if (!loadingConcepts && recentConcepts.length === 0) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-6 text-center">
        <h3 className="text-lg font-semibold text-indigo-800 mb-4">No concepts yet</h3>
        <p className="text-indigo-600 mb-6">
          Your recent concepts will appear here after you generate them.
        </p>
        <Link 
          to="/" 
          className="inline-block px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white rounded-full"
        >
          Create New Concept
        </Link>
      </div>
    );
  }
  
  // Handle loading state
  if (loadingConcepts) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-6 text-center">
        <div className="animate-pulse">
          <div className="h-6 bg-indigo-200 rounded mb-4 w-3/4 mx-auto"></div>
          <div className="h-20 bg-indigo-100 rounded mb-4"></div>
          <div className="h-4 bg-indigo-100 rounded mb-2 w-1/2 mx-auto"></div>
          <div className="h-4 bg-indigo-100 rounded w-2/3 mx-auto"></div>
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (errorLoadingConcepts) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-6 text-center">
        <h3 className="text-lg font-semibold text-red-600 mb-4">Error Loading Concepts</h3>
        <p className="text-indigo-600 mb-6">{errorLoadingConcepts}</p>
        <button 
          onClick={() => refreshConcepts()}
          className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
        >
          Try Again
        </button>
      </div>
    );
  }
  
  // Safety check for null concepts array (should never happen, but just in case)
  if (!recentConcepts || !Array.isArray(recentConcepts)) {
    console.error('recentConcepts is not an array:', recentConcepts);
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-6 text-center">
        <h3 className="text-lg font-semibold text-red-600 mb-4">Something went wrong</h3>
        <p className="text-indigo-600 mb-6">Invalid data received from the server</p>
        <button 
          onClick={() => refreshConcepts()}
          className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
        >
          Try Again
        </button>
      </div>
    );
  }
  
  // Render the list of concepts
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-6">
      <h2 className="text-xl font-semibold text-indigo-800 mb-6">
        Recent Concepts
      </h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {recentConcepts.map((concept) => {
          // Add a safety check for each concept before rendering
          if (!concept || !concept.base_image_url) {
            console.warn('Invalid concept data:', concept);
            return null;
          }
          
          return (
            <Link 
              key={concept.id} 
              to={`/concepts/${concept.id}`}
              className="block"
            >
              <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow duration-200">
                {/* Header with gradient */}
                <div className="bg-gradient-to-r from-indigo-600 to-indigo-400 p-4 flex items-center">
                  {/* Circle with initials */}
                  <div className="w-10 h-10 rounded-full bg-white flex items-center justify-center mr-3">
                    <span className="text-indigo-600 font-medium">
                      {getConceptInitials(concept.logo_description)}
                    </span>
                  </div>
                  
                  {/* Concept title */}
                  <div className="text-white truncate">
                    <h3 className="font-medium">{concept.logo_description}</h3>
                  </div>
                </div>
                
                {/* Concept image - with error handling */}
                <div className="p-2">
                  {concept.base_image_url ? (
                    <img
                      src={concept.base_image_url}
                      alt={concept.logo_description}
                      className="w-full h-40 object-contain rounded"
                      onError={(e) => {
                        console.error('Error loading image:', concept.base_image_url);
                        e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YwZjBmZiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5JbWFnZSBOb3QgTG9hZGVkPC90ZXh0Pjwvc3ZnPg=='; // Base64 placeholder image
                      }}
                    />
                  ) : (
                    <div className="w-full h-40 bg-indigo-50 flex items-center justify-center rounded">
                      <span className="text-indigo-300">No image available</span>
                    </div>
                  )}
                </div>
                
                {/* Color palette preview - use the first variation if available */}
                {concept.color_variations && concept.color_variations.length > 0 && concept.color_variations[0].colors && (
                  <div className="p-4 pt-2">
                    <div className="text-xs text-indigo-500 mb-1">
                      {concept.color_variations[0].palette_name || 'Color Palette'}
                    </div>
                    <ColorPalette 
                      palette={{
                        primary: concept.color_variations[0].colors[0] || '#4F46E5',
                        secondary: concept.color_variations[0].colors[1] || '#818CF8',
                        accent: concept.color_variations[0].colors[2] || '#C7D2FE',
                        background: concept.color_variations[0].colors[3] || '#EEF2FF',
                        text: concept.color_variations[0].colors[4] || '#312E81',
                        additionalColors: Array.isArray(concept.color_variations[0].colors.slice(5)) 
                          ? concept.color_variations[0].colors.slice(5) 
                          : []
                      }}
                      showLabels={false}
                      size="sm"
                    />
                  </div>
                )}
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}; 