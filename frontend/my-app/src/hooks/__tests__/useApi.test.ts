import { renderHook, act, waitFor } from '@testing-library/react';
import { useApi } from '../useApi';
import * as AuthContext from '../../contexts/AuthContext';

// Mock the AuthContext
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: jest.fn()
}));

// Mock fetch globally
global.fetch = jest.fn();

describe('useApi Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Setup default mock values for AuthContext
    (AuthContext.useAuth as jest.Mock).mockReturnValue({
      session: {
        access_token: 'mock-access-token',
        user: { id: 'mock-user-id' }
      },
      isLoading: false,
      user: { id: 'mock-user-id' },
      isAnonymous: true,
      error: null
    });
  });

  // Mock successful response
  const mockSuccessResponse = { data: 'test data' };
  const mockJsonPromise = Promise.resolve(mockSuccessResponse);
  const mockFetchPromise = Promise.resolve({
    ok: true,
    json: () => mockJsonPromise,
    status: 200,
    statusText: 'OK',
  });

  // Mock error response
  const mockErrorResponse = { message: 'Not found' };
  const mockErrorJsonPromise = Promise.resolve(mockErrorResponse);
  const mockErrorFetchPromise = Promise.resolve({
    ok: false,
    json: () => mockErrorJsonPromise,
    status: 404,
    statusText: 'Not Found',
  });

  test('should return initial state', () => {
    const { result } = renderHook(() => useApi());
    
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeUndefined();
    expect(result.current.authInitialized).toBe(true);
  });

  test('should handle GET request successfully', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result } = renderHook(() => useApi());
    
    let responsePromise;
    act(() => {
      responsePromise = result.current.get('/test');
    });
    
    expect(result.current.loading).toBe(true);
    
    // Wait for the async operation to complete
    const response = await responsePromise;
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(response.data).toEqual(mockSuccessResponse);
    expect(result.current.error).toBeUndefined();
    
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/test'), expect.objectContaining({
      method: 'GET',
      headers: expect.objectContaining({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-access-token'
      }),
      body: undefined,
    }));
  });

  test('should handle POST request successfully', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result } = renderHook(() => useApi());
    const requestData = { test: 'data' };
    
    let responsePromise;
    act(() => {
      responsePromise = result.current.post('/test', requestData);
    });
    
    expect(result.current.loading).toBe(true);
    
    // Wait for the async operation to complete
    const response = await responsePromise;
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(response.data).toEqual(mockSuccessResponse);
    expect(result.current.error).toBeUndefined();
    
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/test'), expect.objectContaining({
      method: 'POST',
      headers: expect.objectContaining({
        'Content-Type': 'application/json',
        'Authorization': 'Bearer mock-access-token'
      }),
      body: JSON.stringify(requestData),
    }));
  });

  test('should handle API error responses', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockErrorFetchPromise);
    
    const { result } = renderHook(() => useApi());
    
    let responsePromise;
    act(() => {
      responsePromise = result.current.get('/test/nonexistent');
    });
    
    expect(result.current.loading).toBe(true);
    
    // Wait for the async operation to complete
    const response = await responsePromise;
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(response.error).toEqual(expect.objectContaining({
      status: 404,
      message: 'Not found',
    }));
    expect(result.current.error).toEqual(expect.objectContaining({
      status: 404,
      message: 'Not found',
    }));
  });

  test('should handle network errors', async () => {
    const networkError = new Error('Network error');
    (fetch as jest.Mock).mockImplementationOnce(() => Promise.reject(networkError));
    
    const { result } = renderHook(() => useApi());
    
    let responsePromise;
    act(() => {
      responsePromise = result.current.get('/test');
    });
    
    expect(result.current.loading).toBe(true);
    
    // Wait for the async operation to complete
    const response = await responsePromise;
    await waitFor(() => expect(result.current.loading).toBe(false));
    
    expect(response.error).toEqual(expect.objectContaining({
      status: 500,
      message: 'Network error',
    }));
    expect(result.current.error).toEqual(expect.objectContaining({
      status: 500,
      message: 'Network error',
    }));
  });

  test('should clear error when calling clearError', async () => {
    // Mock a failed fetch to generate an error
    const networkError = new Error('Network error');
    (fetch as jest.Mock).mockImplementationOnce(() => Promise.reject(networkError));
    
    const { result } = renderHook(() => useApi());
    
    // Generate an error
    let responsePromise;
    act(() => {
      responsePromise = result.current.get('/test');
    });
    
    // Wait for the error to be set
    await responsePromise;
    await waitFor(() => expect(result.current.error).toBeDefined());
    
    // Clear the error
    act(() => {
      result.current.clearError();
    });
    
    // Verify the error was cleared
    expect(result.current.error).toBeUndefined();
  });
  
  test('should handle request without auth token', async () => {
    // Mock AuthContext to return no session
    (AuthContext.useAuth as jest.Mock).mockReturnValue({
      session: null,
      isLoading: false,
      user: null,
      isAnonymous: true,
      error: null
    });
    
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result } = renderHook(() => useApi());
    
    let responsePromise;
    act(() => {
      responsePromise = result.current.get('/test');
    });
    
    // Wait for the async operation to complete
    const response = await responsePromise;
    
    // Should not have Authorization header
    expect(fetch).toHaveBeenCalledWith(expect.stringContaining('/test'), expect.objectContaining({
      headers: expect.not.objectContaining({
        'Authorization': expect.anything()
      })
    }));
    
    expect(response.data).toEqual(mockSuccessResponse);
  });
}); 