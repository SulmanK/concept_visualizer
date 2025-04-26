import { renderHook, act } from "@testing-library/react";
import { vi, describe, test, expect, beforeEach, afterEach } from "vitest";
import useNetworkStatus from "../useNetworkStatus";
import { apiClient } from "../../services/apiClient";

// Define useToast mock with proper functions
const useToastMock = vi.hoisted(() =>
  vi.fn().mockReturnValue({
    showSuccess: vi.fn(),
    showError: vi.fn(),
    showInfo: vi.fn(),
    showWarning: vi.fn(),
    showToast: vi.fn(),
    dismissToast: vi.fn(),
    dismissAll: vi.fn(),
  }),
);

// Mock the useToast hook
vi.mock("../useToast", () => {
  return {
    useToast: useToastMock,
    default: useToastMock,
    __esModule: true,
  };
});

// Mock the apiClient
vi.mock("../../services/apiClient", () => ({
  apiClient: {
    get: vi.fn().mockImplementation(() => Promise.resolve({ status: 200 })),
  },
}));

// Set up mock navigator
const originalNavigator = { ...navigator };
const mockAddEventListener = vi.fn();
const mockRemoveEventListener = vi.fn();

// Preserve the original Date implementation
const RealDate = Date;

describe("useNetworkStatus", () => {
  let originalDateNow: typeof Date.now;

  beforeEach(() => {
    vi.resetAllMocks();

    // Preserve the original Date.now function
    originalDateNow = Date.now;

    // Mock Date.now properly
    Date.now = vi.fn(() => 1672531200000); // 2023-01-01

    // Create a fixed mock date
    const mockDate = new RealDate(2023, 0, 1);
    vi.spyOn(global, "Date").mockImplementation(() => mockDate);

    // Reset navigator mock
    Object.defineProperty(window, "navigator", {
      configurable: true,
      writable: true,
      value: {
        ...originalNavigator,
        onLine: true,
        connection: {
          effectiveType: "4g",
          addEventListener: mockAddEventListener,
          removeEventListener: mockRemoveEventListener,
        },
      },
    });

    // Mock window event listeners
    window.addEventListener = vi.fn();
    window.removeEventListener = vi.fn();
  });

  afterEach(() => {
    vi.clearAllMocks();

    // Restore Date.now
    Date.now = originalDateNow;

    // Restore the global Date constructor
    vi.restoreAllMocks();
  });

  test("initializes with online status based on navigator.onLine", async () => {
    // Create the hook outside of act for proper access
    const { result } = renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkInterval: 0, // Disable interval checks to avoid async issues
      }),
    );

    // Allow initial async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Now we can access the result object safely
    expect(result.current.isOnline).toBe(true);
  });

  test("detects offline status correctly", async () => {
    // Set navigator to offline before rendering the hook
    Object.defineProperty(window.navigator, "onLine", {
      configurable: true,
      value: false,
    });

    // Mock a network error for API calls while offline
    vi.mocked(apiClient.get).mockRejectedValueOnce(new Error("Network error"));

    // Create the hook outside of act
    const { result } = renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkInterval: 0,
      }),
    );

    // Allow async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Now check the value
    expect(result.current.isOnline).toBe(false);
  });

  test("sets connection type based on navigator.connection", async () => {
    // Mock slow connection
    Object.defineProperty(window.navigator, "connection", {
      configurable: true,
      writable: true,
      value: {
        effectiveType: "2g",
        addEventListener: mockAddEventListener,
        removeEventListener: mockRemoveEventListener,
      },
    });

    // Create the hook
    const { result } = renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkInterval: 0,
      }),
    );

    // Allow async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    expect(result.current.connectionType).toBe("2g");
    expect(result.current.isSlowConnection).toBe(true);
  });

  test("registers event listeners on mount", async () => {
    renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkInterval: 0,
      }),
    );

    // Allow async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Should register online/offline listeners
    expect(window.addEventListener).toHaveBeenCalledWith(
      "online",
      expect.any(Function),
    );
    expect(window.addEventListener).toHaveBeenCalledWith(
      "offline",
      expect.any(Function),
    );

    // Should register connection change listener if available
    expect(mockAddEventListener).toHaveBeenCalledWith(
      "change",
      expect.any(Function),
    );
  });

  test("unregisters event listeners on unmount", async () => {
    // Create the hook
    const { unmount } = renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkInterval: 0,
      }),
    );

    // Allow async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Unmount the component
    unmount();

    // Should unregister all listeners
    expect(window.removeEventListener).toHaveBeenCalledWith(
      "online",
      expect.any(Function),
    );
    expect(window.removeEventListener).toHaveBeenCalledWith(
      "offline",
      expect.any(Function),
    );
    expect(mockRemoveEventListener).toHaveBeenCalledWith(
      "change",
      expect.any(Function),
    );
  });

  test("makes health check API call on initialization", async () => {
    renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkInterval: 0,
      }),
    );

    // Allow async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Should make API call to health endpoint
    expect(apiClient.get).toHaveBeenCalledWith(
      "/health",
      expect.objectContaining({
        headers: { "Cache-Control": "no-cache" },
      }),
    );
  });

  test("uses custom health check endpoint when provided", async () => {
    const customEndpoint = "/api/ping";

    renderHook(() =>
      useNetworkStatus({
        notifyOnStatusChange: false,
        checkEndpoint: customEndpoint,
        checkInterval: 0,
      }),
    );

    // Allow async operations to complete
    await act(async () => {
      await new Promise((resolve) => setTimeout(resolve, 0));
    });

    // Should use the custom endpoint
    expect(apiClient.get).toHaveBeenCalledWith(
      customEndpoint,
      expect.anything(),
    );
  });
});
