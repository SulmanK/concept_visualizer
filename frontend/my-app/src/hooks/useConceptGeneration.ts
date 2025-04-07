/**
 * Hook for generating visual concepts via the API.
 */

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import { 
  GenerationResponse,
  PromptRequest,
  FormStatus
} from '../types';
import { useConceptContext } from '../contexts/ConceptContext';
import { RateLimitError } from '../services/apiClient';
import { useErrorHandling } from './useErrorHandling';
import { eventService, AppEvent } from '../services/eventService';

export interface ConceptGenerationState {
  status: FormStatus;
  result: GenerationResponse | null;
  error: string | null;
}

/**
 * Hook for generating visual concepts based on descriptions
 */
export function useConceptGeneration() {
  const { post, loading, error, clearError } = useApi();
  const { refreshConcepts } = useConceptContext();
  const { handleError: handleApiError } = useErrorHandling();
  
  const [generationState, setGenerationState] = useState<ConceptGenerationState>({
    status: 'idle',
    result: null,
    error: null,
  });

  /**
   * Generate a new concept based on provided descriptions
   */
  const generateConcept = useCallback(async (
    logoDescription: string,
    themeDescription: string
  ) => {
    // Validate inputs
    if (!logoDescription.trim() || !themeDescription.trim()) {
      setGenerationState({
        status: 'error',
        result: null,
        error: 'Please provide both logo and theme descriptions',
      });
      return;
    }

    try {
      setGenerationState({
        status: 'submitting',
        result: null,
        error: null,
      });

      const request: PromptRequest = {
        logo_description: logoDescription,
        theme_description: themeDescription,
      };

      // Use the generate-with-palettes endpoint to get variations
      const response = await post<GenerationResponse>('/concepts/generate-with-palettes', request);

      if (response.error) {
        setGenerationState({
          status: 'error',
          result: null,
          error: response.error.message,
        });
        return;
      }

      if (response.data) {
        // Make sure the variations array is included in the result
        const result = {
          ...response.data,
          variations: response.data.variations || []
        };
        
        console.log('Generated concept with variations:', result);
        
        setGenerationState({
          status: 'success',
          result,
          error: null,
        });
        
        // Refresh the recent concepts list after successful generation
        await refreshConcepts();
        
        // Emit an event to notify other components about the concept creation
        eventService.emit(AppEvent.CONCEPT_CREATED, result);
      }
    } catch (err) {
      console.error('Concept generation error:', err);
      
      // Special handling for rate limit errors
      if (err instanceof RateLimitError) {
        // Use the handleApiError to properly format and categorize the error
        handleApiError(err);
        
        setGenerationState({
          status: 'error',
          result: null,
          error: err.message,
        });
        return;
      }
      
      setGenerationState({
        status: 'error',
        result: null,
        error: err instanceof Error ? err.message : 'Failed to generate concept',
      });
    }
  }, [post, refreshConcepts, handleApiError]);

  /**
   * Reset the generation state
   */
  const resetGeneration = useCallback(() => {
    setGenerationState({
      status: 'idle',
      result: null,
      error: null,
    });
    clearError();
  }, [clearError]);

  return {
    generateConcept,
    resetGeneration,
    ...generationState,
    isLoading: generationState.status === 'submitting',
  };
} 