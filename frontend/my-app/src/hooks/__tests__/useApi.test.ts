import { apiClient } from '../../services/apiClient';
import axios from 'axios';

// Mock axios
jest.mock('axios', () => ({
  isAxiosError: jest.fn(),
  create: jest.fn().mockReturnValue({
    interceptors: {
      request: { use: jest.fn() },
      response: { use: jest.fn() }
    },
    get: jest.fn(),
    post: jest.fn()
  })
}));

describe('apiClient', () => {
  const mockedAxios = axios.create() as jest.Mocked<typeof axios>;
  
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('apiClient.get should call axios instance get method', async () => {
    const mockResponse = { data: 'test data' };
    mockedAxios.get.mockResolvedValueOnce(mockResponse);
    
    await apiClient.get('/test-endpoint');
    
    expect(mockedAxios.get).toHaveBeenCalledWith(
      expect.stringContaining('/test-endpoint'),
      expect.any(Object)
    );
  });

  test('apiClient.post should call axios instance post method', async () => {
    const mockResponse = { data: 'test data' };
    const requestData = { test: 'data' };
    
    mockedAxios.post.mockResolvedValueOnce(mockResponse);
    
    await apiClient.post('/test-endpoint', requestData);
    
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/test-endpoint'),
      requestData,
      expect.any(Object)
    );
  });

  test('apiClient.exportImage should make a POST request with blob response type', async () => {
    const mockBlob = new Blob(['test data'], { type: 'image/png' });
    const mockResponse = { data: mockBlob };
    
    mockedAxios.post.mockResolvedValueOnce(mockResponse);
    
    const result = await apiClient.exportImage(
      'test-image-path',
      'png',
      'medium'
    );
    
    expect(mockedAxios.post).toHaveBeenCalledWith(
      expect.stringContaining('/export/process'),
      expect.objectContaining({
        image_identifier: 'test-image-path',
        target_format: 'png',
        target_size: 'medium'
      }),
      expect.objectContaining({
        responseType: 'blob'
      })
    );
    
    expect(result).toBe(mockBlob);
  });
}); 