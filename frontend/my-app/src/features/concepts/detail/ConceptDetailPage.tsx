/**
 * Component for displaying detailed concept information
 */

import React, { useState, useEffect, useMemo } from 'react';
import { useParams, Link, useNavigate, useLocation } from 'react-router-dom';
import { ColorPalette } from '../../../components/ui/ColorPalette';
import { ErrorBoundary, OptimizedImage } from '../../../components/ui';
import { ColorVariationData } from '../../../services/supabaseClient';
import { useAuth } from '../../../contexts/AuthContext';
import { ExportOptions } from './components/ExportOptions';
import { useConceptDetail } from '../../../hooks/useConceptQueries';
import { useQueryClient } from '@tanstack/react-query';
import { eventService, AppEvent } from '../../../services/eventService';
import { QueryResultHandler } from '../../../components/common/QueryResultHandler';
import { logger } from '../../../utils/logger';

/**
 * Custom hook to fetch concept detail data
 * The base useConceptDetail hook now handles proper refetching, making this wrapper simpler
 */
function useConceptDetailWithLogging(conceptId: string | undefined, userId: string | undefined) {
  // Use the regular hook which now has optimized refetching behavior
  const result = useConceptDetail(conceptId, userId);
  
  // Just add some debug logging
  useEffect(() => {
    if (conceptId && userId) {
      logger.debug('[useConceptDetailWithLogging] Using concept detail hook for conceptId:', conceptId);
    }
  }, [conceptId, userId]);
  
  return result;
}

/**
 * Component to display concept details
 */
const ConceptDetailContent: React.FC = () => {
  const params = useParams();
  const conceptId = params.conceptId || '';
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const colorId = searchParams.get('colorId');
  const showExport = searchParams.get('showExport') === 'true';
  const { user } = useAuth();
  
  // Use our custom hook with logging
  const { 
    data: concept, 
    isLoading: loading, 
    error: queryError,
    refetch 
  } = useConceptDetailWithLogging(conceptId, user?.id);
  
  const [selectedVariation, setSelectedVariation] = useState<ColorVariationData | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  // Update error state based on query error
  useEffect(() => {
    if (queryError) {
      setError('Error loading concept details');
      logger.error('Error loading concept:', queryError);
    } else if (!conceptId) {
      setError('No concept ID provided');
    } else if (!concept && !loading) {
      setError('Concept not found');
    } else {
      setError(null);
    }
  }, [queryError, concept, conceptId, loading]);
  
  // Set selected variation when concept or colorId changes
  useEffect(() => {
    if (concept && concept.color_variations) {
      // If colorId is provided in the URL, select that specific variation
      if (colorId) {
        const foundVariation = concept.color_variations.find(v => v.id === colorId);
        if (foundVariation) {
          setSelectedVariation(foundVariation);
        } else {
          // If the specified colorId doesn't exist, fall back to the first variation
          setSelectedVariation(concept.color_variations[0]);
        }
      } else {
        // If no colorId specified, use original image (null variation)
        setSelectedVariation(null);
      }
    }
  }, [concept, colorId]);
  
  const errorMessage = error || queryError ? (error || 'Error loading concept details') : null;
  
  // Custom loading component
  const loadingComponent = (
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
  
  // Custom error component
  const errorComponent = (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
        <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
        <p className="text-indigo-600 mb-6">{errorMessage}</p>
        <Link 
          to="/"
          className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full hover:bg-indigo-700 transition-colors"
        >
          Back to Home
        </Link>
      </div>
    </div>
  );
  
  // Use QueryResultHandler for managing loading, error, and data states
  return (
    <QueryResultHandler
      isLoading={loading}
      error={errorMessage}
      data={concept}
      loadingComponent={loadingComponent}
      errorComponent={errorComponent}
      emptyMessage="Concept not found"
    >
      {(concept) => (
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
                className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white rounded-full hover:from-indigo-700 hover:to-indigo-500 transition-colors"
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
                <div className="rounded-lg overflow-hidden shadow-md mb-6 bg-indigo-50 flex items-center justify-center aspect-square p-10">
                  <OptimizedImage 
                    src={selectedVariation ? (selectedVariation.image_url || '') : (concept.image_url || concept.base_image_url || '')} 
                    alt={concept.logo_description}
                    className="max-w-full max-h-full w-auto h-auto object-contain"
                    objectFit="scale-down"
                    lazy={false} // Load this image immediately as it's above the fold
                    backgroundColor="#EEF2FF"
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
                
                {/* Color variations */}
                {concept.color_variations && concept.color_variations.length > 0 && (
                  <div className="mt-4">
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                      {/* Base/original image option */}
                      <div 
                        className={`flex flex-col items-center cursor-pointer rounded-lg overflow-hidden transition-all ${
                          selectedVariation === null ? 'ring-2 ring-indigo-500 shadow-md transform scale-[1.02]' : 'shadow hover:shadow-md'
                        }`}
                        onClick={() => setSelectedVariation(null)}
                      >
                        <div className="w-full aspect-square bg-indigo-50 overflow-hidden flex items-center justify-center p-3">
                          <OptimizedImage
                            src={concept.image_url || concept.base_image_url || ''}
                            alt="Original concept"
                            className="max-w-full max-h-full w-auto h-auto object-contain"
                            objectFit="scale-down"
                            lazy={true}
                            backgroundColor="#EEF2FF"
                          />
                        </div>
                        <span className="text-xs font-semibold text-indigo-800 mt-2 text-center truncate px-2 py-1 bg-indigo-50 rounded-md w-full max-w-[6rem] shadow-sm">Original</span>
                      </div>
                      
                      {/* Variations */}
                      {concept.color_variations.map(variation => (
                        <div 
                          key={variation.id}
                          className={`flex flex-col items-center cursor-pointer rounded-lg overflow-hidden transition-all ${
                            selectedVariation?.id === variation.id ? 'ring-2 ring-indigo-500 shadow-md transform scale-[1.02]' : 'shadow hover:shadow-md'
                          }`}
                          onClick={() => setSelectedVariation(variation)}
                        >
                          <div className="w-full aspect-square bg-indigo-50 overflow-hidden flex items-center justify-center p-3">
                            <OptimizedImage
                              src={variation.image_url || ''}
                              alt={variation.palette_name}
                              className="max-w-full max-h-full w-auto h-auto object-contain"
                              objectFit="scale-down"
                              lazy={true}
                              backgroundColor="#EEF2FF"
                            />
                          </div>
                          <span className="text-xs font-semibold text-indigo-800 mt-2 text-center truncate px-2 py-1 bg-indigo-50 rounded-md w-full max-w-[6rem] shadow-sm">{variation.palette_name}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Export options */}
                {showExport && (
                  <div className="mt-8">
                    <ExportOptions 
                      conceptId={conceptId} 
                      colorVariationId={selectedVariation?.id || null}
                      onSuccess={() => {
                        // Handle successful export
                      }}
                    />
                  </div>
                )}
              </div>
              
              {/* Right column - Details */}
              <div className="w-full md:w-1/2">
                {/* Description */}
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-indigo-700 mb-2">Description</h2>
                  <p className="text-gray-700">{concept.logo_description}</p>
                </div>
                
                {/* Theme Description */}
                {concept.theme_description && (
                  <div className="mb-6">
                    <h2 className="text-lg font-semibold text-indigo-700 mb-2">Theme</h2>
                    <p className="text-gray-700">{concept.theme_description}</p>
                  </div>
                )}
                
                {/* Color Palette */}
                <div className="mb-6">
                  <h2 className="text-lg font-semibold text-indigo-700 mb-4">Color Palette</h2>
                  {selectedVariation ? (
                    <div>
                      <h3 className="text-md font-medium text-indigo-600 mb-3">
                        {selectedVariation.palette_name || 'Variation Colors'}
                      </h3>
                      <div className="space-y-3">
                        {selectedVariation.colors?.length > 0 ? (
                          <>
                            <div className="flex items-center">
                              <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm bg-[{selectedVariation.colors[0] || '#4F46E5'}]"></div>
                              <span className="text-sm text-gray-700 uppercase">Primary: {selectedVariation.colors[0] || 'N/A'}</span>
                            </div>
                            {selectedVariation.colors[1] && (
                              <div className="flex items-center">
                                <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm bg-[{selectedVariation.colors[1] || '#818CF8'}]"></div>
                                <span className="text-sm text-gray-700 uppercase">Secondary: {selectedVariation.colors[1]}</span>
                              </div>
                            )}
                            {selectedVariation.colors[2] && (
                              <div className="flex items-center">
                                <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm bg-[{selectedVariation.colors[2] || '#C7D2FE'}]"></div>
                                <span className="text-sm text-gray-700 uppercase">Accent: {selectedVariation.colors[2]}</span>
                              </div>
                            )}
                            {selectedVariation.colors[3] && (
                              <div className="flex items-center">
                                <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm bg-[{selectedVariation.colors[3] || '#EEF2FF'}]"></div>
                                <span className="text-sm text-gray-700 uppercase">Background: {selectedVariation.colors[3]}</span>
                              </div>
                            )}
                            {selectedVariation.colors[4] && (
                              <div className="flex items-center">
                                <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm bg-[{selectedVariation.colors[4] || '#312E81'}]"></div>
                                <span className="text-sm text-gray-700 uppercase">Text: {selectedVariation.colors[4]}</span>
                              </div>
                            )}
                          </>
                        ) : (
                          <p className="text-gray-600 italic">No color information available</p>
                        )}
                      </div>
                      
                      {/* Full color palette display */}
                      {selectedVariation.colors?.length > 0 && (
                        <div className="mt-4">
                          <ColorPalette colors={selectedVariation.colors} />
                        </div>
                      )}
                    </div>
                  ) : (
                    <div>
                      <h3 className="text-md font-medium text-indigo-600 mb-3">
                        Original Colors
                      </h3>
                      {concept.colors?.length > 0 ? (
                        <>
                          <div className="space-y-3">
                            <div className="flex items-center">
                              <div className="w-6 h-6 mr-3 rounded-md border border-gray-300 shadow-sm bg-[{concept.colors[0] || '#4F46E5'}]"></div>
                              <span className="text-sm text-gray-700 uppercase">Primary: {concept.colors[0] || 'N/A'}</span>
                            </div>
                            {/* Display other colors similar to variation colors */}
                          </div>
                          
                          {/* Full color palette display */}
                          <div className="mt-4">
                            <ColorPalette colors={concept.colors} />
                          </div>
                        </>
                      ) : (
                        <p className="text-gray-600 italic">No color information available</p>
                      )}
                    </div>
                  )}
                </div>
                
                {/* Creation details */}
                <div className="mt-8 p-4 bg-indigo-50 rounded-lg">
                  <h3 className="text-sm font-medium text-indigo-700 mb-2">Created</h3>
                  <p className="text-sm text-gray-600">
                    {concept.created_at 
                      ? new Date(concept.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })
                      : 'Unknown date'}
                  </p>
                </div>
                
                {/* Button to show export options */}
                {!showExport && (
                  <div className="mt-6">
                    <button
                      onClick={() => navigate(`/concept/${conceptId}?showExport=true${colorId ? `&colorId=${colorId}` : ''}`)}
                      className="w-full py-2 bg-indigo-100 text-indigo-700 rounded-md border border-indigo-200 hover:bg-indigo-200 transition-colors"
                    >
                      Export Options
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </QueryResultHandler>
  );
};

/**
 * Wrapper component with ErrorBoundary
 */
export const ConceptDetailPage: React.FC = () => {
  const params = useParams();
  const conceptId = params.conceptId || '';
  
  return (
    <ErrorBoundary
      errorMessage="We're having trouble loading this concept. Please try again or return to the home page."
      canRetry={true}
    >
      <ConceptDetailContent />
    </ErrorBoundary>
  );
}; 