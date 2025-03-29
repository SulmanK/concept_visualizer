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

      const response = await post<GenerationResponse>('/concepts/generate', request);

      if (response.error) {
        setGenerationState({
          status: 'error',
          result: null,
          error: response.error.message,
        });
        return;
      }

      if (response.data) {
        setGenerationState({
          status: 'success',
          result: response.data,
          error: null,
        });
      }
    } catch (err) {
      setGenerationState({
        status: 'error',
        result: null,
        error: err instanceof Error ? err.message : 'Failed to generate concept',
      });
    }
  }, [post]);

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