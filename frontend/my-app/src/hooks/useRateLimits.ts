import { useState, useEffect, useCallback, useRef } from 'react';
import { 
  fetchRateLimits, 
  RateLimitsResponse, 
  RateLimitCategory,
  decrementRateLimit,
  getRateLimitInfoForCategory
} from '../services/rateLimitService';
import { eventService, AppEvent } from '../services/eventService';

interface UseRateLimitsResult {
  rateLimits: RateLimitsResponse | null;
  isLoading: boolean;
  error: string | null;
  refetch: (forceRefresh?: boolean) => Promise<void>;
  /**
   * Immediately decrement a rate limit category for optimistic UI updates
   * @param category Rate limit category to decrement
   * @param amount Amount to decrement (default: 1)
   */
  decrementLimit: (category: RateLimitCategory, amount?: number) => void;
}

/**
 * Hook for fetching and managing rate limit information
 * @returns Object containing rate limits, loading state, error state, and functions to interact with rate limits
 */
export function useRateLimits(): UseRateLimitsResult {
  const [rateLimits, setRateLimits] = useState<RateLimitsResponse | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  
  // Use useRef to track if a fetch is in progress
  const isFetchRunning = useRef(false);

  // Fetch data with optional force refresh
  const fetchData = useCallback(async (forceRefresh: boolean = false) => {
    // Prevent starting a new fetch if one is already running
    if (isFetchRunning.current) {
      console.warn('Rate limit fetch already in progress, skipping new request.');
      return;
    }

    try {
      // Set loading state: true for initial fetch and forced refreshes
      if (!rateLimits || forceRefresh) {
        setIsLoading(true);
      }
      
      // Mark fetch as running
      isFetchRunning.current = true;
      
      // Clear any previous errors
      setError(null);
      
      // Call the service function (which now handles its own caching)
      const data = await fetchRateLimits(forceRefresh);
      setRateLimits(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch rate limits');
    } finally {
      // Always ensure loading is false after attempt completes
      setIsLoading(false);
      // Mark fetch as complete
      isFetchRunning.current = false;
    }
  }, []); // No dependencies needed since we don't reference any external state

  // Function to optimistically decrement a rate limit
  const decrementLimit = useCallback((category: RateLimitCategory, amount: number = 1) => {
    // First update the service cache directly
    const updatedInfo = decrementRateLimit(category, amount);
    
    // Then update our local state if we have data
    if (updatedInfo && rateLimits) {
      setRateLimits(prev => {
        if (!prev) return prev;
        
        // Create a deep copy of the limits
        const updated = { ...prev };
        
        // Update the specific category
        if (updated.limits[category]) {
          updated.limits[category] = updatedInfo;
        }
        
        return updated;
      });
    }
  }, [rateLimits]);

  // Initial fetch and interval setup
  useEffect(() => {
    fetchData(true); // Initial fetch should always be forced to ensure fresh data
    
    // Set up periodic refreshing - 30 seconds interval
    const intervalId = setInterval(() => {
      fetchData(false); // Regular refreshes use cache when appropriate
    }, 30000); 

    return () => clearInterval(intervalId);
  }, [fetchData]);

  // Listen for events that should trigger a refresh
  useEffect(() => {
    // SVG conversion events
    const svgConversionListener = eventService.subscribe(AppEvent.SVG_CONVERTED, () => {
      console.log('SVG conversion detected, forcing rate limits refresh');
      // No need to decrement optimistically here since the event means the action already happened
      fetchData(true);
    });

    // Concept generation events
    const conceptGeneratedListener = eventService.subscribe(AppEvent.CONCEPT_CREATED, () => {
      console.log('Concept created, forcing rate limits refresh');
      // No need to decrement optimistically here since the event means the action already happened
      fetchData(true);
    });

    return () => {
      svgConversionListener();
      conceptGeneratedListener();
    };
  }, [fetchData]);

  return {
    rateLimits,
    isLoading,
    error,
    refetch: fetchData,
    decrementLimit
  };
} 