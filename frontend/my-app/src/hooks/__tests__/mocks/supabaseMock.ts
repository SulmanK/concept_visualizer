import { vi } from 'vitest';

// Define mock functions
export const mockSubscribe = vi.fn().mockReturnValue('SUBSCRIBED');
export const mockOn = vi.fn().mockReturnThis();
export const mockRemoveChannel = vi.fn();
export const mockChannel = vi.fn().mockReturnValue({
  on: mockOn,
  subscribe: mockSubscribe
});

// Create the mock object
export const mockSupabase = {
  channel: mockChannel,
  removeChannel: mockRemoveChannel
};

// Export a function to reset all mocks
export const resetSupabaseMocks = () => {
  mockSubscribe.mockClear();
  mockOn.mockClear();
  mockRemoveChannel.mockClear();
  mockChannel.mockClear();
}; 