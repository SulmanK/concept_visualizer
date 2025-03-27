import { renderHook, act } from '@testing-library/react-hooks';
import { useApi } from '../useApi';

// Mock fetch globally
global.fetch = jest.fn();

describe('useApi Hook', () => {
  beforeEach(() => {
    jest.clearAllMocks();
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
    
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });

  test('should handle GET request successfully', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result, waitForNextUpdate } = renderHook(() => useApi());
    
    act(() => {
      result.current.get('/api/test');
    });
    
    expect(result.current.isLoading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toEqual(mockSuccessResponse);
    expect(result.current.error).toBeNull();
    
    expect(fetch).toHaveBeenCalledWith('/api/test', {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  test('should handle POST request successfully', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result, waitForNextUpdate } = renderHook(() => useApi());
    const requestData = { test: 'data' };
    
    act(() => {
      result.current.post('/api/test', requestData);
    });
    
    expect(result.current.isLoading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toEqual(mockSuccessResponse);
    expect(result.current.error).toBeNull();
    
    expect(fetch).toHaveBeenCalledWith('/api/test', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });
  });

  test('should handle PUT request successfully', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result, waitForNextUpdate } = renderHook(() => useApi());
    const requestData = { test: 'updated data' };
    
    act(() => {
      result.current.put('/api/test/1', requestData);
    });
    
    expect(result.current.isLoading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toEqual(mockSuccessResponse);
    expect(result.current.error).toBeNull();
    
    expect(fetch).toHaveBeenCalledWith('/api/test/1', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestData),
    });
  });

  test('should handle DELETE request successfully', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockFetchPromise);
    
    const { result, waitForNextUpdate } = renderHook(() => useApi());
    
    act(() => {
      result.current.delete('/api/test/1');
    });
    
    expect(result.current.isLoading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toEqual(mockSuccessResponse);
    expect(result.current.error).toBeNull();
    
    expect(fetch).toHaveBeenCalledWith('/api/test/1', {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
    });
  });

  test('should handle API error responses', async () => {
    (fetch as jest.Mock).mockImplementationOnce(() => mockErrorFetchPromise);
    
    const { result, waitForNextUpdate } = renderHook(() => useApi());
    
    act(() => {
      result.current.get('/api/test/nonexistent');
    });
    
    expect(result.current.isLoading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toEqual({
      status: 404,
      statusText: 'Not Found',
      message: 'Not found',
    });
  });

  test('should handle network errors', async () => {
    const networkError = new Error('Network error');
    (fetch as jest.Mock).mockImplementationOnce(() => Promise.reject(networkError));
    
    const { result, waitForNextUpdate } = renderHook(() => useApi());
    
    act(() => {
      result.current.get('/api/test');
    });
    
    expect(result.current.isLoading).toBe(true);
    
    await waitForNextUpdate();
    
    expect(result.current.isLoading).toBe(false);
    expect(result.current.data).toBeNull();
    expect(result.current.error).toEqual({
      status: 0,
      statusText: 'Network Error',
      message: 'Network error',
    });
  });

  test('should reset state when calling reset', () => {
    const { result } = renderHook(() => useApi());
    
    // Manually set some state
    result.current.setState({
      data: { some: 'data' },
      error: { status: 500, statusText: 'Error', message: 'An error occurred' },
      isLoading: false,
    });
    
    expect(result.current.data).toEqual({ some: 'data' });
    expect(result.current.error).not.toBeNull();
    
    // Reset the state
    act(() => {
      result.current.reset();
    });
    
    expect(result.current.data).toBeNull();
    expect(result.current.error).toBeNull();
    expect(result.current.isLoading).toBe(false);
  });
}); 