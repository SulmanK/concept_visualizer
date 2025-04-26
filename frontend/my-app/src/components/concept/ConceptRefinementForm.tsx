import React, { useState, useRef, useEffect, FormEvent } from "react";
import { Button } from "../ui/Button";
import { TextArea } from "../ui/TextArea";
import { Card } from "../ui/Card";
import { FormStatus } from "../../types/ui.types";
import { Spinner } from "../ui";
import { useTaskContext, useOnTaskCleared } from "../../hooks/useTask";

// Define a refinement method type that was implicitly used
export type RefinementMethod = "both" | "description" | "feedback";

export interface ConceptRefinementFormProps {
  /**
   * Original image URL
   */
  originalImageUrl: string;

  /**
   * Handle form submission
   */
  onSubmit: (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[],
  ) => void;

  /**
   * Form submission status
   */
  status: FormStatus;

  /**
   * Error message from submission
   */
  error?: string | null;

  /**
   * Cancel refinement
   */
  onCancel?: () => void;

  /**
   * Initial logo description
   */
  initialLogoDescription?: string;

  /**
   * Initial theme description
   */
  initialThemeDescription?: string;

  /**
   * Custom placeholder text for refinement prompt
   */
  refinementPlaceholder?: string;

  /**
   * Default preserve aspects to pre-select
   */
  defaultPreserveAspects?: string[];

  /**
   * Whether we're refining a color variation
   */
  isColorVariation?: boolean;

  /**
   * Color information for the current variation
   */
  colorInfo?: {
    colors: string[];
    name: string;
  };

  /**
   * Whether the refinement request is being processed
   */
  isProcessing?: boolean;

  /**
   * Message to display during processing
   */
  processingMessage?: string;
}

/**
 * Form for submitting concept refinement requests
 */
export const ConceptRefinementForm: React.FC<ConceptRefinementFormProps> = ({
  originalImageUrl,
  onSubmit,
  status,
  error,
  onCancel,
  initialLogoDescription = "",
  initialThemeDescription = "",
  refinementPlaceholder = "Describe how you want to refine this concept...",
  defaultPreserveAspects = [],
  isColorVariation = false,
  colorInfo,
  isProcessing = false,
  processingMessage = "Processing your refinement request...",
}) => {
  const [refinementPrompt, setRefinementPrompt] = useState("");
  const [logoDescription, setLogoDescription] = useState(
    initialLogoDescription,
  );
  const [themeDescription, setThemeDescription] = useState(
    initialThemeDescription,
  );
  const [preserveAspects, setPreserveAspects] = useState<string[]>(
    defaultPreserveAspects,
  );
  const [validationError, setValidationError] = useState<string | undefined>(
    undefined,
  );
  const formRef = useRef<HTMLFormElement>(null);

  // Get global task status
  const { hasActiveTask, isTaskPending, isTaskProcessing, activeTaskData } =
    useTaskContext();

  // Use the dedicated selector hook for onTaskCleared
  const onTaskCleared = useOnTaskCleared();

  // Reset form when task is cleared
  useEffect(() => {
    if (!onTaskCleared) {
      console.warn("[ConceptRefinementForm] onTaskCleared is not available");
      return;
    }

    try {
      const unsubscribe = onTaskCleared(() => {
        console.log(
          "[ConceptRefinementForm] Task cleared event received, resetting form",
        );
        setRefinementPrompt("");
        setLogoDescription(initialLogoDescription);
        setThemeDescription(initialThemeDescription);
        setPreserveAspects(defaultPreserveAspects);
        setValidationError(undefined);
        if (formRef.current) {
          formRef.current.reset();
        }
      });

      // Clean up subscription when component unmounts
      return unsubscribe;
    } catch (e) {
      console.error(
        "[ConceptRefinementForm] Error setting up task cleared listener:",
        e,
      );
    }
  }, [
    onTaskCleared,
    initialLogoDescription,
    initialThemeDescription,
    defaultPreserveAspects,
  ]);

  // Update preserve aspects when defaultPreserveAspects changes
  useEffect(() => {
    setPreserveAspects(defaultPreserveAspects);
  }, [defaultPreserveAspects]);

  const aspectOptions = [
    { id: "layout", label: "Layout" },
    { id: "colors", label: "Colors" },
    { id: "style", label: "Style" },
    { id: "symbols", label: "Symbols/Icons" },
    { id: "proportions", label: "Proportions" },
    { id: "color_scheme", label: "Color Scheme" },
  ];

  const showProcessing = isProcessing || isTaskPending || isTaskProcessing;

  // Derive submission status from props
  const isSubmittingForm = status === "submitting";
  const isSuccess = status === "success";

  // Check if any task is in progress
  const isTaskInProgress =
    hasActiveTask || isSubmittingForm || isSuccess || isProcessing;

  // Get active task type for message customization
  const activeTaskType = activeTaskData?.type || "";
  const isActiveTaskGeneration = activeTaskType === "generate_concept";
  const isActiveTaskRefinement = activeTaskType === "refine_concept";

  // Create a more descriptive task message based on the active task type
  const getTaskInProgressMessage = () => {
    if (isActiveTaskGeneration) {
      return "A concept generation task is already in progress";
    } else if (isActiveTaskRefinement) {
      return "A concept refinement task is already in progress";
    } else if (hasActiveTask) {
      return "A task is already in progress";
    }
    return "";
  };

  const validateForm = (): boolean => {
    if (!refinementPrompt.trim()) {
      setValidationError("Please provide refinement instructions");
      return false;
    }

    if (refinementPrompt.length < 5) {
      setValidationError(
        "Refinement instructions must be at least 5 characters",
      );
      return false;
    }

    setValidationError(undefined);
    return true;
  };

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();

    if (validateForm()) {
      onSubmit(
        refinementPrompt,
        logoDescription,
        themeDescription,
        preserveAspects,
      );
    }
  };

  const toggleAspect = (aspectId: string) => {
    setPreserveAspects((prev) =>
      prev.includes(aspectId)
        ? prev.filter((id) => id !== aspectId)
        : [...prev, aspectId],
    );
  };

  return (
    <Card
      variant="gradient"
      className="max-w-xl mx-auto"
      header={
        <h2 className="text-xl font-semibold text-indigo-900">
          Refine Concept
          {isColorVariation && colorInfo && (
            <span className="ml-2 text-sm font-normal text-indigo-600">
              ({colorInfo.name})
            </span>
          )}
        </h2>
      }
    >
      {showProcessing ? (
        <div className="py-8 flex flex-col items-center text-center">
          <Spinner size="lg" className="mb-4" />
          <p className="text-indigo-700 font-medium">{processingMessage}</p>
          <p className="text-sm text-indigo-500 mt-2">
            This might take a minute. Please wait while we process your request.
          </p>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4" ref={formRef}>
          {/* Original image thumbnail */}
          <div className="flex justify-center mb-4">
            <div className="w-40 h-40 border border-indigo-200 rounded-lg overflow-hidden shadow-sm">
              <img
                src={originalImageUrl}
                alt="Original concept"
                className="w-full h-full object-cover"
              />
            </div>
          </div>

          {/* Color palette for variations */}
          {isColorVariation && colorInfo && colorInfo.colors.length > 0 && (
            <div className="mb-4">
              <p className="text-sm font-medium text-indigo-700 mb-2">
                Color Palette
              </p>
              <div className="flex flex-wrap gap-2">
                {colorInfo.colors.map((color, index) => (
                  <div
                    key={index}
                    className="w-8 h-8 rounded-full border border-gray-200"
                    style={{ backgroundColor: color }}
                    title={color}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Refinement instructions */}
          <div>
            <TextArea
              label="Refinement Instructions"
              placeholder={refinementPlaceholder}
              value={refinementPrompt}
              onChange={(e) => setRefinementPrompt(e.target.value)}
              error={validationError}
              fullWidth
              disabled={isTaskInProgress}
              helperText={
                isColorVariation
                  ? "Describe what you want to change while keeping the color scheme (minimum 5 characters)"
                  : "Be specific about what you want to change (minimum 5 characters)"
              }
              rows={3}
            />
          </div>

          {/* Optional: Updated logo description */}
          <div>
            <TextArea
              label="Updated Logo Description (Optional)"
              placeholder="Update the logo description or leave as is..."
              value={logoDescription}
              onChange={(e) => setLogoDescription(e.target.value)}
              fullWidth
              disabled={isTaskInProgress}
              helperText="Leave empty to keep original description"
              rows={2}
            />
          </div>

          {/* Optional: Updated theme description */}
          <div>
            <TextArea
              label="Updated Theme Description (Optional)"
              placeholder="Update the theme description or leave as is..."
              value={themeDescription}
              onChange={(e) => setThemeDescription(e.target.value)}
              fullWidth
              disabled={isTaskInProgress}
              helperText="Leave empty to keep original description"
              rows={2}
            />
          </div>

          {/* Preserve aspects checkboxes */}
          <div>
            <label className="block text-sm font-medium text-indigo-900 mb-2">
              Preserve Aspects (Optional)
            </label>
            <div className="flex flex-wrap gap-2">
              {aspectOptions.map((aspect) => (
                <div
                  key={aspect.id}
                  onClick={() => !isTaskInProgress && toggleAspect(aspect.id)}
                  className={`
                    px-3 py-1 rounded-full text-sm cursor-pointer transition-colors
                    ${
                      preserveAspects.includes(aspect.id)
                        ? "bg-indigo-600 text-white"
                        : "bg-indigo-100 text-indigo-800 hover:bg-indigo-200"
                    }
                    ${isTaskInProgress ? "opacity-50 cursor-not-allowed" : ""}
                  `}
                >
                  {aspect.label}
                </div>
              ))}
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Select aspects of the original design you'd like to preserve
            </p>
          </div>

          {/* Error message */}
          {error && (
            <div
              className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded relative"
              role="alert"
            >
              <strong className="font-bold">Error: </strong>
              <span className="block sm:inline">{error}</span>
            </div>
          )}

          {/* Active task message */}
          {hasActiveTask && !isSubmittingForm && !showProcessing && (
            <div
              className="flex items-center bg-amber-50 border border-amber-200 text-amber-700 px-4 py-3 rounded relative"
              role="alert"
            >
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 mr-2 flex-shrink-0"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
              <span className="block sm:inline font-medium">
                {getTaskInProgressMessage()}
              </span>
            </div>
          )}

          {/* Action buttons */}
          <div className="flex justify-between items-center pt-2">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                size="md"
                onClick={onCancel}
                disabled={isTaskInProgress}
              >
                Cancel
              </Button>
            )}

            <div className="flex items-center ml-auto">
              {isSubmittingForm && (
                <div className="flex items-center mr-4">
                  <Spinner size="sm" className="mr-2" />
                  <span className="text-indigo-600 text-sm">Submitting...</span>
                </div>
              )}

              <Button
                type="submit"
                variant="primary"
                size="lg"
                disabled={isTaskInProgress}
                className={hasActiveTask ? "opacity-50" : ""}
              >
                {isSubmittingForm
                  ? "Please wait..."
                  : hasActiveTask
                  ? "Task in progress..."
                  : "Refine Concept"}
              </Button>
            </div>
          </div>
        </form>
      )}
    </Card>
  );
};

export default ConceptRefinementForm;
