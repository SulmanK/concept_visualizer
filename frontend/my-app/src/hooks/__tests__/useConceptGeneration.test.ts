import { renderHook, act, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { useConceptGeneration } from '../useConceptGeneration';
import { mockApiService } from '../../services/mocks/mockApiService';
import { 
  setupMockApi, 
  resetMockApi, 
  mockApiFailure 
} from '../../services/mocks/testSetup';

// Mock the actual useApi hook to use our mock implementation
vi.mock('../useApi', () => {
  return {
    useApi: () => {
      const post = async (endpoint: string, body: any) => {
        if (endpoint.includes('/concepts/generate')) {
          return mockApiService.generateConcept(body);
        }
        return { error: { status: 404, message: 'Not found' }, loading: false };
      };
      
      return {
        post,
        loading: false,
        error: undefined,
        clearError: vi.fn(),
      };
    }
  };
});

describe('useConceptGeneration Hook', () => {
  // Reset mocks before each test
  beforeEach(() => {
    resetMockApi();
  });
  
  test('should return initial state', () => {
    const { result } = renderHook(() => useConceptGeneration());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.result).toBeNull();
    expect(result.current.status).toBe('idle');
  });

  test('should handle validation errors correctly', () => {
    const { result } = renderHook(() => useConceptGeneration());

    // Call generateConcept with empty strings
    act(() => {
      result.current.generateConcept('', '');
    });

    // Verify validation error
    expect(result.current.status).toBe('error');
    expect(result.current.error).toBe('Please provide both logo and theme descriptions');
  });

  test('should set status to submitting when valid inputs are provided', () => {
    const { result } = renderHook(() => useConceptGeneration());

    // Call generateConcept with valid inputs
    act(() => {
      result.current.generateConcept('Valid logo description', 'Valid theme description');
    });

    // Verify submitting state
    expect(result.current.status).toBe('submitting');
    expect(result.current.isLoading).toBe(true);
  });
  
  test('should handle successful concept generation', async () => {
    // Setup mock API with custom response
    setupMockApi({
      responseDelay: 10, // Fast response for tests
      customResponses: {
        generateConcept: {
          imageUrl: 'https://example.com/test-concept.png',
          colorPalette: {
            primary: '#123456',
            secondary: '#654321',
            accent: '#ABCDEF',
            background: '#FFFFFF',
            text: '#000000'
          },
          generationId: 'test-123',
          createdAt: '2023-05-01T12:00:00Z'
        }
      }
    });
    
    const { result } = renderHook(() => useConceptGeneration());
    
    // Call generateConcept with valid inputs
    act(() => {
      result.current.generateConcept('Test logo', 'Test theme');
    });
    
    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });
    
    // Verify success state
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.result).toEqual(expect.objectContaining({
      imageUrl: 'https://example.com/test-concept.png',
      colorPalette: expect.objectContaining({
        primary: '#123456',
        secondary: '#654321'
      }),
      generationId: 'test-123'
    }));
  });
  
  test('should handle API errors', async () => {
    // Setup mock API to fail
    mockApiFailure();
    
    const { result } = renderHook(() => useConceptGeneration());
    
    // Call generateConcept with valid inputs
    act(() => {
      result.current.generateConcept('Test logo', 'Test theme');
    });
    
    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.status).toBe('error');
    });
    
    // Verify error state
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Failed to generate concept');
    expect(result.current.result).toBeNull();
  });
  
  test('should reset generation state', async () => {
    // First generate a concept
    const { result } = renderHook(() => useConceptGeneration());
    
    // Call generateConcept
    act(() => {
      result.current.generateConcept('Test logo', 'Test theme');
    });
    
    // Wait for success state
    await waitFor(() => {
      expect(result.current.status).not.toBe('submitting');
    });
    
    // Reset the generation
    act(() => {
      result.current.resetGeneration();
    });
    
    // Verify reset state
    expect(result.current.status).toBe('idle');
    expect(result.current.result).toBeNull();
    expect(result.current.error).toBeNull();
  });
}); 