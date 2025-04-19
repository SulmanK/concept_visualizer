import '@testing-library/jest-dom';
import { vi } from 'vitest';
import { QueryClient } from '@tanstack/react-query';

// Add vi (Vitest) to global to allow usage like jest in tests
// This allows existing jest-style tests to work with Vitest
global.jest = {
  fn: vi.fn,
  mock: vi.mock,
  spyOn: vi.spyOn,
  resetAllMocks: vi.resetAllMocks,
  clearAllMocks: vi.clearAllMocks
} as any;

// Create a mock DOM element for the root
const mockRootElement = document.createElement('div');
mockRootElement.id = 'root';
document.body.appendChild(mockRootElement);

// Mock document.getElementById to return our mock element
document.getElementById = vi.fn((id) => {
  if (id === 'root') {
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
vi.mock('./main', () => ({
  queryClient: global.queryClient,
}));

// Mock problematic modules
vi.mock('./services/rateLimitService', () => ({
  mapEndpointToCategory: vi.fn(),
  extractRateLimitHeaders: vi.fn(),
  formatTimeRemaining: vi.fn(),
  decrementRateLimit: vi.fn(),
}));

// Mock any animation hooks
vi.mock('./hooks/animation/usePrefersReducedMotion', () => ({
  default: () => false,
}));

// Optional: Set up any global mocks or configurations here 