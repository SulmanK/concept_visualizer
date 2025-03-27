/**
 * Hook for refining visual concepts via the API.
 */

import { useState, useCallback } from 'react';
import { useApi } from './useApi';
import { 
  GenerationResponse,
  RefinementRequest,
  FormStatus
} from '../types';

export interface ConceptRefinementState {
  status: FormStatus;
  result: GenerationResponse | null;
  error: string | null;
}

/**
 * Hook for refining existing visual concepts
 */
export function useConceptRefinement() {
  const { post, loading, error, clearError } = useApi();
  const [refinementState, setRefinementState] = useState<ConceptRefinementState>({
    status: 'idle',
    result: null,
    error: null,
  });

  /**
   * Refine an existing concept based on provided instructions
   */
  const refineConcept = useCallback(async (
    originalImageUrl: string,
    refinementPrompt: string,
    logoDescription?: string,
    themeDescription?: string,
    preserveAspects: string[] = []
  ) => {
    // Validate inputs
    if (!originalImageUrl || !refinementPrompt.trim()) {
      setRefinementState({
        status: 'error',
        result: null,
        error: 'Please provide both an image to refine and refinement instructions',
      });
      return;
    }

    try {
      setRefinementState({
        status: 'submitting',
        result: null,
        error: null,
      });

      const request: RefinementRequest = {
        originalImageUrl,
        refinementPrompt,
        logoDescription,
        themeDescription,
        preserveAspects
      };

      const response = await post<GenerationResponse>('/concepts/refine', request);

      if (response.error) {
        setRefinementState({
          status: 'error',
          result: null,
          error: response.error.message,
        });
        return;
      }

      if (response.data) {
        setRefinementState({
          status: 'success',
          result: response.data,
          error: null,
        });
      }
    } catch (err) {
      setRefinementState({
        status: 'error',
        result: null,
        error: err instanceof Error ? err.message : 'Failed to refine concept',
      });
    }
  }, [post]);

  /**
   * Reset the refinement state
   */
  const resetRefinement = useCallback(() => {
    setRefinementState({
      status: 'idle',
      result: null,
      error: null,
    });
    clearError();
  }, [clearError]);

  return {
    refineConcept,
    resetRefinement,
    ...refinementState,
    isLoading: refinementState.status === 'submitting',
  };
} 