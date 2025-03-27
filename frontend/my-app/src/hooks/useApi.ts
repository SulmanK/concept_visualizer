/**
 * Custom hook for making API requests to the Concept Visualizer backend.
 */

import { useState, useCallback } from 'react';
import { ApiError, ApiResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
}

/**
 * Hook for making API requests with error handling
 */
export function useApi() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | undefined>(undefined);
  
  /**
   * Reset the error state
   */
  const clearError = useCallback(() => {
    setError(undefined);
  }, []);
  
  /**
   * Make a request to the API
   */
  const request = useCallback(async <T>(
    endpoint: string,
    options: RequestOptions = {}
  ): Promise<ApiResponse<T>> => {
    const { method = 'GET', headers = {}, body } = options;
    
    try {
      setLoading(true);
      setError(undefined);
      
      const url = `${API_BASE_URL}${endpoint}`;
      
      const requestHeaders = {
        'Content-Type': 'application/json',
        ...headers,
      };
      
      const requestOptions: RequestInit = {
        method,
        headers: requestHeaders,
        body: body ? JSON.stringify(body) : undefined,
      };
      
      const response = await fetch(url, requestOptions);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({
          message: 'An unexpected error occurred',
        }));
        
        const apiError: ApiError = {
          status: response.status,
          message: errorData.message || 'An unexpected error occurred',
          details: errorData.detail,
        };
        
        setError(apiError);
        setLoading(false);
        
        return { error: apiError, loading: false };
      }
      
      const data = await response.json();
      
      setLoading(false);
      
      return { data, loading: false };
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
  
  /**
   * GET request helper
   */
  const get = useCallback(<T>(endpoint: string, headers?: Record<string, string>) => {
    return request<T>(endpoint, { method: 'GET', headers });
  }, [request]);
  
  /**
   * POST request helper
   */
  const post = useCallback(<T>(
    endpoint: string,
    body: any,
    headers?: Record<string, string>
  ) => {
    return request<T>(endpoint, { method: 'POST', body, headers });
  }, [request]);
  
  return {
    request,
    get,
    post,
    loading,
    error,
    clearError,
  };
} 