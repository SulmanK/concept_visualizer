import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useRateLimitsQuery, useOptimisticRateLimitUpdate } from '../useRateLimitsQuery';
import * as rateLimitService from '../../services/rateLimitService';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';
import { apiClient } from '../../services/apiClient';
import { API_ENDPOINTS } from '../../config/apiEndpoints';

// Mock the rateLimitService
vi.mock('../../services/rateLimitService', () => ({
  fetchRateLimits: vi.fn(),
  RateLimitCategory: {
    GENERATE_CONCEPT: 'generate_concept',
    REFINE_CONCEPT: 'refine_concept'
  }
}));

// Mock useErrorHandling
vi.mock('../useErrorHandling', () => ({
  useErrorHandling: () => ({
    handleError: vi.fn(),
    setError: vi.fn(),
    clearError: vi.fn()
  })
}));

// Mock API client
vi.mock('../../services/apiClient', () => ({
  apiClient: {
    get: vi.fn()
  }
}));

// Sample rate limits response for tests
const mockRateLimitsResponse = {
  user_identifier: 'test-user',
  limits: {
    generate_concept: { limit: '10/day', remaining: 8, reset_after: 86400 },
    refine_concept: { limit: '5/day', remaining: 4, reset_after: 86400 },
    store_concept: { limit: '25/day', remaining: 22, reset_after: 86400 },
    get_concepts: { limit: '100/day', remaining: 98, reset_after: 86400 },
    sessions: { limit: '10/hour', remaining: 9, reset_after: 3600 },
    export_action: { limit: '10/day', remaining: 9, reset_after: 86400 }
  },
  default_limits: ['generate_concept', 'refine_concept']
};

describe('useRateLimitsQuery', () => {
  let queryClient: QueryClient;
  
  // Define wrapper component
  function TestWrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  }

  beforeEach(() => {
    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0, // Use gcTime instead of cacheTime which is deprecated
        },
      },
    });

    // Reset the mocks
    vi.resetAllMocks();
    
    // Set up default mock implementation
    vi.mocked(rateLimitService.fetchRateLimits).mockResolvedValue(mockRateLimitsResponse);
  });

  afterEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
  });

  describe('Basic query functionality', () => {
    it('should return loading state initially', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Should start with loading state
      expect(result.current.isLoading).toBe(true);
      
      // Should finish loading
      await waitFor(() => !result.current.isLoading);
      expect(result.current.isLoading).toBe(false);
    });

    it('should fetch rate limits on mount', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Should have called fetchRateLimits
      expect(rateLimitService.fetchRateLimits).toHaveBeenCalledTimes(1);
      expect(rateLimitService.fetchRateLimits).toHaveBeenCalledWith(false);
      
      // Wait for the query to resolve
      await waitFor(() => !result.current.isLoading);
      
      // Should have rate limits data
      expect(result.current.data).toEqual(mockRateLimitsResponse);
    });

    it('should handle fetch error', async () => {
      // Mock an error response
      const testError = new Error('Failed to fetch rate limits');
      vi.mocked(rateLimitService.fetchRateLimits).mockRejectedValueOnce(testError);
      
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Wait for the query to fail
      await waitFor(() => !result.current.isLoading);
      
      // Should have error
      expect(result.current.error).toBeDefined();
      expect(result.current.data).toBeUndefined();
    });
  });

  describe('Refetch functionality', () => {
    it('should refetch rate limits', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Wait for initial fetch to complete
      await waitFor(() => !result.current.isLoading);
      
      // Reset the mock to track next call
      vi.mocked(rateLimitService.fetchRateLimits).mockClear();
      
      // Call refetch
      await act(async () => {
        await result.current.refetch();
      });
      
      // Should have called fetchRateLimits with force=true
      expect(rateLimitService.fetchRateLimits).toHaveBeenCalledTimes(1);
      expect(rateLimitService.fetchRateLimits).toHaveBeenCalledWith(true);
    });

    it('should handle refetch error', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Wait for initial fetch to complete
      await waitFor(() => !result.current.isLoading);
      
      // Mock an error for refetch
      const testError = new Error('Failed to refetch rate limits');
      vi.mocked(rateLimitService.fetchRateLimits).mockRejectedValueOnce(testError);
      
      // Call refetch
      let refetchResult;
      await act(async () => {
        refetchResult = await result.current.refetch();
      });
      
      // Should have returned error info
      expect(refetchResult.isError).toBe(true);
      expect(refetchResult.error).toBe(testError);
    });
  });

  describe('Decrement limit functionality', () => {
    it('should decrement rate limit for a category', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Wait for initial fetch to complete
      await waitFor(() => !result.current.isLoading);
      
      // Verify initial state
      expect(result.current.data?.limits.generate_concept.remaining).toBe(8);
      
      // Decrement the limit
      act(() => {
        result.current.decrementLimit('generate_concept', 1);
      });
      
      // Verify the limit was decremented
      expect(result.current.data?.limits.generate_concept.remaining).toBe(7);
    });

    it('should handle decrement with no initial data', async () => {
      // Mock no data returned
      vi.mocked(rateLimitService.fetchRateLimits).mockResolvedValueOnce(undefined as any);
      
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Wait for initial fetch to complete
      await waitFor(() => !result.current.isLoading);
      
      // Decrement the limit (should not throw)
      act(() => {
        result.current.decrementLimit('generate_concept', 1);
      });
      
      // No assertions needed, just verifying it doesn't throw
    });

    it('should not allow decrementing below zero', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });
      
      // Wait for initial fetch to complete
      await waitFor(() => !result.current.isLoading);
      
      // Decrement the limit by more than the remaining value
      act(() => {
        result.current.decrementLimit('generate_concept', 10);
      });
      
      // Verify the limit doesn't go below zero
      expect(result.current.data?.limits.generate_concept.remaining).toBe(0);
    });
  });

  describe('API functionality', () => {
    it('should fetch rate limits and return the data', async () => {
      // Mock API response
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockRateLimitsResponse });

      // Render the hook with the wrapper
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });

      // Initially, it should be in loading state
      expect(result.current.isLoading).toBe(true);
      expect(result.current.data).toBeUndefined();

      // Wait for the query to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Verify data is returned
      expect(result.current.data).toEqual(mockRateLimitsResponse);
      expect(result.current.error).toBeNull();

      // Verify API was called correctly
      expect(apiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.RATE_LIMITS);
    });

    it('should handle API errors', async () => {
      // Mock API error
      const mockError = new Error('API Error');
      vi.mocked(apiClient.get).mockRejectedValueOnce(mockError);

      // Render the hook with the wrapper
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });

      // Wait for the query to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Verify error is handled
      expect(result.current.error).not.toBeNull();
      expect(result.current.data).toBeUndefined();
    });

    it('should use the provided options', async () => {
      // Mock API response
      vi.mocked(apiClient.get).mockResolvedValueOnce({ data: mockRateLimitsResponse });

      // Custom options
      const options = {
        enabled: false, 
        staleTime: 60000,
        refetchOnWindowFocus: false,
      };

      // Render the hook with options
      renderHook(() => useRateLimitsQuery(options), {
        wrapper: TestWrapper
      });

      // Since enabled is false, API should not be called
      expect(apiClient.get).not.toHaveBeenCalled();
    });

    it('should refetch data when triggered', async () => {
      // Mock API responses
      vi.mocked(apiClient.get)
        .mockResolvedValueOnce({ data: mockRateLimitsResponse })
        .mockResolvedValueOnce({ data: { ...mockRateLimitsResponse, user_identifier: 'updated-user' } });

      // Render the hook with the wrapper
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: TestWrapper
      });

      // Wait for the initial query to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Trigger a refetch
      await result.current.refetch();

      // Verify API was called twice
      expect(apiClient.get).toHaveBeenCalledTimes(2);

      // Verify data was updated
      expect(result.current.data?.user_identifier).toBe('updated-user');
    });
  });
});

describe('useOptimisticRateLimitUpdate', () => {
  let queryClient: QueryClient;
  
  // Define wrapper component
  function TestWrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  }

  beforeEach(() => {
    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
        },
      },
    });

    // Set the initial query data
    queryClient.setQueryData(['rateLimits'], mockRateLimitsResponse);
  });

  afterEach(() => {
    queryClient.clear();
  });

  it('should decrement rate limit optimistically', async () => {
    const { result } = renderHook(() => useOptimisticRateLimitUpdate(), {
      wrapper: TestWrapper
    });
    
    // Verify initial data in the query cache
    const initialData = queryClient.getQueryData(['rateLimits']);
    expect(initialData).toEqual(mockRateLimitsResponse);
    
    // Decrement the limit
    act(() => {
      result.current('generate_concept', 2);
    });
    
    // Verify the optimistic update in the query cache
    const updatedData = queryClient.getQueryData(['rateLimits']) as typeof mockRateLimitsResponse;
    expect(updatedData.limits.generate_concept.remaining).toBe(6);
  });

  it('should handle case with no data in cache', async () => {
    // Clear the query cache
    queryClient.removeQueries({ queryKey: ['rateLimits'] });
    
    const { result } = renderHook(() => useOptimisticRateLimitUpdate(), {
      wrapper: TestWrapper
    });
    
    // Decrement the limit (should not throw)
    act(() => {
      result.current('generate_concept', 1);
    });
    
    // No assertion needed, just verifying it doesn't throw
  });
}); 