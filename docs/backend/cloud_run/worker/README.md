# Worker Module

## Overview

The Worker module is the core component of the Cloud Function infrastructure. It processes tasks from a Pub/Sub queue, dispatches them to the appropriate task processor, and manages their lifecycle.

## Deployment

This worker is deployed as a **Google Cloud Function (2nd Gen)** triggered by Pub/Sub messages. The deployment uses the source-based deployment method with the `./backend` directory as the source and `handle_pubsub` as the entry point.

## Key Components

- **main.py**: Main entry point that handles Pub/Sub messages and initializes global services
- **Processors**: Task-specific classes that implement the processing logic for different task types
- **Stages**: Reusable components for specific processing steps that can be shared across processors

## Message Processing Flow

1. A Pub/Sub message is received and passed to the `handle_pubsub` function
2. The message is decoded from base64 and parsed as JSON
3. The `process_pubsub_message` function identifies the task type and validates required fields
4. An appropriate processor instance is created based on the task type
5. The processor's `process` method is called to execute the task

## Services Initialization

The worker initializes a set of global service instances on startup:

- **Supabase Client**: For database operations
- **Persistence Services**: For storing images and concepts
- **Image Services**: For processing and manipulating images
- **JigsawStack Client**: For AI-based image generation and refinement
- **Task Service**: For updating task status

## Error Handling

Error handling occurs at multiple levels:

1. **Global Level**: Exceptions in the main handler are caught and logged
2. **Task Level**: Processors manage task-specific exceptions and update task status accordingly
3. **Stage Level**: Individual processing stages handle their specific errors and propagate them when necessary

## Health Checks

The worker exposes an HTTP endpoint at `/` that returns a simple health status response, used by Cloud Functions to verify instance health.

## Configuration

The worker is configured via environment variables:

- `CONCEPT_LOG_LEVEL`: Sets the logging level (default: INFO)
- `CONCEPT_SUPABASE_URL`: Supabase URL for database operations
- `CONCEPT_SUPABASE_SERVICE_ROLE`: Service role key for database access
- `CONCEPT_JIGSAWSTACK_API_KEY`: API key for JigsawStack services
- `CONCEPT_JIGSAWSTACK_API_URL`: JigsawStack API URL

## Submodules

- [Processors](processors/): Task-specific processor implementations
- [Stages](stages/): Reusable processing stages
