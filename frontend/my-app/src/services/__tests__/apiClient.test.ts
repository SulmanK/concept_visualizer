import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import type {
  AxiosInstance,
  AxiosRequestConfig,
  AxiosError,
  AxiosResponse,
} from "axios";
import { API_BASE_URL } from "../../config/apiEndpoints";
import {
  AuthError,
  RateLimitError,
  ValidationError,
  PermissionError,
  NotFoundError,
  ServerError,
  NetworkError,
} from "../../utils/errorUtils";

// Mock axios module
const mockGet = vi.fn();
const mockPost = vi.fn();
const mockPut = vi.fn();
const mockDelete = vi.fn();
const mockPatch = vi.fn();
const mockRequestUse = vi.fn();
const mockResponseUse = vi.fn();
const mockAxiosInstance = {
  defaults: {
    baseURL: API_BASE_URL,
    headers: {
      common: {},
    },
  },
  interceptors: {
    request: {
      use: mockRequestUse,
      eject: vi.fn(),
    },
    response: {
      use: mockResponseUse,
      eject: vi.fn(),
    },
  },
  get: mockGet,
  post: mockPost,
  put: mockPut,
  delete: mockDelete,
  patch: mockPatch,
  request: vi.fn(), // Add mock for the generic request method if used by interceptors
};

vi.mock("axios", () => {
  return {
    default: {
      create: vi.fn().mockReturnValue(mockAxiosInstance),
      isAxiosError: vi.fn((error: any) => error && error.isAxiosError === true), // More robust check
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

// Import after mock setup
import { apiClient, setAuthToken, clearAuthToken } from "../apiClient";
import { supabase } from "../supabaseClient";
import * as rateLimitService from "../rateLimitService";
import axios from "axios";

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: vi.fn((key: string) => store[key] || null),
    setItem: vi.fn((key: string, value: string) => {
      store[key] = String(value);
    }),
    removeItem: vi.fn((key: string) => {
      delete store[key];
    }),
    clear: vi.fn(() => {
      store = {};
    }),
  };
})();

Object.defineProperty(window, "localStorage", {
  value: localStorageMock,
});

describe("API Client", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorageMock.clear();
    // Reset axios mocks
    mockGet.mockReset();
    mockPost.mockReset();
    mockPut.mockReset();
    mockDelete.mockReset();
    mockPatch.mockReset();
    mockRequestUse.mockClear(); // Clear calls, but keep interceptor reference if needed
    mockResponseUse.mockClear();
    vi.mocked(supabase.auth.getSession).mockReset();
    vi.mocked(supabase.auth.refreshSession).mockReset();
    vi.mocked(rateLimitService.extractRateLimitHeaders).mockReset();
  });

  // Test the apiClient methods directly
  describe("Request Methods", () => {
    it("apiClient.get should call the underlying axios get", async () => {
      mockGet.mockResolvedValue({ data: "get response" });
      await apiClient.get("/get-test");
      expect(mockGet).toHaveBeenCalledWith("/get-test", expect.any(Object)); // Check config object exists
    });

    it("apiClient.post should call the underlying axios post", async () => {
      mockPost.mockResolvedValue({ data: "post response" });
      const postData = { id: 1 };
      await apiClient.post("/post-test", postData);
      expect(mockPost).toHaveBeenCalledWith(
        "/post-test",
        postData,
        expect.any(Object),
      );
    });
  });

  describe("Request Interceptor", () => {
    it("should add auth header if session exists", async () => {
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: { session: { access_token: "mock-token" } },
        error: null,
      });
      mockGet.mockResolvedValue({ data: { success: true } });
      await apiClient.get("/test-endpoint");
      // Axios request interceptor runs *before* the actual call
      // Check the config passed to the final axios call
      expect(mockGet).toHaveBeenCalledWith(
        "/test-endpoint",
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer mock-token",
          }),
        }),
      );
    });

    it("should not add auth header if no session exists", async () => {
      vi.mocked(supabase.auth.getSession).mockResolvedValueOnce({
        data: { session: null },
        error: null,
      });
      mockGet.mockResolvedValue({ data: { success: true } });
      await apiClient.get("/test-endpoint");
      expect(mockGet).toHaveBeenCalledWith(
        "/test-endpoint",
        expect.objectContaining({
          headers: expect.not.objectContaining({
            Authorization: expect.any(String),
          }),
        }),
      );
    });
  });

  describe("Response Interceptor", () => {
    it("should extract rate limit headers from successful responses", async () => {
      const mockResponse = {
        data: { success: true },
        status: 200,
        statusText: "OK",
        headers: {
          "x-ratelimit-limit": "100",
          "x-ratelimit-remaining": "99",
          "x-ratelimit-reset": "1600000000",
        },
        config: { url: "/test-endpoint" }, // Need config for interceptor
      };
      mockGet.mockResolvedValue(mockResponse); // Mock axios.get
      await apiClient.get("/test-endpoint"); // Trigger the request
      expect(rateLimitService.extractRateLimitHeaders).toHaveBeenCalledWith(
        expect.objectContaining({ headers: mockResponse.headers }), // Check response passed
        "/test-endpoint", // Check endpoint passed
      );
    });

    it("should handle 401 errors by refreshing the session", async () => {
      const mockAxiosError = {
        response: { status: 401, data: { message: "Unauthorized" } },
        config: { url: "/test-endpoint", headers: {} }, // Need headers in config
        isAxiosError: true,
      } as AxiosError;

      // First call fails, second succeeds
      mockGet
        .mockRejectedValueOnce(mockAxiosError)
        .mockResolvedValueOnce({ data: { success: true } });

      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: { session: { access_token: "new-token" } },
        error: null,
      });

      // We need to mock the retry mechanism which happens *inside* the interceptor
      // Instead of mocking axios.get again, we mock the axios instance itself
      // to simulate the retry call
      vi.mocked(mockAxiosInstance.request).mockResolvedValueOnce({
        data: { success: true },
        status: 200,
      });

      await apiClient.get("/test-endpoint");

      expect(supabase.auth.refreshSession).toHaveBeenCalledTimes(1);
      // Check that the *instance* was called for the retry
      expect(mockAxiosInstance.request).toHaveBeenCalledWith(
        expect.objectContaining({
          headers: expect.objectContaining({
            Authorization: "Bearer new-token",
          }),
        }),
      );
    });

    it("should throw AuthError for 401 responses that cannot be recovered", async () => {
      const mockAxiosError = {
        response: { status: 401, data: { message: "Unauthorized" } },
        config: { url: "/test-endpoint", headers: {} },
        isAxiosError: true,
      } as AxiosError;

      vi.mocked(supabase.auth.refreshSession).mockResolvedValueOnce({
        data: { session: null },
        error: { message: "Cannot refresh" },
      });

      mockGet.mockRejectedValueOnce(mockAxiosError); // Mock the initial request failure

      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(AuthError);
      expect(supabase.auth.refreshSession).toHaveBeenCalledTimes(1);
    });

    it("should throw RateLimitError for 429 responses", async () => {
      const mockAxiosError = {
        response: {
          status: 429,
          data: {
            message: "Rate limit exceeded",
            reset_after_seconds: 60,
            limit: 10,
            current: 10,
          },
          headers: { "retry-after": "60", "x-ratelimit-limit": "10" },
        },
        config: { url: "/test-endpoint" },
        isAxiosError: true,
      } as AxiosError;
      mockGet.mockRejectedValueOnce(mockAxiosError);
      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(
        RateLimitError,
      );
    });

    it("should throw ValidationError for 422 responses", async () => {
      const mockAxiosError = {
        response: {
          status: 422,
          data: {
            message: "Validation failed",
            errors: { name: ["required"] },
          },
        },
        config: { url: "/test-endpoint" },
        isAxiosError: true,
      } as AxiosError;
      mockGet.mockRejectedValueOnce(mockAxiosError);
      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(
        ValidationError,
      );
    });

    it("should throw PermissionError for 403 responses", async () => {
      const mockAxiosError = {
        response: { status: 403, data: { message: "Forbidden" } },
        config: { url: "/test-endpoint" },
        isAxiosError: true,
      } as AxiosError;
      mockGet.mockRejectedValueOnce(mockAxiosError);
      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(
        PermissionError,
      );
    });

    it("should throw NotFoundError for 404 responses", async () => {
      const mockAxiosError = {
        response: { status: 404, data: { message: "Not Found" } },
        config: { url: "/test-endpoint" },
        isAxiosError: true,
      } as AxiosError;
      mockGet.mockRejectedValueOnce(mockAxiosError);
      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(
        NotFoundError,
      );
    });

    it("should throw ServerError for 5xx responses", async () => {
      const mockAxiosError = {
        response: { status: 500, data: { message: "Server Error" } },
        config: { url: "/test-endpoint" },
        isAxiosError: true,
      } as AxiosError;
      mockGet.mockRejectedValueOnce(mockAxiosError);
      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(
        ServerError,
      );
    });

    it("should throw NetworkError for network failures", async () => {
      const mockAxiosError = {
        request: {}, // Indicates no response received
        config: { url: "/test-endpoint" },
        message: "Network Error", // Often the message for network issues
        isAxiosError: true,
      } as AxiosError;
      mockGet.mockRejectedValueOnce(mockAxiosError);
      await expect(apiClient.get("/test-endpoint")).rejects.toThrow(
        NetworkError,
      );
    });
  });

  describe("exportImage Function", () => {
    it("should make a POST request with blob response type", async () => {
      // Setup the mockPost to check config
      mockPost.mockImplementation((url, data, config) => {
        expect(config?.responseType).toBe("blob");
        return Promise.resolve({
          data: new Blob(["test"], { type: "image/png" }),
        });
      });

      await apiClient.exportImage("test-id", "png", "medium");

      expect(mockPost).toHaveBeenCalledWith(
        "/export/process", // Ensure the correct endpoint is used
        expect.objectContaining({
          image_identifier: "test-id",
          target_format: "png",
          target_size: "medium",
        }),
        expect.objectContaining({ responseType: "blob" }),
      );
    });
  });
});
