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
  const { latestResultId } = useTaskContext();
  
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
  const [completedResultId, setCompletedResultId] = useState<string | null>(null);
  
  const queryClient = useQueryClient();
  
  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Effect to detect when task completes and set the result ID for direct fetch
  useEffect(() => {
    if (taskData?.status === 'completed' && taskData.result_id) {
      console.log(`[LandingPage] Task completed with result_id: ${taskData.result_id}`);
      setCompletedResultId(taskData.result_id);
      
      // Force invalidate the cache for this concept to ensure fresh data
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'detail', taskData.result_id]
      });
      
      // Also refresh recent concepts to ensure this appears there
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent'] 
      });
    }
  }, [taskData?.status, taskData?.result_id, queryClient]);
  
  // Directly fetch the concept when we have a result ID
  const { 
    data: directConceptData,
    isLoading: isLoadingDirectConcept
  } = useConceptDetail(
    completedResultId || undefined, // Convert null to undefined for proper type compatibility
    user?.id
  );
  
  // Effect to debug direct concept fetching
  useEffect(() => {
    if (completedResultId) {
      console.log(`[LandingPage] Direct concept fetch state:`, {
        resultId: completedResultId,
        isLoading: isLoadingDirectConcept,
        hasData: !!directConceptData,
        conceptId: directConceptData?.id
      });
    }
  }, [completedResultId, directConceptData, isLoadingDirectConcept]);
  
  // Use the latestResultId from TaskContext as a fallback if we don't get it from taskData
  const effectiveResultId = (taskData?.status === 'completed' && taskData.result_id) 
    ? taskData.result_id 
    : (taskData?.status === 'completed' ? latestResultId : null);
  
  // Map task and mutation state to form status
  const getFormStatus = () => {
    if (isSubmitting) return 'submitting';
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
    if (isSubmitting || (taskData?.status === 'pending' || taskData?.status === 'processing')) {
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
  }, [isSubmitting, taskData, resetGeneration, generateConceptMutation]);
  
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
    
    // Return the first three concepts directly - no transformation needed
    // Our new RecentConceptsSection works directly with Concept data
    return recentConcepts.slice(0, 3);
  };
  
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
          isProcessing={taskData?.status === 'processing'}
          processingMessage={taskData?.status === 'processing' ? 'Generating your concept...' : undefined}
        />
        
        {/* Show results when we have an effective result ID from either source */}
        {(taskData?.status === 'completed' && (taskData.result_id || latestResultId)) && (
          <ResultsSection
            conceptId={taskData.result_id || latestResultId!}
            onEdit={handleEdit}
            onViewDetails={handleViewDetails}
            onColorSelect={handleColorSelect}
            selectedColor={selectedColor}
          />
        )}

        {/* Fallback to direct fetch data if available */}
        {!(taskData?.status === 'completed' && (taskData.result_id || latestResultId)) && completedResultId && directConceptData && (
          <div className="mb-4">
            <p className="text-sm text-indigo-600 mb-2">Using direct concept data:</p>
            <ResultsSection
              conceptId={completedResultId}
              onEdit={handleEdit}
              onViewDetails={handleViewDetails}
              onColorSelect={handleColorSelect}
              selectedColor={selectedColor}
            />
          </div>
        )}

        {/* Debug section to show task data details */}
        {taskData && (
          <div className="p-4 mb-4 bg-blue-50 rounded-lg text-sm border border-blue-200">
            <div>Task ID: {taskData.id || taskData.task_id}</div>
            <div>Task Status: {taskData.status}</div>
            <div>Result ID: {taskData.result_id || 'Not set'}</div>
            <div>Latest Result ID from Context: {latestResultId || 'Not set'}</div>
            <div>Effective Result ID: {effectiveResultId || 'Not available'}</div>
            <div>Error: {taskData.error_message || 'None'}</div>
            <div>Render condition met: {(taskData.status === 'completed' && (taskData.result_id || latestResultId)) ? 'Yes' : 'No'}</div>
            {completedResultId && (
              <>
                <div>Completed Result ID: {completedResultId}</div>
                <div>Direct data loaded: {directConceptData ? 'Yes' : 'No'}</div>
              </>
            )}
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