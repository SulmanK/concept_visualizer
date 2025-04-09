/**
 * API utilities for making requests to the Concept Visualizer backend.
 * This is a simplified version of the original useApi hook that focuses only on
 * providing basic API request utilities without state management, which is now
 * handled by React Query.
 */

import { apiClient } from '../services/apiClient';
import { ApiError } from '../types';

// API base URL is now centralized in apiClient

/**
 * Makes a GET request to the API
 * @param endpoint The API endpoint to call
 * @param headers Optional additional headers
 * @returns Promise resolving to the API response
 */
export const apiGet = async <T>(
  endpoint: string,
  headers?: Record<string, string>
): Promise<T> => {
  try {
    const response = await apiClient.get<T>(endpoint, { headers });
    return response.data;
  } catch (error) {
    console.error(`API GET error (${endpoint}):`, error);
    throw error;
  }
};

/**
 * Makes a POST request to the API
 * @param endpoint The API endpoint to call
 * @param data The data to send in the request body
 * @param headers Optional additional headers
 * @returns Promise resolving to the API response
 */
export const apiPost = async <T>(
  endpoint: string,
  data: any,
  headers?: Record<string, string>
): Promise<T> => {
  try {
    const response = await apiClient.post<T>(endpoint, data, { headers });
    return response.data;
  } catch (error) {
    console.error(`API POST error (${endpoint}):`, error);
    throw error;
  }
};

/**
 * @deprecated Use apiGet or apiPost directly, or use React Query's queryFn/mutationFn with apiClient.
 * This hook is kept for backward compatibility only.
 */
export function useApi() {
  console.warn(
    'useApi is deprecated. Consider using apiGet/apiPost directly or React Query with apiClient instead.'
  );
  
  return {
    request: async <T>(endpoint: string, options: any = {}) => {
      try {
        const { method = 'GET', headers = {}, body } = options;
        
        if (method === 'GET') {
          const data = await apiGet<T>(endpoint, headers);
          return { data, loading: false };
        } else if (method === 'POST') {
          const data = await apiPost<T>(endpoint, body, headers);
          return { data, loading: false };
        } else {
          throw new Error(`Method ${method} not implemented in simplified useApi`);
        }
      } catch (err) {
        const apiError: ApiError = {
          status: 500,
          message: err instanceof Error ? err.message : 'An unexpected error occurred',
        };
        
        return { error: apiError, loading: false };
      }
    },
    
    get: async <T>(endpoint: string, headers?: Record<string, string>) => {
      try {
        const data = await apiGet<T>(endpoint, headers);
        return { data, loading: false };
      } catch (err) {
        const apiError: ApiError = {
          status: 500,
          message: err instanceof Error ? err.message : 'An unexpected error occurred',
        };
        
        return { error: apiError, loading: false };
      }
    },
    
    post: async <T>(endpoint: string, body: any, headers?: Record<string, string>) => {
      try {
        const data = await apiPost<T>(endpoint, body, headers);
        return { data, loading: false };
      } catch (err) {
        const apiError: ApiError = {
          status: 500,
          message: err instanceof Error ? err.message : 'An unexpected error occurred',
        };
        
        return { error: apiError, loading: false };
      }
    },
    
    loading: false,
    error: undefined,
    clearError: () => {},
    authInitialized: true
  };
} 