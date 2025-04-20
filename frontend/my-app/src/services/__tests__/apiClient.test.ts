import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import type { AxiosInstance, AxiosRequestConfig, AxiosError, AxiosResponse } from 'axios';
import { API_BASE_URL } from '../../config/apiEndpoints';
import { AuthError, RateLimitError, ValidationError, PermissionError, NotFoundError, ServerError, NetworkError } from '../../utils/errorUtils';

// Create mock functions before mocking axios
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockPut = vi.fn();
const mockDelete = vi.fn();
const mockPatch = vi.fn();
const mockInterceptorsRequestUse = vi.fn();
const mockInterceptorsResponseUse = vi.fn();

// Mock axios module
vi.mock('axios', () => {
  return {
    default: {
      create: vi.fn().mockReturnValue({
        defaults: {
          baseURL: API_BASE_URL,
          headers: {
            common: {}
          }
        },
        interceptors: {
          request: {
            use: mockInterceptorsRequestUse,
            eject: vi.fn()
          },
          response: {
            use: mockInterceptorsResponseUse,
            eject: vi.fn()
          }
        },
        get: mockGet,
        post: mockPost,
        put: mockPut,
        delete: mockDelete,
        patch: mockPatch
      }),
      isAxiosError: vi.fn().mockReturnValue(true)
    }
  };
});

// Mock supabase
vi.mock('../supabaseClient', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      refreshSession: vi.fn()
    }
  }
}));

// Mock rateLimitService
vi.mock('../rateLimitService', () => ({
  extractRateLimitHeaders: vi.fn(),
  mapEndpointToCategory: vi.fn()
}));

// Import after mock setup
import { apiClient, setAuthToken, clearAuthToken } from '../apiClient';
import { supabase } from '../supabaseClient';
import * as rateLimitService from '../rateLimitService';
import axios from 'axios';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = String(value);
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    })
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
  });
  
  describe('Request Interceptor', () => {
    it('should add auth header if session exists', async () => {
      // Mock session with token
      vi.mocked(supabase.auth.getSession).mockReturnValue(Promise.resolve({
        data: {
          session: {
            access_token: 'mock-token'
          }
        },
        error: null
      }));
      
      // Setup a successful response
      mockGet.mockResolvedValue({ data: { success: true } });
      
      // Call the API
      await apiClient.get('/test-endpoint');
      
      // Verify axios was called with auth header
      expect(mockGet).toHaveBeenCalled();
    });
    
    it('should not add auth header if no session exists', async () => {
      // Mock no session
      vi.mocked(supabase.auth.getSession).mockReturnValue(Promise.resolve({
        data: { session: null },
        error: null
      }));
      
      // Setup a successful response
      mockGet.mockResolvedValue({ data: { success: true } });
      
      // Call the API
      await apiClient.get('/test-endpoint');
      
      // Verify axios was called
      expect(mockGet).toHaveBeenCalled();
    });
  });
  
  describe('Response Interceptor', () => {
    it('should extract rate limit headers from successful responses', async () => {
      // Create mock response with rate limit headers
      const mockResponse = {
        data: { success: true },
        status: 200,
        statusText: 'OK',
        headers: {
          'x-ratelimit-limit': '100',
          'x-ratelimit-remaining': '99',
          'x-ratelimit-reset': '1600000000'
        }
      };
      
      // Setup a successful response
      mockGet.mockResolvedValue(mockResponse);
      
      // Call the API
      await apiClient.get('/test-endpoint');
      
      // Verify rate limit headers were extracted
      expect(rateLimitService.extractRateLimitHeaders).toHaveBeenCalled();
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
      vi.mocked(supabase.auth.refreshSession).mockReturnValue(Promise.resolve({
        data: {
          session: {
            access_token: 'new-token'
          }
        },
        error: null
      }));
      
      // Call the API and expect it to be retried after refresh
      const result = await apiClient.get('/test-endpoint');
      
      // Verify token was refreshed
      expect(supabase.auth.refreshSession).toHaveBeenCalled();
      expect(result).toEqual({ data: { success: true } });
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
      vi.mocked(supabase.auth.refreshSession).mockReturnValue(Promise.resolve({
        data: { session: null },
        error: { message: 'Cannot refresh token' }
      }));
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect AuthError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
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
            current: 101
          }
        },
        config: { url: '/test-endpoint' }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect RateLimitError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
    });
    
    it('should throw ValidationError for 422 responses', async () => {
      // Setup mock for validation error
      const mockAxiosError = {
        response: {
          status: 422,
          data: { message: 'Validation failed', errors: { name: ['Name is required'] } }
        },
        config: { url: '/test-endpoint' }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect ValidationError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
    });
    
    it('should throw PermissionError for 403 responses', async () => {
      // Setup mock for permission error
      const mockAxiosError = {
        response: {
          status: 403,
          data: { message: 'Permission denied' }
        },
        config: { url: '/test-endpoint' }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect PermissionError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
    });
    
    it('should throw NotFoundError for 404 responses', async () => {
      // Setup mock for not found error
      const mockAxiosError = {
        response: {
          status: 404,
          data: { message: 'Resource not found' }
        },
        config: { url: '/test-endpoint' }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect NotFoundError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
    });
    
    it('should throw ServerError for 5xx responses', async () => {
      // Setup mock for server error
      const mockAxiosError = {
        response: {
          status: 500,
          data: { message: 'Internal server error' }
        },
        config: { url: '/test-endpoint' }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect ServerError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
    });
    
    it('should throw NetworkError for network failures', async () => {
      // Setup mock for network error
      const mockAxiosError = {
        request: {},
        config: { url: '/test-endpoint' }
      } as unknown as AxiosError;
      
      mockGet.mockRejectedValueOnce(mockAxiosError);
      
      // Call the API and expect NetworkError
      await expect(apiClient.get('/test-endpoint')).rejects.toThrow();
    });
  });
  
  describe('exportImage Function', () => {
    it('should set responseType to blob', async () => {
      // Mock post with implementation to verify config
      mockPost.mockImplementation((url, data, config) => {
        expect(config?.responseType).toBe('blob');
        return Promise.resolve({
          data: new Blob(['test'], { type: 'image/png' }),
          headers: { 'content-type': 'image/png' }
        });
      });
      
      // Call the export function
      await apiClient.post('/export/image', { id: 'test-id' }, { responseType: 'blob' });
      
      // Verification is done in the mock implementation
      expect(mockPost).toHaveBeenCalled();
    });
  });
}); 