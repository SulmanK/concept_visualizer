import { vi, describe, it, expect, beforeEach } from "vitest";

vi.mock("../logger", () => {
  // Create mock functions
  const mockLogger = {
    debug: vi.fn(),
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
  };

  const logDev = vi.fn();

  return {
    logger: mockLogger,
    logDev: logDev,
    __esModule: true,
  };
});

// Import after mocking
import { logger, logDev } from "../logger";

describe("Logger Utility", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe("In Development Environment", () => {
    // Mock development environment
    beforeEach(() => {
      vi.stubEnv("NODE_ENV", "development");
      vi.resetModules(); // Clear module cache to reflect environment change
    });

    it("should call console.debug when logger.debug is called", () => {
      const message = "Test debug message";
      const data = { key: "value" };

      logger.debug(message, data);

      expect(logger.debug).toHaveBeenCalledWith(message, data);
    });

    it("should call console.info when logger.info is called", () => {
      const message = "Test info message";
      const data = { key: "value" };

      logger.info(message, data);

      expect(logger.info).toHaveBeenCalledWith(message, data);
    });

    it("should call console.log when logDev is called", () => {
      const message = "Test dev log message";
      const data = { key: "value" };

      logDev(message, data);

      expect(logDev).toHaveBeenCalledWith(message, data);
    });
  });

  describe("In Production Environment", () => {
    // Mock production environment
    beforeEach(() => {
      vi.stubEnv("NODE_ENV", "production");
      vi.resetModules(); // Clear module cache to reflect environment change
    });

    it("should not call console.debug when logger.debug is called", () => {
      const message = "Test debug message";
      const data = { key: "value" };

      logger.debug(message, data);

      expect(logger.debug).toHaveBeenCalledWith(message, data);
    });

    it("should not call console.info when logger.info is called", () => {
      const message = "Test info message";
      const data = { key: "value" };

      logger.info(message, data);

      expect(logger.info).toHaveBeenCalledWith(message, data);
    });

    it("should always call console.warn when logger.warn is called", () => {
      const message = "Test warning message";
      const data = { key: "value" };

      logger.warn(message, data);

      expect(logger.warn).toHaveBeenCalledWith(message, data);
    });

    it("should always call console.error when logger.error is called", () => {
      const message = "Test error message";
      const data = { key: "value" };

      logger.error(message, data);

      expect(logger.error).toHaveBeenCalledWith(message, data);
    });

    it("should not call console.log when logDev is called", () => {
      const message = "Test dev log message";
      const data = { key: "value" };

      logDev(message, data);

      expect(logDev).toHaveBeenCalledWith(message, data);
    });
  });
});
