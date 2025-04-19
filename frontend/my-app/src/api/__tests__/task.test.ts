import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { fetchTaskStatus, cancelTask } from '../task';
import { apiClient } from '../../services/apiClient';
import { API_ENDPOINTS } from '../../config/apiEndpoints';

// Mock the apiClient
vi.mock('../../services/apiClient', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}));

describe('Task API', () => {
  const mockTaskId = 'test-task-id';
  const mockTaskResponse = {
    id: mockTaskId,
    task_id: mockTaskId,
    status: 'completed',
    created_at: '2023-01-01T00:00:00Z',
    result_id: 'result-123',
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe('fetchTaskStatus', () => {
    it('should call apiClient.get with the correct URL', async () => {
      // Mock the apiClient.get response
      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: mockTaskResponse,
      });

      // Call the function
      const result = await fetchTaskStatus(mockTaskId);

      // Verify that apiClient.get was called with the correct URL
      expect(apiClient.get).toHaveBeenCalledWith(API_ENDPOINTS.TASK_STATUS_BY_ID(mockTaskId));
      
      // Verify the result is correct
      expect(result).toEqual(mockTaskResponse);
    });

    it('should normalize the response when id is missing but task_id is present', async () => {
      // Create a response missing the id property
      const responseWithoutId = {
        task_id: mockTaskId,
        status: 'completed',
        created_at: '2023-01-01T00:00:00Z',
        result_id: 'result-123',
      };
      
      // Mock the apiClient.get response
      vi.mocked(apiClient.get).mockResolvedValueOnce({
        data: responseWithoutId,
      });

      // Call the function
      const result = await fetchTaskStatus(mockTaskId);

      // Verify that the response was normalized with the id field added
      expect(result.id).toBe(mockTaskId);
      expect(result.id).toBe(result.task_id);
    });

    it('should throw an error when no taskId is provided', async () => {
      // Call the function with an empty string
      await expect(fetchTaskStatus('')).rejects.toThrow('No task ID provided for status check');
    });
  });

  describe('cancelTask', () => {
    it('should call apiClient.post with the correct URL', async () => {
      // Mock the apiClient.post response
      vi.mocked(apiClient.post).mockResolvedValueOnce({
        data: { ...mockTaskResponse, status: 'canceled' },
      });

      // Call the function
      const result = await cancelTask(mockTaskId);

      // Verify that apiClient.post was called with the correct URL and empty body
      expect(apiClient.post).toHaveBeenCalledWith(API_ENDPOINTS.TASK_CANCEL(mockTaskId), {});
      
      // Verify the result is correct
      expect(result.status).toBe('canceled');
    });

    it('should throw an error when no taskId is provided', async () => {
      // Call the function with an empty string
      await expect(cancelTask('')).rejects.toThrow('No task ID provided for cancellation');
    });
  });
}); 