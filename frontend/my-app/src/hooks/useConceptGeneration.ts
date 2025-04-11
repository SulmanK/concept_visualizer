/**
 * Hook for generating visual concepts via the API.
 */

import { useState, useCallback } from 'react';
import { 
  GenerationResponse,
  PromptRequest,
  FormStatus
} from '../types';
import { useErrorHandling } from './useErrorHandling';
import { useRateLimitContext } from '../contexts/RateLimitContext';
import { createAsyncErrorHandler } from '../utils/errorUtils';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';
import { apiClient } from '../services/apiClient';

export interface ConceptGenerationState {
  status: FormStatus;
  result: GenerationResponse | null;
  error: string | null;
}

/**
 * Hook for generating visual concepts based on descriptions
 */
export function useConceptGeneration() {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const errorHandler = useErrorHandling();
  const { decrementLimit } = useRateLimitContext();
  
  // Create a standardized async error handler
  const handleAsync = createAsyncErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to generate concept',
    showToast: true
  });
  
  const [generationState, setGenerationState] = useState<ConceptGenerationState>({
    status: 'idle',
    result: null,
    error: null,
  });

  // Create a mutation for generating concepts
  const conceptMutation = useMutation({
    mutationFn: async (data: { logoDescription: string, themeDescription: string }) => {
      const request: PromptRequest = {
        logo_description: data.logoDescription,
        theme_description: data.themeDescription,
      };

      // Make the API call using apiClient
      const response = await apiClient.post<GenerationResponse>('/concepts/generate-with-palettes', request);
      
      // Make sure the variations array is included in the result
      return {
        ...response.data,
        variations: response.data.variations || []
      };
    },
    onMutate: () => {
      // Set submitting state
      setGenerationState({
        status: 'submitting',
        result: null,
        error: null,
      });
      
      // Apply optimistic update BEFORE making the API call
      // This immediately decrements the count in the UI
      decrementLimit('generate_concept');
    },
    onSuccess: (result) => {
      console.log('Generated concept with variations:', result);
      
      setGenerationState({
        status: 'success',
        result,
        error: null,
      });
      
      // Invalidate the recent concepts query
      queryClient.invalidateQueries({ 
        queryKey: ['concepts', 'recent', user?.id] 
      });
      
      // Also invalidate any specific concept query if needed
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
      setGenerationState({
        status: 'error',
        result: null,
        error: error instanceof Error ? error.message : 'Failed to generate concept',
      });
      
      // Let the error handler display the error
      errorHandler.handleError(error);
    }
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

    // Run the mutation
    conceptMutation.mutate({ logoDescription, themeDescription });
  }, [conceptMutation]);

  /**
   * Reset the generation state
   */
  const resetGeneration = useCallback(() => {
    setGenerationState({
      status: 'idle',
      result: null,
      error: null,
    });
    errorHandler.clearError();
  }, [errorHandler]);

  return {
    generateConcept,
    resetGeneration,
    ...generationState,
    isLoading: generationState.status === 'submitting',
  };
} 