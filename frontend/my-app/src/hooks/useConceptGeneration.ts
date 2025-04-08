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
import { useErrorHandling } from './useErrorHandling';
import { useRateLimitContext } from '../contexts/RateLimitContext';
import { createAsyncErrorHandler } from '../utils/errorUtils';
import { useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../contexts/AuthContext';

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

    // Set submitting state
    setGenerationState({
      status: 'submitting',
      result: null,
      error: null,
    });

    // Apply optimistic update BEFORE making the API call
    // This immediately decrements the count in the UI
    decrementLimit('generate_concept');

    // Use our standardized error handler to wrap the API call
    const result = await handleAsync(async () => {
      const request: PromptRequest = {
        logo_description: logoDescription,
        theme_description: themeDescription,
      };

      // Use the generate-with-palettes endpoint to get variations
      const response = await post<GenerationResponse>('/concepts/generate-with-palettes', request);

      if (response.error) {
        throw new Error(response.error.message);
      }

      if (!response.data) {
        throw new Error('No data returned from API');
      }

      // Make sure the variations array is included in the result
      return {
        ...response.data,
        variations: response.data.variations || []
      };
    }, 'concept generation');

    if (result) {
      console.log('Generated concept with variations:', result);
      
      setGenerationState({
        status: 'success',
        result,
        error: null,
      });
      
      // REPLACING EVENT EMISSION WITH DIRECT CACHE INVALIDATION
      // Instead of using events, directly invalidate the concepts cache
      console.log('Directly invalidating concepts query cache');
      
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
    } else {
      // If result is undefined, an error occurred and was handled by handleAsync
      setGenerationState({
        status: 'error',
        result: null,
        error: errorHandler.error?.message || 'Failed to generate concept',
      });
    }
  }, [post, queryClient, user?.id, decrementLimit, handleAsync, errorHandler]);

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
    errorHandler.clearError();
  }, [clearError, errorHandler]);

  return {
    generateConcept,
    resetGeneration,
    ...generationState,
    isLoading: generationState.status === 'submitting',
  };
} 