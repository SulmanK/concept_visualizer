import { describe, it, expect } from 'vitest';
import { 
  DEFAULT_POLLING_INTERVAL, 
  TASK_STATUS, 
  API_ENDPOINTS 
} from '../apiEndpoints';

describe('API Endpoints Configuration', () => {
  describe('DEFAULT_POLLING_INTERVAL', () => {
    it('should be set to 2000 milliseconds', () => {
      expect(DEFAULT_POLLING_INTERVAL).toBe(2000);
    });
  });

  describe('TASK_STATUS', () => {
    it('should define the base path', () => {
      expect(TASK_STATUS.BASE_PATH).toBe('tasks');
    });

    it('should define all task status types', () => {
      expect(TASK_STATUS.PENDING).toBe('pending');
      expect(TASK_STATUS.PROCESSING).toBe('processing');
      expect(TASK_STATUS.COMPLETED).toBe('completed');
      expect(TASK_STATUS.FAILED).toBe('failed');
      expect(TASK_STATUS.CANCELED).toBe('canceled');
    });
  });

  describe('API_ENDPOINTS', () => {
    it('should define the generate concept endpoint', () => {
      expect(API_ENDPOINTS.GENERATE_CONCEPT).toBe('concepts/generate-with-palettes');
    });

    it('should define the refine concept endpoint', () => {
      expect(API_ENDPOINTS.REFINE_CONCEPT).toBe('concepts/refine');
    });

    it('should define the recent concepts endpoint', () => {
      expect(API_ENDPOINTS.RECENT_CONCEPTS).toBe('storage/recent');
    });

    it('should define the export image endpoint', () => {
      expect(API_ENDPOINTS.EXPORT_IMAGE).toBe('export/process');
    });

    it('should define the rate limits endpoint', () => {
      expect(API_ENDPOINTS.RATE_LIMITS).toBe('health/rate-limits-status');
    });

    it('should generate the correct task status URL from a task ID', () => {
      const taskId = 'test-task-123';
      const expectedUrl = 'tasks/test-task-123';
      expect(API_ENDPOINTS.TASK_STATUS_BY_ID(taskId)).toBe(expectedUrl);
    });

    it('should generate the correct task cancel URL from a task ID', () => {
      const taskId = 'test-task-123';
      const expectedUrl = 'tasks/test-task-123/cancel';
      expect(API_ENDPOINTS.TASK_CANCEL(taskId)).toBe(expectedUrl);
    });

    it('should generate the correct concept detail URL from a concept ID', () => {
      const conceptId = 'concept-123';
      const expectedUrl = 'storage/concept/concept-123';
      expect(API_ENDPOINTS.CONCEPT_DETAIL(conceptId)).toBe(expectedUrl);
    });
  });
}); 