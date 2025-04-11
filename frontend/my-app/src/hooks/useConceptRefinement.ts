/**
 * Hook for refining visual concepts via the API.
 */

import { useState, useCallback } from 'react';
import { 
  GenerationResponse,
  RefinementRequest,
  FormStatus
} from '../types';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { useErrorHandling } from './useErrorHandling';
import { useRateLimitContext } from '../contexts/RateLimitContext';

export interface ConceptRefinementState {
  status: FormStatus;
  result: GenerationResponse | null;
  error: string | null;
}

interface RefinementParams {
  originalImageUrl: string;
  refinementPrompt: string;
  logoDescription?: string;
  themeDescription?: string;
  preserveAspects?: string[];
}

/**
 * Hook for refining existing visual concepts
 */
export function useConceptRefinement() {
  const queryClient = useQueryClient();
  const errorHandler = useErrorHandling();
  const { decrementLimit } = useRateLimitContext();
  
  const [refinementState, setRefinementState] = useState<ConceptRefinementState>({
    status: 'idle',
    result: null,
    error: null,
  });

  // Create a mutation for refining concepts
  const refinementMutation = useMutation({
    mutationFn: async (params: RefinementParams) => {
      const request: RefinementRequest = {
        original_image_url: params.originalImageUrl,
        refinement_prompt: params.refinementPrompt,
        logo_description: params.logoDescription,
        theme_description: params.themeDescription,
        preserve_aspects: params.preserveAspects || []
      };

      // Make the API call using apiClient
      const response = await apiClient.post<GenerationResponse>('/concepts/refine', request);
      return response.data;
    },
    onMutate: () => {
      // Set submitting state
      setRefinementState({
        status: 'submitting',
        result: null,
        error: null,
      });
      
      // Apply optimistic update - decrement rate limit
      decrementLimit('refine_concept');
    },
    onSuccess: (result) => {
      setRefinementState({
        status: 'success',
        result,
        error: null,
      });
      
      // Invalidate queries to reflect the new data
      if (result.id) {
        queryClient.invalidateQueries({ 
          queryKey: ['concepts', 'detail', result.id] 
        });
      }
      
      // Also invalidate any other related queries
      queryClient.invalidateQueries({
        queryKey: ['concepts'],
        exact: false
      });
    },
    onError: (error) => {
      setRefinementState({
        status: 'error',
        result: null,
        error: error instanceof Error ? error.message : 'Failed to refine concept',
      });
      
      // Let the error handler display the error
      errorHandler.handleError(error);
    }
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

    // Run the mutation
    refinementMutation.mutate({
      originalImageUrl,
      refinementPrompt,
      logoDescription,
      themeDescription,
      preserveAspects
    });
  }, [refinementMutation]);

  /**
   * Reset the refinement state
   */
  const resetRefinement = useCallback(() => {
    setRefinementState({
      status: 'idle',
      result: null,
      error: null,
    });
  }, []);

  return {
    refineConcept,
    resetRefinement,
    ...refinementState,
    isLoading: refinementState.status === 'submitting',
  };
} 