# Task Processors

Task processors handle the execution of specific task types in the worker. Each processor is responsible for managing the complete lifecycle of a task, from claiming it to updating its status upon completion or failure.

## Base Processor

The `BaseTaskProcessor` is an abstract base class that provides common functionality for all task processors:

- Task claiming and status management
- Error handling and logging
- Task timing metrics

## Generation Processor

The `GenerationTaskProcessor` handles concept generation tasks. It orchestrates the following stages:

1. Generating a base concept image
2. Concurrently storing the base image and generating color palettes
3. Creating palette variations for the concept
4. Storing the final concept with all variations

### Key Features

- **Concurrent Processing**: Performs image storage and palette generation in parallel
- **Comprehensive Error Handling**: Captures and categorizes errors at each stage
- **Detailed Timing**: Logs performance metrics for each processing step

## Refinement Processor

The `RefinementTaskProcessor` handles concept refinement tasks. It orchestrates the following stages:

1. Refining an image based on user prompt
2. Storing the refined image
3. Storing the refined concept data

### Key Features

- **Image Refinement**: Uses the concept service to refine images based on user instructions
- **Metadata Management**: Preserves original concept information while adding refinement details
- **Error Handling**: Provides specific error messages for refinement-related issues

## Processing Flow

All processors follow a similar flow:

1. **Claim Task**: Attempt to claim the task for processing
2. **Process Steps**: Execute task-specific processing steps
3. **Complete Task**: Mark the task as completed with a result ID
4. **Handle Errors**: Capture any errors and update task status accordingly

## Usage

Processors are instantiated by the main worker module based on the `task_type` field in the incoming message. They receive the following common parameters:

- `task_id`: The ID of the task to process
- `user_id`: The ID of the user who created the task
- `message_payload`: The full payload from the Pub/Sub message
- `services`: A dictionary containing all service instances
