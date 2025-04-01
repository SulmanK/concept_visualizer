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
  
  // Define styles to match the ConceptGenerator.tsx styling
  const titleStyle = {
    fontSize: '2rem',
    fontWeight: 'bold',
    color: '#312e81', // Indigo-900
    marginBottom: '2.5rem'
  };

  const conceptGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '2rem',
    width: '100%'
  };

  const conceptCardStyle = {
    display: 'flex',
    flexDirection: 'column' as const,
    backgroundColor: 'white',
    borderRadius: '0.5rem',
    overflow: 'hidden',
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
    height: '100%',
    border: '1px solid #E5E7EB',
  };

  const conceptHeaderStyle = (color: string = '#4F46E5') => ({
    background: color,
    height: '200px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  });

  const initialsStyle = (color: string = '#4F46E5') => ({
    width: '70px',
    height: '70px',
    backgroundColor: 'white',
    borderRadius: '50%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 'bold',
    fontSize: '20px',
    color: color
  });

  const conceptContentStyle = {
    padding: '1.25rem 1.5rem',
    flexGrow: 1
  };

  const conceptTitleStyle = {
    fontWeight: 600,
    fontSize: '1rem',
    color: '#1E293B',
    marginBottom: '0.5rem'
  };

  const conceptDescriptionStyle = {
    fontSize: '0.875rem',
    color: '#64748B',
    lineHeight: '1.25rem',
    marginBottom: '1rem'
  };

  const colorDotsContainerStyle = {
    display: 'flex',
    gap: '0.5rem',
    marginBottom: '1.5rem'
  };

  const colorDotStyle = (color: string) => ({
    backgroundColor: color,
    width: '1.5rem',
    height: '1.5rem',
    borderRadius: '9999px',
    display: 'inline-block'
  });

  const actionsContainerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    paddingTop: '1rem',
    borderTop: '1px solid #E2E8F0'
  };

  const actionLinkStyle = {
    color: '#6366F1',
    fontWeight: 500,
    fontSize: '0.875rem',
    textDecoration: 'none',
    cursor: 'pointer',
    padding: '0.25rem 0'
  };
  
  // Handle empty state
  if (!loadingConcepts && recentConcepts.length === 0) {
    return (
      <div>
        <h2 style={titleStyle}>Recent Concepts</h2>
        <div className="text-center bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-lg font-semibold text-indigo-800 mb-4">No concepts yet</h3>
          <p className="text-indigo-600 mb-6">
            Your recent concepts will appear here after you generate them.
          </p>
          <Link 
            to="/" 
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold"
          >
            Create New Concept
          </Link>
        </div>
      </div>
    );
  }
  
  // Handle loading state
  if (loadingConcepts) {
    return (
      <div>
        <h2 style={titleStyle}>Recent Concepts</h2>
        <div className="animate-pulse bg-white p-6 rounded-xl shadow-md">
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
      <div>
        <h2 style={titleStyle}>Recent Concepts</h2>
        <div className="text-center bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Error Loading Concepts</h3>
          <p className="text-indigo-600 mb-6">{errorLoadingConcepts}</p>
          <button 
            onClick={() => refreshConcepts()}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Safety check for null concepts array
  if (!recentConcepts || !Array.isArray(recentConcepts)) {
    console.error('recentConcepts is not an array:', recentConcepts);
    return (
      <div>
        <h2 style={titleStyle}>Recent Concepts</h2>
        <div className="text-center bg-white p-6 rounded-xl shadow-md">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Something went wrong</h3>
          <p className="text-indigo-600 mb-6">Invalid data received from the server</p>
          <button 
            onClick={() => refreshConcepts()}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Render the list of concepts
  return (
    <div>
      <h2 style={titleStyle}>Recent Concepts</h2>
      
      <div style={conceptGridStyle}>
        {recentConcepts.map((concept) => {
          // Add a safety check for each concept before rendering
          if (!concept || !concept.base_image_url) {
            console.warn('Invalid concept data:', concept);
            return null;
          }

          // Get main color for concept (use first color or default to indigo)
          const mainColor = concept.color_variations && 
                          concept.color_variations.length > 0 && 
                          concept.color_variations[0].colors ? 
                          concept.color_variations[0].colors[0] : 
                          '#4F46E5';
          
          return (
            <Link 
              key={concept.id} 
              to={`/concepts/${concept.id}`}
              className="block"
              style={{ textDecoration: 'none' }}
            >
              <div style={conceptCardStyle}>
                {/* Header with main color */}
                <div style={conceptHeaderStyle(mainColor)}>
                  {/* Circle with initials */}
                  <div style={initialsStyle(mainColor)}>
                    {getConceptInitials(concept.logo_description)}
                  </div>
                </div>
                
                {/* Content area */}
                <div style={conceptContentStyle}>
                  <h3 style={conceptTitleStyle}>
                    {concept.logo_description}
                  </h3>
                  <p style={conceptDescriptionStyle}>
                    {concept.theme_description || 'No description available'}
                  </p>
                  
                  {/* Color palette preview */}
                  {concept.color_variations && concept.color_variations.length > 0 && concept.color_variations[0].colors && (
                    <div style={colorDotsContainerStyle}>
                      {concept.color_variations[0].colors.slice(0, 3).map((color, index) => (
                        <span 
                          key={index}
                          style={colorDotStyle(color)}
                          title={color}
                        />
                      ))}
                    </div>
                  )}
                  
                  {/* Actions */}
                  <div style={actionsContainerStyle}>
                    <Link 
                      to={`/refine/${concept.id}`}
                      style={actionLinkStyle}
                    >
                      Edit
                    </Link>
                    <Link 
                      to={`/concepts/${concept.id}`}
                      style={actionLinkStyle}
                    >
                      View Details
                    </Link>
                  </div>
                </div>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}; 