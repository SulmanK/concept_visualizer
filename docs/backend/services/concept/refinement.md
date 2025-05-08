# Concept Refinement Service

The `refinement.py` module provides specialized functionality for refining and iteratively improving existing visual concepts.

## Overview

The concept refinement service enables:

1. Iterative improvement of previously generated visual concepts
2. Processing of user feedback to enhance designs
3. Integration with the task-based processing system
4. Asynchronous refinement via Google Cloud Pub/Sub

This service is crucial for implementing an iterative design workflow, allowing users to progressively refine their concepts until they achieve the desired result.

## Key Components

### ConceptRefiner

```python
class ConceptRefiner:
    """Service for refining existing visual concepts."""

    def __init__(self, client: JigsawStackClient):
        """Initialize the concept refiner with required dependencies."""
        self.client = client
        self.logger = get_logger("concept_service.refiner")
```

The ConceptRefiner is responsible for improving existing concepts by applying refinement prompts to generate improved versions.

## Core Functionality

### Refine Image

```python
async def refine_image(
    self,
    original_image_data: bytes,
    refinement_prompt: str,
    strength: float = 0.7,
) -> Dict[str, Any]:
    """Refine an existing image based on refinement instructions."""
```

This method sends an image and refinement instructions to the JigsawStack API to create an improved version.

**Parameters:**

- `original_image_data`: Binary data of the image to refine
- `refinement_prompt`: Textual instructions for refining the image
- `strength`: Control how much to preserve of the original (0.0-1.0)

**Returns:**

- Dictionary containing the refined image information

**Raises:**

- `JigsawStackConnectionError`: If connection to the API fails
- `JigsawStackAuthenticationError`: If authentication fails
- `JigsawStackGenerationError`: If refinement fails
- `ConceptError`: For other refinement-related errors

### Process Refinement Prompt

```python
def process_refinement_prompt(
    self,
    refinement_prompt: str,
    logo_description: Optional[str] = None,
    theme_description: Optional[str] = None,
) -> str:
    """Process a refinement prompt to optimize the refinement outcome."""
```

This method enhances raw refinement instructions to improve the refinement results.

**Parameters:**

- `refinement_prompt`: Original refinement instructions from the user
- `logo_description`: Original or updated logo description (optional)
- `theme_description`: Original or updated theme description (optional)

**Returns:**

- Enhanced refinement prompt optimized for the AI service

## Integration with Task-Based Processing

The refinement service integrates with the task-based processing system:

```python
@router.post("/refine", response_model=TaskResponse)
async def refine_concept(
    request: RefinementRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Refine a concept based on refinement prompt."""
```

This endpoint:

1. Creates a task record in the database
2. Publishes a message to Google Pub/Sub with task details
3. Returns the task information for the client to poll

## Refinement Flow

The refinement process follows these steps:

1. **Task Creation**: Create a task record and publish a message to Pub/Sub
2. **Background Processing**:
   - A Cloud Function processes the Pub/Sub message
   - It downloads the original image from the provided URL
   - It uses the ConceptRefiner to refine the image
   - It stores the refined image and updates the task status
3. **Client Polling**: The client polls the task status endpoint until completion
4. **Result Delivery**: The final result includes the URL of the refined image

## Usage Examples

### Refining a Concept (API Client)

```javascript
// Start concept refinement
async function refineConceptWithPrompt(
  originalImageUrl,
  refinementPrompt,
  logoDesc,
  themeDesc,
) {
  try {
    const response = await fetch("/api/concepts/refine", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        original_image_url: originalImageUrl,
        refinement_prompt: refinementPrompt,
        logo_description: logoDesc,
        theme_description: themeDesc,
      }),
    });

    // Check for conflict (existing task)
    if (response.status === 409) {
      const existingTask = await response.json();
      console.log("A refinement task is already in progress:", existingTask);
      return existingTask;
    }

    const taskData = await response.json();
    return taskData; // Contains task_id to track progress
  } catch (error) {
    console.error("Error starting concept refinement:", error);
    throw error;
  }
}

// Poll task status until complete
async function pollTaskUntilComplete(taskId, onProgress) {
  const poll = async () => {
    const status = await checkTaskStatus(taskId);
    onProgress(status);

    if (status.status === "completed" || status.status === "failed") {
      return status;
    }

    // Wait 2 seconds before checking again
    await new Promise((resolve) => setTimeout(resolve, 2000));
    return poll();
  };

  return poll();
}
```

### Direct Usage in Service Code

```python
from app.services.concept.refinement import ConceptRefiner
from app.services.jigsawstack.client import JigsawStackClient

# Create dependencies
client = JigsawStackClient(api_key="your_api_key")

# Initialize the refiner
refiner = ConceptRefiner(client)

# Load image data
with open("original_image.png", "rb") as f:
    image_data = f.read()

# Refine an image
result = await refiner.refine_image(
    original_image_data=image_data,
    refinement_prompt="Make the logo more minimalist and use a brighter blue color",
    strength=0.8
)

# Access the refinement result
refined_image_data = result.get("binary_data")
```

## Error Handling

The refinement service implements comprehensive error handling:

1. **API Connection Errors**: When the JigsawStack API is unavailable
2. **Authentication Errors**: When API credentials are invalid
3. **Generation Errors**: When the refinement process fails
4. **Task Handling Errors**: When task creation or processing fails

## Performance Considerations

- Refinement operations are performed asynchronously via background tasks
- Task status provides visibility into processing progress
- Cloud Functions scale automatically to handle load
- Concurrent tasks are managed with a "one active task per user" policy

## Related Documentation

- [Concept Service](service.md): Main concept service that uses the refiner
- [Task Service](../task/service.md): Service for managing background tasks
- [JigsawStack Client](../jigsawstack/client.md): Client for the external AI service
- [Refinement API Routes](../../api/routes/concept/refinement.md): API routes that use this service
