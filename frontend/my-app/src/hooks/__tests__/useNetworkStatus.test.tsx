import React from 'react';
import { renderHook } from '@testing-library/react';
import { vi, describe, test, expect, beforeEach, afterEach } from 'vitest';
import useNetworkStatus from '../useNetworkStatus';
import { apiClient } from '../../services/apiClient';

// Define useToast mock with proper functions
const useToastMock = vi.hoisted(() => vi.fn().mockReturnValue({
  showSuccess: vi.fn(),
  showError: vi.fn(),
  showInfo: vi.fn(),
  showWarning: vi.fn(),
  showToast: vi.fn(),
  dismissToast: vi.fn(),
  dismissAll: vi.fn()
}));

// Mock the useToast hook
vi.mock('../useToast', () => {
  return {
    useToast: useToastMock,
    default: useToastMock,
    __esModule: true
  };
});

// Mock the apiClient
vi.mock('../../services/apiClient', () => ({
  apiClient: {
    get: vi.fn(() => Promise.resolve({ status: 200 })),
  },
}));

// Set up mock navigator
const originalNavigator = { ...navigator };
const mockAddEventListener = vi.fn();
const mockRemoveEventListener = vi.fn();

describe('useNetworkStatus', () => {
  beforeEach(() => {
    vi.resetAllMocks();
    
    // Mock the Date constructor
    const mockDate = new Date(2023, 0, 1);
    vi.spyOn(global, 'Date').mockImplementation(() => mockDate);
    
    // Reset navigator mock
    Object.defineProperty(window, 'navigator', {
      writable: true,
      value: {
        ...originalNavigator,
        onLine: true,
        connection: {
          effectiveType: '4g',
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
  });

  test('initializes with online status based on navigator.onLine', () => {
    // Test online
    const { result: onlineResult } = renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkInterval: 0 // Disable interval checks to avoid async issues
    }));
    expect(onlineResult.current.isOnline).toBe(true);
    
    // Test offline
    Object.defineProperty(window.navigator, 'onLine', {
      writable: true,
      value: false,
    });
    
    const { result: offlineResult } = renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkInterval: 0 // Disable interval checks to avoid async issues
    }));
    expect(offlineResult.current.isOnline).toBe(false);
  });

  test('sets connection type based on navigator.connection', () => {
    // Mock slow connection
    Object.defineProperty(window.navigator, 'connection', {
      writable: true,
      value: {
        effectiveType: '2g',
        addEventListener: mockAddEventListener,
        removeEventListener: mockRemoveEventListener,
      },
    });

    const { result } = renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkInterval: 0
    }));
    
    expect(result.current.connectionType).toBe('2g');
    expect(result.current.isSlowConnection).toBe(true);
  });

  test('registers event listeners on mount', () => {
    renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkInterval: 0
    }));

    // Should register online/offline listeners
    expect(window.addEventListener).toHaveBeenCalledWith('online', expect.any(Function));
    expect(window.addEventListener).toHaveBeenCalledWith('offline', expect.any(Function));
    
    // Should register connection change listener if available
    expect(mockAddEventListener).toHaveBeenCalledWith('change', expect.any(Function));
  });

  test('unregisters event listeners on unmount', () => {
    const { unmount } = renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkInterval: 0
    }));
    
    unmount();

    // Should unregister all listeners
    expect(window.removeEventListener).toHaveBeenCalledWith('online', expect.any(Function));
    expect(window.removeEventListener).toHaveBeenCalledWith('offline', expect.any(Function));
    expect(mockRemoveEventListener).toHaveBeenCalledWith('change', expect.any(Function));
  });

  test('makes health check API call on initialization', () => {
    renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkInterval: 0
    }));
    
    // Should make API call to health endpoint
    expect(apiClient.get).toHaveBeenCalledWith('/health', expect.objectContaining({
      headers: { 'Cache-Control': 'no-cache' }
    }));
  });

  test('uses custom health check endpoint when provided', () => {
    const customEndpoint = '/api/ping';
    
    renderHook(() => useNetworkStatus({
      notifyOnStatusChange: false,
      checkEndpoint: customEndpoint,
      checkInterval: 0
    }));
    
    // Should use the custom endpoint
    expect(apiClient.get).toHaveBeenCalledWith(customEndpoint, expect.anything());
  });
}); 