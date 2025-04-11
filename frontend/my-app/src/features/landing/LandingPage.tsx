import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useGenerateConceptMutation } from '../../hooks/useConceptMutations';
import { useRecentConcepts, useConceptDetail } from '../../hooks/useConceptQueries';
import { useAuth } from '../../contexts/AuthContext';
import { ErrorBoundary } from '../../components/ui';
import { ConceptHeader } from './components/ConceptHeader';
import { HowItWorks } from './components/HowItWorks';
import { ConceptFormSection } from './components/ConceptFormSection';
import { ResultsSection } from './components/ResultsSection';
import { RecentConceptsSection } from './components/RecentConceptsSection';
import { ConceptData } from '../../services/supabaseClient';
import { useQueryClient } from '@tanstack/react-query';
import { TaskResponse } from '../../types';
import { useTaskContext } from '../../contexts/TaskContext';

/**
 * Main landing page content component
 */
const LandingPageContent: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const { 
    activeTaskId,
    isTaskCompleted,
    isTaskPending,
    isTaskProcessing,
    isTaskInitiating,
    latestResultId
  } = useTaskContext();
  
  // Use React Query mutation hook for generation
  const { 
    mutate: generateConceptMutation,
    data: taskData,
    isPending: isSubmitting,
    isSuccess: isTaskStarted,
    isError,
    error,
    reset: resetGeneration
  } = useGenerateConceptMutation();
  
  // Use the React Query hook instead of context
  const { 
    data: recentConcepts = [],
    isLoading: loadingConcepts,
    refetch: refreshConcepts
  } = useRecentConcepts(user?.id, 10);
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  const queryClient = useQueryClient();
  
  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Use the best available result ID for fetching concept data
  const effectiveResultId = 
    // First try task data result ID
    (taskData?.status === 'completed' && taskData.result_id) ? taskData.result_id 
    // Then try latest result ID from context
    : (isTaskCompleted && latestResultId) ? latestResultId 
    // Finally, nothing
    : null;
  
  // Directly fetch the concept when we have a result ID
  const { 
    data: conceptData,
    isLoading: isLoadingConcept
  } = useConceptDetail(
    effectiveResultId || undefined, // Convert null to undefined for proper type compatibility
    user?.id
  );
  
  // Effect to debug concept fetching and cache invalidation
  useEffect(() => {
    if (effectiveResultId) {
      console.log(`[LandingPage] Concept fetch state:`, {
        resultId: effectiveResultId,
        isLoading: isLoadingConcept,
        hasData: !!conceptData,
        conceptId: conceptData?.id,
        timestamp: new Date().toISOString()
      });
      
      // Force invalidate the cache for this concept to ensure fresh data
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'detail', effectiveResultId]
      });
      
      // Also refresh recent concepts to ensure this appears there
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent'] 
      });
    }
  }, [effectiveResultId, conceptData, isLoadingConcept, queryClient]);
  
  // Map task and mutation state to form status
  const getFormStatus = () => {
    if (isSubmitting) return 'submitting';
    if (isTaskInitiating) return 'initiating';
    if (isTaskPending) return 'pending';
    if (isTaskProcessing) return 'processing';
    if (isTaskCompleted) return 'success';
    if (taskData?.status === 'failed') return 'error';
    if (isError) return 'error';
    return 'idle';
  };
  
  // Get the appropriate processing message based on task state
  const getProcessingMessage = (): string | undefined => {
    if (isTaskInitiating) return 'Preparing your request...';
    if (isTaskPending) return 'Request queued...';
    if (isTaskProcessing) return 'Generating your concept...';
    return undefined;
  };
  
  // Extract error message from the error object or task
  const getErrorMessage = (): string | null => {
    if (taskData?.status === 'failed') {
      return taskData.error_message || 'Task failed';
    }
    if (!error) return null;
    return error instanceof Error ? error.message : String(error);
  };
  
  // Steps for how it works section
  const howItWorksSteps = [
    {
      number: 1,
      title: 'Describe Your Vision',
      description: 'Provide detailed descriptions of your logo concept and color preferences.',
    },
    {
      number: 2,
      title: 'AI Generation',
      description: 'Our AI processes your description and creates unique visual concepts.',
    },
    {
      number: 3,
      title: 'Refine & Download',
      description: 'Refine the generated concepts and download your final designs.',
    },
  ];
  
  const handleReset = useCallback(() => {
    console.log('[LandingPage] Resetting concept generation state', {
      timestamp: new Date().toISOString()
    });
    
    // First reset the query client state for the mutation
    queryClient.removeQueries({ queryKey: ['conceptGeneration'] });
    
    // Then reset the local React Query mutation state
    resetGeneration();
    
    // Reset UI state
    setSelectedColor(null);
  }, [resetGeneration, queryClient]);
  
  // Make sure generation can only be triggered when not already pending
  const handleGenerateConcept = useCallback((logoDescription: string, themeDescription: string) => {
    // Safety check to prevent multiple submissions
    if (isSubmitting || isTaskPending || isTaskProcessing) {
      console.warn('[LandingPage] Generation already in progress, ignoring duplicate submission');
      return;
    }
    
    console.log('[LandingPage] Starting concept generation', {
      timestamp: new Date().toISOString(),
      logoDescriptionLength: logoDescription.length,
      themeDescriptionLength: themeDescription.length
    });
    
    // Clear any previous state first
    resetGeneration();
    
    // Make the mutation call
    generateConceptMutation({ 
      logo_description: logoDescription, 
      theme_description: themeDescription 
    });
    
    setSelectedColor(null);
  }, [isSubmitting, isTaskPending, isTaskProcessing, resetGeneration, generateConceptMutation]);
  
  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    
    // Copy color to clipboard
    navigator.clipboard.writeText(color)
      .then(() => {
        // Could show a toast notification here
        console.log(`Copied ${color} to clipboard`);
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  };
  
  const handleEdit = (conceptId: string, variationId?: string | null) => {
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      alert('This is a sample concept. Please generate a real concept to edit it.');
      return;
    }
    
    console.log('handleEdit in LandingPage:', { conceptId, variationId });
    
    // Navigate directly with concept ID and variationId (if available)
    if (variationId) {
      navigate(`/refine/${conceptId}?colorId=${variationId}`);
    } else {
      navigate(`/refine/${conceptId}`);
    }
  };
  
  const handleViewDetails = (conceptId: string, variationId?: string | null) => {
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      alert('This is a sample concept. Please generate a real concept to view details.');
      return;
    }
    
    console.log('handleViewDetails in LandingPage:', { conceptId, variationId });
    
    // Navigate directly with concept ID and variationId (if available)
    if (variationId) {
      navigate(`/concepts/${conceptId}?colorId=${variationId}`);
    } else {
      navigate(`/concepts/${conceptId}`);
    }
  };
  
  const handleGetStarted = () => {
    // Scroll to form
    const formElement = document.getElementById('create-form');
    if (formElement) {
      formElement.scrollIntoView({ behavior: 'smooth' });
    }
  };
  
  // Transform the concept data for the RecentConceptsSection
  const formatConceptsForDisplay = () => {
    if (!recentConcepts || recentConcepts.length === 0) return [];
    
    // Our new RecentConceptsSection works directly with Concept data
    return recentConcepts.slice(0, 3);
  };
  
  // Determine if we should show results
  const shouldShowResults = isTaskCompleted && effectiveResultId;
  
  return (
    <div className="min-h-screen bg-gray-50">
      <ConceptHeader onGetStarted={handleGetStarted} />
      
      <main className="container mx-auto px-4 py-8 space-y-12">
        <HowItWorks steps={howItWorksSteps} onGetStarted={handleGetStarted} />
        
        <ConceptFormSection
          id="create-form"
          onSubmit={handleGenerateConcept}
          onReset={handleReset}
          status={getFormStatus()}
          errorMessage={getErrorMessage()}
          isProcessing={isTaskPending || isTaskProcessing || isTaskInitiating}
          processingMessage={getProcessingMessage()}
        />
        
        {/* Show results using the effectiveResultId and pre-fetched concept data */}
        {shouldShowResults && (
          <ResultsSection
            conceptId={effectiveResultId!}
            conceptData={conceptData}
            isLoading={isLoadingConcept}
            onEdit={handleEdit}
            onViewDetails={handleViewDetails}
            onColorSelect={handleColorSelect}
            selectedColor={selectedColor}
          />
        )}

        {/* Debug section to show task data details */}
        {activeTaskId && (
          <div className="p-4 mb-4 bg-blue-50 rounded-lg text-sm border border-blue-200">
            <div>Task ID: {activeTaskId}</div>
            <div>Task Status: {taskData?.status || (isTaskInitiating ? 'initiating' : 'unknown')}</div>
            <div>Result ID: {taskData?.result_id || 'Not set'}</div>
            <div>Latest Result ID from Context: {latestResultId || 'Not set'}</div>
            <div>Effective Result ID: {effectiveResultId || 'Not available'}</div>
            <div>Error: {taskData?.error_message || 'None'}</div>
            <div>Should Show Results: {shouldShowResults ? 'Yes' : 'No'}</div>
            <div>Concept Data Loaded: {conceptData ? 'Yes' : 'No'}</div>
            <div>Loading Concept: {isLoadingConcept ? 'Yes' : 'No'}</div>
          </div>
        )}
        
        <RecentConceptsSection
          concepts={formatConceptsForDisplay()}
          isLoading={loadingConcepts}
          onEdit={handleEdit}
          onViewDetails={handleViewDetails}
        />
      </main>
    </div>
  );
};

/**
 * Landing page component wrapped in error boundary
 */
export const LandingPage: React.FC = () => {
  return (
    <ErrorBoundary>
      <LandingPageContent />
    </ErrorBoundary>
  );
}; 