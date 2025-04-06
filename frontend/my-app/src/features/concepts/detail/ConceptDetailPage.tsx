/**
 * Component for displaying detailed concept information
 */

import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import { ColorPalette } from '../../../components/ui/ColorPalette';
import { ErrorBoundary } from '../../../components/ui';
import { fetchConceptDetail, ConceptData, ColorVariationData } from '../../../services/supabaseClient';
import { getSessionId } from '../../../services/sessionManager';
import { ExportOptions } from './components/ExportOptions';

/**
 * Component to display concept details
 */
const ConceptDetailContent: React.FC = () => {
  const { conceptId } = useParams<{ conceptId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const colorId = searchParams.get('colorId');
  const showExport = searchParams.get('showExport') === 'true';
  
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
        
        // If colorId is provided in the URL, select that specific variation
        if (colorId && conceptData.color_variations) {
          const foundVariation = conceptData.color_variations.find(v => v.id === colorId);
          if (foundVariation) {
            setSelectedVariation(foundVariation);
          } else {
            // If the specified colorId doesn't exist, fall back to the first variation
            setSelectedVariation(conceptData.color_variations[0]);
          }
        } else {
          // If no colorId specified, use original image (null variation)
          setSelectedVariation(null);
        }
        
        setLoading(false);
      } catch (err) {
        setError('Error loading concept details');
        setLoading(false);
        console.error('Error loading concept:', err);
      }
    };
    
    loadConceptDetail();
  }, [conceptId, colorId]);
  
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
            onClick={() => {
              if (selectedVariation) {
                navigate(`/refine/${conceptId}?colorId=${selectedVariation.id}`);
              } else {
                navigate(`/refine/${conceptId}`);
              }
            }}
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
                src={selectedVariation ? selectedVariation.image_url : concept.image_url || concept.base_image_url} 
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
                  Select a Color Palette ({concept.color_variations && concept.color_variations.length + 1} options)
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
                        src={concept.image_url || concept.base_image_url} 
                        alt="Original" 
                        className="w-full h-full object-cover"
                      />
                    </button>
                    <span className="text-sm font-semibold text-indigo-800 mt-2 text-center bg-indigo-50 px-2 py-1 rounded-md w-full shadow-sm">Original</span>
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
                      <span className="text-sm font-semibold text-indigo-800 mt-2 text-center truncate px-2 py-1 bg-indigo-50 rounded-md w-full max-w-[6rem] shadow-sm">{variation.palette_name}</span>
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
                
                {/* Visual color palette display */}
                <div className="mb-4 p-3 bg-white rounded-lg border border-indigo-100 shadow-sm">
                  <div className="flex justify-between items-center mb-2">
                    <h4 className="text-sm font-medium text-indigo-700">Color Palette</h4>
                  </div>
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
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 mt-5 p-4 bg-gray-50 rounded-lg border border-indigo-100">
                    <div className="flex items-center">
                      <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm" style={{ backgroundColor: selectedVariation.colors[0] || '#4F46E5' }}></div>
                      <div>
                        <div className="text-xs font-medium text-indigo-700">Primary</div>
                        <div className="font-mono text-sm font-bold">{selectedVariation.colors[0] || '#4F46E5'}</div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm" style={{ backgroundColor: selectedVariation.colors[1] || '#818CF8' }}></div>
                      <div>
                        <div className="text-xs font-medium text-indigo-700">Secondary</div>
                        <div className="font-mono text-sm font-bold">{selectedVariation.colors[1] || '#818CF8'}</div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm" style={{ backgroundColor: selectedVariation.colors[2] || '#C7D2FE' }}></div>
                      <div>
                        <div className="text-xs font-medium text-indigo-700">Accent</div>
                        <div className="font-mono text-sm font-bold">{selectedVariation.colors[2] || '#C7D2FE'}</div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm" style={{ backgroundColor: selectedVariation.colors[3] || '#EEF2FF' }}></div>
                      <div>
                        <div className="text-xs font-medium text-indigo-700">Background</div>
                        <div className="font-mono text-sm font-bold">{selectedVariation.colors[3] || '#EEF2FF'}</div>
                      </div>
                    </div>
                    <div className="flex items-center">
                      <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm" style={{ backgroundColor: selectedVariation.colors[4] || '#312E81' }}></div>
                      <div>
                        <div className="text-xs font-medium text-indigo-700">Text</div>
                        <div className="font-mono text-sm font-bold">{selectedVariation.colors[4] || '#312E81'}</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                {/* Move palette description here, above export options */}
                {selectedVariation.description && (
                  <div className="mt-4 mb-6">
                    <div className="flex items-center mb-2">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-indigo-700 mr-1" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                      </svg>
                      <h4 className="text-sm font-medium text-indigo-700">Palette Description</h4>
                    </div>
                    <p className="text-gray-700 p-4 bg-indigo-50 rounded-md leading-relaxed text-sm border border-indigo-100">{selectedVariation.description}</p>
                  </div>
                )}

                {/* Add export options with improved readability */}
                <div className="mt-6 bg-white rounded-xl shadow-sm border border-indigo-100">
                  <details className="group" open={showExport}>
                    <summary className="p-4 cursor-pointer text-lg font-semibold text-indigo-800 flex items-center hover:bg-indigo-50 transition-colors rounded-t-xl">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 transition-transform group-open:rotate-180" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      Export Options
                    </summary>
                    <div className="p-5 border-t border-indigo-100">
                      <ExportOptions
                        imageUrl={selectedVariation.image_url}
                        conceptTitle={concept.logo_description || 'Concept'}
                        variationName={selectedVariation.palette_name}
                        onDownload={(format, size) => {
                          // Just log the export details, actual download handled by ExportOptions
                          console.log(`Exporting ${selectedVariation.palette_name} variation in ${format} format at ${size} size`);
                          // No need to manually download here anymore
                        }}
                      />
                    </div>
                  </details>
                </div>
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
                <div className="flex items-center mb-2">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 text-indigo-700 mr-1" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                  </svg>
                  <h4 className="text-sm font-medium text-indigo-700">Information</h4>
                </div>
                <p className="text-gray-700 p-4 bg-indigo-50 rounded-md leading-relaxed text-sm border border-indigo-100 mb-5">
                  This is the original concept without any color variations applied. Select one of the color variations above to see how different color palettes affect the design.
                </p>
                
                {/* Add export options for original concept */}
                <div className="mt-6 bg-white rounded-xl shadow-sm border border-indigo-100">
                  <details className="group" open={showExport}>
                    <summary className="p-4 cursor-pointer text-lg font-semibold text-indigo-800 flex items-center hover:bg-indigo-50 transition-colors rounded-t-xl">
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 transition-transform group-open:rotate-180" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                      Export Options
                    </summary>
                    <div className="p-5 border-t border-indigo-100">
                      <ExportOptions
                        imageUrl={concept.image_url || concept.base_image_url}
                        conceptTitle={concept.logo_description || 'Concept'}
                        variationName="Original"
                        onDownload={(format, size) => {
                          // Just log the export details, actual download handled by ExportOptions
                          console.log(`Exporting original concept in ${format} format at ${size} size`);
                          // No need to manually download here anymore
                        }}
                      />
                    </div>
                  </details>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Wrapper component with ErrorBoundary
 */
export const ConceptDetailPage: React.FC = () => {
  return (
    <ErrorBoundary
      errorMessage="We're having trouble loading this concept. Please try again or return to the home page."
      canRetry={true}
    >
      <ConceptDetailContent />
    </ErrorBoundary>
  );
}; 