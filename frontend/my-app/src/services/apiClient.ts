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
  /**
   * Response type to expect from the request
   */
  responseType?: 'json' | 'blob' | 'text';
  /**
   * Request signal for cancellation
   */
  signal?: AbortSignal;
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
      case 'image_export': return 'Image export';
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
    console.log('[AUTH] Getting auth headers for request');
    
    // First check for an existing session
    const { data: { session } } = await supabase.auth.getSession();
    
    // If we have a session with a valid token, use it
    if (session?.access_token) {
      const now = Math.floor(Date.now() / 1000);
      
      // If token expires in less than 5 minutes, refresh it
      if (session.expires_at && session.expires_at - now < 300) {
        console.log('[AUTH] Token is about to expire in', session.expires_at - now, 'seconds. Refreshing before request');
        // Refresh the session
        const { data: refreshData } = await supabase.auth.refreshSession();
        if (refreshData.session?.access_token) {
          const newExpiresAt = refreshData.session.expires_at;
          const validFor = newExpiresAt ? newExpiresAt - now : 'unknown';
          console.log('[AUTH] Successfully refreshed token before request. Valid for', validFor, 'seconds');
          return {
            'Authorization': `Bearer ${refreshData.session.access_token}`
          };
        } else {
          console.error('[AUTH] Failed to refresh token - no new token received');
        }
      } else {
        const validFor = session.expires_at ? session.expires_at - now : 'unknown';
        console.log('[AUTH] Using existing token for request. Valid for', validFor, 'seconds');
        return {
          'Authorization': `Bearer ${session.access_token}`
        };
      }
    }
    
    console.log('[AUTH] No valid session found, attempting to sign in anonymously');
    // Try to get a new anonymous session
    const newSession = await initializeAnonymousAuth();
    if (newSession?.access_token) {
      const now = Math.floor(Date.now() / 1000);
      const validFor = newSession.expires_at ? newSession.expires_at - now : 'unknown';
      console.log('[AUTH] Generated new auth token from anonymous sign-in. Valid for', validFor, 'seconds');
      return {
        'Authorization': `Bearer ${newSession.access_token}`
      };
    }
    
    console.error('[AUTH] Failed to get authentication token');
    return {};
  } catch (error) {
    console.error('[AUTH] Error getting auth token:', error);
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
    rateLimitToastMessage,
    responseType,
    signal
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
      signal,
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
        
        if (data.session) {
          console.log('Successfully refreshed session, retrying request');
          
          // Retry the request with the new token, but don't allow another retry
          // to avoid potential infinite loops
          return request<T>(endpoint, {
            method,
            headers,
            body,
            withCredentials,
            retryAuth: false,
            showToastOnRateLimit,
            rateLimitToastMessage,
            responseType,
            signal
          });
        }
      }
      
      // Handle rate limit errors (429)
      if (response.status === 429) {
        // Try to extract rate limit information from headers
        const limit = parseInt(response.headers.get('X-RateLimit-Limit') || '0', 10);
        const remaining = parseInt(response.headers.get('X-RateLimit-Remaining') || '0', 10);
        const current = limit - remaining;
        
        // Try to get reset time from headers
        const resetHeader = response.headers.get('X-RateLimit-Reset');
        const retryAfter = response.headers.get('Retry-After');
        let resetAfterSeconds = 0;
        
        // Parse X-RateLimit-Reset header if available
        if (resetHeader) {
          // If it's a timestamp
          if (!isNaN(Number(resetHeader))) {
            resetAfterSeconds = Math.max(0, Math.ceil((Number(resetHeader) * 1000 - Date.now()) / 1000));
          }
        }
        
        // Parse Retry-After header as fallback
        if (resetAfterSeconds === 0 && retryAfter) {
          // Try to parse retry-after (could be a number in seconds or a date)
          if (!isNaN(Number(retryAfter))) {
            resetAfterSeconds = Number(retryAfter);
          } 
          // If it's a HTTP date format
          else if (new Date(retryAfter).getTime() > 0) {
            resetAfterSeconds = Math.ceil((new Date(retryAfter).getTime() - Date.now()) / 1000);
          }
        }
        
        // Get error data from response
        let errorData;
        try {
          errorData = await response.json();
        } catch (e) {
          errorData = {
            message: 'Rate limit exceeded',
            reset_after_seconds: resetAfterSeconds
          };
        }
        
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
      
      // Handle error responses based on content type
      try {
        if (response.headers.get('content-type')?.includes('application/json')) {
          const errorData = await response.json();
          throw new Error(errorData.message || `Request failed with status ${response.status}`);
        } else {
          throw new Error(`Request failed with status ${response.status}`);
        }
      } catch (error) {
        if (error instanceof SyntaxError) {
          // JSON parsing error - probably not JSON
          throw new Error(`Request failed with status ${response.status}`);
        }
        throw error;
      }
    }
    
    // Handle the response based on the expected type
    if (responseType === 'blob') {
      const blob = await response.blob();
      return { data: blob as unknown as T };
    } else if (responseType === 'text') {
      const text = await response.text();
      return { data: text as unknown as T };
    } else {
      // Default to JSON
      const data = await response.json() as T;
      return { data };
    }
  } catch (err) {
    // Re-throw RateLimitError directly
    if (err instanceof RateLimitError) {
      throw err;
    }
    
    console.error('API request failed:', err);
    throw err;
  }
}

// Export types for use in the export image function
export type ExportFormat = 'png' | 'jpg' | 'svg';
export type ExportSize = 'small' | 'medium' | 'large' | 'original';

/**
 * Export an image with the specified format and size
 * @param imageIdentifier Storage path identifier for the image
 * @param format Target format (png, jpg, svg)
 * @param size Target size (small, medium, large, original)
 * @param svgParams Optional SVG conversion parameters (only used when format is 'svg')
 * @param bucket Optional storage bucket name ('concept-images' or 'palette-images')
 * @returns Blob containing the exported image data
 */
async function exportImage(
  imageIdentifier: string, 
  format: ExportFormat, 
  size: ExportSize,
  svgParams?: Record<string, any>,
  bucket?: string
): Promise<Blob> {
  // Create the request body
  const body = {
    image_identifier: imageIdentifier,
    target_format: format,
    target_size: size,
    svg_params: svgParams,
    storage_bucket: bucket || 'concept-images' // Default to concept-images if not specified
  };
  
  // Set up the AbortController for timeout
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), 30000); // 30-second timeout
  
  try {
    // Make the API call with blob response type
    const response = await request<Blob>('export/process', {
      method: 'POST',
      body,
      responseType: 'blob',
      signal: controller.signal
    });
    
    return response.data;
  } finally {
    clearTimeout(timeoutId);
  }
}

// Export the API client interfaces
export const apiClient = {
  get,
  post,
  exportImage,
  request
}; 