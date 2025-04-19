/**
 * Tests for the Axios interceptors in apiClient.ts
 */

import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import axios from 'axios';
import { apiClient } from '../apiClient';
import { supabase } from '../supabaseClient';
import * as rateLimitService from '../rateLimitService';

// Mock axios
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => ({
      interceptors: {
        request: {
          use: vi.fn((onFulfilled) => {
            mockRequestInterceptor = onFulfilled;
          })
        },
        response: {
          use: vi.fn((onFulfilled, onRejected) => {
            mockResponseInterceptor = onFulfilled;
            mockResponseErrorInterceptor = onRejected;
          })
        }
      },
      get: vi.fn(),
      post: vi.fn()
    })),
    get: vi.fn(),
    post: vi.fn()
  };
  return mockAxios;
});

// Mock supabase client
vi.mock('../supabaseClient', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      refreshSession: vi.fn()
    }
  },
  initializeAnonymousAuth: vi.fn()
}));

// Mock rate limit service
vi.mock('../rateLimitService', () => ({
  extractRateLimitHeaders: vi.fn(),
  mapEndpointToCategory: vi.fn()
}));

// Global interceptor functions
let mockRequestInterceptor: any;
let mockResponseInterceptor: any;
let mockResponseErrorInterceptor: any;

describe('API Client Interceptors', () => {
  // Mock for document.dispatchEvent
  let dispatchEventSpy: any;
  
  beforeEach(() => {
    vi.clearAllMocks();
    dispatchEventSpy = vi.spyOn(document, 'dispatchEvent');
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('Request Interceptor', () => {
    it('adds Authorization header when session token exists', async () => {
      // Setup a mock request config
      const config = { headers: {}, url: '/test-endpoint' };
      
      // Mock the session with a valid token
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'valid-token-123',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Apply the interceptor manually
      const result = await mockRequestInterceptor(config);

      // Verify authorization header was added
      expect(result.headers).toHaveProperty('Authorization', 'Bearer valid-token-123');
    });

    it('removes Authorization header when no session exists', async () => {
      // Setup a mock request config with existing auth header
      const config = { 
        headers: { Authorization: 'Bearer old-token' },
        url: '/test-endpoint'
      };
      
      // Mock no session
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: { session: null },
        error: null
      });

      // Apply the interceptor manually
      const result = await mockRequestInterceptor(config);

      // Verify Authorization header was removed
      expect(result.headers.Authorization).toBeUndefined();
    });
  });

  describe('Response Interceptor', () => {
    it('extracts rate limit headers from successful responses', async () => {
      // Setup a mock response with rate limit headers
      const mockResponse = {
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: {
          'x-ratelimit-limit': '100',
          'x-ratelimit-remaining': '99',
          'x-ratelimit-reset': '60'
        },
        config: { url: '/test-endpoint' }
      };

      // Apply the response interceptor
      const result = mockResponseInterceptor(mockResponse);

      // Verify headers were extracted
      expect(rateLimitService.extractRateLimitHeaders).toHaveBeenCalledWith(
        mockResponse,
        '/test-endpoint'
      );
      
      // Verify response is unchanged
      expect(result).toEqual(mockResponse);
    });

    it('refreshes token and retries request on 401 error', async () => {
      // Setup mock error
      const mockAxiosError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        },
        config: {
          url: '/test-endpoint',
          method: 'GET',
          headers: { 'Authorization': 'Bearer expired-token' }
        }
      };
      
      // Mock successful token refresh
      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'new-refreshed-token',
            user: { id: 'user-123' }
          }
        },
        error: null
      });
      
      // Mock successful retry
      vi.mocked(axios.get).mockResolvedValueOnce({ 
        data: { success: true },
        status: 200 
      });

      // Apply the error interceptor
      try {
        await mockResponseErrorInterceptor(mockAxiosError);
        
        // Verify token refresh was called
        expect(supabase.auth.refreshSession).toHaveBeenCalled();
        
        // Verify request was retried with new token
        expect(axios.get).toHaveBeenCalledWith(
          '/test-endpoint',
          expect.objectContaining({
            headers: expect.objectContaining({
              'Authorization': 'Bearer new-refreshed-token'
            })
          })
        );
      } catch (error) {
        // This should not happen
        expect(true).toBe(false);
      }
    });

    it('dispatches auth-error-needs-logout event when token refresh fails', async () => {
      // Setup mock error
      const mockAxiosError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        },
        config: {
          url: '/test-endpoint',
          method: 'GET',
          headers: { 'Authorization': 'Bearer expired-token' }
        }
      };
      
      // Mock failed token refresh
      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: { session: null },
        error: { message: 'Failed to refresh token' }
      });

      // Apply the error interceptor and expect it to throw
      try {
        await mockResponseErrorInterceptor(mockAxiosError);
        // Should not reach here
        expect(true).toBe(false);
      } catch (error) {
        // Verify token refresh was attempted
        expect(supabase.auth.refreshSession).toHaveBeenCalled();
        
        // Verify the auth-error-needs-logout event was dispatched
        expect(dispatchEventSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            type: 'auth-error-needs-logout'
          })
        );
      }
    });

    it('handles rate limit errors (429)', async () => {
      // Setup mock error
      const mockAxiosError = {
        response: {
          status: 429,
          data: { 
            message: 'Rate limit exceeded',
            reset_after_seconds: 60,
            limit: 100,
            current: 101
          }
        },
        config: {
          url: '/concepts/generate',
          method: 'POST'
        }
      };
      
      // Mock category mapping
      vi.mocked(rateLimitService.mapEndpointToCategory).mockReturnValueOnce('generate_concept');

      // Apply the error interceptor and expect it to throw
      try {
        await mockResponseErrorInterceptor(mockAxiosError);
        // Should not reach here
        expect(true).toBe(false);
      } catch (error: any) {
        // Verify error has rate limit properties
        expect(error.name).toBe('RateLimitError');
        expect(error.status).toBe(429);
        expect(error.resetAfterSeconds).toBe(60);
        expect(error.category).toBe('generate_concept');
        
        // Verify toast event was dispatched
        expect(dispatchEventSpy).toHaveBeenCalledWith(
          expect.objectContaining({
            type: 'show-api-toast'
          })
        );
      }
    });
  });
}); 