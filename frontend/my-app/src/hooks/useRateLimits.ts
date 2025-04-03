import { useState, useEffect } from 'react';
import { fetchRateLimits, RateLimitsResponse } from '../services/rateLimitService';

interface UseRateLimitsResult {
  rateLimits: RateLimitsResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Hook for fetching and managing rate limit information
 * @returns Object containing rate limits, loading state, error state, and refetch function
 */
export function useRateLimits(): UseRateLimitsResult {
  const [rateLimits, setRateLimits] = useState<RateLimitsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const data = await fetchRateLimits();
      setRateLimits(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch rate limits');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Optional: Set up periodic refreshing
    const intervalId = setInterval(() => {
      fetchData();
    }, 180000); // Refresh every 3 minutes
    
    return () => clearInterval(intervalId);
  }, []);

  return {
    rateLimits,
    isLoading,
    error,
    refetch: fetchData
  };
} 