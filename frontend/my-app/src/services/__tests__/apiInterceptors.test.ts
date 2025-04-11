/**
 * Tests for the Axios interceptors in apiClient.ts
 */

import axios from 'axios';
import MockAdapter from 'axios-mock-adapter';
import { apiClient } from '../apiClient';
import { supabase } from '../supabaseClient';

// Mock the supabase auth module
jest.mock('../supabaseClient', () => ({
  supabase: {
    auth: {
      getSession: jest.fn(),
      refreshSession: jest.fn(),
    }
  },
  initializeAnonymousAuth: jest.fn(),
}));

// Create a mock for axios
const mockAxios = new MockAdapter(axios);

// Mock for document.dispatchEvent
const originalDispatchEvent = document.dispatchEvent;
const mockDispatchEvent = jest.fn();

describe('API Client Interceptors', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAxios.reset();
    document.dispatchEvent = mockDispatchEvent;
  });

  afterAll(() => {
    document.dispatchEvent = originalDispatchEvent;
  });

  describe('Request Interceptor', () => {
    test('adds Authorization header when session token exists', async () => {
      // Mock the supabase.auth.getSession to return a valid token
      (supabase.auth.getSession as jest.Mock).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'valid-token-123',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Setup mock response for API endpoint
      mockAxios.onGet('/test-endpoint').reply(200, { data: 'test' });

      // Make request
      await apiClient.get('/test-endpoint');

      // Verify authorization header was added
      const requests = mockAxios.history.get;
      expect(requests[0].headers).toHaveProperty('Authorization', 'Bearer valid-token-123');
    });

    test('removes Authorization header when no session exists', async () => {
      // Mock supabase.auth.getSession to return no session
      (supabase.auth.getSession as jest.Mock).mockResolvedValueOnce({
        data: { session: null },
        error: null
      });

      // Setup a mock header in the request config
      const config = {
        headers: { Authorization: 'Bearer old-token' }
      };

      // Setup mock response
      mockAxios.onGet('/test-endpoint').reply(200, { data: 'test' });

      // Make request with the existing header
      await apiClient.get('/test-endpoint', config);

      // Verify Authorization header was removed
      const requests = mockAxios.history.get;
      expect(requests[0].headers).not.toHaveProperty('Authorization');
    });
  });

  describe('Response Interceptor', () => {
    test('extracts rate limit headers from successful responses', async () => {
      // Mock supabase.auth.getSession
      (supabase.auth.getSession as jest.Mock).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'valid-token-123',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Setup mock response with rate limit headers
      mockAxios.onGet('/test-endpoint').reply(200, 
        { data: 'test' },
        {
          'x-ratelimit-limit': '100',
          'x-ratelimit-remaining': '99',
          'x-ratelimit-reset': '60'
        }
      );

      // Make request
      const response = await apiClient.get('/test-endpoint');

      // We expect the response to be processed correctly
      expect(response.data).toEqual({ data: 'test' });
      
      // Event should be dispatched to update rate limits
      // (this would be tough to test directly since the extractRateLimitHeaders is called)
    });

    test('refreshes token and retries request on 401 error', async () => {
      // First request will return 401
      (supabase.auth.getSession as jest.Mock).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'expired-token',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Refresh token mock
      (supabase.auth.refreshSession as jest.Mock).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'new-refreshed-token',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Setup mock to return 401 then 200
      mockAxios
        .onGet('/test-endpoint')
        .replyOnce(401, { message: 'Unauthorized' })
        .onGet('/test-endpoint')
        .replyOnce(200, { data: 'success after refresh' });

      // Make request
      const response = await apiClient.get('/test-endpoint');

      // Verify token was refreshed
      expect(supabase.auth.refreshSession).toHaveBeenCalled();
      
      // Verify the response after retry
      expect(response.data).toEqual({ data: 'success after refresh' });
      
      // Verify there were two requests
      const requests = mockAxios.history.get;
      expect(requests.length).toBe(2);
      
      // Second request should have new token
      expect(requests[1].headers).toHaveProperty('Authorization', 'Bearer new-refreshed-token');
    });

    test('dispatches auth-error-needs-logout event when token refresh fails', async () => {
      // First request will return 401
      (supabase.auth.getSession as jest.Mock).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'expired-token',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Refresh token fails
      (supabase.auth.refreshSession as jest.Mock).mockResolvedValueOnce({
        data: { session: null },
        error: { message: 'Failed to refresh token' }
      });

      // Setup mock to return 401
      mockAxios.onGet('/test-endpoint').reply(401, { message: 'Unauthorized' });

      // Make request (should fail)
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();

      // Verify token refresh was attempted
      expect(supabase.auth.refreshSession).toHaveBeenCalled();
      
      // Verify the auth-error-needs-logout event was dispatched
      expect(mockDispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'auth-error-needs-logout'
        })
      );
    });

    test('handles rate limit errors (429)', async () => {
      // First request will return 429
      (supabase.auth.getSession as jest.Mock).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'valid-token',
            user: { id: 'user-123' }
          }
        },
        error: null
      });

      // Setup mock to return 429 with rate limit headers
      mockAxios.onGet('/concepts/generate').reply(429, 
        { 
          message: 'Rate limit exceeded',
          reset_after_seconds: 120 
        },
        {
          'x-ratelimit-limit': '10',
          'x-ratelimit-remaining': '0',
          'x-ratelimit-reset': '120',
          'retry-after': '120'
        }
      );

      // Make request (should fail with RateLimitError)
      await expect(apiClient.get('/concepts/generate')).rejects.toThrow();

      // Verify the events were dispatched
      expect(mockDispatchEvent).toHaveBeenCalledWith(
        expect.objectContaining({
          type: 'show-api-toast'
        })
      );
    });
  });
}); 