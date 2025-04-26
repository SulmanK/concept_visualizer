import React, { useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useGenerateConceptMutation } from "../../hooks/useConceptMutations";
import {
  useRecentConcepts,
  useConceptDetail,
} from "../../hooks/useConceptQueries";
import { useAuth } from "../../hooks/useAuth";
import { ErrorBoundary } from "../../components/ui";
import { ConceptHeader } from "./components/ConceptHeader";
import { ConceptFormSection } from "./components/ConceptFormSection";
import { ResultsSection } from "./components/ResultsSection";
import { RecentConceptsSection } from "./components/RecentConceptsSection";
import { useQueryClient } from "@tanstack/react-query";
import { useTaskContext } from "../../hooks/useTask";

/**
 * Main landing page content component
 */
const LandingPageContent: React.FC = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const {
    isTaskCompleted,
    isTaskPending,
    isTaskProcessing,
    isTaskInitiating,
    latestResultId,
    clearActiveTask,
    activeTaskData,
  } = useTaskContext();

  // Use React Query mutation hook for generation
  const {
    mutate: generateConceptMutation,
    data: taskData,
    isPending: isSubmitting,
    isError,
    error,
    reset: resetGeneration,
  } = useGenerateConceptMutation();

  // Use the React Query hook instead of context
  const {
    data: recentConcepts = [],
    isLoading: loadingConcepts,
    refetch: refreshConcepts,
  } = useRecentConcepts(user?.id, 10);

  const queryClient = useQueryClient();

  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Use the best available result ID for fetching concept data
  const effectiveResultId =
    // First try task data result ID
    taskData?.status === "completed" && taskData.result_id
      ? taskData.result_id
      : // Then try latest result ID from context
      isTaskCompleted && latestResultId
      ? latestResultId
      : // Finally, nothing
        null;

  // Directly fetch the concept when we have a result ID
  const { data: conceptData, isLoading: isLoadingConcept } = useConceptDetail(
    effectiveResultId || undefined, // Convert null to undefined for proper type compatibility
    user?.id,
  );

  // Map task and mutation state to form status
  const getFormStatus = () => {
    if (isSubmitting) return "submitting";
    if (isTaskInitiating) return "initiating";
    if (isTaskPending) return "pending";
    if (isTaskProcessing) return "processing";
    if (isTaskCompleted) return "success";
    if (activeTaskData?.status === "failed") return "error";
    if (isError) return "error";
    return "idle";
  };

  // Get the appropriate processing message based on task state
  const getProcessingMessage = (): string | undefined => {
    if (isTaskInitiating) return "Preparing your request...";
    if (isTaskPending) return "Request queued, waiting to start...";
    if (isTaskProcessing) return "Generating your concept design...";
    return undefined;
  };

  // Extract error message from the error object or task
  const getErrorMessage = (): string | null => {
    if (activeTaskData?.status === "failed") {
      return activeTaskData.error_message || "Task failed";
    }
    if (!error) return null;
    return error instanceof Error ? error.message : String(error);
  };

  const handleReset = useCallback(() => {
    // First reset the query client state for the mutation
    queryClient.removeQueries({ queryKey: ["conceptGeneration"] });

    // Then reset the local React Query mutation state
    resetGeneration();
  }, [resetGeneration, queryClient]);

  // Handler for the "Start Over" button
  const handleStartOver = useCallback(() => {
    // Clear the active task from the context
    if (clearActiveTask) {
      clearActiveTask();
    }

    // Reset the generation state
    handleReset();

    // Optionally, scroll to the form
    const formElement = document.getElementById("create-form");
    if (formElement) {
      formElement.scrollIntoView({ behavior: "smooth" });
    }
  }, [clearActiveTask, handleReset]);

  // Make sure generation can only be triggered when not already pending
  const handleGenerateConcept = useCallback(
    (logoDescription: string, themeDescription: string) => {
      // Safety check to prevent multiple submissions
      if (isSubmitting || isTaskPending || isTaskProcessing) {
        return;
      }

      // Clear any previous state first
      resetGeneration();

      // Make the mutation call
      generateConceptMutation({
        logo_description: logoDescription,
        theme_description: themeDescription,
      });
    },
    [
      isSubmitting,
      isTaskPending,
      isTaskProcessing,
      resetGeneration,
      generateConceptMutation,
    ],
  );

  // New handler for exporting selected concept variation
  const handleExportSelected = useCallback(
    (conceptId: string, variationId?: string | null) => {
      // Check if this is a sample concept
      if (conceptId.startsWith("sample-")) {
        alert("Cannot export sample concepts.");
        return;
      }

      // Construct the path to the detail page, including the variationId if present
      const path = variationId
        ? `/concepts/${conceptId}?colorId=${variationId}&showExport=true`
        : `/concepts/${conceptId}?showExport=true`;

      navigate(path);
    },
    [navigate],
  );

  // Keep existing handlers for the RecentConceptsSection
  const handleEdit = (conceptId: string, variationId?: string | null) => {
    // Check if this is a sample concept
    if (conceptId.startsWith("sample-")) {
      alert(
        "This is a sample concept. Please generate a real concept to edit it.",
      );
      return;
    }

    // Navigate directly with concept ID and variationId (if available)
    if (variationId) {
      navigate(`/refine/${conceptId}?colorId=${variationId}`);
    } else {
      navigate(`/refine/${conceptId}`);
    }
  };

  const handleViewDetails = (
    conceptId: string,
    variationId?: string | null,
  ) => {
    // Check if this is a sample concept
    if (conceptId.startsWith("sample-")) {
      alert(
        "This is a sample concept. Please generate a real concept to view details.",
      );
      return;
    }

    // Navigate directly with concept ID and variationId (if available)
    if (variationId) {
      navigate(`/concepts/${conceptId}?colorId=${variationId}`);
    } else {
      navigate(`/concepts/${conceptId}`);
    }
  };

  const handleGetStarted = () => {
    // Scroll to form
    const formElement = document.getElementById("create-form");
    if (formElement) {
      formElement.scrollIntoView({ behavior: "smooth" });
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
    <div className="min-h-screen bg-gradient-to-b from-indigo-50 to-white">
      <ConceptHeader onGetStarted={handleGetStarted} />

      <main className="container mx-auto px-4 py-8 space-y-12">
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
            onExportSelected={handleExportSelected}
            onStartOver={handleStartOver}
          />
        )}

        {/* Show loading skeleton for results section if task completed but concept still loading */}
        {isTaskCompleted &&
          effectiveResultId &&
          isLoadingConcept &&
          !conceptData && (
            <ResultsSection
              conceptId={effectiveResultId}
              conceptData={null}
              isLoading={true}
              onExportSelected={handleExportSelected}
            />
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
