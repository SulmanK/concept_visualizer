import React, { useState, FormEvent, useEffect, useRef } from 'react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';
import { TextArea } from '../ui/TextArea';
import { Card } from '../ui/Card';
import { LoadingIndicator } from '../ui/LoadingIndicator';
import { ErrorMessage, RateLimitErrorMessage } from '../ui/ErrorMessage';
import { useToast } from '../../hooks/useToast';
import { useErrorHandling, ErrorWithCategory, ErrorCategory } from '../../hooks/useErrorHandling';
import { FormStatus } from '../../types';
import { useTaskContext } from '../../contexts/TaskContext';

export interface ConceptFormProps {
  /**
   * Handle form submission
   */
  onSubmit: (logoDescription: string, themeDescription: string) => void;
  
  /**
   * Form submission status
   */
  status: FormStatus;
  
  /**
   * Error message from submission
   */
  error?: string | null;
  
  /**
   * Reset form and results
   */
  onReset?: () => void;
  
  /**
   * Whether the concept generation is being processed asynchronously
   */
  isProcessing?: boolean;
  
  /**
   * Message to display during processing
   */
  processingMessage?: string;
}

/**
 * Form for submitting concept generation requests
 */
export const ConceptForm: React.FC<ConceptFormProps> = ({
  onSubmit,
  status,
  error,
  onReset,
  isProcessing = false,
  processingMessage = 'Processing your concept generation request...'
}) => {
  const [logoDescription, setLogoDescription] = useState('');
  const [themeDescription, setThemeDescription] = useState('');
  const [validationError, setValidationError] = useState<string | undefined>(undefined);
  const formRef = useRef<HTMLFormElement>(null);
  const toast = useToast();
  const errorHandler = useErrorHandling();
  
  // Get global task status
  const { hasActiveTask, isTaskPending, isTaskProcessing, activeTaskData } = useTaskContext();
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    
    if (validateForm()) {
      onSubmit(logoDescription, themeDescription);
    }
  };
  
  const validateForm = (): boolean => {
    // Check if logo description is empty
    if (!logoDescription.trim()) {
      setValidationError('Please provide a logo description');
      return false;
    }
    
    // Check if theme description is empty
    if (!themeDescription.trim()) {
      setValidationError('Please provide a theme description');
      return false;
    }
    
    // Check minimum length for logo description
    if (logoDescription.trim().length < 5) {
      setValidationError('Logo description must be at least 5 characters');
      return false;
    }
    
    // Check minimum length for theme description
    if (themeDescription.trim().length < 5) {
      setValidationError('Theme description must be at least 5 characters');
      return false;
    }
    
    // No validation errors
    setValidationError(undefined);
    return true;
  };
  
  // Reset the form when status changes to 'success'
  useEffect(() => {
    if (status === 'success' && formRef.current) {
      // Optionally reset the form after successful submission
      // formRef.current.reset();
    }
  }, [status]);
  
  // Handle rate limit errors - removed the direct call that was causing linter errors
  useEffect(() => {
    // Just detect rate limit errors but don't try to call a method that doesn't exist
    if (error && error.includes('rate limit')) {
      // Note: we'd handle this with a rate limit handler if one was available
    }
  }, [error]);
  
  const isSubmitting = status === 'submitting';
  const isSuccess = status === 'success';
  const showProcessing = isProcessing || isTaskPending || isTaskProcessing;
  
  // Check if any task is in progress
  const isTaskInProgress = hasActiveTask || isSubmitting || isSuccess || isProcessing;
  
  // Get active task type for message customization
  const activeTaskType = activeTaskData?.type || '';
  const isActiveTaskGeneration = activeTaskType === 'generate_concept';
  const isActiveTaskRefinement = activeTaskType === 'refine_concept';
  
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
  
  // Create a mock error for the RateLimitErrorMessage when needed
  const createRateLimitError = (): ErrorWithCategory => {
    return {
      message: error || 'Rate limit exceeded',
      category: 'rateLimit' as ErrorCategory,
      details: 'You have reached your usage limit. Please try again later.',
      limit: 10,
      current: 10,
      period: 'hour',
      resetAfterSeconds: 3600
    };
  };
  
  return (
    <div className="max-w-4xl mx-auto">
      {error && !error.includes('rate limit') && (
        <ErrorMessage 
          message={error} 
          className="mb-4"
          onDismiss={() => {
            if (onReset) onReset();
          }}
        />
      )}
      
      {error && error.includes('rate limit') && (
        <RateLimitErrorMessage 
          error={createRateLimitError()}
          className="mb-4" 
          onDismiss={() => {
            if (onReset) onReset();
          }}
        />
      )}
      
      <Card variant="default" className="p-6 shadow-lg bg-white border border-indigo-100 rounded-xl">
        {showProcessing ? (
          <div className="py-8 flex flex-col items-center">
            <LoadingIndicator size="large" className="mb-4" />
            <p className="text-indigo-700 font-medium">{processingMessage}</p>
            <p className="text-sm text-indigo-500 mt-2">
              This might take a minute. Please wait while we process your request.
            </p>
          </div>
        ) : (
          <form ref={formRef} onSubmit={handleSubmit} className="space-y-6">
            {validationError && (
              <ErrorMessage 
                message={validationError} 
                className="mb-4" 
                onDismiss={() => setValidationError(undefined)}
              />
            )}
            
            <TextArea
              label="Logo Description"
              placeholder="Describe the logo you want to create (e.g., A modern tech startup logo with abstract geometric shapes)"
              value={logoDescription}
              onChange={e => setLogoDescription(e.target.value)}
              rows={2}
              disabled={isTaskInProgress}
              fullWidth
              required
              helperText="Must be at least 5 characters"
            />
            
            <TextArea
              label="Theme/Style Description"
              placeholder="Describe the theme or style (e.g., Minimalist corporate design with blue and gray tones)"
              value={themeDescription}
              onChange={e => setThemeDescription(e.target.value)}
              rows={2}
              disabled={isTaskInProgress}
              fullWidth
              required
              helperText="Must be at least 5 characters"
            />
            
            <div className="flex justify-end items-center">
              {isSubmitting && (
                <div className="flex items-center mr-4">
                  <LoadingIndicator size="small" showLabel labelText="Generating concept..." />
                </div>
              )}
              
              {hasActiveTask && !isSubmitting && (
                <div className="flex items-center mr-4">
                  <p className="text-amber-600 text-sm font-medium flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                    {getTaskInProgressMessage()}
                  </p>
                </div>
              )}
              
              <Button
                type="submit"
                disabled={isTaskInProgress}
                variant="primary"
                size="lg"
                className={hasActiveTask ? "opacity-50" : ""}
              >
                {isSubmitting ? 'Please wait...' : 
                 hasActiveTask ? 'Task in progress...' : 
                 'Generate Concept'}
              </Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}; 