import { renderHook, act, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { useConceptRefinement } from '../useConceptRefinement';
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
        if (endpoint.includes('/concepts/refine')) {
          return mockApiService.refineConcept(body);
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

describe('useConceptRefinement Hook', () => {
  // Reset mocks before each test
  beforeEach(() => {
    resetMockApi();
  });
  
  test('should return initial state', () => {
    const { result } = renderHook(() => useConceptRefinement());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.result).toBeNull();
    expect(result.current.status).toBe('idle');
  });

  test('should handle validation errors', () => {
    const { result } = renderHook(() => useConceptRefinement());

    // Call refineConcept with empty strings
    act(() => {
      result.current.refineConcept('', '');
    });

    // Verify validation error
    expect(result.current.status).toBe('error');
    expect(result.current.error).toBe('Please provide both an image to refine and refinement instructions');
  });

  test('should set status to submitting when valid inputs are provided', () => {
    const { result } = renderHook(() => useConceptRefinement());

    // Call refineConcept with valid inputs
    act(() => {
      result.current.refineConcept(
        'https://example.com/image.jpg',
        'Make it more vibrant'
      );
    });

    // Verify submitting state
    expect(result.current.status).toBe('submitting');
    expect(result.current.isLoading).toBe(true);
  });
  
  test('should handle successful concept refinement', async () => {
    // Setup mock API with custom response
    setupMockApi({
      responseDelay: 10, // Fast response for tests
      customResponses: {
        refineConcept: {
          imageUrl: 'https://example.com/refined-concept.png',
          colorPalette: {
            primary: '#123456',
            secondary: '#654321',
            accent: '#ABCDEF',
            background: '#FFFFFF',
            text: '#000000'
          },
          generationId: 'refined-123',
          createdAt: '2023-05-01T12:00:00Z',
          originalImageUrl: 'https://example.com/original.png',
          refinementPrompt: 'Make it more vibrant'
        }
      }
    });
    
    const { result } = renderHook(() => useConceptRefinement());
    
    // Call refineConcept with valid inputs
    act(() => {
      result.current.refineConcept(
        'https://example.com/original.png',
        'Make it more vibrant',
        'Updated logo description',
        'Updated theme description',
        ['colors', 'style']
      );
    });
    
    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.status).toBe('success');
    });
    
    // Verify success state
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.result).toEqual(expect.objectContaining({
      imageUrl: 'https://example.com/refined-concept.png',
      colorPalette: expect.objectContaining({
        primary: '#123456',
        secondary: '#654321'
      }),
      generationId: 'refined-123',
      originalImageUrl: 'https://example.com/original.png',
      refinementPrompt: 'Make it more vibrant'
    }));
  });
  
  test('should handle API errors', async () => {
    // Setup mock API to fail
    mockApiFailure();
    
    const { result } = renderHook(() => useConceptRefinement());
    
    // Call refineConcept with valid inputs
    act(() => {
      result.current.refineConcept(
        'https://example.com/original.png',
        'Make it more vibrant'
      );
    });
    
    // Wait for the async operation to complete
    await waitFor(() => {
      expect(result.current.status).toBe('error');
    });
    
    // Verify error state
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Failed to refine concept');
    expect(result.current.result).toBeNull();
  });
}); 