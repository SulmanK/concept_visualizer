import { apiClient } from './apiClient';

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

interface RateLimitHeaderInfo {
  limit: number;
  remaining: number;
  reset: number;     // Unix timestamp when this limit resets
  endpoint: string;
  updatedAt: number; // Time when this header info was last updated
}

interface RateLimitCache {
  limits: RateLimitsResponse;
  timestamp: number; // When the cache was last updated
  expiresAt: number; // When the cache expires
}

// Global cache for rate limits from the API
const rateLimitCache: Record<string, RateLimitCache> = {};

// Cache for endpoint-specific rate limit headers
// This is the primary cache we'll be using for more accurate limit tracking
const rateLimitHeaderCache: Record<string, RateLimitHeaderInfo> = {};

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
 * Get the most recent header info for a specific category
 * @param category Rate limit category
 * @returns The most recent header info or null if none exists
 */
export const getMostRecentHeaderInfoForCategory = (
  category: RateLimitCategory
): RateLimitHeaderInfo | null => {
  // Get all endpoints for this category
  const endpoints = categoryToEndpointMap[category] || [];
  if (endpoints.length === 0) return null;
  
  // Find the most recent header info across all endpoints for this category
  let mostRecent: RateLimitHeaderInfo | null = null;
  
  for (const endpoint of endpoints) {
    // Check each endpoint that might contain info for this category
    for (const cachedEndpoint in rateLimitHeaderCache) {
      if (cachedEndpoint.includes(endpoint)) {
        const info = rateLimitHeaderCache[cachedEndpoint];
        if (!mostRecent || info.updatedAt > mostRecent.updatedAt) {
          mostRecent = info;
        }
      }
    }
  }
  
  return mostRecent;
};

/**
 * Check if header-based cache is valid for a specific category
 * @param category Rate limit category
 * @returns True if valid header cache exists for this category
 */
export const hasValidHeaderCache = (category: RateLimitCategory): boolean => {
  const headerInfo = getMostRecentHeaderInfoForCategory(category);
  if (!headerInfo) return false;
  
  // Check if the reset time is in the future
  const now = Math.floor(Date.now() / 1000); // Current time in seconds
  return headerInfo.reset > now;
};

/**
 * Update rate limit cache based on headers from API response
 * @param response Fetch Response object
 * @param endpoint API endpoint that was called
 */
export const extractRateLimitHeaders = (
  response: Response,
  endpoint: string
): void => {
  // Get header values
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');
  
  if (limit && remaining && reset) {
    console.log(`Extracted rate limit headers from ${endpoint}:`, { 
      limit, 
      remaining, 
      reset,
      timestamp: new Date().toISOString()
    });
    
    // Find category for this endpoint
    const category = mapEndpointToCategory(endpoint);
    
    if (category) {
      console.log(`Updating rate limit for category: ${category} with remaining: ${remaining}`);
    }
    
    // Update cache for this specific endpoint with current timestamp
    updateRateLimitHeaderCache(endpoint, {
      limit: parseInt(limit, 10),
      remaining: parseInt(remaining, 10),
      reset: parseInt(reset, 10),
      endpoint,
      updatedAt: Math.floor(Date.now() / 1000) // Current time in seconds
    });
    
    // Also update the main rate limit cache if we have an appropriate category
    if (category && rateLimitCache.main?.limits) {
      // Create a deep copy of the existing limits
      const updatedLimits = JSON.parse(JSON.stringify(rateLimitCache.main.limits));
      
      // Only update the specific category
      if (updatedLimits.limits[category]) {
        const oldRemaining = updatedLimits.limits[category].remaining;
        
        updatedLimits.limits[category] = {
          ...updatedLimits.limits[category],
          limit: `${limit}/custom`,
          remaining: parseInt(remaining, 10),
          reset_after: parseInt(reset, 10) - Math.floor(Date.now() / 1000) // Convert to seconds from now
        };
        
        console.log(`Rate limit for ${category} updated: ${oldRemaining} -> ${remaining}`);
        
        // Update the main cache
        updateRateLimitCache('main', updatedLimits);
      }
    }
  } else {
    // Log if we expected but didn't get rate limit headers
    if (endpoint.includes('/export/process')) {
      console.warn(`Expected rate limit headers from ${endpoint} but didn't receive them:`, { 
        hasLimit: !!limit,
        hasRemaining: !!remaining,
        hasReset: !!reset
      });
      
      // Log all headers for debugging
      const headers: Record<string, string> = {};
      response.headers.forEach((value, key) => {
        headers[key] = value;
      });
      console.debug('Response headers:', headers);
    }
  }
};

/**
 * Update the rate limit header cache for an endpoint
 * @param endpoint API endpoint
 * @param headerInfo Rate limit header information
 */
export const updateRateLimitHeaderCache = (
  endpoint: string,
  headerInfo: RateLimitHeaderInfo
): void => {
  rateLimitHeaderCache[endpoint] = headerInfo;
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
 * Get rate limit info for a specific category using header cache if available
 * @param category Rate limit category
 * @returns Rate limit info or null if not available
 */
export const getRateLimitInfoForCategory = (
  category: RateLimitCategory
): RateLimitInfo | null => {
  // Try to get info from header cache first (most accurate)
  const headerInfo = getMostRecentHeaderInfoForCategory(category);
  
  if (headerInfo) {
    const now = Math.floor(Date.now() / 1000);
    return {
      limit: `${headerInfo.limit}/custom`,
      remaining: headerInfo.remaining,
      reset_after: Math.max(0, headerInfo.reset - now) // Ensure positive or zero
    };
  }
  
  // Fall back to main API cache if available
  if (rateLimitCache.main?.limits?.limits[category]) {
    return rateLimitCache.main.limits.limits[category];
  }
  
  return null;
};

/**
 * Optimistically update a rate limit category before the API call completes
 * This provides immediate UI feedback while waiting for the actual server response
 * @param category Rate limit category to decrement
 * @param amount Amount to decrement (default: 1)
 * @returns Updated rate limit info (or null if category not found)
 */
export const decrementRateLimit = (
  category: RateLimitCategory,
  amount: number = 1
): RateLimitInfo | null => {
  // Get current info for this category
  const currentInfo = getRateLimitInfoForCategory(category);
  if (!currentInfo) return null;
  
  // Create updated info with decremented remaining count
  const updatedInfo: RateLimitInfo = {
    ...currentInfo,
    remaining: Math.max(0, currentInfo.remaining - amount)
  };
  
  // If we have header cache for this category, update it
  const headerInfo = getMostRecentHeaderInfoForCategory(category);
  if (headerInfo) {
    headerInfo.remaining = Math.max(0, headerInfo.remaining - amount);
    updateRateLimitHeaderCache(headerInfo.endpoint, headerInfo);
  }
  
  // If we have main cache that includes this category, update it
  if (rateLimitCache.main?.limits?.limits[category]) {
    const updatedLimits = { ...rateLimitCache.main.limits };
    updatedLimits.limits[category] = updatedInfo;
    updateRateLimitCache('main', updatedLimits);
  }
  
  return updatedInfo;
};

/**
 * Fetch current rate limit information for the user
 * Uses a non-counting endpoint and implements caching
 * @param forceRefresh Force a refresh of the cache
 * @returns Promise resolving to rate limit information
 */
export const fetchRateLimits = async (forceRefresh: boolean = false): Promise<RateLimitsResponse> => {
  try {
    // Get fresh data from API when forced or cache is expired
    if (forceRefresh || !hasCachedRateLimits()) {
      console.log('Fetching fresh rate limits from API');
      
      // Use the non-counting endpoint to avoid decrementing the rate limit
      const response = await apiClient.get<RateLimitsResponse>('/health/rate-limits-status');
      
      // Cache the results
      updateRateLimitCache('main', response.data);
      
      // Before returning, apply any header-based updates
      // This ensures we use the most accurate data from recent API calls
      const mergedData = applyHeaderUpdatesToLimits(response.data);
      return mergedData;
    } else {
      console.log('Using cached rate limits');
      
      // Apply any header-based updates to ensure accuracy
      const mergedData = applyHeaderUpdatesToLimits(rateLimitCache.main.limits);
      return mergedData;
    }
  } catch (error) {
    console.error('Failed to fetch rate limits:', error);
    
    // Check if we have expired cached data as fallback
    if (rateLimitCache.main) {
      console.log('Using expired cache as fallback');
      
      // Even for fallback, apply header updates for accuracy
      const mergedData = applyHeaderUpdatesToLimits(rateLimitCache.main.limits);
      return mergedData;
    }
    
    // Return a fallback response with default values
    return {
      user_identifier: 'unknown',
      limits: {
        generate_concept: {
          limit: '10/month',
          remaining: 10,
          reset_after: 0,
          error: 'Failed to fetch rate limits'
        },
        refine_concept: {
          limit: '10/hour',
          remaining: 10,
          reset_after: 0,
          error: 'Failed to fetch rate limits'
        },
        store_concept: {
          limit: '10/month',
          remaining: 10,
          reset_after: 0,
          error: 'Failed to fetch rate limits'
        },
        get_concepts: {
          limit: '30/minute',
          remaining: 30,
          reset_after: 0,
          error: 'Failed to fetch rate limits'
        },
        sessions: {
          limit: '60/hour',
          remaining: 60,
          reset_after: 0,
          error: 'Failed to fetch rate limits'
        },
        export_action: {
          limit: '20/hour',
          remaining: 20,
          reset_after: 0,
          error: 'Failed to fetch rate limits'
        }
      },
      default_limits: ['200/day', '50/hour', '10/minute']
    };
  }
};

/**
 * Apply the most recent header-based updates to rate limit data
 * This ensures we always show the most accurate values from actual API responses
 * @param baseData Base rate limit data to update
 * @returns Updated rate limit data with header-based information applied
 */
function applyHeaderUpdatesToLimits(baseData: RateLimitsResponse): RateLimitsResponse {
  // Create a deep copy to avoid mutating the original
  const updatedData = JSON.parse(JSON.stringify(baseData));
  let hasUpdates = false;
  
  // For each category, check if we have more recent header info
  for (const category in updatedData.limits) {
    const typedCategory = category as RateLimitCategory;
    const headerInfo = getMostRecentHeaderInfoForCategory(typedCategory);
    
    if (headerInfo) {
      const now = Math.floor(Date.now() / 1000);
      const oldRemaining = updatedData.limits[typedCategory].remaining;
      const newRemaining = headerInfo.remaining;
      
      // Only update if header value is different (helps with debugging)
      if (oldRemaining !== newRemaining) {
        console.log(`Applying header update for ${typedCategory}: ${oldRemaining} -> ${newRemaining}`);
        
        updatedData.limits[typedCategory] = {
          ...updatedData.limits[typedCategory],
          remaining: newRemaining,
          reset_after: Math.max(0, headerInfo.reset - now) // Ensure positive or zero
        };
        hasUpdates = true;
      }
    }
  }
  
  // Update the main cache if we made changes
  if (hasUpdates) {
    updateRateLimitCache('main', updatedData);
    console.log('Updated rate limit cache with header-based values');
  }
  
  return updatedData;
}

/**
 * Format seconds into a human-readable time string
 * @param seconds Number of seconds
 * @returns Formatted time string (e.g., "2h 15m 30s" or "5d 12h")
 */
export const formatTimeRemaining = (seconds: number): string => {
  if (seconds < 0) return 'Unknown';
  
  const days = Math.floor(seconds / (24 * 60 * 60));
  seconds -= days * 24 * 60 * 60;
  
  const hours = Math.floor(seconds / (60 * 60));
  seconds -= hours * 60 * 60;
  
  const minutes = Math.floor(seconds / 60);
  seconds -= minutes * 60;
  
  if (days > 0) {
    return `${days}d ${hours}h`;
  } else if (hours > 0) {
    return `${hours}h ${minutes}m`;
  } else if (minutes > 0) {
    return `${minutes}m ${seconds}s`;
  } else {
    return `${seconds}s`;
  }
}; 