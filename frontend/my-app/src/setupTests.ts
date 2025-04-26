import "@testing-library/jest-dom";
import { vi, afterEach } from "vitest";
import { QueryClient } from "@tanstack/react-query";
import { cleanup } from "@testing-library/react";
import "@testing-library/jest-dom/vitest";

// Add vi (Vitest) to global to allow usage like jest in tests
// This allows existing jest-style tests to work with Vitest
global.jest = {
  fn: vi.fn,
  mock: vi.mock,
  spyOn: vi.spyOn,
  resetAllMocks: vi.resetAllMocks,
  clearAllMocks: vi.clearAllMocks,
} as {
  fn: typeof vi.fn;
  mock: typeof vi.mock;
  spyOn: typeof vi.spyOn;
  resetAllMocks: typeof vi.resetAllMocks;
  clearAllMocks: typeof vi.clearAllMocks;
};

// Create a mock DOM element for the root
const mockRootElement = document.createElement("div");
mockRootElement.id = "root";
document.body.appendChild(mockRootElement);

// Mock document.getElementById to return our mock element
document.getElementById = vi.fn((id) => {
  if (id === "root") {
    return mockRootElement;
  }
  return null;
});

// Mock window.matchMedia - required for tests that use media queries
window.matchMedia = vi.fn().mockImplementation((query) => ({
  matches: false,
  media: query,
  onchange: null,
  addListener: vi.fn(), // Deprecated but may be used in some libraries
  removeListener: vi.fn(), // Deprecated
  addEventListener: vi.fn(),
  removeEventListener: vi.fn(),
  dispatchEvent: vi.fn(),
}));

// Create a global QueryClient instance for tests
global.queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
      cacheTime: 0,
    },
  },
});

// Mock the main.tsx file to prevent it from initializing React during tests
vi.mock("./main", () => ({
  queryClient: global.queryClient,
}));

// Mock problematic modules
vi.mock("./services/rateLimitService", () => ({
  mapEndpointToCategory: vi.fn(),
  extractRateLimitHeaders: vi.fn(),
  formatTimeRemaining: vi.fn(),
  decrementRateLimit: vi.fn(),
}));

// Mock any animation hooks
vi.mock("./hooks/animation/usePrefersReducedMotion", () => ({
  default: () => false,
}));

// Optional: Set up any global mocks or configurations here

// Clean up after each test
afterEach(() => {
  cleanup();
  // Clear all mocks after each test
  vi.clearAllMocks();
});

// Mock IntersectionObserver
class MockIntersectionObserver {
  readonly root: Element | null;
  readonly rootMargin: string;
  readonly thresholds: ReadonlyArray<number>;

  constructor(
    callback: IntersectionObserverCallback,
    options?: IntersectionObserverInit,
  ) {
    this.root = options?.root ?? null;
    this.rootMargin = options?.rootMargin ?? "0px";
    this.thresholds = Array.isArray(options?.threshold)
      ? options.threshold
      : [options?.threshold ?? 0];
  }

  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
  takeRecords = vi.fn(() => []);
}

// Fix for Date.now not being a function in JSDOM
Object.defineProperty(global.Date, "now", {
  writable: true,
  value: () => new Date().getTime(),
});

// Mock window.matchMedia
Object.defineProperty(window, "matchMedia", {
  writable: true,
  value: vi.fn().mockImplementation((query) => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn(),
  })),
});

// Mock for resizeObserver
class MockResizeObserver {
  observe = vi.fn();
  unobserve = vi.fn();
  disconnect = vi.fn();
}

// Set global mocks
global.IntersectionObserver =
  MockIntersectionObserver as unknown as typeof IntersectionObserver;
global.ResizeObserver = MockResizeObserver as unknown as typeof ResizeObserver;

// Mocking fetch API
global.fetch = vi.fn(
  () =>
    Promise.resolve({
      json: () => Promise.resolve({}),
      text: () => Promise.resolve(""),
      ok: true,
      status: 200,
      headers: new Headers(),
    }) as unknown as Response,
);

// Mock console.error to fail tests on prop type warnings
const originalConsoleError = console.error;
console.error = (...args: unknown[]) => {
  // Check if this is a PropType validation
  if (typeof args[0] === "string" && args[0]?.includes?.("Failed prop type")) {
    throw new Error(args[0]);
  }
  originalConsoleError(...args);
};
