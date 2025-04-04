/**
 * API client for the Concept Visualizer application.
 */

// Use the full backend URL instead of a relative path
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

interface RequestOptions {
  headers?: Record<string, string>;
  body?: any;
  withCredentials?: boolean;
}

// Custom error class for rate limit errors
export class RateLimitError extends Error {
  status: number;
  limit: number;
  current: number;
  period: string;
  resetAfterSeconds: number;

  constructor(message: string, response: any) {
    super(message);
    this.name = 'RateLimitError';
    this.status = 429;
    this.limit = response.limit || 0;
    this.current = response.current || 0;
    this.period = response.period || 'unknown';
    this.resetAfterSeconds = response.reset_after_seconds || 0;
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
 * Make a request to the API
 * @param endpoint API endpoint path
 * @param options Request options
 * @returns Response with generic type
 */
async function request<T>(
  endpoint: string,
  { method = 'GET', headers = {}, body, withCredentials = true }: RequestOptions & { method: string }
): Promise<{ data: T }> {
  try {
    // Ensure endpoint starts with forward slash if not already
    const sanitizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${API_BASE_URL}${sanitizedEndpoint}`;
    
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
    
    const response = await fetch(url, requestOptions);
    
    if (!response.ok) {
      // Handle different error types based on status code
      if (response.status === 429) {
        // Rate limit exceeded
        const errorData = await response.json().catch(() => ({
          message: 'Rate limit exceeded',
        }));
        
        // Throw a specialized RateLimitError
        throw new RateLimitError(
          errorData.message || 'You have reached your usage limit',
          errorData
        );
      }
      
      const errorData = await response.json().catch(() => ({
        message: 'An unexpected error occurred',
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