# Worker Main Module

The Worker Main module is the entry point for the Google Cloud Function (2nd Gen) worker. It handles Pub/Sub message processing, global service initialization, and task dispatching.

## Deployment

This worker is deployed as a Google Cloud Function (2nd Gen) triggered by Pub/Sub messages. The deployment uses the source-based deployment method with the `./backend` directory as the source and `handle_pubsub` as the entry point function.

## Main Components

### Global Service Initialization

The module initializes a set of global service instances on startup:

```python
# Global service instances
SERVICES_GLOBAL: Optional[Dict[str, Any]] = None

# Initialize on module import
logger.info("Initializing services globally for worker instance...")
try:
    # Create Supabase client (use service role directly for worker)
    _supabase_client_global = SupabaseClient(...)

    # Initialize persistence services
    _image_persistence_service_global = ImagePersistenceService(...)
    _concept_persistence_service_global = ConceptPersistenceService(...)

    # Initialize image services
    _image_processing_service_global = ImageProcessingService()
    _image_service_global = ImageService(...)

    # Initialize JigsawStack client
    _jigsawstack_client_global = JigsawStackClient(...)

    # Initialize concept service
    _concept_service_global = ConceptService(...)

    # Initialize task service
    _task_service_global = TaskService(...)

    SERVICES_GLOBAL = {
        "image_service": _image_service_global,
        "concept_service": _concept_service_global,
        "concept_persistence_service": _concept_persistence_service_global,
        "image_persistence_service": _image_persistence_service_global,
        "task_service": _task_service_global,
        "jigsawstack_client": _jigsawstack_client_global,
    }
    logger.info("Global services initialized successfully.")
except Exception as e:
    logger.critical(f"FATAL: Failed to initialize global services: {e}", exc_info=True)
    SERVICES_GLOBAL = None  # Indicate failure
```

### HTTP Health Check Endpoint

The module provides an HTTP endpoint for health checks:

```python
@functions_framework.http
def http_endpoint(request: Any) -> Dict[str, str]:
    """HTTP handler for health checks.

    Cloud Functions will use this endpoint to verify that the instance is healthy.

    Args:
        request: HTTP request object

    Returns:
        An HTTP response with status information
    """
    logger.info("Received health check request")
    return {"status": "healthy", "message": "Concept worker is ready to process tasks"}
```

### Pub/Sub Message Processing

The module processes Pub/Sub messages with these functions:

```python
async def process_pubsub_message(message: Dict[str, Any], services: ServicesDict) -> None:
    """Process a Pub/Sub message.

    Args:
        message: The Pub/Sub message to process
        services: The global services dictionary
    """
    # Extract task type, ID, and user ID
    # Validate required fields
    # Instantiate appropriate processor
    # Call processor.process()
```

```python
@functions_framework.cloud_event
def handle_pubsub(cloud_event: CloudEvent) -> None:
    """Handle a Pub/Sub CloudEvent.

    This is the entry point for the Cloud Function.

    Args:
        cloud_event: The CloudEvent from Pub/Sub
    """
    # Define an async helper function
    # Extract message data from the event
    # Decode base64 data
    # Call process_pubsub_message
```

## Message Processing Flow

1. A Pub/Sub message is received by the `handle_pubsub` function
2. The message is decoded from base64 and parsed as JSON
3. The message is passed to `process_pubsub_message`
4. Required fields are validated
5. An appropriate processor is instantiated based on the message's `task_type`
6. The processor's `process` method is called to execute the task

## Task Type Validation

The module validates that the required fields are present for each task type:

- **Generation Tasks**: Must include `logo_description` and `theme_description`
- **Refinement Tasks**: Must include `refinement_prompt` and `original_image_url`

If required fields are missing, the task is marked as failed with an appropriate error message.

## Error Handling

The module implements multi-level error handling:

1. **Cloud Event Level**: Catches errors in the Pub/Sub message handling
2. **Message Processing Level**: Validates message content and required fields
3. **Task-Specific Level**: Delegates error handling to appropriate processors

All errors are logged with context to aid in debugging.

## Configuration

The module uses environment variables for configuration:

- `CONCEPT_LOG_LEVEL`: Controls the logging level (default: INFO)
- `CONCEPT_SUPABASE_URL`: Supabase URL
- `CONCEPT_SUPABASE_SERVICE_ROLE`: Service role key for Supabase
- `CONCEPT_JIGSAWSTACK_API_KEY`: API key for JigsawStack
- `CONCEPT_JIGSAWSTACK_API_URL`: JigsawStack API URL

## Service Types

The `ServicesDict` type alias represents the dictionary of services used by the worker:

```python
ServicesDict = Dict[str, Any]
```

The services dictionary includes the following keys:

- `"image_service"`: ImageService instance
- `"concept_service"`: ConceptService instance
- `"concept_persistence_service"`: ConceptPersistenceService instance
- `"image_persistence_service"`: ImagePersistenceService instance
- `"task_service"`: TaskService instance
- `"jigsawstack_client"`: JigsawStackClient instance
