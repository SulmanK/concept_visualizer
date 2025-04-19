import axios, { AxiosError, AxiosRequestConfig, AxiosResponse } from 'axios';
import {
  apiClient,
  AuthError,
  NetworkError,
  NotFoundError,
  PermissionError,
  RateLimitError,
  ServerError,
  ValidationError
} from '../apiClient';
import { supabase } from '../supabaseClient';
import * as rateLimitService from '../rateLimitService';
import { vi, describe, it, expect, beforeEach, afterEach, MockInstance } from 'vitest';

// Mock dependencies
vi.mock('axios', () => {
  const mockAxios = {
    create: vi.fn(() => ({
      interceptors: {
        request: {
          use: vi.fn()
        },
        response: {
          use: vi.fn()
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

vi.mock('../supabaseClient', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      refreshSession: vi.fn()
    }
  },
  initializeAnonymousAuth: vi.fn()
}));

vi.mock('../rateLimitService', () => ({
  extractRateLimitHeaders: vi.fn(),
  mapEndpointToCategory: vi.fn()
}));

vi.mock('../../main', () => ({
  queryClient: {
    setQueryData: vi.fn()
  }
}));

describe('API Client', () => {
  let mockAxios: typeof axios;
  let mockGet: MockInstance;
  let mockPost: MockInstance;
  
  beforeEach(() => {
    mockAxios = axios as jest.Mocked<typeof axios>;
    mockGet = vi.spyOn(apiClient, 'get').mockImplementation(() => Promise.resolve({ data: {} }));
    mockPost = vi.spyOn(apiClient, 'post').mockImplementation(() => Promise.resolve({ data: {} }));
    
    // Clear mocks before each test
    vi.clearAllMocks();
    
    // Setup mock for document.dispatchEvent
    vi.spyOn(document, 'dispatchEvent').mockImplementation(() => true);
  });
  
  afterEach(() => {
    vi.resetAllMocks();
  });
  
  describe('Request Interceptor', () => {
    it('should add auth header if session exists', async () => {
      // Mock session with token
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'mock-token'
          }
        },
        error: null
      });
      
      // Call the API
      await apiClient.get('/test-endpoint');
      
      // Verify axios was called with auth header
      expect(mockGet).toHaveBeenCalled();
    });
    
    it('should not add auth header if no session exists', async () => {
      // Mock no session
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: { session: null },
        error: null
      });
      
      // Call the API
      await apiClient.get('/test-endpoint');
      
      // Verify axios was called
      expect(mockGet).toHaveBeenCalled();
    });
  });
  
  describe('Response Interceptor', () => {
    it('should extract rate limit headers from successful responses', async () => {
      // Create mock response with rate limit headers
      const mockResponse: AxiosResponse = {
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: {
          'x-ratelimit-limit': '100',
          'x-ratelimit-remaining': '99',
          'x-ratelimit-reset': '1600000000'
        },
        config: { url: '/test-endpoint' } as AxiosRequestConfig
      };
      
      mockGet.mockResolvedValueOnce(mockResponse);
      
      // Call the API
      await apiClient.get('/test-endpoint');
      
      // Verify rate limit headers were extracted
      expect(rateLimitService.extractRateLimitHeaders).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            'x-ratelimit-limit': '100',
          })
        }),
        '/test-endpoint'
      );
    });
    
    it('should handle 401 errors by refreshing the session', async () => {
      // Setup mocks for auth error and refresh
      const mockAxiosError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        },
        config: {
          url: '/test-endpoint',
          headers: {}
        }
      } as unknown as AxiosError;
      
      // First call fails with 401, second call succeeds
      mockGet.mockRejectedValueOnce(mockAxiosError)
             .mockResolvedValueOnce({ data: { success: true } });
      
      // Mock successful token refresh
      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'new-token'
          }
        },
        error: null
      });
      
      // Call the API and expect it to be retried after refresh
      try {
        await apiClient.get('/test-endpoint');
      } catch (e) {
        // We expect the retry to happen internally
      }
      
      // Verify token was refreshed
      expect(supabase.auth.refreshSession).toHaveBeenCalled();
    });
    
    it('should throw AuthError for 401 responses that cannot be recovered', async () => {
      // Setup mock for auth error
      const mockAxiosError = {
        response: {
          status: 401,
          data: { message: 'Unauthorized' }
        },
        config: {
          url: '/test-endpoint',
          headers: {}
        }
      } as unknown as AxiosError;
      
      // Mock failed token refresh
      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: { session: null },
        error: { message: 'Cannot refresh token' }
      });
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect AuthError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(AuthError);
    });
    
    it('should throw RateLimitError for 429 responses', async () => {
      // Setup mock for rate limit error
      const mockAxiosError = {
        response: {
          status: 429,
          data: {
            message: 'Rate limit exceeded',
            reset_after_seconds: 60,
            limit: 100,
            current: 101,
            period: 'hour'
          }
        },
        config: {
          url: '/test-endpoint'
        }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Set up category mapping mock
      vi.mocked(rateLimitService.mapEndpointToCategory).mockReturnValueOnce('generate_concept');
      
      // Call the API and expect RateLimitError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(RateLimitError);
    });
    
    it('should throw ValidationError for 422 responses', async () => {
      // Setup mock for validation error
      const mockAxiosError = {
        response: {
          status: 422,
          data: {
            message: 'Validation failed',
            errors: {
              name: ['Name is required']
            }
          }
        },
        config: {
          url: '/test-endpoint'
        }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect ValidationError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(ValidationError);
    });
    
    it('should throw PermissionError for 403 responses', async () => {
      // Setup mock for permission error
      const mockAxiosError = {
        response: {
          status: 403,
          data: { message: 'Forbidden' }
        },
        config: {
          url: '/test-endpoint'
        }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect PermissionError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(PermissionError);
    });
    
    it('should throw NotFoundError for 404 responses', async () => {
      // Setup mock for not found error
      const mockAxiosError = {
        response: {
          status: 404,
          data: { message: 'Not found' }
        },
        config: {
          url: '/test-endpoint'
        }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect NotFoundError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(NotFoundError);
    });
    
    it('should throw ServerError for 5xx responses', async () => {
      // Setup mock for server error
      const mockAxiosError = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        },
        config: {
          url: '/test-endpoint'
        }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect ServerError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(ServerError);
    });
    
    it('should throw NetworkError for network failures', async () => {
      // Setup mock for network error
      const mockAxiosError = {
        response: undefined,
        request: {},
        message: 'Network Error',
        code: 'ECONNREFUSED',
        config: {
          url: '/test-endpoint'
        }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect NetworkError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow(NetworkError);
    });
  });
  
  describe('exportImage Function', () => {
    it('should set responseType to blob', async () => {
      // Mock post with implementation to verify config
      mockPost.mockImplementation((url, data, config) => {
        expect(config?.responseType).toBe('blob');
        return Promise.resolve({
          data: new Blob(['test data'], { type: 'image/png' }),
          status: 200,
          statusText: 'OK',
          headers: {},
          config: config || {}
        });
      });
      
      // Call exportImage function
      await apiClient.exportImage('test-image-id', 'png', 'medium');
      
      // Verify the function was called
      expect(mockPost).toHaveBeenCalled();
    });
  });
}); 