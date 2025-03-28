import { renderHook, act } from '@testing-library/react';
import { useConceptRefinement } from '../useConceptRefinement';
import { useApi } from '../useApi';

// Mock the useApi hook
jest.mock('../useApi', () => ({
  useApi: jest.fn(),
}));

describe('useConceptRefinement Hook', () => {
  // Mock original concept
  const mockOriginalConcept = {
    id: 'concept-123',
    prompt: 'A violet gradient UI theme',
    palettes: [
      {
        name: 'Violet Dream',
        colors: [
          { hex: '#4C1D95', name: 'Deep Purple' },
          { hex: '#7C3AED', name: 'Violet' },
          { hex: '#A78BFA', name: 'Lavender' },
          { hex: '#C4B5FD', name: 'Light Lavender' },
          { hex: '#EDE9FE', name: 'Pale Lavender' },
        ],
        description: 'A gradient of purple shades',
      },
    ],
    message: 'Concept generated successfully',
  };

  // Mock refined concept
  const mockRefinedConcept = {
    id: 'concept-456',
    prompt: 'A violet gradient UI theme, make it darker',
    originalConceptId: 'concept-123',
    palettes: [
      {
        name: 'Dark Violet',
        colors: [
          { hex: '#2D1151', name: 'Midnight Purple' },
          { hex: '#4C1D95', name: 'Deep Purple' },
          { hex: '#6D28D9', name: 'Royal Violet' },
          { hex: '#7C3AED', name: 'Violet' },
          { hex: '#8B5CF6', name: 'Bright Violet' },
        ],
        description: 'A darker gradient of violet shades',
      },
    ],
    message: 'Concept refined successfully',
  };

  // Reset all mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('should return initial state', () => {
    // Mock the useApi hook implementation
    const postMock = jest.fn();
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: false,
      post: postMock,
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.refinements).toEqual([]);
    expect(result.current.selectedRefinement).toBeNull();
  });

  test('should refine concept successfully', async () => {
    // Mock the useApi hook implementation
    const postMock = jest.fn((_url, _data, callback) => {
      callback?.(mockRefinedConcept);
    });

    (useApi as jest.Mock).mockReturnValue({
      data: mockRefinedConcept,
      error: null,
      isLoading: false,
      post: postMock,
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    // Call the refineConcept function
    act(() => {
      result.current.refineConcept(
        mockOriginalConcept.id,
        'make it darker'
      );
    });

    // Verify that the POST request was made
    expect(postMock).toHaveBeenCalledWith(
      '/api/concepts/refine',
      {
        originalConceptId: mockOriginalConcept.id,
        refinementPrompt: 'make it darker',
      },
      expect.any(Function)
    );

    // Verify that the state was updated
    expect(result.current.refinements).toEqual([mockRefinedConcept]);
    expect(result.current.selectedRefinement).toEqual(mockRefinedConcept);
  });

  test('should handle refinement error', async () => {
    // Mock error state
    const mockError = {
      message: 'Failed to refine concept',
      status: 500,
      statusText: 'Internal Server Error',
    };

    // Mock the useApi hook implementation with error
    const postMock = jest.fn();
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: mockError,
      isLoading: false,
      post: postMock,
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    // Call the refineConcept function
    act(() => {
      result.current.refineConcept(
        mockOriginalConcept.id,
        'make it darker'
      );
    });

    // Verify that the error state was set
    expect(result.current.error).toEqual(mockError);
  });

  test('should set selected refinement', () => {
    // Mock the useApi hook implementation
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: false,
      post: jest.fn(),
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    // Manually set refinements array
    act(() => {
      result.current.setRefinements([mockRefinedConcept]);
    });

    // Set the selected refinement
    act(() => {
      result.current.setSelectedRefinement(mockRefinedConcept);
    });

    // Verify that the selected refinement was set
    expect(result.current.selectedRefinement).toEqual(mockRefinedConcept);
  });

  test('should clear refinements', () => {
    // Mock the useApi hook implementation
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: false,
      post: jest.fn(),
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    // Manually set refinements array and selected refinement
    act(() => {
      result.current.setRefinements([mockRefinedConcept]);
      result.current.setSelectedRefinement(mockRefinedConcept);
    });

    // Verify refinements were set
    expect(result.current.refinements.length).toBe(1);
    expect(result.current.selectedRefinement).not.toBeNull();

    // Clear refinements
    act(() => {
      result.current.clearRefinements();
    });

    // Verify that refinements and selected refinement were cleared
    expect(result.current.refinements).toEqual([]);
    expect(result.current.selectedRefinement).toBeNull();
  });

  test('should handle loading state', () => {
    // Mock the useApi hook implementation with loading state
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: true,
      post: jest.fn(),
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    // Verify loading state
    expect(result.current.isLoading).toBe(true);
  });

  test('should track refinement history for a concept', async () => {
    // Mock the useApi hook implementation
    const postMock = jest.fn((_url, _data, callback) => {
      callback?.(mockRefinedConcept);
    });

    (useApi as jest.Mock).mockReturnValue({
      data: mockRefinedConcept,
      error: null,
      isLoading: false,
      post: postMock,
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptRefinement());

    // Make first refinement
    act(() => {
      result.current.refineConcept(
        mockOriginalConcept.id,
        'make it darker'
      );
    });

    // Create a second refinement with different data
    const secondRefinement = {
      ...mockRefinedConcept,
      id: 'concept-789',
      prompt: 'A violet gradient UI theme, add more blue tones',
    };

    // Update the mock to return the second refinement
    postMock.mockImplementationOnce((_url, _data, callback) => {
      callback?.(secondRefinement);
    });

    // Make second refinement
    act(() => {
      result.current.refineConcept(
        mockOriginalConcept.id,
        'add more blue tones'
      );
    });

    // Verify that we have two refinements in history
    expect(result.current.refinements.length).toBe(2);
    expect(result.current.refinements[0]).toEqual(mockRefinedConcept);
    expect(result.current.refinements[1]).toEqual(secondRefinement);
    expect(result.current.selectedRefinement).toEqual(secondRefinement);
  });
}); 