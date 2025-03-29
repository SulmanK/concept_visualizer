/**
 * Configuration and utilities for using mock services in tests.
 * This file provides helpers to setup and reset mock services between tests.
 */

import { mockApiService, MockApiConfig } from './mockApiService';

/**
 * Setup the mock API for a test.
 * This allows configuring the mock API service for specific test scenarios.
 */
export function setupMockApi(config: Partial<MockApiConfig> = {}): void {
  mockApiService.configure(config);
}

/**
 * Reset the mock API to its default state.
 * Call this in beforeEach to ensure tests don't affect each other.
 */
export function resetMockApi(): void {
  mockApiService.configure({
    shouldFail: false,
    responseDelay: 0, // Use 0 for fast tests
    customResponses: undefined,
  });
}

/**
 * Configure the mock API to simulate failures.
 */
export function mockApiFailure(): void {
  mockApiService.configure({
    shouldFail: true,
  });
}

/**
 * Configure the mock API with custom responses.
 */
export function mockApiCustomResponse(customResponses: MockApiConfig['customResponses']): void {
  mockApiService.configure({
    customResponses,
  });
}

/**
 * Setup mocks for all tests in a test file.
 * Call this in the describe block outside of any individual test.
 */
export function setupTestMocks(): void {
  beforeEach(() => {
    resetMockApi();
    jest.clearAllMocks();
  });
  
  afterEach(() => {
    jest.restoreAllMocks();
  });
} 