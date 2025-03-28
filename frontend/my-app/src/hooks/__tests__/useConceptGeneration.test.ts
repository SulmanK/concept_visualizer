import { renderHook, act } from '@testing-library/react';
import { useConceptGeneration } from '../useConceptGeneration';
import { useApi } from '../useApi';

// Mock the useApi hook
jest.mock('../useApi', () => ({
  useApi: jest.fn(),
}));

describe('useConceptGeneration Hook', () => {
  // Mock success response
  const mockGenerationResponse = {
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

    const { result } = renderHook(() => useConceptGeneration());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
    expect(result.current.concepts).toEqual([]);
    expect(result.current.selectedConcept).toBeNull();
  });

  test('should generate concept successfully', async () => {
    // Mock the useApi hook implementation
    const postMock = jest.fn((_url, _data, callback) => {
      callback?.(mockGenerationResponse);
    });

    (useApi as jest.Mock).mockReturnValue({
      data: mockGenerationResponse,
      error: null,
      isLoading: false,
      post: postMock,
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptGeneration());

    // Call the generateConcept function
    act(() => {
      result.current.generateConcept('A violet gradient UI theme');
    });

    // Verify that the POST request was made
    expect(postMock).toHaveBeenCalledWith(
      '/api/concepts/generate',
      { prompt: 'A violet gradient UI theme' },
      expect.any(Function)
    );

    // Verify that the state was updated
    expect(result.current.concepts).toEqual([mockGenerationResponse]);
    expect(result.current.selectedConcept).toEqual(mockGenerationResponse);
  });

  test('should handle generation error', async () => {
    // Mock error state
    const mockError = {
      message: 'Failed to generate concept',
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

    const { result } = renderHook(() => useConceptGeneration());

    // Call the generateConcept function
    act(() => {
      result.current.generateConcept('A violet gradient UI theme');
    });

    // Verify that the error state was set
    expect(result.current.error).toEqual(mockError);
  });

  test('should set selected concept', () => {
    // Mock the useApi hook implementation
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: false,
      post: jest.fn(),
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptGeneration());

    // Manually set concepts array
    act(() => {
      result.current.setConcepts([mockGenerationResponse]);
    });

    // Set the selected concept
    act(() => {
      result.current.setSelectedConcept(mockGenerationResponse);
    });

    // Verify that the selected concept was set
    expect(result.current.selectedConcept).toEqual(mockGenerationResponse);
  });

  test('should clear concepts', () => {
    // Mock the useApi hook implementation
    (useApi as jest.Mock).mockReturnValue({
      data: null,
      error: null,
      isLoading: false,
      post: jest.fn(),
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptGeneration());

    // Manually set concepts array and selected concept
    act(() => {
      result.current.setConcepts([mockGenerationResponse]);
      result.current.setSelectedConcept(mockGenerationResponse);
    });

    // Verify concepts were set
    expect(result.current.concepts.length).toBe(1);
    expect(result.current.selectedConcept).not.toBeNull();

    // Clear concepts
    act(() => {
      result.current.clearConcepts();
    });

    // Verify that concepts and selected concept were cleared
    expect(result.current.concepts).toEqual([]);
    expect(result.current.selectedConcept).toBeNull();
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

    const { result } = renderHook(() => useConceptGeneration());

    // Verify loading state
    expect(result.current.isLoading).toBe(true);
  });

  test('should cache generated concepts', async () => {
    // Mock the useApi hook implementation
    const postMock = jest.fn((_url, _data, callback) => {
      callback?.(mockGenerationResponse);
    });

    (useApi as jest.Mock).mockReturnValue({
      data: mockGenerationResponse,
      error: null,
      isLoading: false,
      post: postMock,
      reset: jest.fn(),
    });

    const { result } = renderHook(() => useConceptGeneration());

    // Generate first concept
    act(() => {
      result.current.generateConcept('A violet gradient UI theme');
    });

    // Generate second concept with same prompt
    act(() => {
      result.current.generateConcept('A violet gradient UI theme');
    });

    // Verify that the API was only called once (caching worked)
    expect(postMock).toHaveBeenCalledTimes(1);
  });
}); 