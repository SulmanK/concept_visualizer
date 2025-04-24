/**
 * Tests for the Axios interceptors in apiClient.ts
 */

import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import { AxiosRequestConfig, AxiosResponse, AxiosError } from "axios";
import axios from "axios"; // Import the real axios first

// --- Mocks ---
// Define mock interceptor functions captured during module initialization
let capturedRequestInterceptor: ((config: any) => Promise<any>) | null = null;
let capturedResponseInterceptor: ((response: any) => any) | null = null;
let capturedResponseErrorInterceptor: ((error: any) => Promise<any>) | null =
  null;

// Mock axios module
const mockRequestUse = vi.fn((onFulfilled) => {
  capturedRequestInterceptor = onFulfilled; // Capture the function
  return 1;
});
const mockResponseUse = vi.fn((onFulfilled, onRejected) => {
  capturedResponseInterceptor = onFulfilled; // Capture the function
  capturedResponseErrorInterceptor = onRejected; // Capture the function
  return 2;
});
const mockEject = vi.fn();
const mockAxiosInstance = {
  defaults: { headers: { common: {} } },
  interceptors: {
    request: { use: mockRequestUse, eject: mockEject },
    response: { use: mockResponseUse, eject: mockEject },
  },
  get: vi.fn(),
  post: vi.fn(),
  request: vi.fn(), // Mock the generic request method used for retries
  create: vi.fn(), // Keep create mock if needed elsewhere
};
vi.mock("axios", () => {
  mockAxiosInstance.create.mockReturnValue(mockAxiosInstance); // Ensure create returns the mock
  return {
    default: {
      ...mockAxiosInstance,
      isAxiosError: vi.fn((error: any) => error && error.isAxiosError === true), // More robust check
      create: vi.fn().mockReturnValue(mockAxiosInstance), // Ensure create returns the mock
    },
  };
});

// Mock supabase
vi.mock("../supabaseClient", () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      refreshSession: vi.fn(),
    },
  },
}));

// Mock rateLimitService
vi.mock("../rateLimitService", () => ({
  extractRateLimitHeaders: vi.fn(),
  mapEndpointToCategory: vi.fn(),
}));

// Mock RateLimitError (as it's defined in apiClient usually)
class RateLimitError extends Error {
  status: number;
  resetAfterSeconds: number;
  constructor(message: string, status = 429, resetAfterSeconds = 60) {
    super(message);
    this.name = "RateLimitError";
    this.status = status;
    this.resetAfterSeconds = resetAfterSeconds;
  }
}
vi.stubGlobal("RateLimitError", RateLimitError);

// Import apiClient AFTER mocks are set up
import { apiClient } from "../apiClient";
import { supabase } from "../supabaseClient";
import * as rateLimitService from "../rateLimitService";

// Mock window.dispatchEvent
vi.stubGlobal("dispatchEvent", vi.fn());

describe("API Client Interceptors", () => {
  let dispatchEventSpy: any;

  beforeEach(() => {
    vi.clearAllMocks();
    dispatchEventSpy = vi.spyOn(document, "dispatchEvent");

    // Ensure interceptors are captured before each test
    if (
      !capturedRequestInterceptor ||
      !capturedResponseInterceptor ||
      !capturedResponseErrorInterceptor
    ) {
      console.warn("Interceptors not captured correctly. Check mock setup.");
      // Attempt to re-initialize the client to trigger interceptor setup again
      // This is a workaround and might indicate deeper issues if needed frequently.
      vi.resetModules(); // Reset modules to force re-initialization
      require("../apiClient"); // Re-import to trigger setup
    }
  });

  afterEach(() => {
    vi.resetAllMocks();
    dispatchEventSpy.mockRestore(); // Restore the original dispatchEvent
  });

  describe("Request Interceptor", () => {
    it("adds Authorization header when session token exists", async () => {
      const config = {
        headers: {},
        url: "/test-endpoint",
      } as AxiosRequestConfig;
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: { session: { access_token: "valid-token-123" } },
        error: null,
      });

      // Manually call the captured interceptor
      expect(capturedRequestInterceptor).toBeDefined();
      const result = await capturedRequestInterceptor!(config);

      expect(result.headers).toHaveProperty(
        "Authorization",
        "Bearer valid-token-123",
      );
    });

    it("removes Authorization header when no session exists", async () => {
      const config = {
        headers: { Authorization: "Bearer old-token" }, // Start with an existing header
        url: "/test-endpoint",
      } as AxiosRequestConfig;

      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: { session: null },
        error: null,
      });

      // Manually call the captured interceptor
      expect(capturedRequestInterceptor).toBeDefined();
      const result = await capturedRequestInterceptor!(config);

      expect(result.headers?.Authorization).toBeUndefined(); // Use optional chaining
    });
  });

  describe("Response Interceptor", () => {
    it("extracts rate limit headers from successful responses", async () => {
      const mockResponse = {
        data: { success: true },
        status: 200,
        headers: {
          "x-ratelimit-limit": "100",
          "x-ratelimit-remaining": "99",
          "x-ratelimit-reset": "1600000000",
        },
        config: { url: "/test-endpoint" }, // Added config
      } as AxiosResponse;

      // Manually call the captured interceptor
      expect(capturedResponseInterceptor).toBeDefined();
      const result = capturedResponseInterceptor!(mockResponse);

      expect(rateLimitService.extractRateLimitHeaders).toHaveBeenCalledWith(
        mockResponse, // Pass the whole response
        "/test-endpoint", // Extract URL from config
      );
      expect(result).toEqual(mockResponse); // Interceptor should return the response
    });

    it("refreshes token and retries request on 401 error", async () => {
      const mockAxiosError = {
        response: { status: 401, data: { message: "Unauthorized" } },
        config: { url: "/test-endpoint", method: "get", headers: {} }, // Ensure method is present
        isAxiosError: true,
      } as AxiosError;

      // Mock successful refresh
      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: { session: { access_token: "new-token" } },
        error: null,
      });

      // Mock the retry request (using the axios instance mock)
      vi.mocked(mockAxiosInstance.request).mockResolvedValueOnce({
        data: { success: true },
        status: 200,
      });

      // Manually call the captured error interceptor
      expect(capturedResponseErrorInterceptor).toBeDefined();
      await capturedResponseErrorInterceptor!(mockAxiosError);

      expect(supabase.auth.refreshSession).toHaveBeenCalledTimes(1);
      // Verify the retry call on the instance
      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer new-token",
          }),
        }),
      );
    });

    it("dispatches auth-error-needs-logout event when token refresh fails", async () => {
      const mockAxiosError = {
        response: { status: 401, data: { message: "Unauthorized" } },
        config: { url: "/test-endpoint", method: "get", headers: {} },
        isAxiosError: true,
      } as AxiosError;

      // Mock failed refresh
      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: { session: null },
        error: { message: "Refresh failed" },
      });

      // Manually call the captured error interceptor
      expect(capturedResponseErrorInterceptor).toBeDefined();
      await expect(
        capturedResponseErrorInterceptor!(mockAxiosError),
      ).rejects.toThrow(Error); // Expect it to re-throw or throw AuthError

      expect(supabase.auth.refreshSession).toHaveBeenCalledTimes(1);
      // Verify the event dispatch
      expect(dispatchEventSpy).toHaveBeenCalledWith(expect.any(CustomEvent));
      expect(dispatchEventSpy.mock.calls[0][0].type).toBe(
        "auth-error-needs-logout",
      );
    });

    it("handles rate limit errors (429)", async () => {
      const mockAxiosError = {
        response: {
          status: 429,
          data: { message: "Rate limit exceeded", reset_after_seconds: 60 },
          headers: { "retry-after": "60" }, // Add headers
        },
        config: { url: "/test-endpoint" },
        isAxiosError: true,
      } as AxiosError;

      // Manually call the captured error interceptor
      expect(capturedResponseErrorInterceptor).toBeDefined();
      await expect(
        capturedResponseErrorInterceptor!(mockAxiosError),
      ).rejects.toThrow(RateLimitError);
    });
  });
});
