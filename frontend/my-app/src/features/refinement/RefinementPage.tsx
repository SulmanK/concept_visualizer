import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useRefineConceptMutation } from '../../hooks/useConceptMutations';
import { RefinementHeader } from './components/RefinementHeader';
import { RefinementForm } from './components/RefinementForm';
import { ComparisonView } from './components/ComparisonView';
import { RefinementActions } from './components/RefinementActions';
import { Card } from '../../components/ui/Card';
import { fetchConceptDetail } from '../../services/supabaseClient';
import { useAuth } from '../../contexts/AuthContext';
import { TaskResponse } from '../../types';

/**
 * Main page component for the Concept Refinement feature
 */
export const RefinementPage: React.FC = () => {
  const params = useParams();
  const conceptId = params.conceptId || '';
  const navigate = useNavigate();
  const location = useLocation();
  const searchParams = new URLSearchParams(location.search);
  const colorId = searchParams.get('colorId');
  const { user, isLoading: authLoading } = useAuth();
  
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
      
      // Wait for auth to finish loading
      if (authLoading) {
        return;
      }
      
      if (!user || !user.id) {
        setConceptLoadError('Not authenticated');
        setIsLoadingConcept(false);
        return;
      }
      
      try {
        setIsLoadingConcept(true);
        const conceptData = await fetchConceptDetail(conceptId, user.id);
        
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
              imageUrl: conceptData.image_url || conceptData.base_image_url,
              logoDescription: conceptData.logo_description,
              themeDescription: conceptData.theme_description,
            });
          }
        } else {
          // No color variation specified, use base concept
          setOriginalConcept({
            id: conceptData.id,
            imageUrl: conceptData.image_url || conceptData.base_image_url,
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
  }, [conceptId, colorId, authLoading, user]);
  
  // Use React Query mutation hook for refinement
  const {
    mutate: refineConceptMutation,
    data: taskData,
    isPending,
    isSuccess,
    isError,
    error,
    reset: resetRefinement
  } = useRefineConceptMutation();
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  // Map task and mutation state to form status
  const getFormStatus = () => {
    if (isPending) return 'submitting';
    if (taskData) {
      switch (taskData.status) {
        case 'pending':
        case 'processing':
          return 'processing';
        case 'completed':
          return 'success';
        case 'failed':
          return 'error';
        default:
          return 'idle';
      }
    }
    if (isError) return 'error';
    return 'idle';
  };
  
  // Extract error message from the error object or task
  const getErrorMessage = (): string | null => {
    if (taskData?.status === 'failed') {
      return taskData.error_message || 'Task failed';
    }
    if (!error) return null;
    return error instanceof Error ? error.message : String(error);
  };
  
  const handleRefineConcept = (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[]
  ) => {
    // Refinement is disabled - functionality under construction
    console.log('Refinement functionality is currently disabled (under construction)');
    // Show an alert to inform the user
    alert('The refinement feature is currently under development. Please check back later!');
    
    // Commented out actual refinement code so it doesn't execute yet
    /*
    if (originalConcept?.imageUrl) {
      refineConceptMutation({
        original_image_url: originalConcept.imageUrl,
        refinement_prompt: refinementPrompt,
        logo_description: logoDescription,
        theme_description: themeDescription,
        preserve_aspects: preserveAspects
      });
    }
    */
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
  
  // Check if a completed task result is available
  const showComparisonView = taskData?.status === 'completed' && taskData.result_id;
  
  return (
    <div className="space-y-8 relative">
      {/* Under Construction Watermark */}
      <div className="fixed inset-0 flex items-center justify-center pointer-events-none z-10">
        <div className="transform rotate-[-30deg] bg-red-600/10 text-red-800 font-bold text-6xl p-10 rounded-lg border-4 border-red-600/30 backdrop-blur-sm">
          UNDER CONSTRUCTION
        </div>
      </div>
      
      <RefinementHeader 
        isVariation={!!colorId} 
        variationName={originalConcept.colorVariation?.palette_name} 
      />
      
      {!showComparisonView && (
        <div className="relative">
          <RefinementForm
            originalImageUrl={originalConcept.imageUrl}
            onSubmit={handleRefineConcept}
            status={getFormStatus()}
            error={getErrorMessage()}
            onCancel={handleCancel}
            initialLogoDescription={originalConcept.logoDescription}
            initialThemeDescription={originalConcept.themeDescription}
            colorVariation={originalConcept.colorVariation}
            isProcessing={taskData?.status === 'processing'}
            processingMessage={taskData?.status === 'processing' ? 'Processing your refinement request...' : undefined}
          />
          
          {/* Informational banner */}
          <div className="mt-4 p-4 bg-yellow-50 border border-yellow-300 rounded-lg text-yellow-800 text-center max-w-xl mx-auto">
            <p className="font-medium">
              📝 This feature is currently under development
            </p>
            <p className="text-sm mt-1">
              The refinement functionality is coming soon! You can explore the interface, but submissions are disabled.
            </p>
          </div>
        </div>
      )}
      
      {showComparisonView && taskData.result_id && (
        <div className="mt-8 pt-8 border-t border-dark-200">
          <RefinementActions 
            onReset={handleReset} 
            onCreateNew={() => navigate('/')} 
          />
          
          <ComparisonView
            originalImageUrl={originalConcept.imageUrl}
            refinedConceptId={taskData.result_id}
            onColorSelect={handleColorSelect}
            selectedColor={selectedColor}
          />
        </div>
      )}
    </div>
  );
}; 