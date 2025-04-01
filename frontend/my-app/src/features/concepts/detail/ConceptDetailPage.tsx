/**
 * Component for displaying detailed concept information
 */

import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { ColorPalette } from '../../../components/ui/ColorPalette';
import { fetchConceptDetail, ConceptData, ColorVariationData } from '../../../services/supabaseClient';
import { getSessionId } from '../../../services/sessionManager';

/**
 * Component to display concept details
 */
export const ConceptDetailPage: React.FC = () => {
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
            onClick={() => navigate(`/refine/${conceptId}`)}
            className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white rounded-full"
          >
            Refine This Concept
          </button>
        </div>
        
        {/* Title */}
        <h1 className="text-2xl font-bold text-indigo-800 mb-8">
          Concept
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
            
            {/* Divider with label */}
            <div className="relative mb-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-indigo-200"></div>
              </div>
              <div className="relative flex justify-center">
                <span className="bg-white px-3 text-indigo-600 text-sm font-medium">Color Variations</span>
              </div>
            </div>
            
            {/* Variations thumbnails */}
            {concept.color_variations && concept.color_variations.length > 0 && (
              <div>
                <h3 className="text-md font-semibold text-indigo-700 mb-4">
                  Select a Color Palette ({concept.color_variations.length} options)
                </h3>
                <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4 mb-6">
                  {/* Base image thumbnail */}
                  <div className="flex flex-col items-center">
                    <button 
                      onClick={() => setSelectedVariation(null)}
                      className={`w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 border-3 ${!selectedVariation ? 'border-indigo-600 ring-2 ring-indigo-300' : 'border-transparent'} hover:shadow-lg transition duration-200 ease-in-out transform hover:scale-105`}
                      title="Original image without color transformation"
                    >
                      <img 
                        src={concept.base_image_url} 
                        alt="Original" 
                        className="w-full h-full object-cover"
                      />
                    </button>
                    <span className="text-xs font-medium text-indigo-800 mt-2 text-center bg-indigo-50 px-2 py-1 rounded-md w-full">Original</span>
                  </div>
                  
                  {/* Variation thumbnails */}
                  {concept.color_variations.map((variation) => (
                    <div key={variation.id} className="flex flex-col items-center">
                      <button
                        onClick={() => setSelectedVariation(variation)}
                        className={`w-20 h-20 rounded-lg overflow-hidden flex-shrink-0 border-3 ${selectedVariation?.id === variation.id ? 'border-indigo-600 ring-2 ring-indigo-300' : 'border-transparent'} hover:shadow-lg transition duration-200 ease-in-out transform hover:scale-105`}
                        title={variation.palette_name}
                      >
                        <img 
                          src={variation.image_url} 
                          alt={variation.palette_name} 
                          className="w-full h-full object-cover"
                        />
                      </button>
                      <span className="text-xs font-medium text-indigo-800 mt-2 text-center truncate px-1 py-1 bg-indigo-50 rounded-md w-full max-w-[6rem]">{variation.palette_name}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Right column - Details */}
          <div className="w-full md:w-1/2">
            {/* Concept descriptions */}
            <div className="mb-8 bg-white rounded-xl shadow-sm p-5 border border-indigo-100">
              <h3 className="text-lg font-semibold text-indigo-800 mb-4">Concept Information</h3>
              
              <div className="mb-4">
                <div className="text-indigo-800 font-medium mb-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                  </svg>
                  Logo Description
                </div>
                <p className="text-gray-700 bg-indigo-50 p-3 rounded-md leading-relaxed">{concept.logo_description}</p>
              </div>
              
              <div>
                <div className="text-indigo-800 font-medium mb-2 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M4 2a2 2 0 00-2 2v11a3 3 0 106 0V4a2 2 0 00-2-2H4zm1 14a1 1 0 100-2 1 1 0 000 2zm5-1.757l4.9-4.9a2 2 0 000-2.828L13.485 5.1a2 2 0 00-2.828 0L10 5.757v8.486zM16 18H9.071l6-6H16a2 2 0 012 2v2a2 2 0 01-2 2z" clipRule="evenodd" />
                  </svg>
                  Theme Description
                </div>
                <p className="text-gray-700 bg-indigo-50 p-3 rounded-md leading-relaxed">{concept.theme_description}</p>
              </div>
            </div>
            
            {/* Selected color palette */}
            {selectedVariation ? (
              <div className="mb-6 bg-white rounded-xl shadow-sm p-4 border border-indigo-100">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-indigo-800">
                    {selectedVariation.palette_name}
                  </h3>
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-800 text-sm font-medium rounded-full flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Selected
                  </span>
                </div>
                <div className="mb-4">
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
                    className="mb-3"
                  />
                  
                  {/* Color hex codes */}
                  <div className="grid grid-cols-2 gap-2 mt-4 text-xs">
                    <div className="flex items-center">
                      <div className="w-4 h-4 mr-2 rounded-full" style={{ backgroundColor: selectedVariation.colors[0] || '#4F46E5' }}></div>
                      <span className="font-mono">Primary: {selectedVariation.colors[0] || '#4F46E5'}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 mr-2 rounded-full" style={{ backgroundColor: selectedVariation.colors[1] || '#818CF8' }}></div>
                      <span className="font-mono">Secondary: {selectedVariation.colors[1] || '#818CF8'}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 mr-2 rounded-full" style={{ backgroundColor: selectedVariation.colors[2] || '#C7D2FE' }}></div>
                      <span className="font-mono">Accent: {selectedVariation.colors[2] || '#C7D2FE'}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 mr-2 rounded-full" style={{ backgroundColor: selectedVariation.colors[3] || '#EEF2FF' }}></div>
                      <span className="font-mono">Background: {selectedVariation.colors[3] || '#EEF2FF'}</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-4 h-4 mr-2 rounded-full" style={{ backgroundColor: selectedVariation.colors[4] || '#312E81' }}></div>
                      <span className="font-mono">Text: {selectedVariation.colors[4] || '#312E81'}</span>
                    </div>
                  </div>
                </div>
                
                {selectedVariation.description && (
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-indigo-700 mb-2">Palette Description</h4>
                    <p className="text-gray-700 p-3 bg-indigo-50 rounded-md leading-relaxed">{selectedVariation.description}</p>
                  </div>
                )}
              </div>
            ) : (
              <div className="mb-6 bg-white rounded-xl shadow-sm p-4 border border-indigo-100">
                <div className="flex justify-between items-center mb-4">
                  <h3 className="text-xl font-semibold text-indigo-800">
                    Original Concept
                  </h3>
                  <span className="px-3 py-1 bg-indigo-100 text-indigo-800 text-sm font-medium rounded-full flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Base Image
                  </span>
                </div>
                <p className="text-gray-700 p-3 bg-indigo-50 rounded-md leading-relaxed">
                  This is the original concept without any color variations applied. Select one of the color variations above to see how different color palettes affect the design.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}; 