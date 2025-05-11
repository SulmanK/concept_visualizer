# Processing Stages

The `stages` directory contains reusable processing components that are used by the task processors. These stages represent independent, focused operations that may be used across different task types.

## Available Stages

- **image_preparation.py**: Functions for preparing image data for processing
- **palette_generation.py**: Functions for generating color palettes and palette variations
- **concept_storage.py**: Functions for storing base images and concepts
- **refinement.py**: Functions for refining concept images

## Benefits of the Staged Approach

1. **Reusability**: Common operations can be shared across different processor types
2. **Testability**: Each stage can be tested in isolation
3. **Separation of Concerns**: Each stage focuses on a specific aspect of processing
4. **Modularity**: Stages can be combined in different ways to create new workflows

## Common Stage Pattern

Most stage functions follow a common pattern:

1. Accept task-specific parameters and service instances
2. Log the start of the operation
3. Perform the core operation, capturing timing information
4. Handle errors with appropriate context
5. Return the result

## Error Handling

Each stage handles errors specific to its operation and wraps them in an appropriate Exception with context. This allows processors to make informed decisions about how to handle failures.

## Logging

All stages include detailed logging with timing information using the `[WORKER_TIMING]` prefix. This allows for performance analysis and debugging.

## Stage Functions

Stage functions are primarily asynchronous, since they often involve I/O operations like API calls, database access, and file operations. This allows for efficient use of resources in the worker.

## Individual Stage Documentation

- [Image Preparation](image_preparation.md)
- [Palette Generation](palette_generation.md)
- [Concept Storage](concept_storage.md)
- [Refinement](refinement.md)
