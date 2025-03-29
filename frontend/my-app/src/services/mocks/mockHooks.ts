/**
 * Mock implementations of API hooks for testing.
 * These hooks simulate the behavior of the actual hooks but use the mock API service instead.
 */

import { useState, useCallback } from 'react';
import { 
  FormStatus,
  GenerationResponse,
  PromptRequest,
  RefinementRequest,
  ApiError
} from '../../types';
import { mockApiService } from './mockApiService';

interface MockHookState {
  status: FormStatus;
  result: GenerationResponse | null;
  error: string | null;
}

/**
 * Mock implementation of useApi hook
 */
export function useMockApi() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | undefined>(undefined);
  
  const clearError = useCallback(() => {
    setError(undefined);
  }, []);
  
  const get = useCallback(async <T>(endpoint: string) => {
    setLoading(true);
    setError(undefined);
    
    try {
      // Simulate api delay
      await new Promise(resolve => setTimeout(resolve, 200));
      
      // This is a simplified implementation - in a real mock we would
      // handle different endpoints differently
      setLoading(false);
      return { data: {} as T, loading: false };
    } catch (err) {
      const apiError: ApiError = {
        status: 500,
        message: err instanceof Error ? err.message : 'An unexpected error occurred',
      };
      
      setError(apiError);
      setLoading(false);
      return { error: apiError, loading: false };
    }
  }, []);
  
  const post = useCallback(async <T>(endpoint: string, body: any) => {
    setLoading(true);
    setError(undefined);
    
    try {
      // Route to appropriate mock endpoint based on the endpoint path
      if (endpoint.includes('/concepts/generate')) {
        return await mockApiService.generateConcept(body as PromptRequest);
      } else if (endpoint.includes('/concepts/refine')) {
        return await mockApiService.refineConcept(body as RefinementRequest);
      }
      
      // Default response for unhandled endpoints
      setLoading(false);
      return { data: {} as T, loading: false };
    } catch (err) {
      const apiError: ApiError = {
        status: 500,
        message: err instanceof Error ? err.message : 'An unexpected error occurred',
      };
      
      setError(apiError);
      setLoading(false);
      return { error: apiError, loading: false };
    }
  }, []);
  
  return {
    get,
    post,
    loading,
    error,
    clearError,
    isLoading: loading,
  };
}

/**
 * Mock implementation of useConceptGeneration hook
 */
export function useMockConceptGeneration() {
  const { post, loading, error, clearError } = useMockApi();
  const [state, setState] = useState<MockHookState>({
    status: 'idle',
    result: null,
    error: null,
  });
  
  const generateConcept = useCallback(async (
    logoDescription: string,
    themeDescription: string
  ) => {
    // Validate inputs
    if (!logoDescription.trim() || !themeDescription.trim()) {
      setState({
        status: 'error',
        result: null,
        error: 'Please provide both logo and theme descriptions',
      });
      return;
    }
    
    try {
      setState({
        status: 'submitting',
        result: null,
        error: null,
      });
      
      const request: PromptRequest = {
        logoDescription,
        themeDescription
      };
      
      const response = await post<GenerationResponse>('/concepts/generate', request);
      
      if (response.error) {
        setState({
          status: 'error',
          result: null,
          error: response.error.message,
        });
        return;
      }
      
      if (response.data) {
        setState({
          status: 'success',
          result: response.data,
          error: null,
        });
      }
    } catch (err) {
      setState({
        status: 'error',
        result: null,
        error: err instanceof Error ? err.message : 'Failed to generate concept',
      });
    }
  }, [post]);
  
  const resetGeneration = useCallback(() => {
    setState({
      status: 'idle',
      result: null,
      error: null,
    });
  }, []);
  
  return {
    generateConcept,
    resetGeneration,
    status: state.status,
    result: state.result,
    error: state.error,
    isLoading: loading,
    clearError
  };
}

/**
 * Mock implementation of useConceptRefinement hook
 */
export function useMockConceptRefinement() {
  const { post, loading, error, clearError } = useMockApi();
  const [state, setState] = useState<MockHookState>({
    status: 'idle',
    result: null,
    error: null,
  });
  
  const refineConcept = useCallback(async (
    originalImageUrl: string,
    refinementPrompt: string,
    logoDescription?: string,
    themeDescription?: string,
    preserveAspects: string[] = []
  ) => {
    // Validate inputs
    if (!originalImageUrl || !refinementPrompt.trim()) {
      setState({
        status: 'error',
        result: null,
        error: 'Please provide both an image to refine and refinement instructions',
      });
      return;
    }
    
    try {
      setState({
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
        setState({
          status: 'error',
          result: null,
          error: response.error.message,
        });
        return;
      }
      
      if (response.data) {
        setState({
          status: 'success',
          result: response.data,
          error: null,
        });
      }
    } catch (err) {
      setState({
        status: 'error',
        result: null,
        error: err instanceof Error ? err.message : 'Failed to refine concept',
      });
    }
  }, [post]);
  
  return {
    refineConcept,
    status: state.status,
    result: state.result,
    error: state.error,
    isLoading: loading,
    clearError
  };
} 