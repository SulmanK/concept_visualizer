# Cloud Run Worker Module

## Overview

The Cloud Run module is responsible for processing asynchronous tasks in the Concept Visualizer application. It processes tasks from a Pub/Sub queue and calls the appropriate services to handle different types of tasks, such as concept generation and refinement.

## Architecture

The worker follows a modular architecture with clear separation of concerns:

- **Main Module**: Initializes global services and handles Pub/Sub message processing
- **Processors**: Task-specific processors that handle the lifecycle of different task types
- **Stages**: Reusable components for specific processing stages that can be used across task types

### Directory Structure

```
cloud_run/
└── worker/
    ├── main.py                 # Entry point, Pub/Sub handler, global service init
    ├── processors/
    │   ├── __init__.py
    │   ├── base_processor.py   # Abstract base class for task processors
    │   ├── generation_processor.py
    │   └── refinement_processor.py
    └── stages/                 # Reusable processing stages
        ├── __init__.py
        ├── image_preparation.py
        ├── palette_generation.py
        ├── concept_storage.py
        └── refinement.py
```

## Task Flow

1. A Pub/Sub message is received by the Cloud Function
2. The message is decoded and validated
3. Based on the task type, an appropriate task processor is instantiated
4. The processor claims the task and updates its status to "PROCESSING"
5. The processor executes the task-specific steps
6. Upon completion, the processor updates the task status to "COMPLETED" or "FAILED"

## Features

- **Concurrent Processing**: Some operations, like image storage and palette generation, run in parallel
- **Error Handling**: Comprehensive error handling with appropriate status updates
- **Performance Monitoring**: Detailed timing logs to identify bottlenecks
- **Type Safety**: Extensive type annotations for better code quality

## Dependencies

The Cloud Run worker depends on the following core services:

- **Task Service**: For updating task status
- **Concept Service**: For generating and refining concepts
- **Image Service**: For processing and storing images
- **Persistence Services**: For storing data in Supabase

See the [worker module documentation](worker/) for more details on specific components.
