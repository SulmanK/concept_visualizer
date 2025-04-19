import { vi, describe, it, expect, beforeEach } from 'vitest';
import { eventService, AppEvent } from '../eventService';

describe('Event Service', () => {
  // Create a spy console.log to prevent noisy output but still check logs
  const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
  const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  
  beforeEach(() => {
    // Clear all subscriptions before each test
    Object.values(AppEvent).forEach(event => {
      eventService.clearListeners(event);
    });
    
    // Clear all mocks
    vi.clearAllMocks();
  });
  
  it('should subscribe to an event and receive when emitted', () => {
    // Create mock handler
    const mockHandler = vi.fn();
    
    // Subscribe to CONCEPT_CREATED event
    eventService.subscribe(AppEvent.CONCEPT_CREATED, mockHandler);
    
    // Emit the event with data
    const testData = { id: '123', name: 'Test Concept' };
    eventService.emit(AppEvent.CONCEPT_CREATED, testData);
    
    // Verify handler was called with correct data
    expect(mockHandler).toHaveBeenCalledTimes(1);
    expect(mockHandler).toHaveBeenCalledWith(testData);
    
    // Verify log was created
    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining(AppEvent.CONCEPT_CREATED)
    );
  });
  
  it('should not call handlers for different events', () => {
    // Create mock handlers
    const mockHandlerA = vi.fn();
    const mockHandlerB = vi.fn();
    
    // Subscribe to different events
    eventService.subscribe(AppEvent.CONCEPT_CREATED, mockHandlerA);
    eventService.subscribe(AppEvent.CONCEPT_UPDATED, mockHandlerB);
    
    // Emit only one event
    eventService.emit(AppEvent.CONCEPT_CREATED, { id: '123' });
    
    // Verify only the correct handler was called
    expect(mockHandlerA).toHaveBeenCalledTimes(1);
    expect(mockHandlerB).not.toHaveBeenCalled();
  });
  
  it('should unsubscribe handlers when unsubscribe function is called', () => {
    // Create mock handler
    const mockHandler = vi.fn();
    
    // Subscribe and get unsubscribe function
    const unsubscribe = eventService.subscribe(AppEvent.CONCEPT_DELETED, mockHandler);
    
    // Emit once before unsubscribing
    eventService.emit(AppEvent.CONCEPT_DELETED, { id: '123' });
    expect(mockHandler).toHaveBeenCalledTimes(1);
    
    // Unsubscribe
    unsubscribe();
    
    // Emit again after unsubscribing
    eventService.emit(AppEvent.CONCEPT_DELETED, { id: '456' });
    
    // Verify handler was not called again
    expect(mockHandler).toHaveBeenCalledTimes(1);
  });
  
  it('should allow multiple handlers for the same event', () => {
    // Create mock handlers
    const mockHandlerA = vi.fn();
    const mockHandlerB = vi.fn();
    
    // Subscribe both handlers to the same event
    eventService.subscribe(AppEvent.SVG_CONVERTED, mockHandlerA);
    eventService.subscribe(AppEvent.SVG_CONVERTED, mockHandlerB);
    
    // Emit the event
    eventService.emit(AppEvent.SVG_CONVERTED, { svg: '<svg></svg>' });
    
    // Verify both handlers were called
    expect(mockHandlerA).toHaveBeenCalledTimes(1);
    expect(mockHandlerB).toHaveBeenCalledTimes(1);
  });
  
  it('should handle errors in event handlers without affecting other handlers', () => {
    // Create handlers, one that throws an error
    const mockHandlerA = vi.fn().mockImplementation(() => {
      throw new Error('Test error');
    });
    const mockHandlerB = vi.fn();
    
    // Subscribe both handlers
    eventService.subscribe(AppEvent.CONCEPT_CREATED, mockHandlerA);
    eventService.subscribe(AppEvent.CONCEPT_CREATED, mockHandlerB);
    
    // Emit the event
    eventService.emit(AppEvent.CONCEPT_CREATED, { id: '123' });
    
    // Verify both handlers were called, error was logged
    expect(mockHandlerA).toHaveBeenCalledTimes(1);
    expect(mockHandlerB).toHaveBeenCalledTimes(1);
    expect(consoleErrorSpy).toHaveBeenCalledWith(
      expect.stringContaining('[EventService] Error in event handler'),
      expect.any(Error)
    );
  });
  
  it('should clear all listeners for a specific event', () => {
    // Create mock handlers
    const mockHandlerA = vi.fn();
    const mockHandlerB = vi.fn();
    const mockHandlerC = vi.fn();
    
    // Subscribe to multiple events
    eventService.subscribe(AppEvent.CONCEPT_CREATED, mockHandlerA);
    eventService.subscribe(AppEvent.CONCEPT_CREATED, mockHandlerB);
    eventService.subscribe(AppEvent.CONCEPT_UPDATED, mockHandlerC);
    
    // Clear listeners for one event
    eventService.clearListeners(AppEvent.CONCEPT_CREATED);
    
    // Emit both events
    eventService.emit(AppEvent.CONCEPT_CREATED, { id: '123' });
    eventService.emit(AppEvent.CONCEPT_UPDATED, { id: '123' });
    
    // Verify only handler for non-cleared event was called
    expect(mockHandlerA).not.toHaveBeenCalled();
    expect(mockHandlerB).not.toHaveBeenCalled();
    expect(mockHandlerC).toHaveBeenCalledTimes(1);
  });
  
  it('should do nothing when emitting an event with no handlers', () => {
    // Emit event with no handlers
    eventService.emit(AppEvent.CONCEPT_DELETED, { id: '123' });
    
    // Verify log was still created
    expect(consoleLogSpy).toHaveBeenCalledWith(
      expect.stringContaining(AppEvent.CONCEPT_DELETED)
    );
    
    // No errors should occur
    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });
}); 