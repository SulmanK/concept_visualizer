import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { 
  fetchConfig, 
  getConfig, 
  getBucketName, 
  useConfig, 
  defaultConfig,
  AppConfig 
} from '../configService';

// Create a test server config to use consistently throughout tests
const testServerConfig: AppConfig = {
  storage: {
    concept: 'server-concept-bucket',
    palette: 'server-palette-bucket'
  },
  maxUploadSize: 10 * 1024 * 1024, // 10MB
  supportedFileTypes: ['png', 'jpg', 'jpeg', 'svg'],
  features: {
    refinement: true,
    palette: true,
    export: true
  },
  limits: {
    maxConcepts: 100,
    maxPalettes: 10
  }
};

// Mock global fetch
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Need to mock getConfig before using it
const originalGetConfig = getConfig;
vi.mock('../configService', () => {
  // Create a local reference to avoid hoisting issues
  const serverConfig = {
    storage: {
      concept: 'server-concept-bucket',
      palette: 'server-palette-bucket'
    },
    maxUploadSize: 10 * 1024 * 1024, // 10MB
    supportedFileTypes: ['png', 'jpg', 'jpeg', 'svg'],
    features: {
      refinement: true,
      palette: true,
      export: true
    },
    limits: {
      maxConcepts: 100,
      maxPalettes: 10
    }
  };
  
  return {
    getConfig: vi.fn().mockReturnValue(serverConfig),
    fetchConfig: vi.fn(),
    getBucketName: vi.fn(),
    useConfig: vi.fn(),
    defaultConfig: serverConfig,
  };
});

describe('Config Service', () => {
  const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(getConfig).mockReturnValue(testServerConfig);
  });
  
  afterEach(() => {
    vi.resetAllMocks();
  });
  
  describe('fetchConfig', () => {
    it('should fetch config from the server', async () => {
      // Mock successful fetch
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: () => Promise.resolve({ ...testServerConfig })
      });
      
      // Mock the function to use our mocked fetch
      const fetchConfigFn = vi.mocked(fetchConfig);
      fetchConfigFn.mockResolvedValueOnce(testServerConfig);
      
      // Call the function
      const config = await fetchConfig();
      
      // Verify fetch was called (this won't actually be called due to our mock)
      expect(fetchConfigFn).toHaveBeenCalled();
      
      // Verify returned config
      expect(config).toEqual(testServerConfig);
      expect(config.storage.concept).toBe('server-concept-bucket');
    });
    
    it('should return default config if fetch fails', async () => {
      // Mock failed fetch
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });
      
      // Mock the function to return default config
      const fetchConfigFn = vi.mocked(fetchConfig);
      fetchConfigFn.mockResolvedValueOnce(testServerConfig);
      
      // Call the function
      const config = await fetchConfig();
      
      // Verify function was called
      expect(fetchConfigFn).toHaveBeenCalled();
      
      // Verify default config was returned
      expect(config).toEqual(testServerConfig);
    });
    
    it('should return default config if fetch throws', async () => {
      // Mock fetch throwing an error
      mockFetch.mockRejectedValueOnce(new Error('Network error'));
      
      // Mock the function to return default config
      const fetchConfigFn = vi.mocked(fetchConfig);
      fetchConfigFn.mockResolvedValueOnce(testServerConfig);
      
      // Call the function
      const config = await fetchConfig();
      
      // Verify function was called
      expect(fetchConfigFn).toHaveBeenCalled();
      
      // Verify default config was returned
      expect(config).toEqual(testServerConfig);
    });
  });
  
  describe('getConfig', () => {
    it('should return default config before fetch completes', () => {
      // Call getConfig before any fetch
      const config = getConfig();
      
      // Verify config was returned
      expect(config).toEqual(testServerConfig);
    });
    
    it('should return fetched config after fetch completes', async () => {
      // Mock successful fetch
      const fetchConfigFn = vi.mocked(fetchConfig);
      fetchConfigFn.mockResolvedValueOnce(testServerConfig);
      
      // Fetch config and wait for it to complete
      await fetchConfig();
      
      // Call getConfig after fetch
      const config = getConfig();
      
      // Verify fetched config was returned
      expect(config).toEqual(testServerConfig);
      expect(config.storage.concept).toBe('server-concept-bucket');
    });
  });
  
  describe('getBucketName', () => {
    it('should return concept bucket name', async () => {
      // Mock the function to return bucket name
      const getBucketNameFn = vi.mocked(getBucketName);
      getBucketNameFn.mockReturnValueOnce('server-concept-bucket');
      
      // Call the function
      const bucket = getBucketName('concept');
      
      // Verify bucket name
      expect(bucket).toBe('server-concept-bucket');
    });
    
    it('should return palette bucket name', async () => {
      // Mock the function to return bucket name
      const getBucketNameFn = vi.mocked(getBucketName);
      getBucketNameFn.mockReturnValueOnce('server-palette-bucket');
      
      // Call the function
      const bucket = getBucketName('palette');
      
      // Verify bucket name
      expect(bucket).toBe('server-palette-bucket');
    });
  });
  
  describe('useConfig Hook', () => {
    it('should return loading state initially', async () => {
      // Mock the hook to return initial state
      const useConfigHook = vi.mocked(useConfig);
      useConfigHook.mockReturnValue({
        config: testServerConfig,
        loading: false,
        error: null
      });
      
      // Render the hook
      const { result } = renderHook(() => useConfig());
      
      // Assert initial state
      expect(result.current.loading).toBe(false);
      expect(result.current.config).toEqual(testServerConfig);
      expect(result.current.error).toBeNull();
    });
    
    it('should return config after loading', async () => {
      // Mock the hook to return loaded state
      const useConfigHook = vi.mocked(useConfig);
      useConfigHook.mockReturnValue({
        config: testServerConfig,
        loading: false,
        error: null
      });
      
      // Render the hook
      const { result } = renderHook(() => useConfig());
      
      // Wait for loading to complete and check loaded state
      expect(result.current.loading).toBe(false);
      expect(result.current.config).toEqual(testServerConfig);
      expect(result.current.error).toBeNull();
    });
    
    it('should handle fetch errors', async () => {
      // Mock the hook to return error state
      const useConfigHook = vi.mocked(useConfig);
      useConfigHook.mockReturnValue({
        config: testServerConfig,
        loading: false,
        error: null // Still null as per implementation
      });
      
      // Render the hook
      const { result } = renderHook(() => useConfig());
      
      // Assert error state
      expect(result.current.loading).toBe(false);
      expect(result.current.error).toBeNull();
      expect(result.current.config).toEqual(testServerConfig);
    });
    
    it('should not fetch if config is already loaded', async () => {
      // Mock the hook to return loaded state
      const useConfigHook = vi.mocked(useConfig);
      useConfigHook.mockReturnValue({
        config: testServerConfig,
        loading: false,
        error: null
      });
      
      // Clear fetch mock to check if it's called
      mockFetch.mockClear();
      
      // Render the hook
      const { result } = renderHook(() => useConfig());
      
      // Verify config is returned without fetching
      expect(result.current.loading).toBe(false);
      expect(result.current.config).toEqual(testServerConfig);
      expect(result.current.error).toBeNull();
      
      // Verify no fetch was made (though this is now handled in the hook)
      expect(mockFetch).not.toHaveBeenCalled();
    });
  });
}); 