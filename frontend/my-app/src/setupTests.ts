import '@testing-library/jest-dom';
import { vi } from 'vitest';

// Add vi (Vitest) to global to allow usage like jest in tests
// This allows existing jest-style tests to work with Vitest
global.jest = {
  fn: vi.fn,
  mock: vi.mock,
  spyOn: vi.spyOn,
  resetAllMocks: vi.resetAllMocks,
  clearAllMocks: vi.clearAllMocks
} as any;

// Optional: Set up any global mocks or configurations here 