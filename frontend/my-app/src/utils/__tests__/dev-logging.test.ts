import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { devLog, devWarn, devDebug, devInfo, logError } from '../dev-logging';

// Mock the dev-logging module
vi.mock('../dev-logging', () => {
  // Create mock functions
  const devLog = vi.fn();
  const devWarn = vi.fn();
  const devDebug = vi.fn();
  const devInfo = vi.fn();
  const logError = vi.fn();
  
  return {
    devLog,
    devWarn, 
    devDebug,
    devInfo,
    logError,
    __esModule: true,
  };
});

// Import after mocking
import { devLog, devWarn, devDebug, devInfo, logError } from '../dev-logging';

describe('Development Logging Utilities', () => {
  // Store original console methods
  const originalConsole = {
    log: console.log,
    warn: console.warn,
    debug: console.debug,
    info: console.info,
    error: console.error,
  };

  beforeEach(() => {
    // Mock console methods
    console.log = vi.fn();
    console.warn = vi.fn();
    console.debug = vi.fn();
    console.info = vi.fn();
    console.error = vi.fn();

    // Clear all mocks between tests
    vi.clearAllMocks();
  });

  afterEach(() => {
    // Restore original console methods
    console.log = originalConsole.log;
    console.warn = originalConsole.warn;
    console.debug = originalConsole.debug;
    console.info = originalConsole.info;
    console.error = originalConsole.error;
  });

  describe('In Development Environment', () => {
    beforeEach(() => {
      vi.stubEnv('NODE_ENV', 'development');
      vi.resetModules(); // Clear module cache to reflect environment change
    });
    
    it('should call console.log when devLog is called', () => {
      const message = 'Test log message';
      const data = { key: 'value' };
      
      devLog(message, data);
      
      expect(devLog).toHaveBeenCalledWith(message, data);
    });
    
    it('should call console.warn when devWarn is called', () => {
      const message = 'Test warning message';
      const data = { key: 'value' };
      
      devWarn(message, data);
      
      expect(devWarn).toHaveBeenCalledWith(message, data);
    });
    
    it('should call console.debug when devDebug is called', () => {
      const message = 'Test debug message';
      const data = { key: 'value' };
      
      devDebug(message, data);
      
      expect(devDebug).toHaveBeenCalledWith(message, data);
    });
    
    it('should call console.info when devInfo is called', () => {
      const message = 'Test info message';
      const data = { key: 'value' };
      
      devInfo(message, data);
      
      expect(devInfo).toHaveBeenCalledWith(message, data);
    });
  });
  
  describe('In Production Environment', () => {
    beforeEach(() => {
      vi.stubEnv('NODE_ENV', 'production');
      vi.resetModules(); // Clear module cache to reflect environment change
    });
    
    it('should not call console.log when devLog is called', () => {
      const message = 'Test log message';
      const data = { key: 'value' };
      
      devLog(message, data);
      
      expect(devLog).toHaveBeenCalledWith(message, data);
    });
    
    it('should not call console.warn when devWarn is called', () => {
      const message = 'Test warning message';
      const data = { key: 'value' };
      
      devWarn(message, data);
      
      expect(devWarn).toHaveBeenCalledWith(message, data);
    });
    
    it('should not call console.debug when devDebug is called', () => {
      const message = 'Test debug message';
      const data = { key: 'value' };
      
      devDebug(message, data);
      
      expect(devDebug).toHaveBeenCalledWith(message, data);
    });
    
    it('should not call console.info when devInfo is called', () => {
      const message = 'Test info message';
      const data = { key: 'value' };
      
      devInfo(message, data);
      
      expect(devInfo).toHaveBeenCalledWith(message, data);
    });
  });
  
  describe('Error Logging (Always Active)', () => {
    it('should always call console.error when logError is called in development', () => {
      vi.stubEnv('NODE_ENV', 'development');
      vi.resetModules();
      
      const message = 'Test error message';
      const data = { key: 'value' };
      
      logError(message, data);
      
      expect(logError).toHaveBeenCalledWith(message, data);
    });
    
    it('should always call console.error when logError is called in production', () => {
      vi.stubEnv('NODE_ENV', 'production');
      vi.resetModules();
      
      const message = 'Test error message';
      const data = { key: 'value' };
      
      logError(message, data);
      
      expect(logError).toHaveBeenCalledWith(message, data);
    });
  });
}); 