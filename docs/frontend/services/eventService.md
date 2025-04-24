# Event Service

The Event Service provides a simple pub/sub (publish-subscribe) event system for global application event handling. It allows components to subscribe to specific events and execute callbacks when those events are triggered.

## Core Features

- Lightweight event emitter system for cross-component communication
- Type-safe event definitions through TypeScript enums
- Automatic unsubscribe functionality through returned cleanup functions
- Error handling for event handlers to prevent cascade failures

## Available Events

```typescript
export enum AppEvent {
  CONCEPT_CREATED = "concept_created",
  CONCEPT_UPDATED = "concept_updated",
  CONCEPT_DELETED = "concept_deleted",
  SVG_CONVERTED = "svg_converted",
}
```

## Key Methods

| Method                      | Description                                                                        |
| --------------------------- | ---------------------------------------------------------------------------------- |
| `subscribe(event, handler)` | Subscribes a handler function to an event type and returns an unsubscribe function |
| `emit(event, ...args)`      | Triggers an event and passes optional arguments to all registered handlers         |
| `clearListeners(event)`     | Removes all handlers registered for a specific event                               |

## Usage Example

```tsx
import { useEffect } from "react";
import { eventService, AppEvent } from "../services/eventService";

const ConceptNotifier = () => {
  useEffect(() => {
    // Subscribe to concept creation events
    const unsubscribe = eventService.subscribe(
      AppEvent.CONCEPT_CREATED,
      (concept) => {
        console.log("New concept created:", concept);
        // Perform any actions needed when a concept is created
      },
    );

    // Clean up subscription when component unmounts
    return unsubscribe;
  }, []);

  return null; // This is a non-visual component
};

// Example of emitting an event elsewhere in the app
const createConcept = async (data) => {
  try {
    const result = await apiClient.post("/concepts/generate", data);
    // Notify the application that a new concept was created
    eventService.emit(AppEvent.CONCEPT_CREATED, result.data);
    return result.data;
  } catch (error) {
    console.error("Failed to create concept:", error);
    throw error;
  }
};
```

## Implementation Notes

- The event service uses a singleton pattern, providing a single instance throughout the application
- Each event can have multiple handlers registered
- Handlers are executed sequentially for each event emission
- Individual handler errors are caught to prevent breaking other handlers
- Error details are logged to the console for debugging
