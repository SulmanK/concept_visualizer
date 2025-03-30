/**
 * Component for displaying detailed concept information
 */

import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ColorPalette } from '../../components/ui/ColorPalette';
import { fetchConceptDetail, ConceptData, ColorVariationData } from '../../services/supabaseClient';
import { getSessionId } from '../../services/sessionManager';

/**
 * Component to display concept details
 */
export const ConceptDetail: React.FC = () => {
  const { conceptId } = useParams<{ conceptId: string }>();
  const navigate = useNavigate();
  
  const [concept, setConcept] = useState<ConceptData | null>(null);
  const [selectedVariation, setSelectedVariation] = useState<ColorVariationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Load concept details when component mounts
  useEffect(() => {
    const loadConceptDetail = async () => {
      if (!conceptId) {
        setError('No concept ID provided');
        setLoading(false);
        return;
      }
      
      const sessionId = getSessionId();
      if (!sessionId) {
        setError('No session found');
        setLoading(false);
        return;
      }
      
      try {
        setLoading(true);
        setError(null);
        
        const conceptData = await fetchConceptDetail(conceptId, sessionId);
        
        if (!conceptData) {
          setError('Concept not found');
          setLoading(false);
          return;
        }
        
        setConcept(conceptData);
        
        // Set the first variation as selected by default
        if (conceptData.color_variations && conceptData.color_variations.length > 0) {
          setSelectedVariation(conceptData.color_variations[0]);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Error loading concept details');
        setLoading(false);
        console.error('Error loading concept:', err);
      }
    };
    
    loadConceptDetail();
  }, [conceptId]);
  
  // Handle loading state
  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8">
          <div className="animate-pulse">
            <div className="h-8 bg-indigo-200 rounded w-1/3 mb-8"></div>
            <div className="flex flex-col md:flex-row gap-8">
              <div className="w-full md:w-1/2">
                <div className="h-80 bg-indigo-100 rounded-lg mb-4"></div>
              </div>
              <div className="w-full md:w-1/2">
                <div className="h-6 bg-indigo-200 rounded mb-4 w-3/4"></div>
                <div className="h-4 bg-indigo-100 rounded mb-8 w-1/2"></div>
                <div className="h-8 bg-indigo-200 rounded mb-4"></div>
                <div className="flex gap-2 mb-6">
                  {[...Array(5)].map((_, i) => (
                    <div key={i} className="h-10 w-10 bg-indigo-100 rounded"></div>
                  ))}
                </div>
                <div className="h-4 bg-indigo-100 rounded mb-2 w-full"></div>
                <div className="h-4 bg-indigo-100 rounded mb-2 w-full"></div>
                <div className="h-4 bg-indigo-100 rounded w-3/4"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (error) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
          <p className="text-indigo-600 mb-6">{error}</p>
          <Link 
            to="/"
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
          >
            Back to Home
          </Link>
        </div>
      </div>
    );
  }
  
  // Render concept details
  if (!concept) {
    // This should never happen as it would be caught in the error state,
    // but TypeScript needs this check
    return null;
  }
  
  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8">
        {/* Navigation */}
        <div className="flex justify-between items-center mb-8">
          <Link 
            to="/"
            className="text-indigo-600 hover:text-indigo-800 font-medium flex items-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-1" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Home
          </Link>
          
          <button
            onClick={() => navigate('/concepts/refine', { 
              state: { 
                originalImageUrl: concept.base_image_url,
                logoDescription: concept.logo_description,
                themeDescription: concept.theme_description
              } 
            })}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white rounded-full"
          >
            Refine This Concept
          </button>
        </div>
        
        {/* Title */}
        <h1 className="text-2xl font-bold text-indigo-800 mb-8">
          {concept.logo_description}
        </h1>
        
        {/* Concept details */}
        <div className="flex flex-col md:flex-row gap-8">
          {/* Left column - Images */}
          <div className="w-full md:w-1/2">
            {/* Main image - either selected variation or base image */}
            <div className="rounded-lg overflow-hidden shadow-md mb-6">
              <img 
                src={selectedVariation ? selectedVariation.image_url : concept.base_image_url} 
                alt={concept.logo_description}
                className="w-full h-auto object-contain bg-indigo-50"
              />
            </div>
            
            {/* Variations thumbnails */}
            {concept.color_variations && concept.color_variations.length > 0 && (
              <div>
                <h3 className="text-sm text-indigo-500 font-medium mb-2">
                  Color Variations
                </h3>
                <div className="flex gap-2 overflow-x-auto pb-2">
                  {/* Base image thumbnail */}
                  <button 
                    onClick={() => setSelectedVariation(null)}
                    className={`w-16 h-16 rounded overflow-hidden flex-shrink-0 border-2 ${!selectedVariation ? 'border-indigo-600' : 'border-transparent'}`}
                  >
                    <img 
                      src={concept.base_image_url} 
                      alt="Original" 
                      className="w-full h-full object-cover"
                    />
                  </button>
                  
                  {/* Variation thumbnails */}
                  {concept.color_variations.map((variation) => (
                    <button
                      key={variation.id}
                      onClick={() => setSelectedVariation(variation)}
                      className={`w-16 h-16 rounded overflow-hidden flex-shrink-0 border-2 ${selectedVariation?.id === variation.id ? 'border-indigo-600' : 'border-transparent'}`}
                    >
                      <img 
                        src={variation.image_url} 
                        alt={variation.palette_name} 
                        className="w-full h-full object-cover"
                      />
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Right column - Details */}
          <div className="w-full md:w-1/2">
            {/* Concept descriptions */}
            <div className="mb-8">
              <div className="text-indigo-800 font-medium mb-2">Logo Description</div>
              <p className="text-gray-600 mb-4">{concept.logo_description}</p>
              
              <div className="text-indigo-800 font-medium mb-2">Theme Description</div>
              <p className="text-gray-600">{concept.theme_description}</p>
            </div>
            
            {/* Selected color palette */}
            {selectedVariation ? (
              <div className="mb-6">
                <h3 className="text-lg font-medium text-indigo-800 mb-3">
                  {selectedVariation.palette_name}
                </h3>
                <ColorPalette 
                  palette={{
                    primary: selectedVariation.colors[0] || '#4F46E5',
                    secondary: selectedVariation.colors[1] || '#818CF8',
                    accent: selectedVariation.colors[2] || '#C7D2FE',
                    background: selectedVariation.colors[3] || '#EEF2FF',
                    text: selectedVariation.colors[4] || '#312E81',
                    additionalColors: selectedVariation.colors.slice(5) || []
                  }}
                  showLabels={true}
                  size="lg"
                />
                {selectedVariation.description && (
                  <p className="text-gray-600 mt-3">{selectedVariation.description}</p>
                )}
              </div>
            ) : (
              <div className="mb-6">
                <h3 className="text-lg font-medium text-indigo-800 mb-3">
                  Original Concept
                </h3>
                <p className="text-gray-600">
                  This is the original concept without any color variations applied.
                </p>
              </div>
            )}
            
            {/* Creation date */}
            <div className="text-xs text-gray-500">
              Created: {new Date(concept.created_at).toLocaleString()}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}; 