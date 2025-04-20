import { renderHook, act, waitFor } from '@testing-library/react';
import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useRateLimitsQuery, useOptimisticRateLimitUpdate } from '../useRateLimitsQuery';
import * as rateLimitService from '../../services/rateLimitService';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import React from 'react';

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

const createWrapper = (queryClient: QueryClient) => {
  return function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    );
  };
};

describe('useRateLimitsQuery', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
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
        wrapper: createWrapper(queryClient)
      });
      
      // Should start with loading state
      expect(result.current.isLoading).toBe(true);
      
      // Should finish loading
      await waitFor(() => !result.current.isLoading);
      expect(result.current.isLoading).toBe(false);
    });

    it('should fetch rate limits on mount', async () => {
      const { result } = renderHook(() => useRateLimitsQuery(), {
        wrapper: createWrapper(queryClient)
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
        wrapper: createWrapper(queryClient)
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
        wrapper: createWrapper(queryClient)
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
        wrapper: createWrapper(queryClient)
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
        wrapper: createWrapper(queryClient)
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
        wrapper: createWrapper(queryClient)
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
        wrapper: createWrapper(queryClient)
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
});

describe('useOptimisticRateLimitUpdate', () => {
  let queryClient: QueryClient;

  beforeEach(() => {
    // Create a new QueryClient for each test
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
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
      wrapper: createWrapper(queryClient)
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
      wrapper: createWrapper(queryClient)
    });
    
    // Decrement the limit (should not throw)
    act(() => {
      result.current('generate_concept', 1);
    });
    
    // No assertion needed, just verifying it doesn't throw
  });
}); 