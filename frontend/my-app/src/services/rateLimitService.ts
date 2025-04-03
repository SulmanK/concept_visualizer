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
    svg_conversion: RateLimitInfo;
  };
  default_limits: string[];
}

/**
 * Fetch current rate limit information for the user
 * @returns Promise resolving to rate limit information
 */
export const fetchRateLimits = async (): Promise<RateLimitsResponse> => {
  const response = await apiClient.get<RateLimitsResponse>('/health/rate-limits');
  return response.data;
};

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