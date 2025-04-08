/**
 * Simple event emitter service for global app events
 */

type EventHandler = (...args: any[]) => void;

export enum AppEvent {
  CONCEPT_CREATED = 'concept_created',
  CONCEPT_UPDATED = 'concept_updated',
  CONCEPT_DELETED = 'concept_deleted',
  SVG_CONVERTED = 'svg_converted',
}

class EventService {
  private listeners: Record<string, EventHandler[]> = {};

  /**
   * Subscribe to an event
   * @param event The event to subscribe to
   * @param handler The handler function to call when the event is emitted
   * @returns A function to unsubscribe the handler
   */
  subscribe(event: AppEvent, handler: EventHandler): () => void {
    if (!this.listeners[event]) {
      this.listeners[event] = [];
    }
    
    this.listeners[event].push(handler);
    
    // Return unsubscribe function
    return () => {
      this.listeners[event] = this.listeners[event].filter(h => h !== handler);
    };
  }

  /**
   * Emit an event with optional data
   * @param event The event to emit
   * @param args Optional arguments to pass to the handlers
   */
  emit(event: AppEvent, ...args: any[]): void {
    console.log(`[EventService] Emitting event: ${event}`);
    
    if (!this.listeners[event]) {
      return;
    }
    
    this.listeners[event].forEach(handler => {
      try {
        handler(...args);
      } catch (error) {
        console.error(`[EventService] Error in event handler for ${event}:`, error);
      }
    });
  }

  /**
   * Remove all listeners for a specific event
   * @param event The event to clear listeners for
   */
  clearListeners(event: AppEvent): void {
    this.listeners[event] = [];
  }
}

// Create singleton instance
export const eventService = new EventService(); 