/**
 * Custom hook for making API requests to the Concept Visualizer backend.
 */

import { useState, useCallback, useEffect } from 'react';
import { ApiError, ApiResponse } from '../types';
import { ensureSession } from '../services/sessionManager';

// Use the full backend URL instead of a relative path
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PUT' | 'DELETE';
  headers?: Record<string, string>;
  body?: any;
  withCredentials?: boolean;
}

/**
 * Hook for making API requests with error handling
 */
export function useApi() {
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<ApiError | undefined>(undefined);
  const [sessionInitialized, setSessionInitialized] = useState<boolean>(false);
  
  // Ensure session is initialized
  useEffect(() => {
    const initSession = async () => {
      try {
        await ensureSession();
        setSessionInitialized(true);
      } catch (error) {
        console.error('Error initializing session:', error);
      }
    };
    
    initSession();
  }, []);
  
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
    const { 
      method = 'GET', 
      headers = {}, 
      body,
      withCredentials = true  // Default to true for cookie support
    } = options;
    
    try {
      setLoading(true);
      setError(undefined);
      
      // Ensure endpoint starts with forward slash if not already
      const sanitizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
      const url = `${API_BASE_URL}${sanitizedEndpoint}`;
      
      console.log(`API Request: ${method} ${url}`);
      
      const requestHeaders = {
        'Content-Type': 'application/json',
        ...headers,
      };
      
      const requestOptions: RequestInit = {
        method,
        headers: requestHeaders,
        body: body ? JSON.stringify(body) : undefined,
        credentials: withCredentials ? 'include' : 'same-origin', // Include cookies
      };
      
      console.log('Request options:', {
        method,
        headers: requestHeaders,
        withCredentials,
      });
      
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
        
        console.error('API error:', apiError);
        
        setError(apiError);
        setLoading(false);
        
        return { error: apiError, loading: false };
      }
      
      const data = await response.json();
      
      console.log('API Response:', data);
      
      setLoading(false);
      
      return { data, loading: false };
    } catch (err) {
      console.error('API request failed:', err);
      
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
  const get = useCallback(<T>(
    endpoint: string, 
    headers?: Record<string, string>,
    withCredentials: boolean = true
  ) => {
    return request<T>(endpoint, { method: 'GET', headers, withCredentials });
  }, [request]);
  
  /**
   * POST request helper
   */
  const post = useCallback(<T>(
    endpoint: string,
    body: any,
    headers?: Record<string, string>,
    withCredentials: boolean = true
  ) => {
    return request<T>(endpoint, { method: 'POST', body, headers, withCredentials });
  }, [request]);
  
  return {
    request,
    get,
    post,
    loading,
    error,
    clearError,
    sessionInitialized,
  };
} 