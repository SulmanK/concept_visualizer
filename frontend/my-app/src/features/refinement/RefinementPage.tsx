import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useConceptRefinement } from '../../hooks/useConceptRefinement';
import { RefinementHeader } from './components/RefinementHeader';
import { RefinementForm } from './components/RefinementForm';
import { ComparisonView } from './components/ComparisonView';
import { RefinementActions } from './components/RefinementActions';
import { Card } from '../../components/ui/Card';
import { fetchConceptDetail } from '../../services/supabaseClient';
import { getSessionId } from '../../services/sessionManager';

/**
 * Main page component for the Concept Refinement feature
 */
export const RefinementPage: React.FC = () => {
  const { conceptId } = useParams<{ conceptId: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const colorId = searchParams.get('colorId');
  
  const [originalConcept, setOriginalConcept] = useState<any>(null);
  const [isLoadingConcept, setIsLoadingConcept] = useState<boolean>(true);
  const [conceptLoadError, setConceptLoadError] = useState<string | null>(null);
  
  // Load the original concept data
  useEffect(() => {
    const loadConcept = async () => {
      if (!conceptId) {
        setConceptLoadError('No concept ID provided');
        setIsLoadingConcept(false);
        return;
      }
      
      const sessionId = getSessionId();
      if (!sessionId) {
        setConceptLoadError('No session found');
        setIsLoadingConcept(false);
        return;
      }
      
      try {
        setIsLoadingConcept(true);
        const conceptData = await fetchConceptDetail(conceptId, sessionId);
        
        if (!conceptData) {
          setConceptLoadError('Concept not found');
          setIsLoadingConcept(false);
          return;
        }
        
        // If colorId is specified, find the matching color variation
        if (colorId && conceptData.color_variations) {
          const colorVariation = conceptData.color_variations.find(v => v.id === colorId);
          
          if (colorVariation) {
            setOriginalConcept({
              id: conceptData.id,
              imageUrl: colorVariation.image_url,
              logoDescription: conceptData.logo_description,
              themeDescription: conceptData.theme_description,
              colorVariation: colorVariation
            });
          } else {
            // If color variation not found, fall back to base concept
            setOriginalConcept({
              id: conceptData.id,
              imageUrl: conceptData.base_image_url,
              logoDescription: conceptData.logo_description,
              themeDescription: conceptData.theme_description,
            });
          }
        } else {
          // No color variation specified, use base concept
          setOriginalConcept({
            id: conceptData.id,
            imageUrl: conceptData.base_image_url,
            logoDescription: conceptData.logo_description,
            themeDescription: conceptData.theme_description,
          });
        }
        
        setIsLoadingConcept(false);
      } catch (err) {
        setConceptLoadError('Error loading concept');
        setIsLoadingConcept(false);
        console.error('Error loading concept:', err);
      }
    };
    
    loadConcept();
  }, [conceptId, colorId]);
  
  const { 
    refineConcept, 
    resetRefinement, 
    status, 
    result, 
    error,
    isLoading
  } = useConceptRefinement();
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  const handleRefineConcept = (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[]
  ) => {
    if (!originalConcept) return;
    
    refineConcept(
      originalConcept.imageUrl,
      refinementPrompt,
      logoDescription || undefined,
      themeDescription || undefined,
      preserveAspects
    );
    setSelectedColor(null);
  };
  
  const handleReset = () => {
    resetRefinement();
    setSelectedColor(null);
  };
  
  const handleCancel = () => {
    navigate(`/concepts/${conceptId}`);
  };
  
  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    
    // Copy color to clipboard
    navigator.clipboard.writeText(color)
      .then(() => {
        console.log(`Copied ${color} to clipboard`);
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  };
  
  // Loading skeleton for when we're fetching the original concept
  if (isLoadingConcept) {
    return (
      <div className="space-y-8">
        <RefinementHeader />
        <Card isLoading={true} className="max-w-xl mx-auto">
          <div className="h-64"></div>
        </Card>
      </div>
    );
  }
  
  // Error state
  if (conceptLoadError || !originalConcept) {
    return (
      <div className="space-y-8">
        <RefinementHeader />
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
          <p className="text-indigo-600 mb-6">{conceptLoadError || 'Could not load concept'}</p>
          <button
            onClick={() => navigate('/')}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
          >
            Back to Home
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="space-y-8">
      <RefinementHeader 
        isVariation={!!colorId} 
        variationName={originalConcept.colorVariation?.palette_name} 
      />
      
      {!result && (
        <RefinementForm
          originalImageUrl={originalConcept.imageUrl}
          onSubmit={handleRefineConcept}
          status={status}
          error={error}
          onCancel={handleCancel}
          initialLogoDescription={originalConcept.logoDescription}
          initialThemeDescription={originalConcept.themeDescription}
          colorVariation={originalConcept.colorVariation}
        />
      )}
      
      {status === 'success' && result && (
        <div className="mt-8 pt-8 border-t border-dark-200">
          <RefinementActions 
            onReset={handleReset} 
            onCreateNew={() => navigate('/')} 
          />
          
          <ComparisonView 
            originalConcept={originalConcept} 
            refinedConcept={result} 
            onColorSelect={handleColorSelect}
            onRefineRequest={handleReset}
          />
          
          {/* Selected color feedback */}
          {selectedColor && (
            <div className="mt-4 text-center text-sm text-dark-600">
              <span className="bg-dark-100 px-2 py-1 rounded font-mono">
                {selectedColor}
              </span>
              <span className="ml-2">
                copied to clipboard
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 