import { vi } from 'vitest';

// Mock services/apiClient before importing
vi.mock('../../services/apiClient', () => {
  class RateLimitError extends Error {
    status: number;
    limit: number;
    current: number;
    period: string;
    resetAfterSeconds: number;
    category?: string;
    retryAfter?: Date;

    constructor(message: string, response: { limit?: number; current?: number; period?: string; reset_after_seconds?: number }) {
      super(message);
      this.name = 'RateLimitError';
      this.status = 429;
      this.limit = response.limit || 0;
      this.current = response.current || 0;
      this.period = response.period || 'unknown';
      this.resetAfterSeconds = response.reset_after_seconds || 0;
      
      if (this.resetAfterSeconds > 0) {
        this.retryAfter = new Date(Date.now() + this.resetAfterSeconds * 1000);
      }
    }
    
    getUserFriendlyMessage(): string {
      return `Rate limit reached (${this.current}/${this.limit}). Please try again later.`;
    }
    
    getCategoryDisplayName(): string {
      return 'Usage';
    }
  }

  return {
    RateLimitError,
    __esModule: true
  };
});

// Mock hooks/useErrorHandling
vi.mock('../../hooks/useErrorHandling', () => ({
  useErrorHandling: vi.fn()
}));

// Now import after mocking
import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { createAsyncErrorHandler, createQueryErrorHandler } from '../errorUtils';
import { RateLimitError } from '../../services/apiClient';

// Mock console methods
const originalConsole = {
  error: console.error,
  warn: console.warn
};

// Create a mock for document.dispatchEvent
const originalDispatchEvent = document.dispatchEvent;

describe('Error Utilities', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock console methods
    console.error = vi.fn();
    console.warn = vi.fn();
    // Mock document.dispatchEvent
    document.dispatchEvent = vi.fn();
  });

  afterEach(() => {
    // Restore original console methods
    console.error = originalConsole.error;
    console.warn = originalConsole.warn;
    // Restore document.dispatchEvent
    document.dispatchEvent = originalDispatchEvent;
  });

  describe('createAsyncErrorHandler', () => {
    // Mock error handler
    const mockErrorHandler = {
      handleError: vi.fn(),
      showErrorToast: vi.fn(),
      showAndClearError: vi.fn(),
      setError: vi.fn(),
      clearError: vi.fn(),
      isErrorVisible: false,
      error: null,
      errorType: null,
      errorDetails: null,
      originalError: null
    };

    it('should return the result of successful async operation', async () => {
      // Create error handler
      const errorHandler = createAsyncErrorHandler(mockErrorHandler);
      const mockOperation = vi.fn().mockResolvedValue('success');

      const result = await errorHandler(mockOperation, 'testOperation');

      expect(result).toBe('success');
      expect(mockOperation).toHaveBeenCalledTimes(1);
      expect(mockErrorHandler.handleError).not.toHaveBeenCalled();
      expect(mockErrorHandler.showErrorToast).not.toHaveBeenCalled();
    });

    it('should handle errors in async operations', async () => {
      // Create error handler
      const errorHandler = createAsyncErrorHandler(mockErrorHandler);
      const testError = new Error('Test error');
      const mockOperation = vi.fn().mockRejectedValue(testError);

      const result = await errorHandler(mockOperation, 'testOperation');

      expect(result).toBeUndefined();
      expect(mockOperation).toHaveBeenCalledTimes(1);
      expect(mockErrorHandler.handleError).toHaveBeenCalledWith(testError);
    });

    it('should show toast when showToast is true', async () => {
      // Create error handler with showToast option
      const errorHandler = createAsyncErrorHandler(mockErrorHandler, { showToast: true });
      const testError = new Error('Test error');
      const mockOperation = vi.fn().mockRejectedValue(testError);

      await errorHandler(mockOperation, 'testOperation');

      expect(mockErrorHandler.handleError).toHaveBeenCalledWith(testError);
      expect(mockErrorHandler.showErrorToast).toHaveBeenCalled();
    });

    it('should call onError callback when provided', async () => {
      const onErrorMock = vi.fn();
      // Create error handler with onError callback
      const errorHandler = createAsyncErrorHandler(mockErrorHandler, { onError: onErrorMock });
      const testError = new Error('Test error');
      const mockOperation = vi.fn().mockRejectedValue(testError);

      await errorHandler(mockOperation, 'testOperation');

      expect(mockErrorHandler.handleError).toHaveBeenCalledWith(testError);
      expect(onErrorMock).toHaveBeenCalledWith(testError);
    });
  });

  describe('createQueryErrorHandler', () => {
    // Mock error handler
    const mockErrorHandler = {
      handleError: vi.fn(),
      setError: vi.fn(),
      clearError: vi.fn(),
      showErrorToast: vi.fn(),
      error: null,
      errorType: null,
      errorDetails: null,
      originalError: null,
      isErrorVisible: false
    };

    it('should handle regular errors with handleError', () => {
      const queryErrorHandler = createQueryErrorHandler(mockErrorHandler);
      const testError = new Error('Test error');

      queryErrorHandler.onQueryError(testError);

      expect(mockErrorHandler.handleError).toHaveBeenCalledWith(testError);
      expect(document.dispatchEvent).not.toHaveBeenCalled();
    });

    it('should handle rate limit errors differently', () => {
      const queryErrorHandler = createQueryErrorHandler(mockErrorHandler);
      
      // Create a RateLimitError using the mock constructor
      const rateLimitError = new RateLimitError('Rate limit exceeded', {
        limit: 100,
        current: 101,
        period: 'month',
        reset_after_seconds: 3600
      });

      queryErrorHandler.onQueryError(rateLimitError);

      expect(mockErrorHandler.setError).toHaveBeenCalledWith(
        expect.any(String),
        'rateLimit',
        expect.any(String),
        rateLimitError
      );
      expect(mockErrorHandler.handleError).not.toHaveBeenCalled();
    });

    it('should dispatch toast event when showToast is true', () => {
      const queryErrorHandler = createQueryErrorHandler(mockErrorHandler, { showToast: true });
      const testError = new Error('Test error');

      queryErrorHandler.onQueryError(testError);

      expect(mockErrorHandler.handleError).toHaveBeenCalledWith(testError);
      expect(document.dispatchEvent).toHaveBeenCalled();
    });

    it('should use default error message when error has no message', () => {
      const queryErrorHandler = createQueryErrorHandler(mockErrorHandler, { 
        showToast: true,
        defaultErrorMessage: 'Custom default error'
      });
      
      queryErrorHandler.onQueryError({});

      expect(document.dispatchEvent).toHaveBeenCalled();
    });
  });
}); 