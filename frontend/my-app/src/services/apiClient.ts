/**
 * API client for the Concept Visualizer application.
 */

import { supabase, initializeAnonymousAuth } from './supabaseClient';
import { 
  extractRateLimitHeaders, 
  formatTimeRemaining, 
  mapEndpointToCategory, 
  RateLimitCategory 
} from './rateLimitService';
import useToast from '../hooks/useToast';

// Use the full backend URL instead of a relative path
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create a toast function for use within this file (outside of React components)
const toast = (options: Parameters<typeof useToast.showToast>[0]) => {
  // We'll handle this through a custom event since we can't directly use hooks outside components
  document.dispatchEvent(
    new CustomEvent('show-api-toast', { 
      detail: options 
    })
  );
};

interface RequestOptions {
  headers?: Record<string, string>;
  body?: any;
  withCredentials?: boolean;
  retryAuth?: boolean; // Whether to retry with fresh auth token on 401
  /**
   * Whether to show a toast notification on rate limit errors
   * @default true
   */
  showToastOnRateLimit?: boolean;
  /**
   * A custom message to show in the toast notification for rate limit errors
   * If not provided, a default message will be generated
   */
  rateLimitToastMessage?: string;
}

// Custom error class for rate limit errors
export class RateLimitError extends Error {
  status: number;
  limit: number;
  current: number;
  period: string;
  resetAfterSeconds: number;
  category?: RateLimitCategory; // Added category for context
  retryAfter?: Date; // Added specific retry time

  constructor(message: string, response: any, endpoint?: string) {
    super(message);
    this.name = 'RateLimitError';
    this.status = 429;
    this.limit = response.limit || 0;
    this.current = response.current || 0;
    this.period = response.period || 'unknown';
    this.resetAfterSeconds = response.reset_after_seconds || 0;
    
    // Try to determine the category from the endpoint
    if (endpoint) {
      const category = mapEndpointToCategory(endpoint);
      if (category !== null) {
        this.category = category;
      }
    }
    
    // Calculate the retry-after time if we have reset seconds
    if (this.resetAfterSeconds > 0) {
      this.retryAfter = new Date(Date.now() + this.resetAfterSeconds * 1000);
    }
  }
  
  /**
   * Get a user-friendly error message for display
   */
  getUserFriendlyMessage(): string {
    const categoryName = this.getCategoryDisplayName();
    const timeRemaining = formatTimeRemaining(this.resetAfterSeconds);
    
    return `${categoryName} limit reached (${this.current}/${this.limit}). Please try again in ${timeRemaining}.`;
  }
  
  /**
   * Get a display-friendly name for the rate limit category
   */
  getCategoryDisplayName(): string {
    switch(this.category) {
      case 'generate_concept': return 'Concept generation';
      case 'refine_concept': return 'Concept refinement';
      case 'store_concept': return 'Concept storage';
      case 'get_concepts': return 'Concept retrieval';
      case 'svg_conversion': return 'SVG conversion';
      case 'sessions': return 'Session';
      default: return 'Usage';
    }
  }
}

/**
 * Make a GET request to the API
 * @param endpoint API endpoint path
 * @param options Request options
 * @returns Response with generic type
 */
async function get<T>(endpoint: string, options: RequestOptions = {}): Promise<{ data: T }> {
  return request<T>(endpoint, { method: 'GET', ...options });
}

/**
 * Make a POST request to the API
 * @param endpoint API endpoint path
 * @param body Request body
 * @param options Request options
 * @returns Response with generic type
 */
async function post<T>(endpoint: string, body: any, options: RequestOptions = {}): Promise<{ data: T }> {
  return request<T>(endpoint, { method: 'POST', body, ...options });
}

/**
 * Get the current auth token from Supabase
 * @returns Authorization header or empty object if no session
 */
async function getAuthHeaders(): Promise<Record<string, string>> {
  try {
    // First check for an existing session
    const { data: { session } } = await supabase.auth.getSession();
    
    // If we have a session with a valid token, use it
    if (session?.access_token) {
      const now = Math.floor(Date.now() / 1000);
      
      // If token expires in less than 5 minutes, refresh it
      if (session.expires_at && session.expires_at - now < 300) {
        console.log('Token is about to expire, refreshing before request');
        // Refresh the session
        const { data: refreshData } = await supabase.auth.refreshSession();
        if (refreshData.session?.access_token) {
          console.log('Successfully refreshed token before request');
          return {
            'Authorization': `Bearer ${refreshData.session.access_token}`
          };
        }
      } else {
        console.log('Using existing token for request');
        return {
          'Authorization': `Bearer ${session.access_token}`
        };
      }
    }
    
    console.log('No valid session found, attempting to sign in anonymously');
    // Try to get a new anonymous session
    const newSession = await initializeAnonymousAuth();
    if (newSession?.access_token) {
      console.log('Generated new auth token from anonymous sign-in');
      return {
        'Authorization': `Bearer ${newSession.access_token}`
      };
    }
    
    console.error('Failed to get authentication token');
    return {};
  } catch (error) {
    console.error('Error getting auth token:', error);
    return {};
  }
}

/**
 * Make a request to the API
 * @param endpoint API endpoint path
 * @param options Request options
 * @returns Response with generic type
 */
async function request<T>(
  endpoint: string,
  { 
    method = 'GET', 
    headers = {}, 
    body, 
    withCredentials = true,
    retryAuth = true,
    showToastOnRateLimit = true,
    rateLimitToastMessage 
  }: RequestOptions & { method: string }
): Promise<{ data: T }> {
  try {
    // Ensure endpoint starts with forward slash if not already
    const sanitizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${API_BASE_URL}${sanitizedEndpoint}`;
    
    // Get auth headers from Supabase session
    const authHeaders = await getAuthHeaders();
    
    const requestHeaders = {
      'Content-Type': 'application/json',
      ...authHeaders,
      ...headers,
    };
    
    const requestOptions: RequestInit = {
      method,
      headers: requestHeaders,
      body: body ? JSON.stringify(body) : undefined,
      credentials: withCredentials ? 'include' : 'same-origin', // Include cookies for backward compatibility
    };
    
    console.log(`Making ${method} request to ${url}`);
    
    const response = await fetch(url, requestOptions);
    
    // Extract rate limit headers from the response 
    // Skip for the rate-limits endpoints to avoid circular updates
    if (!sanitizedEndpoint.includes('/health/rate-limits')) {
      extractRateLimitHeaders(response, sanitizedEndpoint);
    }
    
    if (!response.ok) {
      // Handle 401 Unauthorized - try to refresh auth and retry
      if (response.status === 401 && retryAuth) {
        console.log('Authentication failed (401), refreshing session and retrying');
        
        // Refresh the token using the proper refresh mechanism
        const { data } = await supabase.auth.refreshSession();
        
        if (!data.session) {
          // If refresh failed, try initializing a new session
          await initializeAnonymousAuth();
        }
        
        // Retry the request once with fresh token, but prevent infinite retries
        return request<T>(endpoint, { 
          method, 
          headers, 
          body, 
          withCredentials,
          retryAuth: false // Prevent infinite retry loop
        });
      }
      
      // Handle different error types based on status code
      if (response.status === 429) {
        // Extract retry-after header if present
        const retryAfter = response.headers.get('Retry-After') || response.headers.get('X-RateLimit-Reset');
        let resetAfterSeconds = 0;
        
        if (retryAfter) {
          // If it's a number in seconds
          if (!isNaN(Number(retryAfter))) {
            resetAfterSeconds = Number(retryAfter);
          } 
          // If it's a HTTP date format
          else if (new Date(retryAfter).getTime() > 0) {
            resetAfterSeconds = Math.ceil((new Date(retryAfter).getTime() - Date.now()) / 1000);
          }
        }
        
        // Get error data from response
        const errorData = await response.json().catch(() => ({
          message: 'Rate limit exceeded',
          reset_after_seconds: resetAfterSeconds
        }));
        
        // If reset seconds wasn't in the header, try to get it from the response body
        if (resetAfterSeconds === 0 && errorData.reset_after_seconds) {
          resetAfterSeconds = errorData.reset_after_seconds;
        }
        
        // Ensure reset_after_seconds is included in the error data
        if (!errorData.reset_after_seconds && resetAfterSeconds > 0) {
          errorData.reset_after_seconds = resetAfterSeconds;
        }
        
        // Create specialized error with endpoint context
        const rateLimitError = new RateLimitError(
          errorData.message || 'You have reached your usage limit',
          errorData,
          sanitizedEndpoint
        );
        
        // Show toast notification if enabled
        if (showToastOnRateLimit) {
          const toastMessage = rateLimitToastMessage || rateLimitError.getUserFriendlyMessage();
          
          // Dispatch a custom event that components can listen for
          document.dispatchEvent(
            new CustomEvent('show-api-toast', { 
              detail: {
                title: 'Rate Limit Reached',
                message: toastMessage,
                type: 'error',
                duration: 6000, // Show longer than normal toasts
                action: {
                  label: 'View Limits',
                  onClick: () => {
                    // Trigger the RateLimitsPanel to open
                    document.dispatchEvent(new CustomEvent('show-rate-limits'));
                  }
                }
              }
            })
          );
        }
        
        throw rateLimitError;
      }
      
      const errorData = await response.json().catch(() => ({
        message: `Request failed with status ${response.status}`,
      }));
      
      throw new Error(errorData.message || `Request failed with status ${response.status}`);
    }
    
    const data = await response.json() as T;
    return { data };
  } catch (err) {
    // Re-throw RateLimitError directly
    if (err instanceof RateLimitError) {
      throw err;
    }
    
    console.error('API request failed:', err);
    throw err;
  }
}

export const apiClient = {
  get,
  post,
  request
}; 