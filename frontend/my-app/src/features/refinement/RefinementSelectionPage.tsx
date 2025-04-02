import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConceptContext } from '../../contexts/ConceptContext';
import { ConceptData, ColorVariationData } from '../../services/supabaseClient';

/**
 * Page for selecting a concept to refine
 */
export const RefinementSelectionPage: React.FC = () => {
  const navigate = useNavigate();
  const { recentConcepts, loadingConcepts, errorLoadingConcepts, refreshConcepts } = useConceptContext();
  const [expandedConceptId, setExpandedConceptId] = useState<string | null>(null);
  const [selectedVariation, setSelectedVariation] = useState<{
    conceptId: string;
    variationId?: string;
    imageUrl: string;
    isOriginal: boolean;
  } | null>(null);
  
  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Handle selecting a concept to refine
  const handleSelectConcept = (conceptId: string, colorVariationId?: string) => {
    if (colorVariationId) {
      navigate(`/refine/${conceptId}?colorId=${colorVariationId}`);
    } else {
      navigate(`/refine/${conceptId}`);
    }
  };
  
  // Toggle expanded state of a concept to show its variations
  const toggleExpandConcept = (conceptId: string) => {
    setExpandedConceptId(expandedConceptId === conceptId ? null : conceptId);
  };
  
  // Handle selecting a variation or original image
  const handleSelectVariation = (
    conceptId: string, 
    imageUrl: string, 
    isOriginal: boolean, 
    variationId?: string
  ) => {
    setSelectedVariation({
      conceptId,
      variationId,
      imageUrl,
      isOriginal
    });
  };
  
  // Handle refining the selected variation
  const handleRefineSelected = () => {
    if (!selectedVariation) return;
    
    if (selectedVariation.variationId && !selectedVariation.isOriginal) {
      navigate(`/refine/${selectedVariation.conceptId}?colorId=${selectedVariation.variationId}`);
    } else {
      navigate(`/refine/${selectedVariation.conceptId}`);
    }
  };
  
  // Handle loading state
  if (loadingConcepts) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            Select a Concept to Refine
          </h1>
          <p className="text-indigo-600 max-w-2xl mx-auto">
            Choose one of your concepts to refine and improve.
          </p>
        </div>
        
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center" data-testid="loading-skeleton">
          <div className="animate-pulse">
            <div className="h-8 bg-indigo-200 rounded w-1/3 mb-8 mx-auto"></div>
            <div className="grid grid-cols-1 gap-8">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-32 bg-indigo-100 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (errorLoadingConcepts) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            Select a Concept to Refine
          </h1>
        </div>
        
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
          <p className="text-indigo-600 mb-6">{errorLoadingConcepts}</p>
          <button 
            onClick={() => refreshConcepts()}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Handle empty state
  if (!recentConcepts || recentConcepts.length === 0) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            Select a Concept to Refine
          </h1>
        </div>
        
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
          <h2 className="text-xl font-semibold text-indigo-800 mb-4">No Concepts Available</h2>
          <p className="text-indigo-600 mb-6">
            You need to create concepts before you can refine them.
          </p>
          <button
            onClick={() => navigate('/create')}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
          >
            Create New Concept
          </button>
        </div>
      </div>
    );
  }
  
  // Render a concept row with its variations
  const renderConceptRow = (concept: ConceptData) => {
    const isExpanded = expandedConceptId === concept.id;
    const hasVariations = concept.color_variations && concept.color_variations.length > 0;
    const totalVariations = hasVariations ? concept.color_variations!.length + 1 : 1; // +1 for original
    
    // Check if this concept has a selected variation
    const hasSelectedVariation = selectedVariation && selectedVariation.conceptId === concept.id;
    
    // Check if original is selected for this concept
    const isOriginalSelected = hasSelectedVariation && selectedVariation.isOriginal;
    
    return (
      <div key={concept.id} className="mb-6">
        <div 
          className={`bg-white p-4 rounded-lg shadow-sm border border-indigo-100 transition-all ${isExpanded ? 'shadow-md border-indigo-300' : 'hover:shadow-md hover:border-indigo-200'}`}
        >
          {/* Main concept row */}
          <div className="flex items-center cursor-pointer" onClick={() => toggleExpandConcept(concept.id)}>
            <div className="w-24 h-24 flex-shrink-0 rounded-md overflow-hidden border border-indigo-100">
              <img 
                src={concept.base_image_url} 
                alt={concept.logo_description || 'Concept'} 
                className="w-full h-full object-cover"
              />
            </div>
            <div className="ml-6 flex-grow">
              <h3 className="font-semibold text-lg text-indigo-900 mb-1">
                {concept.logo_description}
              </h3>
              <p className="text-sm text-gray-600 mb-2 line-clamp-1">
                {concept.theme_description}
              </p>
              <div className="flex items-center">
                <span className="text-xs font-medium text-indigo-600 mr-2">
                  {totalVariations} {totalVariations === 1 ? 'option' : 'options'}
                </span>
                <div className="flex space-x-1">
                  {/* Original color option */}
                  <div
                    className="w-4 h-4 rounded-full border border-gray-300 flex items-center justify-center bg-white"
                  >
                    <span className="text-[8px] font-bold text-gray-600">O</span>
                  </div>
                  
                  {/* Color variations */}
                  {hasVariations && concept.color_variations?.slice(0, 3).map((variation, idx) => (
                    <div
                      key={idx}
                      className="w-4 h-4 rounded-full"
                      style={{ backgroundColor: variation.colors[0] || '#4F46E5' }}
                    />
                  ))}
                  {hasVariations && concept.color_variations!.length > 3 && (
                    <div className="w-4 h-4 rounded-full bg-indigo-200 flex items-center justify-center text-indigo-600 text-xs font-bold">
                      +{concept.color_variations!.length - 3}
                    </div>
                  )}
                </div>
              </div>
            </div>
            <div className="ml-4">
              <svg 
                xmlns="http://www.w3.org/2000/svg" 
                className={`h-5 w-5 text-indigo-500 transition-transform ${isExpanded ? 'transform rotate-180' : ''}`} 
                viewBox="0 0 20 20" 
                fill="currentColor"
              >
                <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </div>
          </div>
          
          {/* Expanded variations section */}
          {isExpanded && (
            <div className="mt-4 pt-4 border-t border-indigo-100">
              <div className="flex flex-wrap items-center">
                {/* Original image */}
                <div 
                  className={`w-32 h-32 m-2 rounded-md overflow-hidden border-2 cursor-pointer hover:shadow-md transition-all flex flex-col
                    ${isOriginalSelected ? 'border-indigo-600 ring-2 ring-indigo-300' : 'border-indigo-100 hover:border-indigo-300'}`}
                  onClick={() => handleSelectVariation(concept.id, concept.base_image_url, true)}
                >
                  <div className="h-24 overflow-hidden">
                    <img 
                      src={concept.base_image_url} 
                      alt="Original" 
                      className="w-full h-full object-cover" 
                    />
                  </div>
                  <div className="flex-grow bg-indigo-50 flex items-center justify-center text-xs font-medium text-indigo-700 p-1">
                    Original
                  </div>
                </div>
                
                {/* Color variations */}
                {hasVariations && concept.color_variations?.map((variation, idx) => {
                  const isSelected = hasSelectedVariation && 
                                     !selectedVariation.isOriginal && 
                                     selectedVariation.variationId === variation.id;
                  
                  return (
                    <div 
                      key={idx}
                      className={`w-32 h-32 m-2 rounded-md overflow-hidden border-2 cursor-pointer hover:shadow-md transition-all flex flex-col
                        ${isSelected ? 'border-indigo-600 ring-2 ring-indigo-300' : 'border-indigo-100 hover:border-indigo-300'}`}
                      onClick={() => handleSelectVariation(concept.id, variation.image_url, false, variation.id)}
                    >
                      <div className="h-24 overflow-hidden">
                        <img 
                          src={variation.image_url} 
                          alt={variation.palette_name || `Variation ${idx + 1}`} 
                          className="w-full h-full object-cover" 
                        />
                      </div>
                      <div 
                        className="flex-grow flex items-center justify-center text-xs font-medium text-white p-1"
                        style={{ backgroundColor: variation.colors[0] || '#4F46E5' }}
                      >
                        <div className="truncate max-w-full px-1">{variation.palette_name || `Variation ${idx + 1}`}</div>
                      </div>
                    </div>
                  );
                })}
              </div>
              
              <div className="mt-4 flex justify-end space-x-3">
                {hasSelectedVariation && selectedVariation.conceptId === concept.id && (
                  <button 
                    onClick={handleRefineSelected}
                    className="px-4 py-2 bg-gradient-to-r from-indigo-600 to-indigo-400 text-white rounded-full text-sm shadow-md hover:shadow-lg transform transition-transform hover:scale-105"
                  >
                    Refine Selected
                  </button>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };
  
  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-indigo-900 mb-2">
          Select a Concept to Refine
        </h1>
        <p className="text-indigo-600 max-w-2xl mx-auto">
          Choose one of your concepts to refine and improve. Click on a concept to see all available options.
        </p>
      </div>
      
      <div className="bg-gradient-to-b from-indigo-50 to-white rounded-xl shadow-md p-6 mb-8">
        <div className="mb-6 pb-4 border-b border-indigo-100 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-indigo-600 mr-2" viewBox="0 0 20 20" fill="currentColor">
            <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
          </svg>
          <span className="font-medium text-indigo-900">Click on a concept to see its color variations and select one to refine</span>
        </div>
        
        {recentConcepts.map(renderConceptRow)}
      </div>
    </div>
  );
}; 