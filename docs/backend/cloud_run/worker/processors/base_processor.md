# Base Task Processor

The `BaseTaskProcessor` is an abstract base class that serves as the foundation for all task processors in the worker. It defines a common interface and provides shared functionality for task lifecycle management.

## Class Definition

```python
class BaseTaskProcessor(ABC):
    def __init__(self, task_id: str, user_id: str, message_payload: Dict[str, Any], services: Dict[str, Any]):
        # Initialize instance variables and configure logger

    async def _claim_task(self) -> bool:
        # Attempt to claim the task for processing

    async def _update_task_failed(self, error_message: str) -> None:
        # Update task status to failed

    async def _update_task_completed(self, result_id: str) -> None:
        # Update task status to completed

    @abstractmethod
    async def process(self) -> None:
        # Abstract method to be implemented by subclasses
        pass
```

## Constructor

The constructor initializes the processor instance with task-specific information and sets up logging:

```python
def __init__(self, task_id: str, user_id: str, message_payload: Dict[str, Any], services: Dict[str, Any]):
    self.task_id = task_id
    self.user_id = user_id
    self.payload = message_payload
    self.services = services
    self.logger = logging.getLogger(self.__class__.__name__)  # Processor-specific logger
    self.task_start_time = time.time()
    self.task_service = services["task_service"]
```

## Task Claiming

The `_claim_task` method attempts to claim the task for processing, using the task service:

```python
async def _claim_task(self) -> bool:
    claimed_task = await self.task_service.claim_task_if_pending(task_id=self.task_id, user_id=self.user_id)
    if not claimed_task:
        self.logger.info(f"Task {self.task_id} could not be claimed. Skipping.")
        return False
    self.logger.info(f"[WORKER_TIMING] Task {self.task_id}: Claimed and marked as PROCESSING at {time.time():.2f} ({(time.time() - self.task_start_time):.2f}s elapsed)")
    return True
```

## Task Status Updates

### Updating Task to Failed

The `_update_task_failed` method updates the task status to failed and logs the error:

```python
async def _update_task_failed(self, error_message: str) -> None:
    task_fail_time = time.time()
    self.logger.error(f"Task {self.task_id}: {error_message}")
    self.logger.debug(f"Exception traceback: {traceback.format_exc()}")
    self.logger.error(f"[WORKER_TIMING] Task {self.task_id}: FAILED at {task_fail_time:.2f} (Total Duration: {(task_fail_time - self.task_start_time):.2f}s)")

    try:
        await self.task_service.update_task_status(
            task_id=self.task_id,
            status=TASK_STATUS_FAILED,
            error_message=error_message[:1000]  # Truncate long errors
        )
    except Exception as update_err:
        self.logger.error(f"Task {self.task_id}: Error updating task status to FAILED: {str(update_err)}")
```

### Updating Task to Completed

The `_update_task_completed` method updates the task status to completed with the result ID:

```python
async def _update_task_completed(self, result_id: str) -> None:
    task_end_time = time.time()
    self.logger.info(f"[WORKER_TIMING] Task {self.task_id}: Completed successfully at {task_end_time:.2f} (Total Duration: {(task_end_time - self.task_start_time):.2f}s)")

    await self.task_service.update_task_status(
        task_id=self.task_id,
        status=TASK_STATUS_COMPLETED,
        result_id=result_id
    )

    self.logger.info(f"Task {self.task_id}: Completed successfully with result {result_id}")
```

## Processing

The abstract `process` method defines the interface that all task processors must implement:

```python
@abstractmethod
async def process(self) -> None:
    """Process the task.

    This method must be implemented by each task processor subclass.
    It should contain the main task processing logic.
    """
    pass
```

## Usage

The `BaseTaskProcessor` is not instantiated directly. Instead, specific task processors inherit from it:

```python
class GenerationTaskProcessor(BaseTaskProcessor):
    async def process(self) -> None:
        # Implementation specific to generation tasks

class RefinementTaskProcessor(BaseTaskProcessor):
    async def process(self) -> None:
        # Implementation specific to refinement tasks
```
