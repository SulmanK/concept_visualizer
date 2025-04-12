import { apiClient } from './apiClient';
import { AxiosResponse } from 'axios';
import { queryClient } from '../main';

export interface RateLimitInfo {
  limit: string;
  remaining: number;
  reset_after: number;
  error?: string;
}

export interface RateLimitsResponse {
  user_identifier: string;
  limits: {
    generate_concept: RateLimitInfo;
    refine_concept: RateLimitInfo;
    store_concept: RateLimitInfo;
    get_concepts: RateLimitInfo;
    sessions: RateLimitInfo;
    export_action: RateLimitInfo;
  };
  default_limits: string[];
}

// Valid rate limit categories - used for type checking
export type RateLimitCategory = 
  | 'generate_concept' 
  | 'refine_concept' 
  | 'store_concept' 
  | 'get_concepts' 
  | 'sessions' 
  | 'export_action';

interface RateLimitCache {
  limits: RateLimitsResponse;
  timestamp: number; // When the cache was last updated
  expiresAt: number; // When the cache expires
}

// Global cache for rate limits from the API
const rateLimitCache: Record<string, RateLimitCache> = {};

// Map to track category to endpoint relationships for reverse lookup
const categoryToEndpointMap: Record<string, string[]> = {
  generate_concept: ['/concepts/generate'],
  refine_concept: ['/concepts/refine'],
  store_concept: ['/concepts/store'],
  get_concepts: ['/concepts/list'],
  export_action: ['/export/process'],
  sessions: ['/sessions']
};

/**
 * Map API endpoint to rate limit category
 * @param endpoint API endpoint path
 * @returns Rate limit category (e.g., "generate_concept")
 */
export const mapEndpointToCategory = (endpoint: string): RateLimitCategory | null => {
  // Remove any query parameters
  const path = endpoint.split('?')[0];
  
  // Map API paths to their corresponding rate limit categories  
  if (path.includes('/concepts/generate')) return 'generate_concept';
  if (path.includes('/concepts/refine')) return 'refine_concept';
  if (path.includes('/concepts/store')) return 'store_concept';
  if (path.includes('/concepts/list')) return 'get_concepts';
  if (path.includes('/export/process')) return 'export_action';
  if (path.includes('/sessions')) return 'sessions';
  
  // Return null if no mapping found
  return null;
};

/**
 * Update rate limit cache based on headers from API response
 * @param response Axios Response object
 * @param endpoint API endpoint that was called (or undefined)
 */
export const extractRateLimitHeaders = (
  response: AxiosResponse,
  endpoint: string | undefined
): void => {
  // Get header values - Axios headers are typically lowercase
  const limit = response.headers['x-ratelimit-limit'];
  const remaining = response.headers['x-ratelimit-remaining'];
  const reset = response.headers['x-ratelimit-reset'];
  
  if (limit && remaining && reset) {
    console.log(`Extracted rate limit headers from ${endpoint}:`, { 
      limit, 
      remaining, 
      reset,
      timestamp: new Date().toISOString()
    });
    
    // Find category for this endpoint
    const category = mapEndpointToCategory(endpoint || '');
    
    if (category) {
      console.log(`Updating rate limit for category: ${category} with remaining: ${remaining}`);
      
      // Directly update the React Query cache
      queryClient.setQueryData<RateLimitsResponse>(['rateLimits'], (oldData) => {
        // If we don't have existing data in the cache, we can't update it
        if (!oldData || !oldData.limits || !oldData.limits[category]) {
          console.warn('Cannot update rate limit cache: no existing data for category', category);
          return oldData;
        }
        
        // Create a deep copy to avoid mutation
        const newData = JSON.parse(JSON.stringify(oldData)) as RateLimitsResponse;
        
        // Parse values safely
        const parsedLimit = parseInt(String(limit), 10);
        const parsedRemaining = parseInt(String(remaining), 10);
        const parsedReset = parseInt(String(reset), 10);
        const now = Math.floor(Date.now() / 1000);
        
        // Update the specific category
        newData.limits[category] = {
          ...newData.limits[category],
          limit: `${parsedLimit}/custom`,
          remaining: parsedRemaining,
          reset_after: parsedReset - now // Convert to seconds from now
        };
        
        console.log(`[RateLimitService] Updated rate limit cache for category: ${category}, remaining: ${parsedRemaining}`);
        
        return newData;
      });
    } else {
      console.warn(`Could not map endpoint ${endpoint} to a rate limit category`);
    }
  } else {
    // Log if we expected but didn't get rate limit headers
    if (endpoint && endpoint.includes('/export/process')) {
      console.warn(`Expected rate limit headers from ${endpoint} but didn't receive them:`, { 
        hasLimit: !!limit,
        hasRemaining: !!remaining,
        hasReset: !!reset
      });
      
      // Log all headers for debugging
      const headers: Record<string, string> = {};
      Object.entries(response.headers).forEach(([key, value]) => {
        headers[key] = String(value);
      });
      console.debug('Response headers:', headers);
    }
  }
};

/**
 * Update the main rate limits cache
 * @param cacheKey Cache key (usually 'main')
 * @param limits Rate limits response
 */
export const updateRateLimitCache = (
  cacheKey: string,
  limits: RateLimitsResponse
): void => {
  const now = Date.now();
  rateLimitCache[cacheKey] = {
    limits,
    timestamp: now,
    expiresAt: now + 30000 // Cache for 30 seconds
  };
};

/**
 * Check if cached rate limits are still valid
 * @returns True if valid cache exists
 */
const hasCachedRateLimits = (): boolean => {
  return (
    !!rateLimitCache.main &&
    rateLimitCache.main.expiresAt > Date.now()
  );
};

/**
 * Get rate limit info for a specific category from the React Query cache
 * @param category Rate limit category
 * @returns Rate limit info or null if not available
 */
export const getRateLimitInfoForCategory = (
  category: RateLimitCategory
): RateLimitInfo | null => {
  // Try to get data directly from React Query cache
  const cachedData = queryClient.getQueryData<RateLimitsResponse>(['rateLimits']);
  
  if (cachedData?.limits && cachedData.limits[category]) {
    return cachedData.limits[category];
  }
  
  // Fallback to the separate local cache if React Query cache not available
  if (rateLimitCache.main?.limits?.limits && rateLimitCache.main.limits.limits[category]) {
    return rateLimitCache.main.limits.limits[category];
  }
  
  return null;
};

/**
 * Optimistically decrement the rate limit for a category
 * @param category Category to decrement
 * @param amount Amount to decrement by (default: 1)
 * @returns Updated rate limit info or null if not available
 */
export const decrementRateLimit = (
  category: RateLimitCategory,
  amount: number = 1
): RateLimitInfo | null => {
  const rateLimit = getRateLimitInfoForCategory(category);
  
  if (!rateLimit) {
    console.warn(`Cannot decrement rate limit for ${category}: no rate limit info available`);
    return null;
  }
  
  // Create a copy with decremented remaining value
  const updatedRateLimit: RateLimitInfo = {
    ...rateLimit,
    remaining: Math.max(0, rateLimit.remaining - amount)
  };
  
  // Update React Query cache
  queryClient.setQueryData<RateLimitsResponse>(['rateLimits'], (oldData) => {
    if (!oldData || !oldData.limits) return oldData;
    
    // Create a deep copy
    const updatedData = JSON.parse(JSON.stringify(oldData)) as RateLimitsResponse;
    
    // Update the specific category
    updatedData.limits[category] = updatedRateLimit;
    
    return updatedData;
  });
  
  console.log(`Decremented rate limit for ${category} by ${amount}`, updatedRateLimit);
  return updatedRateLimit;
};

/**
 * Fetch rate limits from the API
 * @param forceRefresh Force a refresh from the API
 * @returns Rate limits response
 */
export const fetchRateLimits = async (forceRefresh: boolean = false): Promise<RateLimitsResponse> => {
  // If we already have cached data and we're not forcing a refresh, use it
  if (!forceRefresh && hasCachedRateLimits()) {
    console.log('Using cached rate limits');
    return rateLimitCache.main.limits;
  }
  
  try {
    console.log(`Fetching rate limits from API (force=${forceRefresh})`);
    
    // Fetch the rate limits from the API
    const response = await apiClient.get<RateLimitsResponse>('/health/rate-limits-status');
    const data = response.data;
    
    // Format the response so it's more usable
    const formattedResponse: RateLimitsResponse = {
      user_identifier: data.user_identifier,
      limits: data.limits,
      default_limits: data.default_limits
    };
    
    // Cache the formatted response
    updateRateLimitCache('main', formattedResponse);
    
    return formattedResponse;
  } catch (error) {
    console.error('Error fetching rate limits:', error);
    
    // If we have cached data, use it as a fallback
    if (hasCachedRateLimits()) {
      console.warn('Using cached rate limits as fallback after API error');
      return rateLimitCache.main.limits;
    }
    
    // Otherwise, create an error response
    const errorResponse: RateLimitsResponse = {
      user_identifier: 'error',
      limits: {
        generate_concept: { limit: 'error', remaining: 0, reset_after: 0, error: 'Error fetching rate limits' },
        refine_concept: { limit: 'error', remaining: 0, reset_after: 0, error: 'Error fetching rate limits' },
        store_concept: { limit: 'error', remaining: 0, reset_after: 0, error: 'Error fetching rate limits' },
        get_concepts: { limit: 'error', remaining: 0, reset_after: 0, error: 'Error fetching rate limits' },
        sessions: { limit: 'error', remaining: 0, reset_after: 0, error: 'Error fetching rate limits' },
        export_action: { limit: 'error', remaining: 0, reset_after: 0, error: 'Error fetching rate limits' }
      },
      default_limits: []
    };
    
    return errorResponse;
  }
};

/**
 * Format seconds into a user-friendly string
 * @param seconds Number of seconds
 * @returns Formatted time string (e.g., "2 minutes")
 */
export const formatTimeRemaining = (seconds: number): string => {
  if (seconds < 60) {
    return seconds === 1 ? '1 second' : `${seconds} seconds`;
  }
  
  if (seconds < 3600) {
    const minutes = Math.ceil(seconds / 60);
    return minutes === 1 ? '1 minute' : `${minutes} minutes`;
  }
  
  const hours = Math.ceil(seconds / 3600);
  return hours === 1 ? '1 hour' : `${hours} hours`;
}; 