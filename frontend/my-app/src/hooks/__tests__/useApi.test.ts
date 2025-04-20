import { apiClient } from '../../services/apiClient';
import axios from 'axios';
import { vi, describe, test, expect, beforeEach } from 'vitest';

// Mock axios
vi.mock('axios', () => ({
  default: {
    isAxiosError: vi.fn(),
    create: vi.fn().mockReturnValue(vi.fn().mockImplementation((config) => {
      // Return a promise that resolves with a response object
      return Promise.resolve({
        data: 'mocked data',
        status: 200,
        statusText: 'OK',
        headers: {},
        config
      });
    }))
  }
}));

describe('apiClient', () => {
  // Get the mocked axios instance
  const mockedAxios = axios.create();
  
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('apiClient.get should call axios instance get method', async () => {
    const mockResponse = { data: 'test data' };
    // Update mock to resolve with the response
    mockedAxios.mockResolvedValueOnce(mockResponse);
    
    await apiClient.get('/test-endpoint');
    
    // Check if axios instance was called with the proper config
    expect(mockedAxios).toHaveBeenCalledWith(
      expect.objectContaining({
        method: 'GET',
        url: expect.stringContaining('/test-endpoint')
      })
    );
  });

  test('apiClient.post should call axios instance post method', async () => {
    const mockResponse = { data: 'test data' };
    const requestData = { test: 'data' };
    
    mockedAxios.mockResolvedValueOnce(mockResponse);
    
    await apiClient.post('/test-endpoint', requestData);
    
    expect(mockedAxios).toHaveBeenCalledWith(
      expect.objectContaining({
        method: 'POST',
        url: expect.stringContaining('/test-endpoint'),
        data: requestData
      })
    );
  });

  test('apiClient.exportImage should make a POST request with blob response type', async () => {
    const mockBlob = new Blob(['test data'], { type: 'image/png' });
    const mockResponse = { data: mockBlob };
    
    mockedAxios.mockResolvedValueOnce(mockResponse);
    
    const result = await apiClient.exportImage(
      'test-image-path',
      'png',
      'medium'
    );
    
    expect(mockedAxios).toHaveBeenCalledWith(
      expect.objectContaining({
        method: 'POST',
        url: expect.stringContaining('/export/process'),
        data: expect.objectContaining({
          image_identifier: 'test-image-path',
          target_format: 'png',
          target_size: 'medium'
        }),
        responseType: 'blob'
      })
    );
    
    expect(result).toBe(mockBlob);
  });
}); 